# Image Processing, Fuzzy Matching, and Sequential Naming Specification

When generating large batches of story images (e.g. 50 to 150+ frames) using AI platforms (Midjourney, Google Flow, DALL-E, ComfyUI), raw downloads arrive with random hashes, truncated prompt slugs, variation suffixes (`_2`, `_3`, timestamp strings), and missing indices.

This specification outlines the deterministic pipeline to extract, match, resolve variations, sequence, and verify 100% complete story image assets.

---

## 1. Input Contract

To process images for a story project, provide:
1. **Prompts Text File (`prompts.txt`)**:
   - One line per scene, in strict sequential story order (Scene 1 to Scene $N$).
   - May contain full descriptive prompts, character keywords, and camera directions.
2. **Raw Images Archive / Folder (`images.zip` or `raw_images/`)**:
   - Contains generated images in JPEG, PNG, or WEBP format.
   - May contain multiple variations for certain prompts and truncated slug filenames.

---

## 2. Filename Normalization & Variation De-duping

AI tools typically export files following patterns such as:
- `A_young_woman_standing_by_the_door…_20260921123456_0.jpeg`
- `015_bakery_counter_2.png`
- `nora_baker_bread_oven_v3.jpeg`

### Normalization Pipeline:
1. **Strip Ellipsis & Trailing Timestamps**:
   - Strip `…`, `...`, and regex `(?:_2026\d+)?(?:_\d+)?\.(?:jpeg|jpg|png)$`.
2. **Extract Base Slug**:
   - Convert to clean alphanumeric tokens (e.g. `['young', 'woman', 'standing', 'door']`).
3. **Group Variations**:
   - Group files sharing the same base slug. If variations exist (`_1`, `_2`), select the highest index or highest resolution variant.

---

## 3. Two-Tier Semantic & Keyword Matching Algorithm

To map each prompt $P_i$ to its corresponding image candidate $F_j$:

### Tier 1: Exact First-Sentence Token Overlap
- Extract the core subject from the prompt's first sentence (before the first period or comma).
- Strip stop-words (`and, the, with, for, from, into, across, behind, that, this`).
- Compute token intersection score:
  $$\text{Score}(P, F) = 3 \times |W(P) \cap W(F)|$$

### Tier 2: Domain Synonym Matching
Map character and setting synonyms to ensure model terminology differences don't break matching:
- `woman` $\leftrightarrow$ `nora`, `baker`, `figure`, `person`
- `man` $\leftrightarrow$ `hale`, `mr_hale`, `shopkeeper`, `elder`
- `child` $\leftrightarrow$ `boy`, `son`
- `app` $\leftrightarrow$ `appliance`, `oven`, `stove`
- `walking` $\leftrightarrow$ `crossing`, `approaching`, `stepping`, `strolling`
- Each synonym match contributes $+2$ to the candidate score.

### Tier 3: Positional Disambiguation
If multiple candidates share identical keywords, tie-break using sequential position in the raw archive or prompt order continuity.

---

## 4. Verification & Gap Detection

Before renaming or moving files, run a strict verification matrix:
1. **Count Match**: $\text{Mapped Count} == \text{Total Prompts Count}$.
2. **Duplicate Detection**: Ensure no image file is assigned to two different prompt numbers.
3. **Missing List Report**: If any prompt has score 0 or no candidate, immediately generate a `missing_prompts.json` listing the exact prompt number and text so the user can generate the missing asset.

---

## 5. Output Standard: 3-Digit Zero-Padded Sequencing

All approved images are moved/copied to `generated_images/` following this uniform naming convention:

```
generated_images/
  ├── 001_Short_descriptive_slug.jpeg
  ├── 002_Next_scene_slug.jpeg
  ├── ...
  └── 087_Final_scene_slug.jpeg
```

- **Format**: `{:03d}_{Slug}.jpeg` (e.g., `001_`, `002_`, ..., `099_`, `100_`).
- **Slugs**: Capitalized words separated by underscores, max 5-6 words, no special characters or trailing periods.

### Output Manifests:
- `scenes_manifest.json`: Full metadata for each scene (prompt number, prompt text, target filename, source image hash).
- `order_index.json`: Fast lookup array mapping index to filename.
