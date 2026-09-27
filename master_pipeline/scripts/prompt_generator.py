"""
prompt_generator.py
Stage 0b: Automated Storyboard & Image Prompt Generator
Analyzes a narrative Script.txt, breaks it down into visual beats,
and generates an 87-scene prompts text file formatted with the
Princess Kaguya hand-drawn watercolor aesthetic.
"""

import argparse
import os
import re
import math

KAGUYA_SUFFIX = (
    "hand-drawn watercolor and ink wash illustration in the style of The Tale of Princess Kaguya, "
    "loose gestural pencil and ink lines that do not fully close, deliberately unfinished sketch edges, "
    "soft desaturated watercolor washes bleeding slightly outside lines, pale warm creams, dusty soft grays, "
    "muted amber lamplight, sage green and faded ink blue as secondary tones, white paper showing through generously, "
    "figures small relative to their environment, painterly atmospheric backgrounds fading to near-white at edges, "
    "quiet melancholy tender mood, no hard outlines, no clean vector lines, no flat color fills, "
    "visible paper texture and brushwork throughout. Vertical 9:16 composition for mobile, generous white negative space, "
    "single unified hand-painted story world, no watermark, no logo, no signature, no text overlays, "
    "ultra-detailed, high resolution, cinematic animated film still aesthetic. NOT digital illustration, "
    "NOT clean anime style, NOT paper collage, NOT 3D render, NOT photorealistic, NOT clipart."
)

CHARACTER_SUFFIX = (
    "Hand-drawn watercolor and ink wash character portrait in the style of The Tale of Princess Kaguya, "
    "loose gestural pencil and ink lines that do not fully close, soft desaturated watercolor washes, "
    "pale warm creams and dusty grays, simple grounded figure, {mood}, "
    "plain studio background dissolving to white paper at the edges, no hard outlines, visible paper texture, "
    "NOT photorealistic, NOT clean anime, NOT 3D render."
)

CANONICAL_PROFILES = {
    "otto": {
        "tag": "otto_man",
        "description": "a man of seventy-one, solidly built, unhurried, the kind of person who has made his peace with most things and is no longer interested in pretending otherwise. White hair, a weathered face with deep lines that suggest more outdoor life than indoor, work-worn hands, plain clothes — thick trousers, a flannel shirt, an old wool jumper. His expression is composed and patient but not passive. There is something behind his eyes that is paying close attention even when he appears to be doing nothing",
        "mood": "quietly alert face"
    },
    "nina": {
        "tag": "nina_daughter",
        "description": "a woman in her mid-forties, capable and warm but currently carrying more worry than she knows what to do with. Dark hair, neat practical clothes, the face of someone who solves problems for a living and has recently encountered one she cannot solve in the usual way. Her expression tends toward concern — not coldness, but the specific tension of love expressed as management",
        "mood": "quietly worried face"
    },
    "marta": {
        "tag": "marta_girl",
        "description": "a girl of nine, small and observant, the kind of child who accepts things that adults say with complete seriousness because she has not yet learned to perform skepticism. Short dark hair, plain clothes, a way of crouching to look at small things that suggests she does this often. Her face is open and curious without being loud about it",
        "mood": "openly curious face"
    },
    "paul": {
        "tag": "paul_neighbor",
        "description": "a man of fifty-three, practical and direct, not unkind but unused to saying things he cannot justify with visible evidence. Average build, plain work clothes, a face that is honest rather than expressive. He means well and shows it clumsily",
        "mood": "plain straightforward face"
    },
    "margaret": {
        "tag": "margaret_woman",
        "description": "a woman of sixty-three, retired, self-contained and precise in the way that people who have spent their lives with language become precise. Silver-gray hair cut simply, reading glasses she takes on and off without thinking about it, plain comfortable clothes in muted colors. Her face carries the particular look of someone who has thought carefully about most things and is still thinking. Not sad exactly — reflective. The kind of person whose silences are full rather than empty",
        "mood": "quietly reflective face"
    },
    "clara": {
        "tag": "clara_woman",
        "description": "a woman of forty-four, lean and self-contained, the kind of person who has learned to take up less space than she needs. Dark hair pulled back simply, plain athletic clothes, no jewelry. Her face is composed but not closed — there is something watchful in her eyes, the look of someone who has recently recalibrated what she expects from a day. She does not perform anything",
        "mood": "quietly expressive face"
    },
    "ruth": {
        "tag": "ruth_woman",
        "description": "a woman of about forty-five, slightly warmer in appearance than clara_woman, with the look of someone who arrived somewhere new and is not yet sure if she belongs there. Light brown hair, plain gym clothes that are newer than they look comfortable, an expression that is trying not to be uncertain and not quite succeeding",
        "mood": "quietly uncertain expression softening over time"
    },
    "frank": {
        "tag": "frank_man",
        "description": "a man of sixty-eight, weathered and observant, forty-two years behind the locksmith counter. Thin silver-gray hair, quiet steady hands accustomed to small delicate tools, plain work shirt with sleeves rolled up, dark woolen trousers. His expression is patient, composed, and carrying the quiet weight of long memory. There is a deep, quiet gentleness behind his gaze",
        "mood": "quietly reflective face"
    },
    "elena": {
        "tag": "elena_woman",
        "description": "a woman in her late fifties, warm and spirited, remembered with vivid clarity. Soft dark hair with touches of gray, a gentle slant to her smile, an energetic and practical demeanor. Wearing a soft cardigan in dusty amber tones. Her expression is bright, direct, and affectionate",
        "mood": "warm affectionate face"
    },
    "cass": {
        "tag": "cass_daughter",
        "description": "a woman in her mid-thirties, practical and perceptive, carrying a direct honesty and deep care for her father. Dark hair pulled back loosely, comfortable everyday clothes in muted sage and blue. Her expression is caring, thoughtful, with a subtle questioning warmth in her eyes",
        "mood": "thoughtful caring face"
    },
    "elias": {
        "tag": "elias_man",
        "description": "a man of thirty-two, thoughtful and unhurried, wearing modest everyday clothes, dark hair neatly combed, an expression of quiet contemplation and steady realization",
        "mood": "quietly contemplative face"
    },
    "voss": {
        "tag": "mrs_voss_elder",
        "description": "a woman in her early seventies, serene and observant, silver hair gathered back, comfortable knitted shawl, hands that have tended gardens for decades, a gentle knowing warmth in her eyes",
        "mood": "serene gentle face"
    },
    "nora": {
        "tag": "nora_baker",
        "description": "a woman in her late thirties, solitary baker, working quietly before dawn. Dust of flour on her apron, sleeves pushed up, hair pinned back, an expression of steady competence and private stillness",
        "mood": "calm composed face"
    },
    "hale": {
        "tag": "hale_man",
        "description": "an elderly man in his seventies, quiet florist, soft cardigan, kind patient demeanor, silver hair, gentle eyes that observe the world with quiet goodwill",
        "mood": "gentle kind face"
    }
}

