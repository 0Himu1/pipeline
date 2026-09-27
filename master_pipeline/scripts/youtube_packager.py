"""
youtube_packager.py
Stage 5: Final Cleanup & YouTube Distribution Packaging
- Creates the exports/ folder for deliverables.
- Moves any exported .mp4 video files from project root to exports/.
- Cleans up heavy temporary intermediate files (.wav) after CapCut ingestion.
- Automatically generates youtube_metadata.txt with:
    1. 5 High-CTR title options (Curiosity Gap, Emotional Hook, SEO, Mobile Short, Poetic).
    2. High-retention description with above-the-fold hook and story synopsis.
    3. Auto-generated chapter timestamps from scene_timings.json.
    4. Art direction & audio credits.
    5. SEO search tags and hashtags.
"""

import argparse
import glob
import json
import os
import shutil
import sys

def ms_to_time(ms):
    total_sec = int(ms // 1000)
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins}:{secs:02d}"

def generate_youtube_metadata(project_name, script_path, timings_path, output_path):
    print(f"[YouTubePackager] Generating YouTube metadata for '{project_name}'...")
    
    # 1. Parse Timestamps
    chapters = []
    if os.path.exists(timings_path):
        try:
            with open(timings_path, 'r', encoding='utf-8') as f:
                timings = json.load(f)
            num_scenes = len(timings)
            # Create 10-14 logical chapters across the scenes
            step = max(1, num_scenes // 12)
            for idx in range(0, num_scenes, step):
                start_ms = timings[idx].get("start_ms", 0)
                time_str = ms_to_time(start_ms)
                chapters.append(f"{time_str} - Chapter {len(chapters) + 1} (Scene {idx + 1})")
        except Exception as e:
            print(f"[YouTubePackager] Warning: Could not parse timings: {e}")

    # Fallback chapters if timings was missing
    if not chapters:
        chapters = [
            "0:00 - Introduction & Opening Scene",
            "1:30 - The Turning Point",
            "3:45 - The Unfolding Journey",
            "6:15 - A Moment of Realization",
            "8:30 - The Resolution & Closing Reflection"
        ]

    # 2. Extract or infer story synopsis
    story_hook = "A quiet, atmospheric story about what matters most, told through gentle hand-drawn animation."
    if script_path and os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines[:8]:
                if len(line) > 50 and not line.lower().startswith("chunk"):
                    story_hook = line
                    break
        except Exception as e:
            pass

    metadata_content = f"""================================================================================
YOUTUBE METADATA & DISTRIBUTION PACKAGE: {project_name.upper()}
================================================================================
Generated for: {project_name}
Art Aesthetic: Hand-drawn Watercolor & Ink Wash (The Tale of Princess Kaguya Style)
Target Audience: Bedtime Stories, Mindful Living, Audiobooks, Calming Stories

--------------------------------------------------------------------------------
1. RECOMMENDED TITLES (Select based on your channel niche)
--------------------------------------------------------------------------------
OPTION 1 (Curiosity Gap / Emotional Hook - HIGHEST RECOMMENDED CTR):
{project_name} | A Calming Story About Time and What Truly Matters

OPTION 2 (Thought-Provoking / Narrative Hook):
The Choice That Changed Everything | An Animated Watercolor Story

OPTION 3 (Short & High-Impact - Mobile Optimized < 55 Characters):
{project_name} | A Gentle Tale of Patience

OPTION 4 (Search & Discovery SEO):
{project_name} — Animated Japanese Watercolor Story with Peaceful Narration

OPTION 5 (Poetic & Cinematic):
What Grows When You Leave It Alone | A Studio Ghibli Inspired Animation


--------------------------------------------------------------------------------
2. VIDEO DESCRIPTION (Copy & Paste directly into YouTube Studio)
--------------------------------------------------------------------------------
{story_hook}

Take a slow breath, grab a warm cup of tea, and let this peaceful narrative wash over you.

🌿 TIMESTAMPS / CHAPTERS:
""" + "\n".join(chapters) + f"""

🎨 VISUALS & ART DIRECTION:
Hand-drawn watercolor and ink wash illustrations inspired by Studio Ghibli and Isao Takahata's *The Tale of Princess Kaguya*. Features expressive pencil contours, soft desaturated washes bleeding across unfinished sketch borders, and warm atmospheric lighting.

🎙️ AUDIO & NARRATION:
Mixed and mastered to audiobook standards with non-clipped speech acoustics and natural breathing pauses, providing a calm, stress-relieving audio sanctuary.

💬 REFLECTION QUESTION FOR THE COMMENTS:
What part of this story resonated with you the most? Tell us your thoughts below.

✨ If this story brought you stillness, consider subscribing and sharing it with someone who needs calm today.

#Storytelling #PrincessKaguya #WatercolorAnimation #Mindfulness #BedtimeStory #CalmStories #AudioStory


--------------------------------------------------------------------------------
3. YOUTUBE TAGS (Copy & Paste into the Tags Box in YouTube Studio)
--------------------------------------------------------------------------------
{project_name.lower()}, animated story, princess kaguya style, watercolor animation, calming bedtime story, audio story for adults, ghibli aesthetic, peaceful storytelling, relax and sleep story, mindfulness story, emotional animation, soothing voiceover story, quiet life story


--------------------------------------------------------------------------------
4. HASHTAGS (Primary 3-5 tags for mobile header)
--------------------------------------------------------------------------------
#Storytelling #WatercolorAnimation #BedtimeStory #Mindfulness #CalmStories
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(metadata_content)
    print(f"[YouTubePackager] Saved metadata to: {output_path}")

def package_project(work_dir, project_name, script_path=None, timings_path=None, clean_temp=True):
    print(f"\n[YouTubePackager] Packaging project '{project_name}' in {work_dir}...")
    exports_dir = os.path.join(work_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    # 1. Move any exported video (.mp4 / .mov) from work_dir to exports_dir
    video_files = glob.glob(os.path.join(work_dir, "*.mp4")) + glob.glob(os.path.join(work_dir, "*.mov"))
    for vf in video_files:
        dest_vf = os.path.join(exports_dir, os.path.basename(vf))
        print(f"[YouTubePackager] Moving exported video: {vf} -> {dest_vf}")
        shutil.move(vf, dest_vf)

    # 2. Cleanup redundant intermediate heavy uncompressed WAVs
    if clean_temp:
        temp_wav = os.path.join(work_dir, "trimmed_voiceover.wav")
        if os.path.exists(temp_wav):
            print(f"[YouTubePackager] Cleaning up intermediate WAV: {temp_wav}")
            try:
                os.remove(temp_wav)
            except Exception as e:
                print(f"[YouTubePackager] Note: Could not remove WAV: {e}")

    # 3. Generate YouTube Metadata file
    metadata_txt = os.path.join(exports_dir, "youtube_metadata.txt")
    if not os.path.exists(metadata_txt):
        if not timings_path:
            timings_path = os.path.join(work_dir, "scene_timings.json")
        if not script_path:
            potential_scripts = glob.glob(os.path.join(work_dir, "*script*.txt")) + glob.glob(os.path.join(work_dir, "*Script*.txt"))
            script_path = potential_scripts[0] if potential_scripts else None
        generate_youtube_metadata(project_name, script_path, timings_path, metadata_txt)
    else:
        print(f"[YouTubePackager] youtube_metadata.txt already exists at {metadata_txt}")

    # 4. Design 3 High-CTR Thumbnails for YouTube (16:9) and Facebook (1:1)
    try:
        from thumbnail_designer import design_project_thumbnails
        design_project_thumbnails(work_dir, project_name)
    except Exception as e:
        print(f"[YouTubePackager] Note: Running thumbnail_designer via subprocess fallback: {e}")
        import subprocess
        script_dir = os.path.dirname(os.path.abspath(__file__))
        designer_py = os.path.join(script_dir, "thumbnail_designer.py")
        if os.path.exists(designer_py):
            subprocess.run([sys.executable, designer_py, "--work-dir", work_dir, "--project-name", project_name])

    print(f"[YouTubePackager] Stage 5 packaging complete! Exports available at: {exports_dir}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 5: Final Cleanup & YouTube Packaging")
    parser.add_argument("--work-dir", required=True, help="Path to project directory")
    parser.add_argument("--project-name", required=True, help="Name of project")
    parser.add_argument("--script", default=None, help="Path to Script.txt (optional)")
    parser.add_argument("--timings", default=None, help="Path to scene_timings.json (optional)")
    parser.add_argument("--no-clean", action="store_true", help="Skip temporary file cleanup")
    args = parser.parse_args()

    package_project(
        work_dir=args.work_dir,
        project_name=args.project_name,
        script_path=args.script,
        timings_path=args.timings,
        clean_temp=not args.no_clean
    )
