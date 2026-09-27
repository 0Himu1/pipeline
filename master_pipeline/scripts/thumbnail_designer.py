"""
thumbnail_designer.py
Stage 5b: High-CTR Graphic Thumbnail & Social Media Packaging Designer

Replaces raw scene copy with Canva-standard graphic design:
1. Builds 3 distinct high-CTR thumbnail archetypes:
   - Archetype 1: 'Action Figure' Character Emotional Close-Up (e.g. "ALREADY ENOUGH")
   - Archetype 2: 'Mystery Anchor' Story Object (e.g. "DON'T OPEN IT")
   - Archetype 3: 'Contrast Dilemma' Fork in the Road (e.g. "WORTH IT?")
2. Produces both:
   - YouTube 16:9 Widescreen (1920x1080) in exports/
   - Facebook 1:1 Square (1080x1080) in facebook/
3. Applies professional Canva design principles:
   - Depth-of-field background blur & atmospheric vignette
   - Scrim / gradient overlay for 100% mobile text legibility
   - Multi-layer drop shadow and accent word color pop (#FFFFFF + #FFD166)
   - Strict YouTube bottom-right timestamp badge avoidance
4. Generates facebook/facebook_copy.txt with copy inspired by the thumbnails.
"""

import argparse
import glob
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

# Preferred Windows System Fonts for High-CTR Thumbnails
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\ariblk.ttf",       # Arial Black
    r"C:\Windows\Fonts\segoeuib.ttf",     # Segoe UI Bold
    r"C:\Windows\Fonts\arialbd.ttf"       # Arial Bold
]

def get_best_font(size):
    for font_path in FONT_CANDIDATES:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_gradient_scrim(width, height, direction="left_to_right", max_alpha=180):
    """Creates a smooth black gradient overlay to make typography pop without harsh borders."""
    scrim = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scrim)
    
    if direction == "left_to_right":
        gradient_width = int(width * 0.65)
        for x in range(gradient_width):
            alpha = int(max_alpha * (1.0 - (x / gradient_width)) ** 1.5)
            draw.line([(x, 0), (x, height)], fill=(12, 12, 14, alpha))
    elif direction == "radial_left":
        cx, cy = int(width * 0.25), int(height * 0.45)
        max_dist = width * 0.6
        for r in range(int(max_dist), 0, -10):
            alpha = int(max_alpha * (1.0 - (r / max_dist)) ** 1.2)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 10, 15, alpha))
            
    return scrim

def draw_text_with_shadow(draw, position, text, font, fill_color, shadow_color=(0, 0, 0, 240), shadow_offset=6):
    """Draws multi-compass drop shadow for 360-degree crispness on mobile screens."""
    x, y = position
    # 8-direction shadow outline for maximum pop
    offsets = [
        (-shadow_offset, 0), (shadow_offset, 0),
        (0, -shadow_offset), (0, shadow_offset),
        (-shadow_offset, -shadow_offset), (shadow_offset, -shadow_offset),
        (-shadow_offset, shadow_offset), (shadow_offset, shadow_offset),
        (0, shadow_offset + 3), (shadow_offset, shadow_offset + 3) # extra bottom weight
    ]
    for ox, oy in offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=shadow_color)
        
    draw.text((x, y), text, font=font, fill=fill_color)

def center_crop_and_resize(img, target_width, target_height):
    """Crops and resizes an image to cleanly fill the target dimensions."""
    orig_w, orig_h = img.size
    target_aspect = target_width / target_height
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        # Source is wider than target -> crop sides
        new_w = int(orig_h * target_aspect)
        left = (orig_w - new_w) // 2
        img_cropped = img.crop((left, 0, left + new_w, orig_h))
    else:
        # Source is taller than target -> crop top/bottom with slight upper bias
        new_h = int(orig_w / target_aspect)
        top = int((orig_h - new_h) * 0.35)
        img_cropped = img.crop((0, top, orig_w, top + new_h))

    return img_cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

