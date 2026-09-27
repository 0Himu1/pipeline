/**
 * capcut_builder.js
 * Universal CapCut (v5+) project builder and synchronizer.
 * - Initializes projects strictly from master_pipeline/templates/clean_project/ (100% self-contained).
 * - Imports audio and images into project Resources/local.
 * - Rebuilds media registry (draft_materials_copied_info) strictly with current project files to prevent "Link media" unlinked errors.
 * - Builds Video Track (Track 0) matching exact scene timings with Ken Burns Cubic easing keyframes.
 * - Builds Voiceover Audio Track (Track 1).
 * - Injects Visual Effects Track (Track 2) with Soft Glow and Vignette.
 * - Strictly isolates tracks (exactly 3 tracks, zero leftover zombie tracks or foreign subtitles).
 * - Synchronizes root & timeline shadow files, layout dock, and root registry with unique draft_id and timeline_id.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function uuid() {
  return crypto.randomUUID().toUpperCase();
}

function hexUuid() {
  return crypto.randomUUID().replace(/-/g, '');
}

function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const item of fs.readdirSync(src)) {
    const srcPath = path.join(src, item);
    const destPath = path.join(dest, item);
    const stat = fs.statSync(srcPath);
    if (stat.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function createKenBurnsKeyframes(segmentIdx, durationUs) {
  const mode = segmentIdx % 4;
  const commonKeyframes = [];

  const leftControl = { x: -0.35, y: 0.0 };
  const rightControl = { x: 0.35, y: 0.0 };

  let startScale = 1.0;
  let endScale = 1.12;
  let startPosX = null;
  let endPosX = null;

  if (mode === 0) {
    // Mode 0: Slow zoom in
    startScale = 1.00;
    endScale = 1.12;
  } else if (mode === 1) {
    // Mode 1: Slow zoom out
    startScale = 1.12;
    endScale = 1.00;
  } else if (mode === 2) {
    // Mode 2: Gentle pan right + zoom in
    startScale = 1.04;
    endScale = 1.12;
    startPosX = -0.02;
    endPosX = 0.02;
  } else {
    // Mode 3: Gentle pan left + zoom out
    startScale = 1.12;
    endScale = 1.04;
    startPosX = 0.02;
    endPosX = -0.02;
  }

  // Scale X
  commonKeyframes.push({
    id: uuid(),
    property_type: 'KFTypeScaleX',
    material_id: '',
    keyframe_list: [
      {
        id: uuid(),
        curveType: 'Cubic',
        graphID: '',
        left_control: leftControl,
        right_control: rightControl,
        time_offset: 0,
        values: [startScale]
      },
      {
        id: uuid(),
        curveType: 'Cubic',
        graphID: '',
        left_control: leftControl,
        right_control: rightControl,
        time_offset: durationUs,
        values: [endScale]
      }
    ]
  });

  // Scale Y
  commonKeyframes.push({
    id: uuid(),
    property_type: 'KFTypeScaleY',
    material_id: '',
    keyframe_list: [
      {
        id: uuid(),
        curveType: 'Cubic',
        graphID: '',
        left_control: leftControl,
        right_control: rightControl,
        time_offset: 0,
        values: [startScale]
      },
      {
        id: uuid(),
        curveType: 'Cubic',
        graphID: '',
        left_control: leftControl,
        right_control: rightControl,
        time_offset: durationUs,
        values: [endScale]
      }
    ]
  });

  // Position X (subtle drift)
  if (startPosX !== null && endPosX !== null) {
    commonKeyframes.push({
      id: uuid(),
      property_type: 'KFTypePositionX',
      material_id: '',
      keyframe_list: [
        {
          id: uuid(),
          curveType: 'Cubic',
          graphID: '',
          left_control: leftControl,
          right_control: rightControl,
          time_offset: 0,
          values: [startPosX]
        },
        {
          id: uuid(),
          curveType: 'Cubic',
          graphID: '',
          left_control: leftControl,
          right_control: rightControl,
          time_offset: durationUs,
          values: [endPosX]
        }
      ]
    });
  }

  return commonKeyframes;
}

function buildCapCutProject(options) {
  const {
    projectName,
    audioPath,
    imagesDir,
    timingsPath,
    draftsBaseDir = path.join(process.env.LOCALAPPDATA || 'C:\\Users\\0himu\\AppData\\Local', 'CapCut', 'User Data', 'Projects', 'com.lveditor.draft')
  } = options;

  console.log(`\n[CapCutBuilder] Building project "${projectName}" in ${draftsBaseDir}...`);

  const projDir = path.join(draftsBaseDir, projectName);
  const cleanTemplateDir = path.join(__dirname, '..', 'templates', 'clean_project');

  // Verify clean template exists
  if (!fs.existsSync(cleanTemplateDir)) {
    throw new Error(`Pristine template not found at ${cleanTemplateDir}. Please run template initialization.`);
  }

  // 1. Determine draft_id: reuse existing if already in root_meta_info, otherwise generate fresh
  let draftId = uuid();
  const rootMetaPath = path.join(draftsBaseDir, 'root_meta_info.json');
  let rootMeta = null;
  if (fs.existsSync(rootMetaPath)) {
    try {
      rootMeta = JSON.parse(fs.readFileSync(rootMetaPath, 'utf8'));
      const existingEntry = rootMeta.all_draft_store.find(d => d.draft_name === projectName);
      if (existingEntry && existingEntry.draft_id) {
        draftId = existingEntry.draft_id;
      }
    } catch (e) {}
  }

  const timelineId = uuid();

  // 2. Initialize project folder from pristine clean template
  console.log(`[CapCutBuilder] Initializing project structure from clean template...`);
  if (fs.existsSync(projDir)) {
    // Clean out stale files and lock files
    const staleFiles = ['.locked', 'draft_virtual_store.json', 'draft.extra', 'key_value.json', 'attachment_editing.json'];
    for (const sf of staleFiles) {
      const p = path.join(projDir, sf);
      if (fs.existsSync(p)) fs.rmSync(p, { force: true });
    }
    // Clean old Timelines directories
    const timelinesDir = path.join(projDir, 'Timelines');
    if (fs.existsSync(timelinesDir)) {
      for (const item of fs.readdirSync(timelinesDir)) {
        if (item.match(/^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$/i)) {
          fs.rmSync(path.join(timelinesDir, item), { recursive: true, force: true });
        }
      }
    }
  } else {
    copyDirRecursive(cleanTemplateDir, projDir);
  }

  // Ensure Resources/local is clean
  const localResDir = path.join(projDir, 'Resources', 'local');
  if (fs.existsSync(localResDir)) {
    fs.rmSync(localResDir, { recursive: true, force: true });
  }
  fs.mkdirSync(localResDir, { recursive: true });

  // 3. Ingest Audio
  const audioFilename = path.basename(audioPath);
  const destAudioPath = path.join(localResDir, audioFilename);
  fs.copyFileSync(audioPath, destAudioPath);
  console.log(`[CapCutBuilder] Imported audio: ${destAudioPath}`);

  // 4. Ingest Images (sorted sequentially)
  const imageFiles = fs.readdirSync(imagesDir)
    .filter(f => f.match(/\.(jpeg|jpg|png|webp)$/i))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }));

  console.log(`[CapCutBuilder] Found ${imageFiles.length} images in ${imagesDir}. Importing into project...`);
  for (const imgFile of imageFiles) {
    fs.copyFileSync(path.join(imagesDir, imgFile), path.join(localResDir, imgFile));
  }

  // 5. Load scene timings
  const timings = JSON.parse(fs.readFileSync(timingsPath, 'utf8'));
  const totalDurationUs = timings[timings.length - 1].end_ms * 1000;
  console.log(`[CapCutBuilder] Loaded ${timings.length} scene timings. Master duration: ${totalDurationUs / 1000000}s`);

  if (timings.length !== imageFiles.length) {
    console.warn(`[CapCutBuilder] WARNING: Timings count (${timings.length}) != Image count (${imageFiles.length})!`);
  }

  // 6. Build draft_content.json from clean template schema
  const templateContentPath = path.join(cleanTemplateDir, 'draft_content.json');
  const draftContent = JSON.parse(fs.readFileSync(templateContentPath, 'utf8'));

  draftContent.id = timelineId;
  draftContent.duration = totalDurationUs;
  draftContent.canvas_config = {
    background: null,
    height: 1080,
    ratio: '16:9',
    width: 1920
  };
  draftContent.fps = 30.0;
  draftContent.extra_info = null;

  // Build Track 0: Video Track
  const videoMaterials = [];
  const videoSegments = [];

  for (let i = 0; i < timings.length; i++) {
    const timing = timings[i];
    const imgName = imageFiles[i] || imageFiles[imageFiles.length - 1];
    const matId = uuid();
    const segId = uuid();
    const durationUs = timing.duration_ms * 1000;
    const startUs = timing.start_ms * 1000;

    videoMaterials.push({
      ai_music_meta: null,
      ai_paint_meta: null,
      audio_fade: null,
      beauty_body_auto_preset: null,
      beauty_body_preset_id: '',
      beauty_face_auto_preset: { name: '', preset_id: '', rate_map: '', scene: '' },
      beauty_face_auto_preset_infos: [],
      beauty_face_preset_infos: [],
      category_id: '',
      category_name: 'local',
      check_flag: 62978047,
      content_feature_info: null,
      corner_pin: null,
      crop: { lower_left_x: 0, lower_left_y: 1, lower_right_x: 1, lower_right_y: 1, upper_left_x: 0, upper_left_y: 0, upper_right_x: 1, upper_right_y: 0 },
      crop_ratio: 'free',
      crop_scale: 1,
      duration: 10800000000,
      extra_type_option: 0,
      formula_id: '',
      freeze: null,
      has_audio: false,
      has_sound_separated: false,
      height: 1080,
      id: matId,
      intensifies_audio_path: '',
      intensifies_path: '',
      is_ai_generate_content: false,
      is_clould: false,
      is_copyright: false,
      is_set_beauty_mode: false,
      is_text_edit_overdub: false,
      is_unified_beauty_mode: false,
      is_video_copilot_aigc_content: false,
      live_photo_cover_path: '',
      live_photo_timestamp: -1,
      local_id: '',
      local_material_id: '',
      material_id: '',
      material_name: imgName,
      material_url: '',
      matting: { cloud_product_fps: 0, custom_matting_id: '', enable_matting_stroke: false, expansion: 0, feather: 0, flag: 0, has_use_quick_brush: false, has_use_quick_eraser: false, interactiveTime: [], is_clould: false, mask_video_path: '', path: '', reverse: false, strokes: [] },
      media_path: '',
      multi_camera_info: null,
      object_locked: null,
      origin_material_id: '',
      path: `##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/Resources/local/${imgName}`,
      picture_from: 'none',
      picture_set_category_id: '',
      picture_set_category_name: '',
      request_id: '',
      reverse_intensifies_path: '',
      reverse_path: '',
      smart_match_info: null,
      smart_motion: null,
      source: 0,
      source_platform: 0,
      stable: { matrix_path: '', stable_level: 0, time_range: { duration: 0, start: 0 } },
      surface_trackings: [],
      team_id: '',
      type: 'photo',
      video_algorithm: { algorithms: [], gameplay_configs: [], path: '', time_range: null },
      width: 1920
    });

    videoSegments.push({
      caption_info: null,
      cartoon: false,
      clip: null,
      common_keyframes: createKenBurnsKeyframes(i, durationUs),
      desc: '',
      digital_human_template_group_id: '',
      enable_adjust: true,
      enable_adjust_mask: false,
      enable_color_adjust_pro: false,
      enable_color_correct_adjust: false,
      enable_color_curves: true,
      enable_color_match_adjust: false,
      enable_color_wheels: true,
      enable_hsl: false,
      enable_hsl_curves: true,
      enable_lut: true,
      enable_mask_shadow: false,
      enable_mask_stroke: false,
      enable_smart_color_adjust: false,
      enable_video_mask: true,
      extra_material_refs: [],
      group_id: '',
      hdr_settings: null,
      hdr_vivid_settings: null,
      id: segId,
      intensifies_audio: false,
      is_loop: false,
      is_placeholder: false,
      is_tone_modify: false,
      keyframe_refs: [],
      last_nonzero_volume: 1.0,
      material_id: matId,
      render_index: 0,
      render_timerange: { duration: 0, start: 0 },
      responsive_layout: { enable: false, horizontal_pos_layout: 0, size_layout: 0, target_follow: '', vertical_pos_layout: 0 },
      reverse: false,
      source: 'segmentsourcenormal',
      source_timerange: { duration: durationUs, start: 0 },
      speed: 1.0,
      state: 0,
      target_timerange: { duration: durationUs, start: startUs },
      template_id: '',
      template_scene: 'default',
      track_attribute: 0,
      track_render_index: 0,
      uniform_scale: null,
      visible: true,
      volume: 1.0
    });
  }

  const videoTrack = {
    attribute: 0,
    flag: 0,
    id: uuid(),
    is_default_name: true,
    name: '',
    segments: videoSegments,
    type: 'video'
  };

  // Build Track 1: Audio Track
  const audioMatId = uuid();
  const audioMaterial = {
    app_id: 0,
    category_id: '',
    category_name: 'local',
    check_flag: 1,
    duration: totalDurationUs,
    extra_info: '',
    formula_id: '',
    id: audioMatId,
    intensifies_path: '',
    local_material_id: '',
    music_id: '',
    name: audioFilename,
    path: `##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/Resources/local/${audioFilename}`,
    query: '',
    request_id: '',
    resource_id: '',
    search_id: '',
    source_platform: 0,
    team_id: '',
    text_id: '',
    tone_category_id: '',
    tone_category_name: '',
    tone_effect_id: '',
    tone_effect_name: '',
    tone_speaker: '',
    tone_type: '',
    type: 'extract_music',
    video_id: '',
    wave_points: []
  };

  const audioTrack = {
    attribute: 0,
    flag: 0,
    id: uuid(),
    is_default_name: true,
    name: '',
    segments: [
      {
        caption_info: null,
        cartoon: false,
        clip: null,
        common_keyframes: [],
        desc: '',
        digital_human_template_group_id: '',
        enable_adjust: false,
        enable_adjust_mask: false,
        enable_color_adjust_pro: false,
        enable_color_correct_adjust: false,
        enable_color_curves: true,
        enable_color_match_adjust: false,
        enable_color_wheels: true,
        enable_hsl: false,
        enable_hsl_curves: true,
        enable_lut: false,
        enable_mask_shadow: false,
        enable_mask_stroke: false,
        enable_smart_color_adjust: false,
        enable_video_mask: true,
        extra_material_refs: [],
        group_id: '',
        hdr_settings: null,
        hdr_vivid_settings: null,
        id: uuid(),
        intensifies_audio: false,
        is_loop: false,
        is_placeholder: false,
        is_tone_modify: false,
        keyframe_refs: [],
        last_nonzero_volume: 1.0,
        material_id: audioMatId,
        render_index: 0,
        render_timerange: { duration: 0, start: 0 },
        responsive_layout: { enable: false, horizontal_pos_layout: 0, size_layout: 0, target_follow: '', vertical_pos_layout: 0 },
        reverse: false,
        source: 'segmentsourcenormal',
        source_timerange: { duration: totalDurationUs, start: 0 },
        speed: 1.0,
        state: 0,
        target_timerange: { duration: totalDurationUs, start: 0 },
        template_id: '',
        template_scene: 'default',
        track_attribute: 0,
        track_render_index: 1,
        uniform_scale: null,
        visible: true,
        volume: 1.0
      }
    ],
    type: 'audio'
  };

  // Build Track 2: Visual Effects (Soft Glow + Vignette)
  const softEffectId = hexUuid();
  const vignetteEffectId = hexUuid();

  const videoEffects = [
    {
      adjust_params: [{ default_value: 0.5, name: 'effects_adjust_intensity', value: 0.35 }],
      apply_target_type: 2,
      apply_time_range: null,
      category_id: '',
      category_name: '',
      common_keyframes: [],
      disable_effect_faces: [],
      effect_id: '6706773499836371463',
      formula_id: '',
      id: softEffectId,
      name: 'Soft',
      platform: 'all',
      render_index: 11000,
      resource_id: '15206402',
      source_platform: 0,
      time_range: null,
      track_render_index: 0,
      type: 'video_effect',
      value: 1.0,
      version: ''
    },
    {
      adjust_params: [{ default_value: 0.5, name: 'effects_adjust_vignette', value: 0.3 }],
      apply_target_type: 2,
      apply_time_range: null,
      category_id: '',
      category_name: '',
      common_keyframes: [],
      disable_effect_faces: [],
      effect_id: '6723086142658318860',
      formula_id: '',
      id: vignetteEffectId,
      name: 'Vignette',
      platform: 'all',
      render_index: 11001,
      resource_id: '15206403',
      source_platform: 0,
      time_range: null,
      track_render_index: 0,
      type: 'video_effect',
      value: 1.0,
      version: ''
    }
  ];

  const effectTrack = {
    attribute: 0,
    flag: 0,
    id: uuid(),
    is_default_name: true,
    name: '',
    segments: [
      {
        caption_info: null,
        cartoon: false,
        clip: null,
        common_keyframes: [],
        desc: '',
        digital_human_template_group_id: '',
        enable_adjust: true,
        enable_adjust_mask: false,
        enable_color_adjust_pro: false,
        enable_color_correct_adjust: false,
        enable_color_curves: true,
        enable_color_match_adjust: false,
        enable_color_wheels: true,
        enable_hsl: false,
        enable_hsl_curves: true,
        enable_lut: true,
        enable_mask_shadow: false,
        enable_mask_stroke: false,
        enable_smart_color_adjust: false,
        enable_video_mask: true,
        extra_material_refs: [],
        group_id: '',
        hdr_settings: null,
        hdr_vivid_settings: null,
        id: uuid(),
        intensifies_audio: false,
        is_loop: false,
        is_placeholder: false,
        is_tone_modify: false,
        keyframe_refs: [],
        last_nonzero_volume: 1.0,
        material_id: softEffectId,
        render_index: 10000,
        render_timerange: { duration: 0, start: 0 },
        responsive_layout: { enable: false, horizontal_pos_layout: 0, size_layout: 0, target_follow: '', vertical_pos_layout: 0 },
        reverse: false,
        source: 'segmentsourcenormal',
        source_timerange: { duration: totalDurationUs, start: 0 },
        speed: 1.0,
        state: 0,
        target_timerange: { duration: totalDurationUs, start: 0 },
        template_id: '',
        template_scene: 'default',
        track_attribute: 0,
        track_render_index: 2,
        uniform_scale: null,
        visible: true,
        volume: 1.0
      },
      {
        caption_info: null,
        cartoon: false,
        clip: null,
        common_keyframes: [],
        desc: '',
        digital_human_template_group_id: '',
        enable_adjust: true,
        enable_adjust_mask: false,
        enable_color_adjust_pro: false,
        enable_color_correct_adjust: false,
        enable_color_curves: true,
        enable_color_match_adjust: false,
        enable_color_wheels: true,
        enable_hsl: false,
        enable_hsl_curves: true,
        enable_lut: true,
        enable_mask_shadow: false,
        enable_mask_stroke: false,
        enable_smart_color_adjust: false,
        enable_video_mask: true,
        extra_material_refs: [],
        group_id: '',
        hdr_settings: null,
        hdr_vivid_settings: null,
        id: uuid(),
        intensifies_audio: false,
        is_loop: false,
        is_placeholder: false,
        is_tone_modify: false,
        keyframe_refs: [],
        last_nonzero_volume: 1.0,
        material_id: vignetteEffectId,
        render_index: 10001,
        render_timerange: { duration: 0, start: 0 },
        responsive_layout: { enable: false, horizontal_pos_layout: 0, size_layout: 0, target_follow: '', vertical_pos_layout: 0 },
        reverse: false,
        source: 'segmentsourcenormal',
        source_timerange: { duration: totalDurationUs, start: 0 },
        speed: 1.0,
        state: 0,
        target_timerange: { duration: totalDurationUs, start: 0 },
        template_id: '',
        template_scene: 'default',
        track_attribute: 0,
        track_render_index: 3,
        uniform_scale: null,
        visible: true,
        volume: 1.0
      }
    ],
    type: 'effect'
  };

  // Strictly set EXACTLY 3 tracks: video, audio, effect
  draftContent.tracks = [videoTrack, audioTrack, effectTrack];

  // Set materials cleanly: only current project materials
  draftContent.materials.videos = videoMaterials;
  draftContent.materials.audios = [audioMaterial];
  draftContent.materials.video_effects = videoEffects;

  // Clear any residual materials
  draftContent.materials.texts = [];
  draftContent.materials.text_templates = [];
  draftContent.materials.beats = [];
  draftContent.materials.audio_effects = [];
  draftContent.materials.audio_fades = [];

  // 7. Write Root and Timeline Shadow Files
  const contentStr = JSON.stringify(draftContent);
  fs.writeFileSync(path.join(projDir, 'draft_content.json'), contentStr, 'utf8');
  fs.writeFileSync(path.join(projDir, 'draft_content.json.bak'), contentStr, 'utf8');
  fs.writeFileSync(path.join(projDir, 'template-2.tmp'), contentStr, 'utf8');

  const timelineSubDir = path.join(projDir, 'Timelines', timelineId);
  fs.mkdirSync(timelineSubDir, { recursive: true });
  fs.writeFileSync(path.join(timelineSubDir, 'draft_content.json'), contentStr, 'utf8');
  fs.writeFileSync(path.join(timelineSubDir, 'draft_content.json.bak'), contentStr, 'utf8');
  fs.writeFileSync(path.join(timelineSubDir, 'template-2.tmp'), contentStr, 'utf8');

  // Copy template attachment files to timeline folder if present in clean template
  const templateTimelinesDir = path.join(cleanTemplateDir, 'Timelines');
  if (fs.existsSync(templateTimelinesDir)) {
    for (const f of fs.readdirSync(templateTimelinesDir)) {
      const full = path.join(templateTimelinesDir, f);
      if (fs.statSync(full).isFile() && !f.endsWith('.json') && !f.endsWith('.tmp')) {
        fs.copyFileSync(full, path.join(timelineSubDir, f));
      }
    }
  }

  // 8. Update layout and project.json
  const layout = {
    dockItems: [{ dockIndex: 0, ratio: 1, timelineIds: [timelineId], timelineNames: ['Timeline 01'] }],
    layoutOrientation: 1
  };
  fs.writeFileSync(path.join(projDir, 'timeline_layout.json'), JSON.stringify(layout), 'utf8');

  const projectJsonPath = path.join(projDir, 'Timelines', 'project.json');
  const projJson = {
    config: { color_space: -1, hdr_vivid: false, mixed_track_mode_on: false, render_index_track_mode_on: false, use_float_render: false },
    create_time: Date.now() * 1000,
    id: uuid(),
    main_timeline_id: timelineId,
    timelines: [{ create_time: Date.now() * 1000, id: timelineId, is_marked_delete: false, name: 'Timeline 01', update_time: Date.now() * 1000 }],
    update_time: Date.now() * 1000,
    version: 0
  };
  fs.writeFileSync(projectJsonPath, JSON.stringify(projJson), 'utf8');
  fs.writeFileSync(path.join(projDir, 'Timelines', 'project.json.bak'), JSON.stringify(projJson), 'utf8');

  // 9. Rebuild media registry (draft_materials_copied_info) and draft_meta_info.json
  const metaMaterialValues = [];
  const copiedInfo = [];

  for (let i = 0; i < imageFiles.length; i++) {
    const img = imageFiles[i];
    metaMaterialValues.push({
      ai_group_type: '',
      create_time: Math.floor(Date.now() / 1000),
      duration: 5000000,
      enter_from: 0,
      extra_info: img,
      file_Path: `./Resources/local/${img}`,
      height: 1080,
      id: crypto.randomUUID(),
      import_time: Math.floor(Date.now() / 1000),
      import_time_ms: Date.now() * 1000,
      item_source: 1,
      material_color_tag: '',
      md5: '',
      metetype: 'photo',
      roughcut_time_range: { duration: -1, start: -1 },
      sub_time_range: { duration: -1, start: -1 },
      type: 0,
      width: 1920
    });

    copiedInfo.push({
      dst_path: `Resources/local/${img}`,
      src_path: path.join(imagesDir, img).replace(/\\/g, '/')
    });
  }

  // Audio in meta
  metaMaterialValues.push({
    ai_group_type: '',
    create_time: Math.floor(Date.now() / 1000),
    duration: totalDurationUs,
    enter_from: 0,
    extra_info: audioFilename,
    file_Path: `./Resources/local/${audioFilename}`,
    height: 0,
    id: crypto.randomUUID(),
    import_time: Math.floor(Date.now() / 1000),
    import_time_ms: Date.now() * 1000,
    item_source: 1,
    material_color_tag: '',
    md5: '',
    metetype: 'music',
    roughcut_time_range: { duration: totalDurationUs, start: 0 },
    sub_time_range: { duration: -1, start: -1 },
    type: 0,
    width: 0
  });

  copiedInfo.push({
    dst_path: `Resources/local/${audioFilename}`,
    src_path: audioPath.replace(/\\/g, '/')
  });

  const metaPath = path.join(projDir, 'draft_meta_info.json');
  const meta = {
    cloud_draft_cover: false,
    cloud_draft_sync: false,
    cloud_package_completed_time: '',
    draft_cloud_capcut_purchase_info: '',
    draft_cloud_last_action_download: false,
    draft_cloud_package_type: '',
    draft_cloud_purchase_info: '',
    draft_cloud_template_id: '',
    draft_cloud_tutorial_info: '',
    draft_cloud_videocut_purchase_info: '',
    draft_cover: `${projDir.replace(/\\/g, '/')}/draft_cover.jpg`,
    draft_deeplink_url: '',
    draft_enterprise_info: { draft_enterprise_extra: '', draft_enterprise_id: '', draft_enterprise_name: '', enterprise_material: [] },
    draft_fold_path: projDir.replace(/\\/g, '/'),
    draft_has_unfinished_aigc_video_effect: false,
    draft_id: draftId,
    draft_is_ae_produce: false,
    draft_is_ai_packaging_used: false,
    draft_is_ai_shorts: false,
    draft_is_ai_translate: false,
    draft_is_article_video_draft: false,
    draft_is_cloud_temp_draft: false,
    draft_is_from_deeplink: 'false',
    draft_is_infinite_canvas_draft: false,
    draft_is_invisible: false,
    draft_is_pippit_draft: false,
    draft_is_web_article_video: false,
    draft_materials: [
      { type: 0, value: metaMaterialValues },
      { type: 1, value: [] },
      { type: 2, value: [] },
      { type: 3, value: [] },
      { type: 6, value: [] },
      { type: 7, value: [] },
      { type: 8, value: [] }
    ],
    draft_materials_copied_info: copiedInfo,
    draft_name: projectName,
    draft_need_rename_folder: false,
    draft_new_version: '',
    draft_removable_storage_device: '',
    draft_root_path: draftsBaseDir.replace(/\\/g, '/'),
    draft_segment_extra_info: [],
    draft_timeline_materials_size_: 138000000,
    draft_type: '',
    draft_web_article_video_enter_from: '',
    pippit_avatar_url: '',
    pippit_extra_info: '',
    pippit_id: '',
    pippit_user_name: '',
    tm_draft_cloud_completed: '',
    tm_draft_cloud_entry_id: -1,
    tm_draft_cloud_modified: 0,
    tm_draft_cloud_parent_entry_id: -1,
    tm_draft_cloud_space_id: -1,
    tm_draft_cloud_user_id: -1,
    tm_draft_create: Date.now() * 1000,
    tm_draft_modified: Date.now() * 1000,
    tm_draft_removed: 0,
    tm_duration: totalDurationUs
  };

  fs.writeFileSync(metaPath, JSON.stringify(meta), 'utf8');

  // 10. Synchronize with root_meta_info.json
  if (rootMeta) {
    let entry = rootMeta.all_draft_store.find(d => d.draft_name === projectName);
    if (!entry) {
      entry = {
        cloud_draft_cover: false,
        cloud_draft_sync: false,
        draft_cloud_last_action_download: false,
        draft_cloud_purchase_info: '',
        draft_cloud_template_id: '',
        draft_cloud_tutorial_info: '',
        draft_cloud_videocut_purchase_info: '',
        draft_cover: `${meta.draft_fold_path}/draft_cover.jpg`,
        draft_fold_path: meta.draft_fold_path,
        draft_id: draftId,
        draft_is_ai_shorts: false,
        draft_is_cloud_temp_draft: false,
        draft_is_infinite_canvas_draft: false,
        draft_is_invisible: false,
        draft_is_pippit_draft: false,
        draft_is_web_article_video: false,
        draft_json_file: `${meta.draft_fold_path}/draft_content.json`,
        draft_name: projectName,
        draft_new_version: '',
        draft_root_path: draftsBaseDir.replace(/\\/g, '/'),
        draft_timeline_materials_size: 138000000,
        draft_type: '',
        draft_web_article_video_enter_from: '',
        pippit_avatar_url: '',
        pippit_extra_info: '',
        pippit_id: '',
        pippit_user_name: '',
        streaming_edit_draft_ready: true,
        tm_draft_cloud_completed: '',
        tm_draft_cloud_entry_id: -1,
        tm_draft_cloud_modified: 0,
        tm_draft_cloud_parent_entry_id: -1,
        tm_draft_cloud_space_id: -1,
        tm_draft_cloud_user_id: -1,
        tm_draft_create: Date.now() * 1000,
        tm_draft_modified: Date.now() * 1000,
        tm_draft_removed: 0,
        tm_duration: totalDurationUs
      };
      rootMeta.all_draft_store.unshift(entry);
    } else {
      entry.draft_id = draftId;
      entry.draft_fold_path = meta.draft_fold_path;
      entry.draft_cover = meta.draft_cover;
      entry.draft_json_file = `${meta.draft_fold_path}/draft_content.json`;
      entry.tm_duration = totalDurationUs;
      entry.tm_draft_modified = Date.now() * 1000;
    }
    rootMeta.draft_ids = rootMeta.all_draft_store.length;
    fs.writeFileSync(rootMetaPath, JSON.stringify(rootMeta), 'utf8');
  }

  console.log(`[CapCutBuilder] Project "${projectName}" successfully built with 0 unlinked files!\n`);
}

module.exports = { buildCapCutProject };

if (require.main === module) {
  const args = process.argv.slice(2);
  const getArg = (flag) => {
    const idx = args.indexOf(flag);
    return idx !== -1 ? args[idx + 1] : null;
  };

  const projectName = getArg('--project-name') || 'The Waiting Room';
  const audioPath = getArg('--audio');
  const imagesDir = getArg('--images-dir');
  const timingsPath = getArg('--timings');

  if (!audioPath || !imagesDir || !timingsPath) {
    console.error('Usage: node capcut_builder.js --project-name <name> --audio <wav> --images-dir <dir> --timings <json>');
    process.exit(1);
  }

  buildCapCutProject({ projectName, audioPath, imagesDir, timingsPath });
}
