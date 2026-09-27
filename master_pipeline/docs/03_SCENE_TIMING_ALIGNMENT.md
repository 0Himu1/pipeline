# Scene Timing Alignment & SRT Subtitle Synchronization Specification

This specification codifies the mathematical models, speech boundary detection algorithms, and subtitle synchronization protocols used in **Stage 3 (`scene_aligner.py`)** of the Master Story Video Production Pipeline.

---

## 1. The Core Objective

The fundamental challenge in AI story video production is ensuring that **the visual scene shown on screen matches the exact dialogue and narrative beat being spoken by the voiceover**.

If a narrator is speaking about an old wooden drawer, the viewer must see the drawer image. If the visual cuts 15 seconds too early or too late, the viewer experiences severe cognitive dissonance, destroying narrative engagement.

```
Visual Timeline:  [ Scene 01: Wooden Drawer ]====>[ Scene 02: Brass Key ]====>[ Scene 03: Town Street ]
Voiceover Dialogue: "There is a kind of keeping... drawer..." ===> "A small brass key..." ===> "Frank on Mill St..."
                      ^ Exact Speech Pause Cut          ^ Exact Speech Pause Cut
```

---

## 2. Why Naive Uniform Snapping Fails (The Drift Problem)

Traditional timeline scripts divide audio duration uniformly:

$$\Delta t_{\text{avg}} = \frac{T_{\text{total}}}{N_{\text{scenes}}}$$

For an 8-minute story (490s) with 87 scenes, $\Delta t_{\text{avg}} \approx 5.63\text{ seconds/scene}$.
Previous aligners attempted to snap to the nearest acoustic silence within $\pm 2.5\text{s}$ of $i \times \Delta t_{\text{avg}}$.

### The Failure Mode:
- In real storytelling, narration density varies widely:
  - Scene A: Short transition sentence (12 words $\approx 3.2\text{s}$).
  - Scene B: Complex evocative sentence (45 words $\approx 11.5\text{s}$).
- With uniform division, Scene B is prematurely cut mid-sentence, while Scene A drags on.
- As errors accumulate, **the timeline drifts by 30 to 50+ seconds** by the middle of the story.

---

## 3. The SRT-Driven Semantic Alignment Engine

To eliminate drift completely, the pipeline utilizes the **SRT subtitle file** (`*.srt`) generated from the voiceover audio.

### Step 1: Subtitle Extraction & Inter-Subtitle Speech Pause Detection
Each subtitle entry $k$ has a time interval $[S_k, E_k]$ and text $T_k$. Between subtitle $k$ and $k+1$, a natural speech pause (breath/inhalation) occurs:

$$\text{Pause Start} = E_k, \quad \text{Pause End} = S_{k+1}$$
$$\text{Midpoint} = \frac{E_k + S_{k+1}}{2}, \quad \text{Duration} = \max(0, S_{k+1} - E_k)$$

### Step 2: Cumulative Spoken Dialogue Density Tracking
The engine computes the cumulative character length of spoken dialogue across all subtitles:

$$C_k = \sum_{j=1}^k \text{len}(T_j), \quad C_{\text{total}} = \sum_{j=1}^M \text{len}(T_j)$$

For scene $i \in [1, N-1]$, the ideal semantic cut point corresponds to dialogue target:

$$C_{\text{target}}(i) = \frac{i}{N} \times C_{\text{total}}$$

The algorithm finds subtitle index $k$ where $C_k \approx C_{\text{target}}(i)$.

### Step 3: Pause Candidate Selection & Optimization
Instead of cutting arbitrarily, the engine searches among candidate breath pauses $p$ in the vicinity of subtitle $k$ ($|p_k - k| \le 3$) and selects the pause that maximizes duration while penalizing distance:

$$\text{Score}(p) = \text{Duration}(p) - 0.4 \times |p_k - k| \times 100$$

### Step 4: Strict Boundary Clamping
To prevent visual flicker or runaway scenes, every cut point is strictly constrained:

$$\text{cut}_i \ge \text{cut}_{i-1} + \text{min\_gap\_ms} \quad (1800\text{ms})$$
$$\text{cut}_i \le T_{\text{total}} - (N - i) \times \text{min\_gap\_ms}$$

---

## 4. Subtitle Timestamp Re-Mapping (Stage 1 Silence Trimming)

When Stage 1 (`audio_trimmer.py`) trims silence gaps, the audio timeline shrinks monotonically. The trimmer records the mapping for each audio piece:

$$[\text{orig\_start}_m, \text{orig\_end}_m] \longrightarrow [\text{new\_start}_m, \text{new\_end}_m]$$

Any subtitle timestamp $t_{\text{orig}}$ is re-mapped:

$$t_{\text{new}} = \text{new\_start}_m + (t_{\text{orig}} - \text{orig\_start}_m)$$

This outputs `trimmed_voiceover.srt`, where subtitle text lines align with the compressed audio to the millisecond.

---

## 5. Acoustic Silence Fallback Mode (`--no-srt`)

If a project lacks an `.srt` file or is invoked with `--no-srt`:
1. `scene_aligner.py` measures audio RMS energy and computes dynamic silence threshold:
   $$\text{Threshold} = \text{dBFS}_{\text{audio}} - 15.0\text{ dB}$$
2. Runs `pydub.silence.detect_silence` with $\text{min\_pause} = 250\text{ms}$.
3. Snaps uniform targets to acoustic silence midpoints within $\pm 2500\text{ms}$.

---

## 6. Output Contract: `scene_timings.json`

The final output is `scene_timings.json`, structured with microsecond precision for CapCut:

```json
[
  {
    "scene_number": 1,
    "start_ms": 0,
    "end_ms": 7150,
    "duration_ms": 7150,
    "start_us": 0,
    "duration_us": 7150000,
    "start_sec": 0.0,
    "duration_sec": 7.15
  },
  {
    "scene_number": 2,
    "start_ms": 7150,
    "end_ms": 13549,
    "duration_ms": 6399,
    "start_us": 7150000,
    "duration_us": 6399000,
    "start_sec": 7.15,
    "duration_sec": 6.399
  }
]
```

### Microsecond Invariant:
$$\sum_{i=1}^N \text{duration\_us}_i \equiv T_{\text{total\_us}}$$
The final scene duration absorbs any single-microsecond rounding residual, ensuring **zero gap and zero overlap** when loaded into CapCut's timeline.
