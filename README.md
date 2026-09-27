# 🎬 Luna: Autonomous Story Video & Social Distribution Pipeline

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![CapCut MCP](https://img.shields.io/badge/CapCut-MCP%20Server-red.svg)](./capcut-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

**Luna** is an end-to-end, reproducible production engine designed for high-retention philosophical video essays and social media storytelling (in the spirit of *Pursuit of Wonder*, *Aperture*, and *Studio Ghibli*). 

It automates the full journey from **conversational concept ideation** to a fully assembled, motion-choreographed **CapCut Desktop timeline**, followed by **Canva-standard multi-platform thumbnail and social packaging**.

---

## 🚀 Key Capabilities

* **🧠 Conversational Story Director**: Bridges ideation to production. Generates 15-chunk narrative scripts engineered with the *Retention Anchor* methodology and *Zoom-In / Zoom-Out* cognitive pacing.
* **🎨 Curated Visual Styles Library**: 5 production-tested visual aesthetics (Princess Kaguya Ink & Watercolor, Studio Ghibli Gouache, 35mm Nostalgic Film, Nordic Editorial Cutout, and Rembrandt Chiaroscuro Oil).
* **🗣️ Automated Voiceover & Breath Synthesis**: Microsoft Edge Neural TTS integration with calibrated `-8%` storytelling cadence and $1.4\text{s}$ chunk breathing pauses.
* **🎭 Character Consistency Engine**: Automatically extracts character profiles and generates standalone reference portrait prompts (`*-character-prompts.txt`) before scene generation.
* **⏱️ SRT-Driven Speech Pause Alignment**: Mathematically aligns cuts strictly to natural speech pauses rather than arbitrary video durations.
* **✂️ Native CapCut Builder via MCP**: Constructs native CapCut Desktop drafts with non-overlapping audio, cubic Ken Burns motion (slow zooms, diagonal pan drifts), and atmospheric blur/vignette effects.
* **🖼️ Canva-Standard Graphic Thumbnail Designer**: Replaces raw scene copies with high-CTR 3-archetype graphic thumbnails (Action Figure Emotion, Mystery Anchor, Contrast Dilemma) for **YouTube (16:9 - 1920x1080)** and **Facebook (1:1 - 1080x1080)** with multi-directional drop shadow typography.

---

## 🏗️ End-to-End Pipeline Architecture

```mermaid
flowchart TD
    %% PHASE 0: CONVERSATIONAL STUDIO
    subgraph P0["PHASE 0: CONVERSATIONAL STUDIO (Interactive AI Director)"]
        UserPrompt["User: 'Let's make a 15-minute video on [Topic]'"] --> AgentMenu["Agent Presents Topic Blueprint & Duration Options<br/>(8m / 12-15m / 18-20m)"]
        AgentMenu --> StyleChoice["User Selects Visual Style & Voice Pairing<br/>(06_VISUAL_STYLES_LIBRARY)"]
        StyleChoice --> ScriptGen["Agent Crafts 15-Chunk Narrative Script<br/>(07_STORY_IDEATION_ENGINE)"]
        ScriptGen --> AutoDir["Auto-Creates 'projects/<Project_Name>/'<br/>and writes 'Script.txt'"]
    end

    %% PHASE 1: PRE-PRODUCTION AUTO-GENERATION
    subgraph P1["PHASE 1: PRE-PRODUCTION AUTOMATION (run_pipeline.py)"]
        AutoDir --> S0a["Stage 0a: Edge-TTS Narration Synthesis<br/>(Auto-generates voiceover with 1.4s breathing pauses)"]
        AutoDir --> S0b["Stage 0b: Prompt & Character Extraction<br/>1. *-character-prompts.txt (Consistent portraits)<br/>2. *-image-prompts.txt (Exact scene storyboard)"]
    end

    %% PHASE 2: HUMAN-IN-THE-LOOP CHECKPOINT
    subgraph P2["PHASE 2: CREATIVE POLISH CHECKPOINT (Human In The Loop)"]
        S0a --> Checkpoint["PIPELINE CHECKPOINT BANNER DISPLAYED"]
        S0b --> Checkpoint
        Checkpoint --> Action1["1. Enhance Audio at Adobe Podcast<br/>(Save as *-enhanced-v2.mp3)"]
        Checkpoint --> Action2["2. Transcribe to SRT<br/>(Save as *-enhanced-v2.srt)"]
        Checkpoint --> Action3["3. Generate Character Portraits in Midjourney/Flux<br/>(Establishes consistent face & clothing)"]
        Checkpoint --> Action4["4. Generate Scene Images using Character Ref<br/>(Zip into images.zip)"]
    end

    %% PHASE 3: AUTOMATED CAPCUT TIMELINE ASSEMBLY
    subgraph P3["PHASE 3: AUTOMATED VIDEO ASSEMBLY & CAPCUT"]
        Action1 & Action2 & Action4 --> Rerun["Re-run: python run_pipeline.py"]
        Rerun --> S1["Stage 1: Audio Trimmer & SRT Re-aligner"]
        S1 --> S2["Stage 2: Image Sequencer (IDF Semantic Match 001-087)"]
        S2 --> S3["Stage 3: SRT-Driven Speech Pause Aligner (scene_timings.json)"]
        S3 --> S4["Stage 4: CapCut Builder via MCP<br/>(Applies Ken Burns Zooms, Pans & Transitions)"]
        S4 --> Export["User Reviews in CapCut Desktop & Clicks Export<br/>(Exports to exports/<Project_Name>.mp4)"]
    end

    %% PHASE 4: POST-PRODUCTION & MULTI-PLATFORM PACKAGING
    subgraph P4["PHASE 4: GRAPHIC PACKAGING & DISTRIBUTION (Stage 5)"]
        Export --> Cleanup["Stage 5a: Automatic Project Cleanup<br/>(Purges heavy intermediate WAV files)"]
        Cleanup --> Thumbs["Stage 5b: Graphic Thumbnail Designer (Pillow Engine)<br/>• Archetype 1: Action Figure Close-up ('ALREADY ENOUGH')<br/>• Archetype 2: Mystery Anchor ('DON'T OPEN IT')<br/>• Archetype 3: Contrast Dilemma ('WORTH IT?')"]
        Thumbs --> DeliverablesYT["📁 exports/<br/>• 3x YouTube 16:9 Thumbnails (1920x1080)<br/>• youtube_metadata.txt (Titles, Chapters, SEO)"]
        Thumbs --> DeliverablesFB["📁 facebook/<br/>• 3x Facebook 1:1 Thumbnails (1080x1080)<br/>• facebook_copy.txt (Headlines, Captions, Discussion)"]
    end
```

---

## 📁 Repository Layout

```text
├── capcut-mcp-server/             # Model Context Protocol (MCP) server for CapCut Desktop
│   ├── src/                       # TypeScript MCP tool definitions & schema
│   ├── dist/                      # Compiled Node.js runtime entrypoint
│   └── package.json
│
├── master_pipeline/               # Core pipeline scripts, templates, and specifications
│   ├── docs/                      # Comprehensive technical manuals & guides
│   │   ├── 00_ENVIRONMENT_AND_SETUP.md
│   │   ├── 00_PRE_PRODUCTION_AND_HANDOFF.md
│   │   ├── 01_AUDIO_ENGINEERING_RULEBOOK.md
│   │   ├── 02_IMAGE_MATCHING_AND_NAMING.md
│   │   ├── 03_SCENE_TIMING_ALIGNMENT.md
│   │   ├── 03_CAPCUT_INTERNALS_SPEC.md
│   │   ├── 04_KEN_BURNS_AND_EFFECTS.md
│   │   ├── 05_YOUTUBE_PACKAGING_AND_CLEANUP.md
│   │   ├── 06_VISUAL_STYLES_LIBRARY.md
│   │   ├── 07_STORY_IDEATION_AND_SCRIPTWRITING_ENGINE.md
│   │   ├── 08_THUMBNAIL_DESIGN_AND_PACKAGING_SPEC.md
│   │   └── NEW_PC_SETUP_PROMPT.md  # 1-click setup prompt for new workstations
│   │
│   ├── scripts/                   # Production-tested Python & Node automation scripts
│   │   ├── run_pipeline.py        # Central orchestrator & checkpoint manager
│   │   ├── speech_synthesizer.py  # Stage 0a: Edge-TTS speech generation
│   │   ├── prompt_generator.py    # Stage 0b: 87-scene & character prompt generator
│   │   ├── audio_trimmer.py       # Stage 1: Smart silence trimmer & SRT re-aligner
│   │   ├── image_processor.py     # Stage 2: IDF semantic image sequence matcher
│   │   ├── scene_aligner.py       # Stage 3: SRT speech pause timing synchronizer
│   │   ├── capcut_builder.js      # Stage 4: CapCut timeline & motion compiler
│   │   ├── youtube_packager.py    # Stage 5: Final cleanup & metadata generator
│   │   ├── thumbnail_designer.py  # Stage 5b: Canva-standard graphic thumbnail designer
│   │   └── create_lightweight_zip.py # Portable project packager
│   │
│   └── templates/                 # Pristine CapCut draft templates
│
└── projects/                      # Story project workspaces (e.g. The Locksmith's Spare Key)
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites (Windows)
* Python 3.12+
* Node.js 18+ LTS
* Gyan FFmpeg & FFprobe
* CapCut Desktop (Windows)

Install dependencies via PowerShell:
```powershell
# Python packages
pip install pydub edge-tts pillow requests

# Build CapCut MCP Server
cd capcut-mcp-server
npm install
npm run build
cd ..
```

### 2. Configure CapCut MCP Server
Add the server entry to your MCP client config (`mcp_config.json`):
```json
{
  "mcpServers": {
    "capcut": {
      "command": "node",
      "args": [
        "D:\\Himu\\Luna\\capcut-mcp-server\\dist\\index.js"
      ]
    }
  }
}
```

### 3. Running a Story Project

1. Create a project folder with your `Script.txt`:
   ```powershell
   New-Item -ItemType Directory -Path "projects/My_New_Story" -Force
   # Place Script.txt inside projects/My_New_Story/
   ```

2. Trigger the Pre-Production Automations:
   ```powershell
   python master_pipeline/scripts/run_pipeline.py --project-dir "projects/My_New_Story"
   ```
   * The pipeline automatically synthesizes your narration audio (`.mp3`), extracts character portrait prompts, and breaks the story into scene storyboard prompts.

3. Enhance audio at [Adobe Podcast](https://podcast.adobe.com/enhance), transcribe to `.srt`, generate character and scene images, and drop them in as `images.zip`.

4. Re-run the pipeline to build your CapCut project:
   ```powershell
   python master_pipeline/scripts/run_pipeline.py --project-dir "projects/My_New_Story"
   ```

5. Open CapCut Desktop, export the final `.mp4` into `exports/`, and inspect your ready-to-publish thumbnails and post copy in `facebook/` and `exports/`.

---

## 📖 Complete Documentation Index

For in-depth specifications, consult the manuals in [`master_pipeline/docs/`](./master_pipeline/docs/):
* [00: Environment & Setup Guide](./master_pipeline/docs/00_ENVIRONMENT_AND_SETUP.md)
* [00: Pre-Production & Handoff Protocol](./master_pipeline/docs/00_PRE_PRODUCTION_AND_HANDOFF.md)
* [01: Audio Engineering & SRT Remapping](./master_pipeline/docs/01_AUDIO_ENGINEERING_RULEBOOK.md)
* [02: Image Matching & Semantic Sequencing](./master_pipeline/docs/02_IMAGE_MATCHING_AND_NAMING.md)
* [03: SRT Speech Pause Synchronization](./master_pipeline/docs/03_SCENE_TIMING_ALIGNMENT.md)
* [03: CapCut Internals & Draft Architecture](./master_pipeline/docs/03_CAPCUT_INTERNALS_SPEC.md)
* [04: Ken Burns Motion & Visual Effects](./master_pipeline/docs/04_KEN_BURNS_AND_EFFECTS.md)
* [05: YouTube Packaging & SEO Architecture](./master_pipeline/docs/05_YOUTUBE_PACKAGING_AND_CLEANUP.md)
* [06: Visual Design Styles Library](./master_pipeline/docs/06_VISUAL_STYLES_LIBRARY.md)
* [07: Story Ideation & Scriptwriting Engine](./master_pipeline/docs/07_STORY_IDEATION_AND_SCRIPTWRITING_ENGINE.md)
* [08: Thumbnail Design & Social Packaging Spec](./master_pipeline/docs/08_THUMBNAIL_DESIGN_AND_PACKAGING_SPEC.md)
* [New PC 1-Click Setup Prompt](./master_pipeline/docs/NEW_PC_SETUP_PROMPT.md)

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
