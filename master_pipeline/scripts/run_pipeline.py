"""
run_pipeline.py
Master Smart Orchestrator for Story Video Production.
Supports end-to-end intelligent execution across two phases:

PHASE 1: PRE-PRODUCTION (Automated if inputs are missing)
  - Stage 0a: Speech Synthesis via edge-tts (if audio is not yet generated)
  - Stage 0b: 87-Scene Prompt Generation (if prompts.txt is not yet generated)
  - User Handoff: Prompts user to enhance audio on Adobe Podcast, generate SRT, & generate images.

PHASE 2: POST-PRODUCTION (Auto-triggered when images, audio & SRT are present)
  - Stage 1: Professional voiceover audio trimming with Rulebook pacing & automatic SRT re-alignment.
  - Stage 2: Image extraction, global bipartite matching & sequencing (001_ to 087_).
  - Stage 3: SRT-driven scene timing alignment snapping to natural speech pauses.
  - Stage 4: CapCut project building with Ken Burns Cubic easing & atmospheric effects.
  - Stage 5: Final cleanup & YouTube distribution packaging (metadata & 3 thumbnails).
"""

import argparse
import glob
import os
import re
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable

def run_step(cmd, desc):
    print(f"\n{'='*60}")
    print(f">> STAGE: {desc}")
    print(f"{'='*60}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"[ERROR] Stage '{desc}' failed with exit code {res.returncode}")
        sys.exit(res.returncode)

def find_script(work_dir):
    matches = glob.glob(os.path.join(work_dir, "*script*.txt")) + glob.glob(os.path.join(work_dir, "*Script*.txt"))
    return matches[0] if matches else None

def find_prompts(work_dir):
    matches = glob.glob(os.path.join(work_dir, "*prompt*.txt")) + glob.glob(os.path.join(work_dir, "*Prompt*.txt"))
    # Prioritize scene image prompts over character prompts
    scene_matches = [m for m in matches if "character" not in os.path.basename(m).lower() and "char" not in os.path.basename(m).lower()]
    return scene_matches[0] if scene_matches else (matches[0] if matches else None)

def find_char_prompts(work_dir):
    matches = glob.glob(os.path.join(work_dir, "*character*.txt")) + glob.glob(os.path.join(work_dir, "*char*.txt"))
    return matches[0] if matches else None

def find_audio(work_dir, project_name):
    # 1. Prioritize enhanced audio from Adobe Podcast
    enhanced = glob.glob(os.path.join(work_dir, "*enhanced*.mp3")) + glob.glob(os.path.join(work_dir, "*enhanced*.wav"))
    if enhanced:
        return enhanced[0]
    
    # 2. Project name audio
    proj_audio = os.path.join(work_dir, f"{project_name}.mp3")
    if os.path.exists(proj_audio):
        return proj_audio
    proj_audio_wav = os.path.join(work_dir, f"{project_name}.wav")
    if os.path.exists(proj_audio_wav):
        return proj_audio_wav

    # 3. Any non-intermediate MP3
    all_mp3 = [f for f in glob.glob(os.path.join(work_dir, "*.mp3")) if not f.endswith("trimmed_voiceover.mp3")]
    if all_mp3:
        return all_mp3[0]

    return None

def find_srt(work_dir, project_name):
    # 1. Prioritize enhanced srt
    enhanced = glob.glob(os.path.join(work_dir, "*enhanced*.srt"))
    if enhanced:
        return enhanced[0]

    # 2. Project name srt
    proj_srt = os.path.join(work_dir, f"{project_name}.srt")
    if os.path.exists(proj_srt):
        return proj_srt

    # 3. Any non-intermediate srt
    all_srt = [f for f in glob.glob(os.path.join(work_dir, "*.srt")) if not f.endswith("trimmed_voiceover.srt")]
    if all_srt:
        return all_srt[0]

    return None

def find_images(work_dir):
    # 1. Zip archive
    zips = [f for f in glob.glob(os.path.join(work_dir, "*.zip")) if not os.path.basename(f).startswith("_")]
    if zips:
        # Prioritize Images.zip or images.zip
        for z in zips:
            if "image" in os.path.basename(z).lower():
                return z
        return zips[0]

    # 2. Existing folder of images
    for folder_name in ["sequenced_images", "generated_images", "images"]:
        p = os.path.join(work_dir, folder_name)
        if os.path.isdir(p):
            imgs = [f for f in os.listdir(p) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if len(imgs) > 10:
                return p

    return None

def main():
    parser = argparse.ArgumentParser(description="Master Story Video Pipeline Runner")
    parser.add_argument("--project-dir", "--work-dir", dest="work_dir", default=".", help="Project directory path")
    parser.add_argument("--project-name", default=None, help="CapCut Project Draft Name (defaults to folder name)")
    parser.add_argument("--script", default=None, help="Path to Script.txt")
    parser.add_argument("--prompts", default=None, help="Path to prompts.txt")
    parser.add_argument("--char-prompts", default=None, help="Path to character prompts.txt")
    parser.add_argument("--audio", default=None, help="Path to audio file (MP3/WAV)")
    parser.add_argument("--srt", default=None, help="Path to SRT subtitle file")
    parser.add_argument("--no-srt", action="store_true", help="Bypass SRT requirement and fall back to acoustic silence alignment")
    parser.add_argument("--images", default=None, help="Path to images directory or zip archive")
    parser.add_argument("--voice", default="en-GB-SoniaNeural", help="TTS Voice (default: en-GB-SoniaNeural)")
    parser.add_argument("--rate", default="-8%", help="TTS Rate (default: -8%%)")
    args = parser.parse_args()

    work_dir = os.path.abspath(args.work_dir)
    os.makedirs(work_dir, exist_ok=True)

    project_name = args.project_name
    if not project_name:
        project_name = os.path.basename(work_dir)

    print(f"\n{'='*60}")
    print(f"MASTER STORY VIDEO PIPELINE: {project_name}")
    print(f"Directory: {work_dir}")
    print(f"{'='*60}\n")

    # 1. Discover or validate inputs
    script_path = args.script or find_script(work_dir)
    prompts_path = args.prompts or find_prompts(work_dir)
    char_prompts_path = args.char_prompts or find_char_prompts(work_dir)
    audio_path = args.audio or find_audio(work_dir, project_name)
    srt_path = args.srt or (None if args.no_srt else find_srt(work_dir, project_name))
    images_path = args.images or find_images(work_dir)

    just_generated_audio = False
    just_generated_prompts = False

    # ---------------------------------------------------------
    # PHASE 1: PRE-PRODUCTION AUTO-GENERATION (If missing)
    # ---------------------------------------------------------
    # A. Check Audio
    if not audio_path:
        if not script_path:
            print("[ERROR] Neither voiceover audio nor Script.txt found in project directory!")
            sys.exit(1)
        print("[Pipeline] No voiceover audio found. Auto-generating Stage 0a Speech Synthesis...")
        synth_script = os.path.join(SCRIPTS_DIR, "speech_synthesizer.py")
        audio_out = os.path.join(work_dir, f"{project_name}.mp3")
        cmd_synth = f'"{PYTHON_EXE}" "{synth_script}" --script "{script_path}" --output "{audio_out}" --voice "{args.voice}" --rate="{args.rate}"'
        run_step(cmd_synth, "0a. Voiceover Speech Synthesis (edge-tts)")
        audio_path = audio_out
        just_generated_audio = True
    else:
        print(f"[Pipeline] Audio detected: {audio_path}")

    # B. Check Prompts
    if not prompts_path:
        if not script_path:
            print("[ERROR] Neither prompts file nor Script.txt found in project directory!")
            sys.exit(1)
        print("[Pipeline] No prompts file found. Auto-generating Stage 0b 87-Scene Kaguya Prompts & Character Prompts...")
        prompt_script = os.path.join(SCRIPTS_DIR, "prompt_generator.py")
        clean_slug = re.sub(r'[^a-zA-Z0-9]+', '-', project_name).strip('-').lower()
        prompts_out = os.path.join(work_dir, f"{clean_slug}-kaguya-image-prompts.txt")
        char_prompts_out = os.path.join(work_dir, f"{clean_slug}-character-prompts.txt")
        cmd_prompts = f'"{PYTHON_EXE}" "{prompt_script}" --script "{script_path}" --output "{prompts_out}" --char-output "{char_prompts_out}" --count 87'
        run_step(cmd_prompts, "0b. 87-Scene Kaguya Image & Character Prompt Generation")
        prompts_path = prompts_out
        char_prompts_path = char_prompts_out
        just_generated_prompts = True
    else:
        print(f"[Pipeline] Scene Prompts detected: {prompts_path}")
        if char_prompts_path:
            print(f"[Pipeline] Character Prompts detected: {char_prompts_path}")

    # ---------------------------------------------------------
    # CHECKPOINT: HUMAN-IN-THE-LOOP ASSET HANDOFF
    # ---------------------------------------------------------
    requires_srt = not args.no_srt
    if not images_path or (requires_srt and not srt_path) or just_generated_audio or just_generated_prompts:
        print(f"\n{'='*70}")
        print(f">> PRE-PRODUCTION COMPLETED (AWAITING USER ASSETS)")
        print(f"{'='*70}")
        print(f"Project: {project_name}")
        print(f"\n1. Voiceover Audio: {audio_path}")
        print(f"   [ACTION]: Enhance this audio at Adobe Podcast (https://podcast.adobe.com/enhance)")
        print(f"             Save the enhanced file as '{project_name}-enhanced-v2.mp3' in:")
        print(f"             {work_dir}")
        print(f"\n2. Subtitle / Transcript File (.srt) [MANDATORY]:")
        print(f"   [ACTION]: Transcribe the enhanced audio (via TurboScribe, Whisper, or Adobe)")
        print(f"             Save the file as '{project_name}-enhanced-v2.srt' in:")
        print(f"             {work_dir}")
        print(f"             * MANDATORY: Guarantees 100% word-for-word timeline sync with the VO!")
        print(f"\n3. Character Generation Prompts: {char_prompts_path or 'Generated in folder'}")
        print(f"   [ACTION]: Generate character portrait reference images first for visual consistency!")
        print(f"\n4. Scene Image Prompts: {prompts_path}")
        print(f"   [ACTION]: Generate the 87 scene images using the character references, and place them as")
        print(f"             'Images.zip' in:")
        print(f"             {work_dir}")
        print(f"\nWhen all assets are placed in the folder, run:")
        print(f'  python "{os.path.abspath(__file__)}" --project-dir "{work_dir}"')
        print(f"{'='*70}\n")
        return

    # ---------------------------------------------------------
    # PHASE 2: POST-PRODUCTION & CAPCUT BUILDING
    # ---------------------------------------------------------
    print(f"\n[Pipeline] All pre-production assets present!")
    print(f"  - Audio:         {audio_path}")
    print(f"  - SRT Subtitles: {srt_path}")
    print(f"  - Scene Prompts: {prompts_path}")
    if char_prompts_path:
        print(f"  - Char Prompts:  {char_prompts_path}")
    print(f"  - Images:        {images_path}")
    print(f"  - Script:        {script_path}")

    trimmed_wav = os.path.join(work_dir, "trimmed_voiceover.wav")
    trimmed_mp3 = os.path.join(work_dir, "trimmed_voiceover.mp3")
    trimmed_srt = os.path.join(work_dir, "trimmed_voiceover.srt")
    images_out = os.path.join(work_dir, "sequenced_images")
    timings_json = os.path.join(work_dir, "scene_timings.json")

    # Stage 1: Audio Trimming & SRT re-alignment
    audio_script = os.path.join(SCRIPTS_DIR, "audio_trimmer.py")
    cmd_audio = f'"{PYTHON_EXE}" "{audio_script}" --input "{audio_path}" --output-wav "{trimmed_wav}" --output-mp3 "{trimmed_mp3}"'
    if srt_path:
        cmd_audio += f' --srt "{srt_path}" --output-srt "{trimmed_srt}"'
    run_step(cmd_audio, "1. Professional Audio Trimming & Subtitle Alignment")

    # Stage 2: Image Processing
    image_script = os.path.join(SCRIPTS_DIR, "image_processor.py")
    cmd_images = f'"{PYTHON_EXE}" "{image_script}" --prompts "{prompts_path}" --input "{images_path}" --output "{images_out}"'
    run_step(cmd_images, "2. Image Extraction, Matching & Sequencing")

    # Count prompts
    with open(prompts_path, 'r', encoding='utf-8') as f:
        num_prompts = len([l for l in f if l.strip()])

    # Stage 3: Scene Alignment with SRT
    active_srt = trimmed_srt if os.path.exists(trimmed_srt) else (srt_path if srt_path and os.path.exists(srt_path) else None)
    align_script = os.path.join(SCRIPTS_DIR, "scene_aligner.py")
    cmd_align = f'"{PYTHON_EXE}" "{align_script}" --audio "{trimmed_wav}" --num-scenes {num_prompts} --output "{timings_json}"'
    if active_srt:
        cmd_align += f' --srt "{active_srt}"'
    if script_path:
        cmd_align += f' --script "{script_path}"'
    if prompts_path:
        cmd_align += f' --prompts "{prompts_path}"'
    run_step(cmd_align, "3. Scene Narration Beat & SRT Speech Alignment")

    # Stage 4: CapCut Project Building
    builder_script = os.path.join(SCRIPTS_DIR, "capcut_builder.js")
    cmd_builder = f'node "{builder_script}" --project-name "{project_name}" --audio "{trimmed_wav}" --images-dir "{images_out}" --timings "{timings_json}"'
    run_step(cmd_builder, "4. CapCut Draft Building & Synchronization")

    # Stage 5: Final Cleanup & YouTube Distribution Packaging
    packager_script = os.path.join(SCRIPTS_DIR, "youtube_packager.py")
    script_arg = f'--script "{script_path}"' if script_path else ''
    cmd_packager = f'"{PYTHON_EXE}" "{packager_script}" --work-dir "{work_dir}" --project-name "{project_name}" {script_arg}'
    run_step(cmd_packager, "5. Final Cleanup & YouTube Distribution Packaging")

    print(f"\n{'='*60}")
    print(f"PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Project '{project_name}' is ready to open in CapCut Desktop.")
    print(f"YouTube distribution package ready at: {os.path.join(work_dir, 'exports')}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
