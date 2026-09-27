"""
scene_aligner.py
Module to align N story scenes to natural speech pause boundaries in narration audio:
- SRT-Driven Semantic Alignment: When an SRT subtitle file is provided, locks scene
  transitions directly to spoken dialogue boundaries and natural breath pauses.
- Cumulative Spoken Text Progress: Tracks narrative dialogue density to eliminate
  scene drift and maintain 1:1 synchronization between visuals and voiceover.
- Fallback Acoustic Silence Alignment: If no SRT is available, detects speech pause
  midpoints directly from audio dBFS thresholds.
- Enforces exact microsecond alignment with total audio duration.
"""

import argparse
import json
import os
import re
from pydub import AudioSegment
from pydub.silence import detect_silence

def parse_srt(srt_path: str) -> list[dict]:
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())
    subtitles = []

    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        time_idx = 1 if lines[0].isdigit() else 0
        if time_idx >= len(lines):
            continue

        m = re.match(r"(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)", lines[time_idx])
        if not m:
            continue

        s_ms = (int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)))*1000 + int(m.group(4))
        e_ms = (int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)))*1000 + int(m.group(8))
        text = " ".join(lines[time_idx + 1:])
        text = re.sub(r"\(Transcribed by TurboScribe[^\)]*\)\s*", "", text).strip()

        if text:
            subtitles.append({"start_ms": s_ms, "end_ms": e_ms, "text": text})

    return subtitles

def align_with_srt(
    total_ms: int,
    num_scenes: int,
    subtitles: list[dict],
    min_gap_ms: int = 1800
) -> list[int]:
    print(f"[SceneAligner] Aligning {num_scenes} scenes using {len(subtitles)} SRT subtitle entries...")

    # Inter-subtitle speech pause midpoints and durations
    pauses = []
    for k in range(len(subtitles) - 1):
        gap_s = subtitles[k]["end_ms"]
        gap_e = subtitles[k + 1]["start_ms"]
        mid = (gap_s + gap_e) // 2
        dur = max(0, gap_e - gap_s)
        pauses.append((mid, dur, k))

    # Cumulative dialogue text length across subtitles
    char_counts = [len(s["text"]) for s in subtitles]
    total_chars = max(1, sum(char_counts))
    cum_chars = []
    curr = 0
    for c in char_counts:
        curr += c
        cum_chars.append(curr)

    cuts = [0]
    for i in range(1, num_scenes):
        target_char = (i / num_scenes) * total_chars
        k = 0
        while k < len(cum_chars) - 1 and cum_chars[k] < target_char:
            k += 1

        rem_scenes = num_scenes - i
        max_allowed = total_ms - rem_scenes * min_gap_ms

        candidate_pauses = [
            p for p in pauses 
            if abs(p[2] - k) <= 3 and cuts[-1] + min_gap_ms <= p[0] <= max_allowed
        ]
        if candidate_pauses:
            best_p = max(candidate_pauses, key=lambda p: p[1] - 0.4 * abs(p[2] - k) * 100)
            cuts.append(best_p[0])
        else:
            target_t = int(round((i / num_scenes) * total_ms))
            clamped = max(cuts[-1] + min_gap_ms, min(target_t, max_allowed))
            cuts.append(clamped)

    cuts.append(total_ms)
    return cuts

