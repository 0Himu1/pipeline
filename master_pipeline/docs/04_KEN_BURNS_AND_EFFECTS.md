# Cinematic Motion (Ken Burns Keyframing) & Visual Effects Guide

Static images in video quickly cause audience drop-off. Applying subtle, fluid camera motion (the Ken Burns effect) and atmospheric visual effects transforms static watercolor or digital illustrations into a dynamic cinematic experience.

---

## 1. Ken Burns Motion Choreography

Across an $N$-scene story project, cycle through 4 alternating camera movements ($i \pmod 4$):

### Pattern 0: Slow Push-In (Focus & Intimacy)
- **Use Case**: Emotional moments, solitary character portraits, interior focus.
- **Scale**: $1.00 \rightarrow 1.12$
- **Position**: Center ($0.0 \rightarrow 0.0$)

### Pattern 1: Slow Pull-Out (Reveal & Context)
- **Use Case**: Setting establishing shots, wide landscapes, character realizing their environment.
- **Scale**: $1.12 \rightarrow 1.00$
- **Position**: Center ($0.0 \rightarrow 0.0$)

### Pattern 2: Gentle Pan-Right & Push (Progressive Narrative)
- **Use Case**: Walking, traveling, approaching a destination.
- **Scale**: $1.04 \rightarrow 1.12$
- **Position X**: $-0.02 \rightarrow +0.02$ (subtle 4% horizontal drift)

### Pattern 3: Gentle Pan-Left & Pull (Reflective / Returning)
- **Use Case**: Looking back, resting, dialogue transitions.
- **Scale**: $1.12 \rightarrow 1.04$
- **Position X**: $+0.02 \rightarrow -0.02$

> [!TIP]
> **Safety Limits**: Scale should never exceed $1.15$ (to avoid pixel degradation on standard 1080p/2K renders). Pan should never exceed $\pm 0.03$ (to prevent black edges or jarring parallax distortion on 16:9 images).

---

## 2. CapCut Keyframe JSON Architecture

Keyframes are injected into each segment's `common_keyframes` array.

### Scale Keyframe Example:
```json
{
  "id": "UUID_LIST",
  "property_type": "KFTypeScaleX",
  "material_id": "",
  "keyframe_list": [
    {
      "id": "UUID_KF_START",
      "curveType": "Cubic",
      "graphID": "",
      "left_control": { "x": -0.35, "y": 0.0 },
      "right_control": { "x": 0.35, "y": 0.0 },
      "time_offset": 0,
      "values": [1.0]
    },
    {
      "id": "UUID_KF_END",
      "curveType": "Cubic",
      "graphID": "",
      "left_control": { "x": -0.35, "y": 0.0 },
      "right_control": { "x": 0.35, "y": 0.0 },
      "time_offset": 5200000,
      "values": [1.12]
    }
  ]
}
```

### Easing Curve Controls:
- `curveType: "Cubic"` with symmetric control handles `{"x": -0.35, "y": 0.0}` and `{"x": 0.35, "y": 0.0}` generates an S-curve easing:
  - **Ease In**: Starts gently from a near-stop.
  - **Constant Float**: Smooth cinematic drift across the scene.
  - **Ease Out**: Decelerates smoothly into the cut point, eliminating abrupt motion snaps.

---

## 3. CapCut Built-in Visual Effects Library

CapCut includes built-in effects that do not require external downloads or VIP subscriptions.

### Recommended Universal Atmosphere Effects:

1. **Soft (Luminous Bloom)**:
   - `effect_id`: `"6706773499836371463"`
   - `resource_id`: `"15206402"`
   - `param`: `effects_adjust_intensity` = `0.35`
   - **Look**: Softens hard digital pixels and adds a subtle warm light bleed, making watercolor paper look illuminated.

2. **Vignette (Cinematic Framing)**:
   - `effect_id`: `"6723086142658318860"`
   - `resource_id`: `"15206403"`
   - `param`: `effects_adjust_vignette` = `0.30`
   - **Look**: Gently darkens outer edges, directing viewer gaze to the character/action.

3. **Grain (Organic Film Texture)**:
   - `effect_id`: `"6732693826135134734"`
   - `resource_id`: `"15207311"`
   - `param`: `effects_adjust_grain` = `0.20`
   - **Look**: Adds subtle film noise to eliminate digital banding.

4. **Cinema (Subtle Contrast & Atmosphere)**:
   - `effect_id`: `"6719333680713568771"`
   - `resource_id`: `"15206416"`
   - `param`: `effects_adjust_filter` = `0.40`