def compose_thumbnail(
    bg_image_path,
    target_size,
    text_lines,
    accent_color="#FFD166",
    blur_bg=True,
    output_path=None
):
    """Composes a professional Canva-style graphic thumbnail."""
    target_w, target_h = target_size
    
    # 1. Base Image Processing
    with Image.open(bg_image_path) as raw_img:
        base_img = raw_img.convert("RGBA")
        
    # Resize and center crop
    canvas = center_crop_and_resize(base_img, target_w, target_h)
    
    # Depth-of-field background softening
    if blur_bg:
        blurred_bg = canvas.filter(ImageFilter.GaussianBlur(radius=5))
        # Mix slightly with original to preserve subtle texture while removing clutter
        canvas = Image.blend(canvas, blurred_bg, 0.6)
        
    # Subtle cinematic grading (boost contrast slightly, warm shadow tint)
    enhancer = ImageEnhance.Contrast(canvas)
    canvas = enhancer.enhance(1.12)
    enhancer = ImageEnhance.Color(canvas)
    canvas = enhancer.enhance(1.10)
    
    # 2. Add Dark Scrim / Vignette for Text Readability
    scrim = create_gradient_scrim(target_w, target_h, direction="left_to_right", max_alpha=190)
    canvas = Image.alpha_composite(canvas, scrim)
    
    # 3. Add Typography Overlay
    draw = ImageDraw.Draw(canvas)
    
    # Calculate responsive font size
    base_font_size = int(target_h * 0.14) # ~150px on 1080p
    font = get_best_font(base_font_size)
    
    # Compute starting position (Upper-Left third, strictly avoiding bottom-right)
    start_x = int(target_w * 0.07)
    start_y = int(target_h * 0.18)
    line_spacing = int(base_font_size * 1.15)
    
    for i, line in enumerate(text_lines):
        line_text = line["text"].upper()
        is_accent = line.get("accent", False)
        color = accent_color if is_accent else "#FFFFFF"
        
        pos = (start_x, start_y + (i * line_spacing))
        draw_text_with_shadow(
            draw=draw,
            position=pos,
            text=line_text,
            font=font,
            fill_color=color,
            shadow_color=(0, 0, 0, 240),
            shadow_offset=max(4, int(base_font_size * 0.05))
        )
        
    # Final Output Save
    final_rgb = canvas.convert("RGB")
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_rgb.save(output_path, "JPEG", quality=95)
        print(f"[ThumbnailDesigner] Generated: {output_path} ({target_w}x{target_h})")
        
    return final_rgb

