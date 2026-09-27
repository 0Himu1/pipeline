# Professional Voiceover Audio Trimming Rulebook & Knowledge Base

This rulebook codifies the audio engineering standards, psychoacoustic principles, and digital signal processing (DSP) rules for voiceover narration editing, silence trimming, and natural breath retention for narrative storytelling, audiobooks, and documentary video production.

---

## 1. The Core Objective

The goal of voiceover trimming is **not** maximum compression or total silence elimination. 
The goal is **removing dead hesitation while preserving human pacing, emotional weight, and seamless phonetic clarity**.

---

## 2. Psychoacoustic Pacing Hierarchy (Tiered Pauses)

Never replace silences with a single arbitrary duration (e.g., 280ms). Human speech has an organic hierarchical cadence:

### Tier 1: Intra-Sentence Micro-Pauses (Commas, Clauses, Thinking Pauses)
- **Natural Duration in Speech**: 300ms – 650ms.
- **Rule**: Retain **350ms – 450ms**.
- **Rationale**: Shortening below 300ms destroys comprehension; listeners need micro-pauses to process clause relationships without feeling rushed.
- **Action**: If a natural pause is $< 650\text{ms}$, either leave it intact or gently compress to ~380ms.

### Tier 2: Inter-Sentence Boundaries (Sentence Breaks)
- **Natural Duration in Speech**: 700ms – 1800ms.
- **Rule**: Standardize to **600ms – 750ms** (650ms target).
- **Rationale**: When a sentence ends, the speaker releases air and inhales. The listener requires cognitive closure before receiving the next thought. Cutting this to $< 500\text{ms}$ creates the auditory illusion that sentences are colliding or interrupting one another.

### Tier 3: Paragraph & Narrative Shift Boundaries (Scene Transitions)
- **Natural Duration in Speech**: 1800ms – 4000ms+.
- **Rule**: Compress dead air to **900ms – 1200ms** (1000ms target).
- **Rationale**: Signals a major shift in scene, topic, or emotional tone. Allows the visual transition (fade, cut, pan) to breathe before the next scene's narration begins.

---

## 3. Phonetic Protection (Zero Phoneme & Consonant Clipping)

Automatic silence removal tools (like naive threshold gates) frequently ruin voiceovers by clipping initial and trailing phonemes. The following buffers are **mandatory**:

```
[ ...SPEECH... ] ===> [ DECAY BUFFER: 250-350ms ] ===> [ COMPRESSED SILENCE ] ===> [ ATTACK BUFFER: 150-200ms ] ===> [ ...NEXT SPEECH... ]
```

### Pre-Speech Attack Padding (150ms – 200ms)
- **Why**: Captures the narrator's subtle inhalation, mouth preparation, and soft consonant onsets (*p, t, k, h, th, b, d*).
- **Failure Mode**: Cutting closer than 100ms creates abrupt, glottal-sounding syllable starts and cuts off breath.

### Post-Speech Decay Padding (250ms – 350ms)
- **Why**: Trailing consonants (*s, z, sh, f, th, d, t, m, n, ed*) carry low acoustic energy that dips below detection thresholds while speech is still occurring. Room acoustic decay also exists here.
- **Failure Mode**: Cutting with $< 200\text{ms}$ trailing margin clips off word endings, turning "passed" into "pass" or dropping soft sentence terminals.

---

## 4. Acoustic Splice & Crossfading Standards

### Never Insert Digital Zero (`0x0000`)
- Splicing pure digital silence against recorded room tone produces a jarring "vacuum" effect where the background room ambiance drops out and abruptly kicks back in.
- **Standard**: Always preserve natural room tone within the retained pause. Trim from the **middle** of the detected pause, preserving the ambient tail of the preceding word and the ambient lead-in of the following word.

### Equal-Power Crossfading (20ms – 30ms)
- Every joined boundary must use a **20ms–25ms equal-power crossfade** (or raised cosine curve).
- Eliminates zero-crossing clicks, DC offset pops, and room-tone phase discontinuity.

---

## 5. DSP Detection Threshold Guidelines

- **Baseline Noise Floor Measurement**: Measure the silent intervals of the recording (typically $-55\text{ to } -65\text{ dBFS}$).
- **Relative Threshold**: Set the silence detector to **$18\text{ to } 22\text{ dB}$ below average speech RMS** (e.g., if speech average is $-33.4\text{ dBFS}$, set silence threshold to $\approx -53.5\text{ dBFS}$).
- **Minimum Qualification Gate**: Candidate silences must sustain below the threshold for at least **600ms** before triggering silence compression. Short dips $< 500\text{ms}$ are natural speech articulation gaps (plosives, short hesitations) and must not be cut.

---

## 6. Trimming Parameters Quick-Reference Table

| Parameter | Recommended Value | Purpose |
| :--- | :--- | :--- |
| **Silence Detection Gate** | `avg_dBFS - 20 dB` ($\approx -53\text{ dBFS}$) | Protects whispers & trailing fricatives |
| **Min Silence Duration** | `600 ms` | Ignores natural micro-plosives inside words |
| **Pre-Speech Attack Pad** | `180 ms` | Preserves breath & consonant attack |
| **Post-Speech Decay Pad** | `300 ms` | Preserves trailing consonants & room decay |
| **Crossfade Window** | `25 ms` (equal power) | Eliminates pops, clicks, and noise jumps |
| **Tier 1 (Micro-pause)** | `380 ms` | Comma / intra-sentence rhythm |
| **Tier 2 (Sentence break)**| `650 ms` | Cognitive reset & breath |
| **Tier 3 (Scene shift)** | `1000 ms` | Dramatic narrative & visual transition |

---

## 7. Automatic SRT Subtitle Re-Alignment

When silence intervals are compressed or excised from the voiceover, the physical duration of the audio shrinks. If subtitle timestamps are not transformed simultaneously, the transcript will immediately drift and fall out of sync with spoken dialogue.

### The Monotonic Mapping Formula:
During audio reconstruction, each retained speech chunk $k$ from original interval $[O_{\text{start}}^{(k)}, O_{\text{end}}^{(k)}]$ is mapped to the new audio timeline interval $[N_{\text{start}}^{(k)}, N_{\text{end}}^{(k)}]$:

$$t_{\text{new}} = \begin{cases}
N_{\text{start}}^{(k)} & \text{if } t_{\text{orig}} < O_{\text{start}}^{(k)} \\
N_{\text{start}}^{(k)} + (t_{\text{orig}} - O_{\text{start}}^{(k)}) & \text{if } O_{\text{start}}^{(k)} \le t_{\text{orig}} \le O_{\text{end}}^{(k)} \\
N_{\text{end}}^{(\text{last})} & \text{if } t_{\text{orig}} > O_{\text{end}}^{(\text{last})}
\end{cases}$$

### Automatic Cleanup:
- Parses timestamps in `HH:MM:SS,mmm` format.
- Strips any third-party watermark notices (e.g. TurboScribe notices).
- Exports `trimmed_voiceover.srt` alongside `trimmed_voiceover.mp3` and `trimmed_voiceover.wav`.
- Subtitle blocks that collapse into zero duration are clamped to a minimum legible duration of $300\text{ms}$.

