# CapCut Desktop (v5+) Project Architecture & Internals Specification

This document details the reverse-engineered internal filesystem architecture, JSON schema bindings, timeline synchronization mechanisms, and integrity rules for automated CapCut desktop draft creation and modification.

---

## 1. Directory Structure & Root Registry

CapCut stores drafts in:
```
%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\
├── root_meta_info.json                     # Global project registry
└── <Project Name>/                         # Project Draft Directory
    ├── draft_content.json                  # Root Timeline mirror
    ├── draft_content.json.bak              # Root Timeline backup
    ├── template-2.tmp                      # Fast-load binary/JSON mirror
    ├── draft_meta_info.json                # Project-level metadata & materials
    ├── timeline_layout.json                # UI dock layout & timeline association
    ├── draft_settings                      # INI settings (timestamps, edit keys)
    ├── Resources/
    │   └── local/                          # Imported audio, image, and video files
    └── Timelines/                          # Multi-timeline architecture
        ├── project.json                    # Project timeline registry
        ├── project.json.bak
        └── <TIMELINE_UUID>/                # Main timeline container folder
            ├── draft_content.json          # Primary timeline definition
            ├── draft_content.json.bak
            ├── template-2.tmp              # Timeline cache mirror
            └── template.tmp                # Timeline initial state
```

---

## 2. The Four Critical UUID Bindings (Integrity Invariants)

If any of these four bindings do not match, **CapCut will refuse to open the project**:

### Invariant 1: Timeline UUID Match
The Timeline UUID (e.g. `0DFA55EC-431B-43bb-8B3A-876DD0ED8428`) must match across:
1. `Timelines/<TIMELINE_UUID>/` (The folder name)
2. `Timelines/project.json` $\rightarrow$ `main_timeline_id`
3. `Timelines/project.json` $\rightarrow$ `timelines[0].id`
4. `timeline_layout.json` $\rightarrow$ `dockItems[0].timelineIds[0]`
5. `draft_content.json` $\rightarrow$ `"id": "<TIMELINE_UUID>"`
6. `Timelines/<TIMELINE_UUID>/draft_content.json` $\rightarrow$ `"id": "<TIMELINE_UUID>"`

> [!CAUTION]
> In older CapCut versions, `draft_content.json` was standalone. In CapCut v5+, changing `draft_content.json.id` without matching `project.json` and the folder name will cause the project to fail silently upon opening.

### Invariant 2: Shadow File Synchronization
The following files **must be byte-identical** at all times:
- Root `draft_content.json` $\equiv$ `Timelines/<TIMELINE_UUID>/draft_content.json`
- Root `template-2.tmp` $\equiv$ `Timelines/<TIMELINE_UUID>/template-2.tmp` $\equiv$ `draft_content.json`

### Invariant 3: Global Registry Count (`root_meta_info.json`)
- `root_meta_info.json` contains `all_draft_store: [...]` and `draft_ids: <Integer>`.
- `draft_ids` **must equal** `all_draft_store.length`. If projects are added without updating `draft_ids`, index corruption occurs.

### Invariant 4: No Lock Files
- If CapCut crashed previously, a `.locked` file may linger in the draft root. Always verify and delete `.locked` before launching CapCut.

---

## 3. Path Placeholders & Media References

In `draft_content.json`, media paths use dynamic draft relative placeholders:

```
##_draftpath_placeholder_<UUID>_##/Resources/local/<filename>
```

- When CapCut loads the draft, it dynamically substitutes `##_draftpath_placeholder_..._##` with the project's absolute directory on the current host.
- Always place imported media in `Resources/local/` and reference them via this placeholder.

---

## 4. Time Units & Timeline Calculations

- **Unit**: All timeline durations, starts, and keyframe offsets are measured in **Microseconds ($\mu\text{s}$)**.
  - $1\text{ ms} = 1,000\ \mu\text{s}$
  - $1\text{ second} = 1,000,000\ \mu\text{s}$
- **Segment Durations**:
  - `target_timerange.start`: The start time on the project master timeline.
  - `target_timerange.duration`: The visible duration on the timeline.
  - `source_timerange.start`: Start offset within the source media asset (0 for images).
  - `source_timerange.duration`: Duration sliced from the source media asset.

---

## 5. Track Schema

In `draft_content.json`:
- `tracks[0]` (Type: `"video"`): Main image/video track containing all scene segments.
- `tracks[1]` (Type: `"audio"`): Narration audio track containing the voiceover segment.
- `tracks[2]` (Type: `"effect"`): Global visual effects track covering the timeline duration.

---

## 6. Media Registry & The "Link Media" Contract (`draft_materials_copied_info`)

In `draft_meta_info.json`, CapCut maintains an internal copy manifest:
```json
"draft_materials_copied_info": [
  {
    "dst_path": "Resources/local/001_A_Wide_Watercolor_Scene_Of.jpeg",
    "src_path": "D:/Himu/Luna/projects/The Waiting Room/sequenced_images/001_A_Wide_Watercolor_Scene_Of.jpeg"
  }
]
```

### Critical Rules for Preventing "Unlinked Media":
1. **Verification on Project Open**: Whenever CapCut opens a draft, it validates every single entry in `draft_materials_copied_info`. For each entry, CapCut checks if `<DraftRoot>/<dst_path>` exists on disk.
2. **Missing Files Trigger Modal**: If any file listed in `draft_materials_copied_info` does not exist in `Resources/local/`, CapCut **blocks project opening** and displays the modal: *"Couldn't find some of the imported media files. Link the media files then edit."*
3. **No Stale References**: When creating or rebuilding a project, `draft_materials_copied_info` **must be rebuilt from scratch** containing *only* files that currently exist in the project's `Resources/local/` directory. Never inherit this array from an existing draft!
4. **Draft Materials Sync**: `draft_materials[0].value` in `draft_meta_info.json` must mirror the exact assets present in `draft_materials_copied_info`.

---

## 7. Project Template Isolation (Clean Project Invariant)

> [!IMPORTANT]
> **Never clone an active user draft as a template.** Active drafts carry over lingering subtitle fragments (`extra_info.subtitle_fragment_info_list`), secondary background music tracks, and old media registries.
> 
> Always initialize new projects from a pristine schema (`master_pipeline/templates/clean_project/`) where:
> - `tracks` is initially empty `[]`.
> - All 55 material arrays are initialized to `[]`.
> - `extra_info` is `null`.
> - `draft_materials_copied_info` is `[]`.
> - Every project generates a fresh `draft_id = uuid()` and `timeline_id = uuid()`.