def design_project_thumbnails(work_dir, project_name):
    """Executes the full Canva-standard graphic design suite for YouTube and Facebook."""
    print(f"\n================================================================================")
    print(f"[ThumbnailDesigner] Initiating Graphic Thumbnail Suite for: {project_name}")
    print(f"================================================================================")
    
    exports_dir = os.path.join(work_dir, "exports")
    facebook_dir = os.path.join(work_dir, "facebook")
    os.makedirs(exports_dir, exist_ok=True)
    os.makedirs(facebook_dir, exist_ok=True)
    
    # Find candidate images from sequenced_images or root
    img_candidates = []
    for search_dir in [os.path.join(work_dir, "sequenced_images"), work_dir]:
        if os.path.exists(search_dir):
            found = sorted(glob.glob(os.path.join(search_dir, "*.jpg")) + 
                           glob.glob(os.path.join(search_dir, "*.png")) + 
                           glob.glob(os.path.join(search_dir, "*.jpeg")))
            if found:
                # filter out exports and existing thumbnails
                img_candidates = [f for f in found if "exports" not in f and "facebook" not in f and "thumb" not in os.path.basename(f).lower()]
                if img_candidates:
                    break
                    
    if not img_candidates:
        print("[ThumbnailDesigner] Error: No source images found to design thumbnails from.")
        return

    # Select 3 distinct visual moments
    num_imgs = len(img_candidates)
    img_early = img_candidates[min(2, num_imgs - 1)]
    img_mid = img_candidates[num_imgs // 2]
    img_climax = img_candidates[max(0, num_imgs - 4)]
    
    # Archetype Definitions (Graphic & Copy Hooks)
    concepts = [
        {
            "id": "01_character_emotion",
            "bg_img": img_mid,
            "text": [
                {"text": "ALREADY", "accent": False},
                {"text": "ENOUGH.", "accent": True}
            ],
            "yt_name": "thumbnail_01_character_emotion_16x9.jpg",
            "fb_name": "fb_post_01_character_emotion_square.jpg",
            "hook_title": f"The Quiet Power of Being Unimportant | {project_name}",
            "social_hook": "We are taught that our worth is measured by how fast we run and how much we accumulate. But at 4:15 PM every day, an old master closes his shop and refuses to optimize."
        },
        {
            "id": "02_mystery_anchor",
            "bg_img": img_early,
            "text": [
                {"text": "DON'T", "accent": False},
                {"text": "OPEN IT.", "accent": True}
            ],
            "yt_name": "thumbnail_02_mystery_anchor_16x9.jpg",
            "fb_name": "fb_post_02_mystery_anchor_square.jpg",
            "hook_title": f"The Secret Behind the {project_name} | A Story About What We Keep",
            "social_hook": "For forty years, he kept a key to a door he was never supposed to unlock. What happens when holding on becomes heavier than letting go?"
        },
        {
            "id": "03_contrast_dilemma",
            "bg_img": img_climax,
            "text": [
                {"text": "WORTH", "accent": False},
                {"text": "IT?", "accent": True}
            ],
            "yt_name": "thumbnail_03_contrast_dilemma_16x9.jpg",
            "fb_name": "fb_post_03_contrast_dilemma_square.jpg",
            "hook_title": f"Why Saving Time Never Makes Us Peaceful | {project_name}",
            "social_hook": "We spend our entire youth building a life so fast that we don't have time to live inside it. Here is the quiet truth about what truly lasts."
        }
    ]
    
    # Dimensions
    YT_16x9 = (1920, 1080)
    FB_SQUARE = (1080, 1080)
    
    for c in concepts:
        # YouTube 16:9
        yt_out = os.path.join(exports_dir, c["yt_name"])
        compose_thumbnail(
            bg_image_path=c["bg_img"],
            target_size=YT_16x9,
            text_lines=c["text"],
            accent_color="#FFD166",
            blur_bg=True,
            output_path=yt_out
        )
        
        # Facebook 1:1 Square
        fb_out = os.path.join(facebook_dir, c["fb_name"])
        compose_thumbnail(
            bg_image_path=c["bg_img"],
            target_size=FB_SQUARE,
            text_lines=c["text"],
            accent_color="#FFD166",
            blur_bg=True,
            output_path=fb_out
        )

    # Generate Facebook Copy Inspired by the Thumbnails
    fb_copy_path = os.path.join(facebook_dir, "facebook_copy.txt")
    with open(fb_copy_path, 'w', encoding='utf-8') as f:
        f.write(f"================================================================================\n")
        f.write(f"FACEBOOK SOCIAL POST PACKAGING: {project_name.upper()}\n")
        f.write(f"================================================================================\n\n")
        
        for idx, c in enumerate(concepts, 1):
            f.write(f"--------------------------------------------------------------------------------\n")
            f.write(f"POST VARIANT {idx}: {c['id'].upper()} (Paired with {c['fb_name']})\n")
            f.write(f"--------------------------------------------------------------------------------\n")
            f.write(f"THUMBNAIL TEXT: {' '.join([t['text'] for t in c['text']])}\n")
            f.write(f"POST HEADLINE: {c['hook_title']}\n\n")
            f.write(f"CAPTION:\n")
            f.write(f"{c['social_hook']}\n\n")
            f.write(f"Take a quiet breath, grab a cup of tea, and watch the full visual essay.\n\n")
            f.write(f"💬 Question: What is one thing in your life you feel pressured to rush, but wish you could slow down?\n\n")
            f.write(f"#Storytelling #MindfulLiving #SlowLiving #EmotionalStory #ArtisticAnimation #PrincessKaguya\n\n\n")
            
    print(f"[ThumbnailDesigner] Created tailored social copy at: {fb_copy_path}")
    print(f"[ThumbnailDesigner] All 3 YouTube (16:9) and Facebook (1:1) thumbnails successfully designed!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Design Canva-Standard High-CTR Thumbnails")
    parser.add_argument("--work-dir", required=True, help="Path to project directory")
    parser.add_argument("--project-name", required=True, help="Name of project")
    args = parser.parse_args()
    
    design_project_thumbnails(work_dir=args.work_dir, project_name=args.project_name)
