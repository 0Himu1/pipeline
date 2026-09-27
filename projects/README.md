# Projects Directory

This directory stores all individual story video production projects. The root repository remains clean and organized.

---

## 1. Directory Layout

```
d:\Himu\Luna\projects\
├── README.md                 # This guide
├── <project_name>/           # Individual story project
│   ├── Script.txt            # Narrative text script (15 chunks)
│   ├── <slug>-character-prompts.txt    # Character reference portraits
│   ├── <slug>-image-prompts.txt        # 87-Scene Kaguya visual prompts
│   ├── <project>-enhanced-v2.mp3       # Adobe Podcast enhanced audio
│   ├── <project>-enhanced-v2.srt       # Subtitle transcript [MANDATORY]
│   ├── Images.zip            # 87 generated AI scene images
│   ├── sequenced_images/     # Deterministically mapped 001_ to 087_
│   ├── scene_timings.json    # Microsecond speech-aligned cut boundaries
│   ├── trimmed_voiceover.mp3 # Dead-air trimmed master voiceover
│   ├── trimmed_voiceover.srt # Re-aligned subtitle transcript
│   └── exports/              # Distribution deliverables
│       ├── thumbnail_01_*.jpg
│       ├── thumbnail_02_*.jpg
│       ├── thumbnail_03_*.jpg
│       └── youtube_metadata.txt
```

---

## 2. How to Start a New Project

1. Create a new folder inside `projects/`, for example:
   `d:\Himu\Luna\projects\my_new_story\`
2. Drop your **`Script.txt`** into that folder.
3. Run the pipeline:
   ```powershell
   python d:\Himu\Luna\master_pipeline\scripts\run_pipeline.py --project-dir "d:\Himu\Luna\projects\my_new_story"
   ```
   The pipeline will auto-generate:
   - Voiceover audio (`my_new_story.mp3` via edge-tts Sonia British calm voice).
   - Character reference prompts (`my-new-story-character-prompts.txt`).
   - 87 scene image prompts (`my-new-story-kaguya-image-prompts.txt`).
4. **Handoff Actions**:
   - Enhance the audio on Adobe Podcast $\rightarrow$ save as `my_new_story-enhanced-v2.mp3`.
   - Transcribe audio to subtitle file $\rightarrow$ save as `my_new_story-enhanced-v2.srt` (**MANDATORY**).
   - Generate character portraits first from `*-character-prompts.txt` to establish character consistency.
   - Generate the 87 scene images using the character references, and place them as `Images.zip`.
5. Re-run the command $\rightarrow$ CapCut project is built automatically!

---

## 3. Automated Execution Command

```bash
python d:\Himu\Luna\master_pipeline\scripts\run_pipeline.py --project-dir "d:\Himu\Luna\projects\my_new_story"
```

The pipeline will automatically:
1. Compact dead-air silences with zero consonant clipping (`trimmed_voiceover.mp3`).
2. Re-align subtitle timestamps to match trimmed audio (`trimmed_voiceover.srt`).
3. Extract and match all 87 images with IDF token weighting & bigram phrases (`sequenced_images/001_` to `087_`).
4. Align visual cuts strictly to natural speech breath pauses from the SRT (`scene_timings.json`).
5. Assemble the CapCut Desktop draft with Ken Burns Cubic easing and atmospheric visual filters.
6. Generate `exports/youtube_metadata.txt` (5 high-CTR titles, timestamps, SEO tags) and clean up temporary files.