def parse_script_chunks(script_path: str) -> list[dict]:
    with open(script_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by Chunk header if present, otherwise split by double newlines
    if re.search(r'Chunk\s+\d+', text, re.I):
        raw_chunks = re.split(r'Chunk\s+\d+', text, flags=re.I)
    else:
        raw_chunks = text.split('\n\n')

    chunks = []
    chunk_idx = 1
    for c in raw_chunks:
        cleaned = c.strip()
        if not cleaned:
            continue
        # Split chunk into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if len(s.strip()) > 10]
        chunks.append({
            "chunk_number": chunk_idx,
            "full_text": cleaned,
            "sentences": sentences
        })
        chunk_idx += 1
    return chunks

def detect_characters(script_text: str) -> dict[str, str]:
    """Detects main character names and creates token tags (e.g. Frank -> frank_man)."""
    common_names = [
        "Frank", "Elena", "Cass", "Otto", "Nina", "Marta", "Paul", 
        "Margaret", "Daniel", "Elias", "Nora", "Hale", "Clara", "Ruth", "James", "Priya", "Elspeth", "Voss"
    ]
    detected = {}
    for name in common_names:
        if re.search(r'\b' + name + r'\b', script_text, re.I):
            lower = name.lower()
            if lower in CANONICAL_PROFILES:
                detected[name] = CANONICAL_PROFILES[lower]["tag"]
            elif lower in ["frank", "otto", "elias", "paul", "daniel", "hale", "james"]:
                tag = f"{lower}_man"
                detected[name] = tag
            elif lower in ["marta"]:
                tag = f"{lower}_girl"
                detected[name] = tag
            elif lower in ["nina", "cass"]:
                tag = f"{lower}_daughter"
                detected[name] = tag
            elif lower in ["elena", "margaret", "nora", "clara", "ruth", "priya", "elspeth"]:
                tag = f"{lower}_woman"
                detected[name] = tag
            elif lower in ["voss"]:
                tag = "mrs_voss_elder"
                detected[name] = tag
            else:
                tag = f"{lower}_character"
                detected[name] = tag
    return detected

def generate_character_prompts(script_path: str, output_path: str = None) -> list[dict]:
    """Generates character generation prompts for character reference consistency."""
    with open(script_path, 'r', encoding='utf-8') as f:
        full_script = f.read()

    characters = detect_characters(full_script)
    if not characters:
        # Fallback to single narrator if no named characters detected
        characters = {"Narrator": "narrator_character"}

    char_prompts = []
    for name, tag in characters.items():
        lower = name.lower()
        if lower in CANONICAL_PROFILES:
            prof = CANONICAL_PROFILES[lower]
            suffix = CHARACTER_SUFFIX.format(mood=prof["mood"])
            prompt_body = f"{prof['tag']} — {prof['description']}. {suffix}"
            char_prompts.append({
                "name": name,
                "tag": prof["tag"],
                "prompt": prompt_body
            })
        else:
            # Dynamically infer character attributes from context in script
            mentions = re.findall(rf'([^.\n]*\b{name}\b[^.\n]*)', full_script)
            context = " ".join(mentions[:3]) if mentions else ""
            
            # Detect age clues
            age_match = re.search(r'\b(\d+|forty-?\w*|fifty-?\w*|sixty-?\w*|seventy-?\w*|eighty-?\w*|thirty-?\w*|twenty-?\w*|nine|ten|twelve)\b', context, re.I)
            age_str = f"of {age_match.group(1)}" if age_match else "of indeterminate age"
            
            # Gender / type
            is_female = bool(re.search(r'\b(she|her|woman|girl|mother|daughter|wife)\b', context, re.I))
            type_str = "woman" if is_female else "man"
            mood_str = "composed watchful face" if is_female else "patient contemplative face"
            
            suffix = CHARACTER_SUFFIX.format(mood=mood_str)
            prompt_body = f"{tag} — a {type_str} {age_str}, grounded and quiet, plain comfortable clothes in muted tones, an observant and unhurried posture. {suffix}"
            char_prompts.append({
                "name": name,
                "tag": tag,
                "prompt": prompt_body
            })

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("Character Generation Prompts\n\n")
            for idx, cp in enumerate(char_prompts, start=1):
                f.write(f"{idx}. {cp['tag']}\n\n")
                f.write(f"{cp['prompt']}\n\n")
        print(f"[PromptGenerator] Successfully saved {len(char_prompts)} character prompts to: {output_path}")

    return char_prompts

def generate_prompts_from_script(script_path: str, output_path: str, target_count: int = 87, char_output_path: str = None):
    print(f"\n[PromptGenerator] Analyzing script: {script_path}")
    chunks = parse_script_chunks(script_path)
    num_chunks = len(chunks)
    print(f"[PromptGenerator] Found {num_chunks} narrative chunks.")

    with open(script_path, 'r', encoding='utf-8') as f:
        full_script = f.read()
    characters = detect_characters(full_script)
    print(f"[PromptGenerator] Detected characters: {characters}")

    # Generate companion character prompts
    if not char_output_path:
        if "-image-prompts.txt" in output_path:
            char_output_path = output_path.replace("-image-prompts.txt", "-character-prompts.txt")
        elif "-prompts.txt" in output_path:
            char_output_path = output_path.replace("-prompts.txt", "-character-prompts.txt")
        else:
            base, ext = os.path.splitext(output_path)
            char_output_path = f"{base}-character-prompts{ext}"

    char_prompts = generate_character_prompts(script_path, char_output_path)

    # Allocate target_count scenes across chunks
    base_per_chunk = target_count // num_chunks
    extra = target_count % num_chunks

    prompts = []
    scene_counter = 1

    shot_types = ["wide watercolor scene", "close watercolor scene", "medium watercolor scene", "close watercolor scene", "wide watercolor scene", "medium watercolor scene"]

    for c_idx, chunk in enumerate(chunks):
        scenes_for_this_chunk = base_per_chunk + (1 if c_idx < extra else 0)
        sentences = chunk["sentences"]

        for s_idx in range(scenes_for_this_chunk):
            shot_type = shot_types[s_idx % len(shot_types)]
            
            # Pick corresponding narrative sentence or interpolate
            if s_idx < len(sentences):
                sentence = sentences[s_idx]
            else:
                sentence = sentences[-1]

            # Simplify sentence into visual beat
            clean_sentence = re.sub(r'[\r\n]+', ' ', re.sub(r'["\']', '', sentence)).strip()
            clean_sentence = re.sub(r'\s{2,}', ' ', clean_sentence)
            if not clean_sentence.endswith('.'):
                clean_sentence += '.'

            # Replace character names with tags
            visual_desc = clean_sentence
            for name, tag in characters.items():
                visual_desc = re.sub(r'\b' + name + r'\b', tag, visual_desc)

            # Build prompt
            prompt_text = (
                f"A {shot_type} illustrating the story beat: {visual_desc} "
                f"loose gestural ink lines barely sketching the figures and environment, pale atmospheric lighting, "
                f"generous white paper showing through at the borders, quiet contemplative mood. {KAGUYA_SUFFIX}"
            )
            prompts.append(prompt_text)
            scene_counter += 1

    print(f"[PromptGenerator] Generated {len(prompts)} scene prompts (Target: {target_count}).")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(f"{p}\n\n")

    print(f"[PromptGenerator] Successfully saved scene prompts to: {output_path}\n")
    return {
        "output_path": output_path,
        "char_output_path": char_output_path,
        "count": len(prompts),
        "character_count": len(char_prompts),
        "target_count": target_count
    }

def main():
    parser = argparse.ArgumentParser(description="Stage 0b: Script to 87-Scene Kaguya Prompt & Character Generator")
    parser.add_argument("--script", required=True, help="Path to Script.txt")
    parser.add_argument("--output", required=True, help="Path to output scene prompts txt file")
    parser.add_argument("--char-output", default=None, help="Optional path to output character prompts txt file")
    parser.add_argument("--count", type=int, default=87, help="Target scene count (default: 87)")
    args = parser.parse_args()

    generate_prompts_from_script(args.script, args.output, args.count, char_output_path=args.char_output)

if __name__ == "__main__":
    main()
