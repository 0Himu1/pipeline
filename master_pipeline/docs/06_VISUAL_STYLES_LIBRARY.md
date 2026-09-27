# Visual Design Styles & Prompt Engineering Library

This document is the master visual catalog for the Story Video Production Pipeline. It defines **5 curated, production-tested visual aesthetics** for generating storyboard illustrations and consistent character reference portraits in Midjourney, Flux, and Bing Image Creator.

---

## Quick-Reference Style Matrix

| Style Code | Aesthetic Name | Visual Mood & Color Tone | Best Story Genres | Paired Voice |
| :--- | :--- | :--- | :--- | :--- |
| **STYLE-01** | **Princess Kaguya Ink & Watercolor** *(Default)* | Unfinished gestural pencil, bleeding soft washes, ample white paper space | Grief, memory, quiet wisdom, aging, bittersweet nostalgia | `en-GB-SoniaNeural` (-8%) |
| **STYLE-02** | **Studio Ghibli Hand-Painted Gouache** | Lush painted nature, warm golden sunlight, cozy architectural details, vintage cel feel | Nature, gardens, childhood, generational bonds, hope | `en-GB-RyanNeural` (-6%) |
| **STYLE-03** | **35mm Nostalgic Cinematic Film** | Kodak Portra 400 grain, soft rim lighting, natural shallow DOF, tactile reality | Daily work, craft, urban solitude, realism, documentary | `en-US-ChristopherNeural` (-8%) |
| **STYLE-04** | **Nordic Editorial Gouache & Cutout** | Textured matte gouache, bold restrained shapes, earthy tones, modern folk art | Habits, routines, time management, personal discipline | `en-GB-SoniaNeural` (-6%) |
| **STYLE-05** | **Rembrandt Chiaroscuro Painterly Oil** | Deep dark shadows, dramatic amber lamplight, heavy impasto oil texture, solemn warmth | Solitude, evening reflections, late-night decisions, legacy | `en-US-GuyNeural` (-8%) |

---

## 1. STYLE-01: Princess Kaguya Hand-Drawn Watercolor & Ink Wash (Core Signature)

### Visual Philosophy
Inspired by Isao Takahata’s *The Tale of Princess Kaguya*. Lines are intentionally incomplete and gestural, capturing the emotional essence rather than rigid anatomical outlines. Heavy use of white negative space evokes memory, impermanence, and internal reflection.

### Scene Prompt Suffix (9:16 Vertical)
```text
hand-drawn watercolor and ink wash illustration in the style of The Tale of Princess Kaguya, loose gestural pencil and ink lines that do not fully close, deliberately unfinished sketch edges, soft desaturated watercolor washes bleeding slightly outside lines, pale warm creams, dusty soft grays, muted amber lamplight, sage green and faded ink blue as secondary tones, white paper showing through generously, figures small relative to their environment, painterly atmospheric backgrounds fading to near-white at edges, quiet melancholy tender mood, no hard outlines, no clean vector lines, no flat color fills, visible paper texture and brushwork throughout. Vertical 9:16 composition for mobile, generous white negative space, single unified hand-painted story world, no watermark, no logo, no signature, no text overlays, ultra-detailed, high resolution, cinematic animated film still aesthetic. NOT digital illustration, NOT clean anime style, NOT paper collage, NOT 3D render, NOT photorealistic, NOT clipart.
```

### Character Portrait Reference Prompt
```text
{tag} — {character profile: age, build, face, clothing, demeanor}. Hand-drawn watercolor and ink wash character portrait in the style of The Tale of Princess Kaguya, loose gestural pencil and ink lines that do not fully close, soft desaturated watercolor washes, pale warm creams and dusty grays, simple grounded figure, {facial expression mood}, plain studio background dissolving to white paper at the edges, no hard outlines, visible paper texture, NOT photorealistic, NOT clean anime, NOT 3D render.
```

---

## 2. STYLE-02: Studio Ghibli Hand-Painted Gouache Animation

### Visual Philosophy
Inspired by classic Studio Ghibli films (*My Neighbor Totoro*, *Whisper of the Heart*). Richly textured matte gouache backgrounds, hand-painted anime cel characters, vibrant yet naturalistic flora, and warm diffused sunlight. Evokes deep warmth, comfort, and reverence for ordinary life.

### Scene Prompt Suffix (9:16 Vertical)
```text
hand-painted anime film still in the style of classic Studio Ghibli and Hayao Miyazaki, traditional matte gouache painted background, clean expressive line art with subtle ink softness, rich natural lighting with warm diffused sunbeams, vibrant moss greens, deep cobalt blues, warm terracotta, and golden hour amber, painterly clouds and detailed organic textures, gentle nostalgic atmosphere, cinematic framing, highly detailed environmental storytelling, charming hand-crafted animation cel aesthetic. Vertical 9:16 composition, balanced framing, no watermark, no logo, no signature, no modern CGI gloss. NOT 3D render, NOT hyper-realistic photo, NOT western comic book style.
```

### Character Portrait Reference Prompt
```text
{tag} — {character profile: age, build, face, clothing, demeanor}. Classic hand-painted anime character sheet in the style of Studio Ghibli, clean expressive line art, soft hand-painted gouache shading, gentle natural skin tones, modest authentic period clothes, {facial expression mood}, soft warm studio backdrop fading to cream paper, timeless animation cel portrait, NOT 3D render, NOT photorealistic, NOT modern digital gradient art.
```

