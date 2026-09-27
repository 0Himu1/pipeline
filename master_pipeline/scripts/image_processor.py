"""
image_processor.py
Module to extract, match, sequence, and rename large batches of AI story images:
- Extracts zip archive if provided.
- Fuzzy token and domain synonym matching against prompt lines.
- Resolves multiple variations and timestamps.
- Sequences to zero-padded 3-digit format (001_slug.jpeg to NNN_slug.jpeg).
- Generates scenes_manifest.json and order_index.json.
"""

import argparse
import json
import os
import re
import shutil
import zipfile

import math
from collections import Counter

STOPWORDS = {'and','the','with','for','from','that','this','into','around','across','behind','onto','through','style','tale','princess','kaguya'}
GENERIC_ART = {
    'watercolor', 'scene', 'shot', 'illustration', 'lines', 'ink', 'wash', 'hand', 'drawn',
    'deliberately', 'gestural', 'pencil', 'edges', 'soft', 'washes', 'bleeding', 'pale', 'creams',
    'dusty', 'grays', 'muted', 'amber', 'sage', 'green', 'white', 'paper', 'showing', 'generously',
    'figures', 'small', 'relative', 'environment', 'painterly', 'atmospheric', 'backgrounds', 'fading',
    'quiet', 'melancholy', 'tender', 'mood', 'hard', 'outlines', 'clean', 'vector', 'flat', 'color',
    'fills', 'visible', 'texture', 'brushwork', 'throughout', 'vertical', 'composition', 'mobile',
    'negative', 'space', 'single', 'unified', 'world', 'watermark', 'logo', 'signature', 'overlays',
    'ultra', 'detailed', 'high', 'resolution', 'cinematic', 'animated', 'film', 'still', 'aesthetic',
    'digital', 'anime', 'collage', 'render', 'photorealistic', 'clipart', 'not'
}

SYNONYMS = {
    'woman': ['clara', 'nora', 'baker', 'figure', 'person', 'female', 'cass', 'daughter', 'elena', 'girl'],
    'clara': ['woman', 'figure', 'person', 'female'],
    'nora': ['woman', 'baker', 'figure', 'person'],
    'baker': ['woman', 'nora', 'person'],
    'man': ['frank', 'hale', 'mr_hale', 'elias', 'tomas', 'figure', 'person', 'shopkeeper', 'elder', 'customer'],
    'frank': ['man', 'figure', 'person', 'shopkeeper'],
    'elias': ['man', 'figure', 'person'],
    'tomas': ['man', 'figure', 'person'],
    'hale': ['man', 'mr_hale', 'shopkeeper'],
    'daughter': ['cass', 'girl', 'woman', 'child'],
    'cass': ['daughter', 'girl', 'woman'],
    'child': ['boy', 'son', 'daughter', 'girl'],
    'boy': ['child', 'son'],
    'son': ['child', 'boy'],
    'girl': ['daughter', 'child', 'woman'],
    'notebook': ['book', 'journal', 'recipes', 'recipe'],
    'key': ['brass', 'cylinder'],
    'drawer': ['box'],
    'pot': ['stove', 'saucepan', 'cooking', 'dish'],
    'table': ['kitchen_table', 'counter', 'desk', 'bench'],
    'app': ['appliance', 'oven', 'stove'],
    'walking': ['crossing', 'approaching', 'stepping', 'strolling'],
    'seated': ['sitting', 'rest'],
    'sleeping': ['asleep']
}

def clean_tokens(text: str) -> list:
    words = re.sub(r'[^a-zA-Z0-9]', ' ', text.lower()).split()
    return [w for w in words if len(w) > 2 and w not in STOPWORDS and w not in GENERIC_ART]

def get_bigrams(words: list) -> set:
    return set(zip(words[:-1], words[1:]))

def slugify(text: str, max_words: int = 5) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    words = cleaned.strip().split()[:max_words]
    return "_".join(w.capitalize() for w in words)