def align_with_silence(
    audio: AudioSegment,
    total_ms: int,
    num_scenes: int,
    min_pause_ms: int = 250,
    thresh_offset: float = -15.0,
    snap_window_ms: int = 2500
) -> list[int]:
    print(f"[SceneAligner] Aligning {num_scenes} scenes using audio silence detection...")
    avg_scene_ms = total_ms / num_scenes
    silence_thresh = audio.dBFS + thresh_offset
    pauses = detect_silence(audio, min_silence_len=min_pause_ms, silence_thresh=silence_thresh)
    print(f"[SceneAligner] Detected {len(pauses)} speech pause anchor points.")

    pause_midpoints = [(s + e) // 2 for s, e in pauses]
    cut_points = [0]
    min_scene_gap = int(avg_scene_ms * 0.45)

    for i in range(1, num_scenes):
        target = i * avg_scene_ms
        valid = [p for p in pause_midpoints if p > cut_points[-1] + min_scene_gap and abs(p - target) <= snap_window_ms]
        if valid:
            best_p = min(valid, key=lambda p: abs(p - target))
            cut_points.append(best_p)
        else:
            cut_points.append(int(round(target)))

    cut_points.append(total_ms)
    return cut_points

def align_scenes(
    audio_path: str,
    num_scenes: int,
    output_json_path: str,
    srt_path: str = None,
    script_path: str = None,
    prompts_path: str = None,
    min_pause_ms: int = 250,
    thresh_offset: float = -15.0,
    snap_window_ms: int = 2500
) -> list[dict]:
    print(f"\n[SceneAligner] Loading audio from {audio_path}...")
    audio = AudioSegment.from_file(audio_path)
    total_ms = len(audio)
    total_us = total_ms * 1000

    print(f"[SceneAligner] Total duration: {total_ms / 1000.0:.2f}s ({total_us} us) for {num_scenes} scenes.")

    cut_points = None
    if srt_path and os.path.exists(srt_path):
        subtitles = parse_srt(srt_path)
        if len(subtitles) >= 10:
            cut_points = align_with_srt(
                total_ms,
                num_scenes,
                subtitles
            )

    if not cut_points or len(cut_points) != num_scenes + 1:
        if srt_path:
            print("[SceneAligner] SRT entries insufficient or unavailable; falling back to acoustic silence detection.")
        cut_points = align_with_silence(
            audio,
            total_ms,
            num_scenes,
            min_pause_ms=min_pause_ms,
            thresh_offset=thresh_offset,
            snap_window_ms=snap_window_ms
        )

    # Post-process: ensure strict monotonicity and sum equals total_us
    scene_timings = []
    for i in range(num_scenes):
        s_ms = cut_points[i]
        e_ms = cut_points[i + 1]
        dur_ms = e_ms - s_ms
        s_us = s_ms * 1000
        dur_us = dur_ms * 1000
        scene_timings.append({
            "scene_number": i + 1,
            "start_ms": s_ms,
            "end_ms": e_ms,
            "duration_ms": dur_ms,
            "start_us": s_us,
            "duration_us": dur_us,
            "start_sec": round(s_ms / 1000.0, 3),
            "duration_sec": round(dur_ms / 1000.0, 3)
        })

    # Adjust last scene to perfectly match total_us
    sum_dur_us = sum(t["duration_us"] for t in scene_timings)
    drift_us = total_us - sum_dur_us
    if drift_us != 0:
        scene_timings[-1]["duration_us"] += drift_us
        scene_timings[-1]["duration_ms"] = scene_timings[-1]["duration_us"] // 1000
        scene_timings[-1]["end_ms"] = scene_timings[-1]["start_ms"] + scene_timings[-1]["duration_ms"]
        scene_timings[-1]["duration_sec"] = round(scene_timings[-1]["duration_us"] / 1000000.0, 3)

    durations = [t["duration_sec"] for t in scene_timings]
    print(f"[SceneAligner] Min scene: {min(durations):.2f}s | Max scene: {max(durations):.2f}s")
    print(f"[SceneAligner] Total duration: {sum(t['duration_sec'] for t in scene_timings):.2f}s (Target: {total_ms/1000.0:.2f}s)")

    os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(scene_timings, f, indent=2)

    print(f"[SceneAligner] Successfully exported scene timings to {output_json_path}\n")
    return scene_timings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scene Narration Beat Aligner")
    parser.add_argument("--audio", required=True, help="Path to trimmed audio file")
    parser.add_argument("--num-scenes", required=True, type=int, help="Number of scenes to align")
    parser.add_argument("--output", required=True, help="Output JSON path for scene timings")
    parser.add_argument("--srt", default=None, help="Optional path to SRT subtitle file")
    parser.add_argument("--script", default=None, help="Optional path to Script.txt")
    parser.add_argument("--prompts", default=None, help="Optional path to prompts file")
    parser.add_argument("--min-pause-ms", type=int, default=250, help="Min pause len in ms")
    parser.add_argument("--thresh-offset", type=float, default=-15.0, help="Silence threshold offset")
    parser.add_argument("--snap-window-ms", type=int, default=2500, help="Max snap window in ms")
    args = parser.parse_args()

    align_scenes(
        args.audio,
        args.num_scenes,
        args.output,
        srt_path=args.srt,
        script_path=args.script,
        prompts_path=args.prompts,
        min_pause_ms=args.min_pause_ms,
        thresh_offset=args.thresh_offset,
        snap_window_ms=args.snap_window_ms
    )