---

## 3. STYLE-03: 35mm Nostalgic Cinematic Film (Documentary Realism)

### Visual Philosophy
Shot on vintage 35mm motion picture film (Kodak Vision3 / Portra 400). Authentic analog grain, gentle halation around warm lamps, soft shallow depth-of-field ($f/1.8$), and honest, unglamorous human framing. Perfect for grounded character pieces, trade crafts, and realistic life dramas.

### Scene Prompt Suffix (9:16 Vertical)
```text
cinematic 35mm film photograph, shot on Kodak Portra 400 with a vintage prime lens at f/1.8, authentic organic analog film grain, gentle natural halation around warm incandescent light sources, soft muted color grading with desaturated tones, dusty ambers, deep slate grays, and muted earth tones, beautiful falloff and natural bokeh, authentic documentary realism, unvarnished human intimacy, cinematic stillness, evocative candid composition. Vertical 9:16 framing, 8k resolution, no lens flare artifacts, no digital noise, no HDR hyper-saturation. NOT AI glossy render, NOT clean digital photo, NOT cartoon, NOT stylized illustration.
```

### Character Portrait Reference Prompt
```text
{tag} — {character profile: age, build, face, clothing, demeanor}. Candid 35mm vintage documentary film portrait, natural soft window lighting, shallow depth of field, authentic fine film grain, honest unretouched skin textures with deep natural lines, work-worn hands, muted clothing fabrics, {facial expression mood}, authentic cinematic character study, neutral quiet room background dissolving into soft blur, shot on 35mm Kodak Portra, NOT digital CGI, NOT airbrushed studio headshot.
```

---

## 4. STYLE-04: Nordic Editorial Gouache & Textured Paper Cutout

### Visual Philosophy
Inspired by modern Scandinavian children’s literature and mid-century editorial illustration. Bold, clean silhouettes with tactile dry-brush gouache textures and subtle layered paper shadows. Balanced, peaceful, and intellectually stimulating.

### Scene Prompt Suffix (9:16 Vertical)
```text
modern Scandinavian editorial storybook illustration, textured matte gouache painting on heavy handmade cotton rag paper, bold restrained geometric shapes combined with delicate hand-drawn details, earthy muted color palette of terracotta, sage green, misty gray, mustard yellow, and raw umber, visible rough paper tooth and dry-brush stippling, clean elegant negative space, quiet contemplative Scandinavian design sensibility, high editorial clarity. Vertical 9:16 composition, museum quality print aesthetic, no digital glow, no gradients, no vector flatness. NOT 3D render, NOT glossy digital art, NOT photorealistic.
```

### Character Portrait Reference Prompt
```text
{tag} — {character profile: age, build, face, clothing, demeanor}. Editorial gouache character illustration, restrained silhouette, textured matte paint on heavy paper, subtle pencil detailing on eyes and hands, {facial expression mood}, muted minimalist background with generous paper margin, timeless Scandinavian storybook portrait, visible paper grain, NOT 3D render, NOT photorealistic.
```

---

## 5. STYLE-05: Rembrandt Chiaroscuro Painterly Oil

### Visual Philosophy
Rooted in 17th-century Golden Age Dutch painting (Rembrandt, Vermeer). Extreme chiaroscuro with dramatic single-point golden candlelight or warm oil lamps surrounded by deep, velvety shadows. Thick impasto texture and soulful dignity for heavy emotional turning points.

### Scene Prompt Suffix (9:16 Vertical)
```text
classical oil painting in the style of Rembrandt and the Dutch Golden Age, masterwork chiaroscuro lighting, single warm candle or oil lamp casting radiant golden light against deep rich shadowy darks, heavy textured impasto oil brushwork on aged linen canvas, warm sienna, burnt umber, deep ochre, and dark olive glazes, dignified contemplative human mood, atmospheric museum oil painting aesthetic. Vertical 9:16 framing, dramatic master lighting, visible canvas grain and cracked oil varnish patina, no watermark, no digital sheen. NOT digital illustration, NOT photorealistic, NOT 3D render.
```

### Character Portrait Reference Prompt
```text
{tag} — {character profile: age, build, face, clothing, demeanor}. Masterwork chiaroscuro oil portrait in the style of Rembrandt, rich side lighting illuminating half the face, deep warm umber shadows, textured impasto brushstrokes, dignified soulful gaze, {facial expression mood}, dark atmospheric oil-glazed background, classical fine art portrait, NOT digital CGI, NOT modern photograph.
```

---

## 6. How to Select & Swap Styles in the Pipeline

When creating a new project via `prompt_generator.py` or the conversational copilot, specify the `--style` parameter:

```powershell
python master_pipeline\scripts\prompt_generator.py \
  --script "projects/<Project Name>/Script.txt" \
  --output "projects/<Project Name>/image-prompts.txt" \
  --style "ghibli"   # Options: kaguya | ghibli | film35mm | nordic | rembrandt
```

The script automatically swaps the aesthetic suffix and generates the matching character reference portraits.