def process_images(
    prompts_path: str,
    input_source: str,
    output_dir: str
) -> dict:
    print(f"[ImageProcessor] Loading prompts from {prompts_path}...")
    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    num_prompts = len(prompts)
    print(f"[ImageProcessor] Loaded {num_prompts} prompts.")

    # 1. Handle zip or folder
    temp_extract = None
    if os.path.isfile(input_source) and input_source.lower().endswith('.zip'):
        temp_extract = os.path.join(os.path.dirname(output_dir), "_temp_extracted_zip")
        os.makedirs(temp_extract, exist_ok=True)
        print(f"[ImageProcessor] Extracting {input_source} to {temp_extract}...")
        with zipfile.ZipFile(input_source, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)
        search_dir = temp_extract
    else:
        search_dir = input_source

    # Collect all image files
    all_images = []
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.lower().endswith(('.jpeg', '.jpg', '.png', '.webp')):
                all_images.append(os.path.join(root, file))

    print(f"[ImageProcessor] Found {len(all_images)} image files.")

    # Precompute prompt tokens & bigrams
    prompt_token_list = []
    for p_idx, prompt_text in enumerate(prompts):
        first_sent = prompt_text.split('.')[0]
        p_words = clean_tokens(first_sent)
        prompt_token_list.append({
            "idx": p_idx,
            "first_sent": first_sent,
            "words": p_words,
            "tokens": set(p_words),
            "bigrams": get_bigrams(p_words)
        })

    # Compute document frequencies and IDF across all prompts
    df_counts = Counter()
    for pd in prompt_token_list:
        for t in pd["tokens"]:
            df_counts[t] += 1

    idf = {}
    for t, cnt in df_counts.items():
        idf[t] = max(0.5, math.log((num_prompts + 1.0) / (cnt + 1.0)) + 1.0)

    # Parse candidate files and their clean token representations
    file_candidates = []
    for c_idx, fpath in enumerate(all_images):
        fname = os.path.basename(fpath)
        base = re.sub(r'^(.*?)(?:_2026\d+)?(?:_\d+)?\.(?:jpeg|jpg|png|webp)$', r'\1', fname, flags=re.I)
        c_words = clean_tokens(base)
        file_candidates.append({
            "c_idx": c_idx,
            "path": fpath,
            "filename": fname,
            "base": base,
            "words": c_words,
            "tokens": set(c_words),
            "bigrams": get_bigrams(c_words)
        })

    # Compute candidate pair scores globally
    pairs = []
    for pd in prompt_token_list:
        p_idx = pd["idx"]
        p_set = pd["tokens"]
        p_bg = pd["bigrams"]

        for cand in file_candidates:
            c_idx = cand["c_idx"]
            c_set = cand["tokens"]
            c_bg = cand["bigrams"]

            # Explicit scene index match in filename (e.g. 001_, scene_1, etc.)
            idx_bonus = 0.0
            m_idx = re.match(r'^(?:scene[_\s\-]*)?0*([1-9]\d*)[_\s\-\.]', cand["filename"], re.I)
            if m_idx and int(m_idx.group(1)) == p_idx + 1:
                idx_bonus = 150.0

            # 1. IDF weighted token overlap
            overlap = p_set & c_set
            score = sum(idf.get(w, 1.0) * 4.0 for w in overlap)

            # 2. Synonym matching
            for pw in p_set:
                if pw in SYNONYMS:
                    for syn in SYNONYMS[pw]:
                        if syn in c_set and syn not in overlap:
                            score += idf.get(syn, 1.0) * 2.0
                            break

            # 3. Bigram phrase matches
            bg_overlap = p_bg & c_bg
            score += len(bg_overlap) * 12.0

            # 4. Proximity bonus (slight tie-breaker to preserve narrative progression)
            norm_p = p_idx / max(1, num_prompts - 1)
            norm_c = c_idx / max(1, len(file_candidates) - 1)
            prox = max(0.0, 1.0 - abs(norm_p - norm_c)) * 2.5
            score += prox + idx_bonus

            if score > 0:
                pairs.append((score, p_idx, c_idx))

    # Sort descending by match score to prioritize highest confidence matches first
    pairs.sort(key=lambda x: x[0], reverse=True)

    assigned_prompts = set()
    assigned_cands = set()
    prompt_matches = {}

    for score, p_idx, c_idx in pairs:
        if p_idx not in assigned_prompts and c_idx not in assigned_cands:
            assigned_prompts.add(p_idx)
            assigned_cands.add(c_idx)
            prompt_matches[p_idx] = (c_idx, score)

    # For any remaining unmatched prompts and candidates, map remaining in sequence
    remaining_prompts = [p for p in range(num_prompts) if p not in assigned_prompts]
    remaining_cands = [c for c in range(len(file_candidates)) if c not in assigned_cands]
    for p_idx, c_idx in zip(remaining_prompts, remaining_cands):
        assigned_prompts.add(p_idx)
        assigned_cands.add(c_idx)
        prompt_matches[p_idx] = (c_idx, 0)

    # Build manifest and missing list
    manifest = []
    missing = []

    for idx, prompt_text in enumerate(prompts, start=1):
        p_idx = idx - 1
        first_sent = prompt_token_list[p_idx]["first_sent"]

        if p_idx in prompt_matches:
            c_idx, score = prompt_matches[p_idx]
            best_cand = file_candidates[c_idx]
            slug = slugify(first_sent)
            ext = os.path.splitext(best_cand["filename"])[1].lower()
            if ext == '.jpg': ext = '.jpeg'
            target_name = f"{idx:03d}_{slug}{ext}"

            manifest.append({
                "scene_number": idx,
                "prompt_summary": first_sent,
                "full_prompt": prompt_text,
                "source_file": best_cand["path"],
                "target_filename": target_name,
                "match_score": score
            })
        else:
            missing.append({
                "scene_number": idx,
                "prompt": prompt_text
            })

    print(f"[ImageProcessor] Successfully matched {len(manifest)} / {num_prompts} images.")
    if missing:
        print(f"[ImageProcessor] WARNING: {len(missing)} scenes are missing matching images!")
        missing_path = os.path.join(output_dir, "missing_scenes.json")
        os.makedirs(output_dir, exist_ok=True)
        with open(missing_path, 'w', encoding='utf-8') as f:
            json.dump(missing, f, indent=2)
        print(f"[ImageProcessor] Missing scenes dumped to {missing_path}")

    # Copy files to output directory
    os.makedirs(output_dir, exist_ok=True)
    order_index = []

    for item in manifest:
        dest_path = os.path.join(output_dir, item["target_filename"])
        shutil.copy2(item["source_file"], dest_path)
        order_index.append({
            "index": item["scene_number"],
            "filename": item["target_filename"]
        })

    # Save manifests
    manifest_path = os.path.join(output_dir, "scenes_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    order_index_path = os.path.join(output_dir, "order_index.json")
    with open(order_index_path, 'w', encoding='utf-8') as f:
        json.dump(order_index, f, indent=2)

    # Clean up temp extract if created
    if temp_extract and os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)

    print(f"[ImageProcessor] Completed! Output saved to {output_dir}")
    return {
        "matched_count": len(manifest),
        "total_prompts": num_prompts,
        "missing_count": len(missing),
        "output_dir": output_dir,
        "manifest_path": manifest_path
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Story Image Matcher and Sequencer")
    parser.add_argument("--prompts", required=True, help="Path to prompts txt file")
    parser.add_argument("--input", required=True, help="Input directory or zip archive")
    parser.add_argument("--output", required=True, help="Output directory for ordered images")
    args = parser.parse_args()

    process_images(args.prompts, args.input, args.output)
