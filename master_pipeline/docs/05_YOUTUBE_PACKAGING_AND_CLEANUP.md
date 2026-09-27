# Stage 5: Final Cleanup & YouTube Distribution Packaging

This document outlines the post-production distribution workflow, automated project cleanup policies, YouTube 2026 algorithmic metadata optimization, and high-CTR thumbnail standards.

---

## 1. Project Directory Cleanup Policy

When running large automated video pipelines, intermediate uncompressed WAV files and extraction scratch folders consume gigabytes of disk space and clutter project workspaces.

### Automated Cleanup Rules:
1. **Uncompressed Intermediate WAVs**: Once CapCut imports audio into its local cache (`Resources/local/`), the intermediate 100MB+ `trimmed_voiceover.wav` in the project root is automatically deleted. The lightweight 320kbps MP3 (`trimmed_voiceover.mp3`) is retained for reference.
2. **Exported Videos Consolidation**: When the user exports the finalized video (`.mp4` / `.mov`) from CapCut into the project directory, Stage 5 automatically moves it into `exports/<ProjectName>.mp4`.
3. **Pristine Project Root**: The root of each project directory retains only:
   - `Script.txt` (Original script)
   - `prompts.txt` (Image prompts)
   - `voiceover.mp3` (Raw audio)
   - `images.zip` (Source image archive)
   - `sequenced_images/` (Matched ordered images)
   - `scene_timings.json` (Narration beat alignment manifest)
   - `exports/` (Final distribution deliverables)

---

## 2. YouTube Metadata Architecture (`exports/youtube_metadata.txt`)

YouTube's recommendation algorithm relies heavily on initial Click-Through Rate (CTR) and Average View Duration (AVD). Every project package generates a production-ready `youtube_metadata.txt` with:

### A. Five High-CTR Title Options
- **Option 1: Curiosity Gap Hook (Recommended)**: Evokes an open loop without clickbait disappointment (e.g. *What Grows When You Leave It Alone | A Story About Time and Patience*).
- **Option 2: Emotional / Empathy Hook**: Focuses on the core human struggle (e.g. *Where Does All the Money Go? | The Story of Nora Baker*).
- **Option 3: Short & Mobile-Optimized**: Under 55 characters to avoid truncation on mobile screens (e.g. *Seeds Need Soil | An Atmospheric Tale of Patience*).
- **Option 4: Search & Discovery SEO**: Target keywords for high-intent viewers (e.g. *Animated Japanese Watercolor Story with Peaceful Narration*).
- **Option 5: Poetic / Cinematic**: Appealing to aesthetic, Ghibli, and art-film audiences.

### B. High-Retention Description
1. **The 2-Line Hook**: Placed *above the fold* (first 120 characters) so mobile viewers read the premise before clicking "Show more".
2. **Chapter Timestamps**: Generated directly from `scene_timings.json`. Timestamps encourage viewer replay, increase engagement metrics, and trigger Google Search video rich snippets.
3. **Art & Sound Credits**: Clear notes on the visual style (*The Tale of Princess Kaguya / Studio Ghibli watercolor*) and voiceover mastering.
4. **Audience Retention Question**: Specific prompt driving comments to signal high community engagement.
5. **SEO Tags & Hashtags**: Comma-separated tags and top 3-5 mobile hashtags.

---

## 3. High-CTR Thumbnail Guidelines (Three Per Video)

Thumbnails must be exported to `exports/` at **16:9 widescreen (1920x1080)** in JPG format with clear focal points:

1. **Thumbnail 1: Emotional Character Focus**
   - Centered on the protagonist at a pivotal emotional juncture.
   - High contrast between subject and background (e.g. warm window light vs cool walls).
   - Filename: `thumbnail_01_<character_or_theme>.jpg`.

2. **Thumbnail 2: Curiosity / Dramatic Hook**
   - Highlights an intriguing physical object or turning point (e.g. the 30-year bank ledger card, the labeled glass jar on the kitchen table).
   - Filename: `thumbnail_02_<object_or_conflict>.jpg`.

3. **Thumbnail 3: Atmospheric / World-Building Scene**
   - Expansive, breathtaking environment showcasing the artistic watercolor aesthetic.
   - Filename: `thumbnail_03_<environment_or_payoff>.jpg`.
