# H3 Continuum — illustrated user guide

[Back to the quick start](../README.md) · [V3.9 References](V39_REFERENCE_INLINE.md) · [History](README_HISTORY.md)

This guide preserves the detailed operating instructions and screenshots from
the README at source commit `894869d9` (package 3.9.8).
V3.8-labeled controls and screenshots describe the retained V3.8X2 workflow;
the V3.9 setup and Reference sections identify the separate current workflow.
Earlier dated fixes, version statements and measurements are historical evidence,
not a new acceptance claim. Use the [current README](../README.md) and the
[v3.9.8 compatibility profile](KJ_PREVIEW_OVERRIDE_V398.md) for current scope.

- [V3.9 template setup](#start-here-v39-and-the-retained-v38x2-workflow)
- [Reference Images](#v39-reference-images)
- [Complete V3.8 control reference](#complete-v38-ui-reference)
- [Review, retry, Takes and extension](#review-continue-and-revise-a-chunked-video)

<!-- Preserved README sections begin. -->

## Start here: V3.9 and the retained V3.8X2 workflow

The ComfyUI **Templates → ComfyUI-H3-Continuum** gallery offers two separate entries: the user-selected [V3.9 workflow](../examples/workflows/MiniMax_H3_Continuum_V39.json) and [V3.8X2 workflow](../examples/workflows/MiniMax_H3_Continuum_V38X2.json). The [V3.8X2 workflow ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip) contains **both unchanged JSON workflows** for one-download setup; the [V3.9 ZIP](../examples/workflows/MiniMax_H3_Continuum_V39.zip) contains only V3.9. These are workflow archives, not custom-node installers. The V3.8 Sampler remains available, so existing V3.8X2 workflows still load. V3.9 does not automatically convert their Reference connections or saved Runs/Takes: preserve the old workflow and open the dedicated V3.9 graph for new work.

The selected V3.9 template has 32 nodes. Image loaders 1–6 are wired to the new helper and bypassed by default; slots 7–9 remain available but require the user to add and connect their own image loaders. Choose actual files and enable only the desired images. The saved size controls are **First Image + Draft — 0.30 MP**, and the separate First Image loader is enabled; select your own First Image file before Queue. The saved 480×640 Width/Height values apply only in Manual mode. `Reference Image Size` is `Match Output`; it resizes conditioning after source-image load, not the source files themselves. For a clear per-chunk Reference test, turn First Image and Last Image off, switch to Manual, and use Reference Images alone. First/Last additionally constrain the video; Last Image may merge the final two logical chunks into one physical group, which requires the same effective Reference set in both. A subject may remain visible in later chunks through video continuity even after its Reference is no longer assigned.

In the helper, `All chunks` uses connected images throughout; `Per chunk` provides an image-by-chunk table. The template starts in `Per chunk` with all assignments off: after enabling a loader, tick the chunks that should use it. Slot numbers never shift: Image 1 is `@R1` and Image 9 is `@R9`, even when intervening slots are empty. In Sequence Prompt, describe the action for each chunk and use `@R` tags only for active References; their actual `<Picture N>` numbers are resolved per group. Unused tags warn without stopping generation. Start with short chunks and pre-resized images: source images may consume RAM before the Sampler's Reference Image Size setting applies.

V3.9.3 is the current source version on `main`. Download versioned source from [GitHub Releases](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases); ComfyUI Registry publication is separate. Historical Releases and tags remain available. Configured 1024×1024 Reference-only GPU/API runs succeeded, but the unchanged default template and browser save/reload remain separate acceptance gates. For a reproducible older environment, use the matching historical Release/tag and workflow; the retained V3.8 Sampler on current `main` specifically supports V3.8X2 workflows.

`pyproject.toml` declares ComfyUI `>=0.32.0`; earlier real-generation/GPU validation used ComfyUI `0.34.2`, and the scoped Fixed cache comparison above used `0.38.0`. The minimum declaration does not establish V3.9 runtime acceptance on 0.32.0. The previous Windows CPU run is `1696 passed / 1 skipped / 0 failed`; the earlier separate Linux rerun report records `1534 passed / 3 skipped / 0 failed` and does not include the new cache or external INT tests. Neither replaces browser save/reload or GPU acceptance for the unchanged official template.

## V3.9 Reference Images

### Reference Images node: choose the image for each chunk

![H3 Continuum Reference Images V3.9 node with fixed image slots and a per-chunk assignment table](images/v39/v39-reference-images-node.png)

*Example UI, not the downloadable workflow's default assignments.* Image 1–9 are fixed slots: Image 1 is always `@R1`, even when other slots are empty. With `Reference Use = Per chunk`, tick the image/chunk intersections you want; each row's `All` / `Off` buttons select or clear that image across chunks. In this screenshot, Image 1 is assigned to Chunks 1 and 2, while other images have different assignments. The official V3.9 workflow starts with its image loaders bypassed and every assignment unchecked; choose real image files, enable their loaders, then tick the intended chunks.

### Sampler V3.9: connect the helper once

![H3 Continuum Sampler V3.9 with one Reference Images Optional input](images/v39/v39-sampler-node.png)

Connect the helper's green `reference_images` output to the Sampler's single `Reference Images (Optional)` input. The V3.8X2 workflow uses its own V3.8 Sampler and older Reference sockets; opening it does not convert those connections to V3.9. This screenshot shows a **Manual 480×640 example**, not the official V3.9 workflow's saved **First Image + Draft 0.30 MP** setting. `Reference Image Size = Match Output` controls Reference conditioning size after image loading; it does not pre-resize source files or set output resolution.

V3.9 now connects all nine fixed Reference Images through one **H3 Continuum Reference Images V3.9** node. Its in-node table selects All chunks or specific chunks. The V3.9 Sampler has one typed Reference Images connection and keeps Sequence Prompt, First/Last, Review and the rest of its generation controls. Use `@R1` for Image 1; the backend converts active tags to the group's actual `<Picture N>`. Both modes use the same group-routing engine.

Prompt parsing never blocks generation. If an explicit Timeline cannot be parsed, the original text falls back to Fixed with diagnostic `H3C-P100`. An uncovered Timeline chunk reuses the previous prompt and reports `H3C-P101`. Select the image for each chunk in the Reference Images node; `@R1`–`@R9` in Sequence Prompt refer to those fixed image numbers.

For the supplied `2 × 10 s` workflow, put each time header on its own line and describe only that chunk's action. For example, after enabling the matching image loaders and checking their chunk assignments:

```text
[0-10s]
@R1 walks forward through a quiet hallway. The camera follows smoothly.

[10-20s]
@R2 enters from the right. The camera turns to follow @R2.
```

Use the actual subjects and actions from your images; this is a syntax example, not a saved prompt in the downloadable workflow. Do not place prompt text on the same line as `[0-10s]`: that is not a Timeline header. A Reference can still influence a chunk without an explicit `@R` mention when its checkbox is enabled.

The [official V3.9 workflow](../examples/workflows/MiniMax_H3_Continuum_V39.json) is the latest user-supplied JSON, copied without editing; its [single-workflow ZIP](../examples/workflows/MiniMax_H3_Continuum_V39.zip) is also available. It preserves the full V38X2 model/LoRA, Decode Cache, Finalize and Save chain. Six image loaders are prewired (initially bypassed); to use Image 7–9, add `H3 Continuum Load Image` nodes and connect them to the matching helper slots. The Sequence Prompt input remains connected but is intentionally blank: write your own prompt before Queue. The saved graph uses `Timeline`, two 10-second chunks, `Full Run` (displayed as Generate Full Video), First Image + Draft 0.30 MP size selection, and a separate Project ID. The earlier [Reference Inline migration fixture](../examples/workflows/MiniMax_H3_Continuum_V39_Reference_Inline.json) remains available unchanged. See the [step-by-step Reference Images guide](V39_REFERENCE_INLINE.md). Replace local media and model filenames as needed before Queue; enabling an image requires choosing a real file. Seven to nine active references can be particularly memory-intensive: start with fewer, smaller source images. A full ComfyUI backend restart and browser hard-refresh are required before the new node definitions appear. Browser save/reload and GPU acceptance of this unchanged default graph are still pending; a GitHub Release does not imply these gates or a Registry package have been completed.

**Compatibility:** Existing V3.8X2 workflows still use the V3.8 Sampler and old Reference Images 4–9 helper. V3.9 needs its new helper and connection. Open the new V3.9 workflow instead of only changing the Sampler type in an old graph: older V3.9 prototype workflows with direct 1–3 connections and Sampler-side routing widgets need manual rewiring, and their saved widget positions may differ. Accepted V3.8 Runs/Takes are not automatically migrated. Keep a copy of the previous workflow and use a new Run Name for V3.9.

Earlier browser checks covered the previous V3.9 controls. The new helper has GPU/API execution evidence; its browser save/reload and the unchanged default template's full acceptance are still open. CPU/JS and manifest results are separate; no V3.9 Release/Registry publication is implied.

**Version boundary:** V3.8X2 package 3.8.3 and V3.9.0 are separate workflows. This update does not create a V3.8X2 or V3.9 GitHub Release, tag, maintenance branch, or Registry version; it does not remove any older Release. The existing [`v3.8.0` tag](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/tree/v3.8.0) remains the reproducible V3.8.0 baseline.

## Loader persistence repair on main (2026-09-21, after 3.8.3)

The current paired V3.8X2 workflows now use **Core Load Audio** and **Core Load Video -> H3 Continuum Video Adapter**. The adapter has Force Rate (default 24) and IMAGE/AUDIO outputs, but **no Enable switch or file selector**. Core owns video selection/upload/save; the established duration-preserving frame selection is reused and audio is passed unchanged. To disable Video Guide, bypass the adapter or the whole video-input group; do not bypass only Load Video while leaving its required-input adapter active.

**H3 Continuum Load Image remains**, including Enable Image. Its mode observer now delegates to inherited Core setters (Issue #23), and no longer replaces the widget collection while drawing or saving. Enable is appended after Core's widgets; Core handles the filename and native Bypass persistence. The older Audio/Video node IDs remain loadable as deprecated compatibility nodes, not as the recommended new-workflow loaders. The V3.8X2 baseline registered ten node IDs including these two legacy nodes; V3.9 adds the V3.9 Sampler and Reference Images helper as separate IDs, for twelve total. V3.8 Sampler inputs, generation parameters, Decode Cache, Finalize and existing latent/storage contracts are unchanged.

After updating, restart ComfyUI and reload/refresh the frontend. A workflow that already omitted its filename or saved an incorrect mode cannot recover those missing values: reselect the intended file and Bypass state, then save once. Existing user workflows and saved Takes are not automatically rewritten. Changing upstream node types can legitimately create a new Run Storage revision; preserve the original workflow when resuming accepted runs.

Validation details and limits: [Loader repair record](LOADER_PERSISTENCE_REPAIR.md). CPU/store-model regression tests are not a substitute for the pending Windows Core 0.36.0 / frontend 1.53.6 browser tab-switch acceptance. No Release/tag or Registry publication is implied by this main-branch repair. Older loader screenshots below describe the retained legacy nodes.


## Timeline Video — Experimental on main

The existing video IMAGE input is now displayed as **`Timeline Video Frames`** and has one appended optional control, **`Video Reference Mode`**. Existing workflows and API calls that do not contain the new setting keep the old behavior through the default **`Repeat Reference`** mode.

- **`Repeat Reference`** keeps the legacy Video Guide contract: each physical generation group receives the same bounded prefix from the source. It does not loop or stretch a short source.
- **`Follow Timeline`** uses the 24 fps source interval corresponding to each physical output group. Continuation-prefix frames are not consumed twice. If the source ends, the remaining groups continue without video reference; a final usable partial interval may receive only H3's short frame-grid padding.

This setting is independent of `Prompt Format = Timeline`. It does not add a new socket or loader, does not use the source video's audio automatically, and does not provide frame-perfect motion copying. The complete decoded IMAGE batch is still held in system memory, so this feature is not a long-input RAM optimization.

Use the existing connection:

```text
Core Load Video -> H3 Continuum Video Adapter -> Timeline Video Frames
```

The two comparison workflows are intentionally separate from the unchanged official V3.8X2 workflows:

- [Follow Timeline JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Follow.json) | [ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Follow.zip)
- [Repeat Reference JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Repeat.json) | [ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Repeat.zip)

Local acceptance passed with full CPU `1424 passed / 1 skipped / 0 failed`, browser save/reload, and Follow/Repeat `2 x 5 s` GPU runs at 704x416, 24 fps, 240 frames, and 10-second 32 kHz stereo audio. Follow changed to the later source interval for Chunk 2 while Repeat retained the shared prefix; both completed without OOM, NaN, allocation failure, or crash. Peak observed VRAM was about 15.6–15.7 GiB on the tested RTX 5060 Ti 16 GB system, so 16 GB headroom was small. This is a functional mode-separation result, not a universal speed or subjective-quality guarantee. See [Timeline Video Experimental](TIMELINE_VIDEO_EXPERIMENTAL.md).

> **V3.8X2** is the product and workflow label for package `3.8.3`. It keeps the V3.8 production sampler and adds optional Reference Images 4–9 plus the built-in Decode Cache Helper. The older V3.8.0 package remains available from tag [`v3.8.0`](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/tree/v3.8.0).
 <img width="1536" height="1024" alt="exec-9cfa73b4-c1d3-4416-8950-fa661b946638_2" src="https://github.com/user-attachments/assets/8df15764-6db6-4d4c-9eb5-0d2c7b0668f0" />


## Official V3.8X2 workflows

- **Standard name:** [JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2.json) | [ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip)
- **Helper-explicit name:** [JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.json) | [ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.zip)

The two V3.8X2 JSON names contain the **same official graph**; they are distribution aliases, not different configurations. Both include the built-in Decode Cache Helper with its saved `Auto / RAM 256MB / Disk 8GB / reset_token 0` settings and the nine-reference helper connection. The standard V3.8X2 ZIP now also contains the separate V3.9 JSON, while the helper-explicit ZIP contains only its correspondingly named V3.8X2 JSON. Older V3.8X workflows remain available for existing projects.

## Nine Reference Images: memory warning

Reference Images 1–3 connect directly to the Sampler. Optional images 4–9 connect through `H3 Continuum Reference Images` and then to `Reference Images (Optional)`. Using all nine is a high-resource configuration, not the normal minimum requirement.

The acceptance run completed on an **RTX 5060 Ti 16 GB / 64 GB system** only after the nine source references were kept near **0.30 MP each**. With `512 × 608` output, `3 × 5 seconds`, Spectrum Off, LoRA Off, Sage Attention, and Balanced 22-frame continuity, Sampling used about **15.0–15.5 GiB of 16,311 MiB VRAM**. There was little 16 GB headroom.

When using many references, especially all nine, resize copies of the source images to about 0.30 MP before loading or connecting them. The Sampler still performs its normal conditioning resize, but smaller source files reduce input and preprocessing pressure. Larger references, larger output sizes, extra wrappers, or concurrent GPU work may require a higher-spec GPU and more system RAM. Nine references are optional and are not guaranteed to improve quality over three.

## Built-in Decode Cache Helper

### Important: this is not an unconditional new-generation speedup

**Manual cache clear:** normally no action is needed. Press the Helper's "キャッシュをクリア" (Clear cache) button to discard that Helper's cache on the next Queue and run native Decode again. It does not delete immediately or queue automatically. The internal `reset_token` remains serialized for workflow/API compatibility and increments once per click (wrapping to 0 at the INT limit). Creating, loading, or cloning a node does not change it. Without JavaScript, or in API workflows, change `reset_token` through the traditional numeric input.

**The Helper saves time only when unchanged latents are decoded again. It does not accelerate Sampling.** A first MISS runs native Decode and stores the result; hashing and storage can make that run slower. Generating different latents with a new random seed each time normally produces MISS, so this feature should not be expected to speed up that usage.

Concrete reuse scenarios:

- **Continue by adding chunks:** when existing chunk latents are retained and decoded again for output, cached existing chunks can HIT; newly generated chunks initially MISS.
- **Fix / partial regeneration:** unchanged chunk latents can HIT when submitted again; regenerated chunks whose latent contents changed MISS.
- **Complete / Resume output:** decoding retained latents again without resampling can benefit. Merely playing an existing video file is not a cache use case.
- **Retry from Decode onward, or change Finalize/output settings:** reuse applies when the same latents and decode-related metadata reach the Helper and Decode runs again.
- **Regenerate with a fixed seed:** reuse requires identical resulting latent contents. The same seed alone does not guarantee HIT.

The action names themselves do not enable reuse. **Each Video/Audio entry must match in latent contents, shape, dtype, decode-related metadata, and VAE identity, and its cache entry must still exist in that Helper.** If ComfyUI reuses an existing output without executing Decode, there is no additional Decode saving attributable to this Helper. Connect the Helper and select `Auto` or `RAM`. In its report, `hit` means reuse, `miss` means native Decode, and `off` / `bypass` mean no cache reuse.

Cache reuse is process-local and does not survive Python restarts. Eviction and VAE identity changes can also cause MISS. Changing mode, RAM/Disk budgets, or `reset_token` clears this implementation's Helper cache. Keeping `reset_token = 0` does not reset it on every Queue.

V3.8X2 ships `H3DecodeCacheHelper` inside this Continuum package. It remains a separate public node under `MiniMax H3/Continuum/Helpers`; no second custom-node addon is needed. The original nine IDs remain registered for compatibility; the loader migration adds H3ContinuumVideoAdapter. Sampler, Finalize, Assembly Plan, Core Decode, and saved Sampler widget/socket contracts are unchanged.

Connect Sampler `video_latents` and `audio_latents` plus their native Video/Audio VAE inputs to the Helper, then connect Helper `images` and `audio` to Finalize. Keep the Sampler `assembly_plan` directly connected to Finalize. The [official V3.8X2 workflow](../examples/workflows/MiniMax_H3_Continuum_V38X2.json) preserves its saved graph and settings. It contains no Core VAE Decode nodes, so returning to Core direct Decode requires adding those two Core nodes and reconnecting Finalize, or loading a prior Core-direct V3.8X workflow. Do not simply remove the Helper and expect automatic rewiring.

`Auto` caches full physical Video decodes on private process-local disk and small Audio decodes in bounded RAM. `Off` delegates native Decode and clears the Helper cache. Cache failure falls back to native Decode; native Decode, OOM and queue interruption are not retried. Files are not reused across Python restarts. Keep only one provider of the `H3DecodeCacheHelper` node ID: the previous standalone addon must be disabled or removed during the migration, after a verified built-in installation.

At 736×416 (0.306MP), 3×5 seconds, Euler/simple 6 steps, Turbo FL2V v1.2, a warm backend and three Video HITs, one measured configuration produced a **mechanistic estimate of about 47 seconds / 24.5% less Full Run Total**. One direct A/B pair observed 50.887 seconds / 26.46%, and two Complete/Resume re-decode pairs averaged 46.309 seconds / 79.826% less Total. These are narrow observations, not repeated universal averages or an unconditional 20%+ speed promise. The first MISS can be slower, new Sampling is not accelerated, and a changed latent or VAE identity produces a MISS.

**Historical V3.8X workflow: [JSON](../examples/workflows/MiniMax_H3_Continuum_V38x.json) | [ZIP](../examples/workflows/MiniMax_H3_Continuum_V38x.zip)** — [Published releases](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases)

✅ V3.8X on `main` includes the September 8, 2026 Review hotfix: Review Each Chunk continuation, stale `Regenerate From` state, completed-sequence extension, and Render History queue handling are repaired. Update with `git pull --ff-only origin main` (or ComfyUI Manager **Update**), restart ComfyUI, and hard-refresh the browser if the old UI remains. Existing saved Takes are preserved. Issue #13 remains a separate open long-continuation quality issue and is not part of this hotfix.


H3 Continuum is a Production Sampler for generating, reviewing, partially regenerating, and resuming long-form MiniMax H3 video without restarting the entire work. V3.8 has two product layers: **Main / Production** and **Advanced**.

## Install or update first

For a new Git installation:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum.git
```

For an existing Git checkout:

```bash
cd ComfyUI/custom_nodes/ComfyUI-H3-Continuum
git pull --ff-only origin main
```

Restart ComfyUI after cloning or pulling. If ComfyUI Manager installed the node, use its **Update** action instead of mixing Manager updates with a second Git checkout.

To install the historical V3.8.0 package into a separate checkout instead:

```bash
cd ComfyUI/custom_nodes
git clone --branch v3.8.0 --single-branch https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum.git ComfyUI-H3-Continuum-v3.8.0
```

Use only one Continuum checkout at a time. ComfyUI Manager **Update** tracks `main`; it does not select historical tags.

Download the current V3.8X2 workflow: [JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2.json) or [combined V3.8X2/V3.9 ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip). The V3.8X2 JSON is one Spectrum-capable graph, also usable with [LightX2V Turbo](https://github.com/ModelTC/Minimax-H3-Turbo); both Spectrum and all Turbo LoRA entries are saved disabled. Install its external Spectrum, rgthree, and KJNodes nodes before opening it. ComfyUI-Easy-Use is not required. See [Spectrum and Turbo setup](#turbo-lora-and-spectrum-in-supplied-workflows) below.

## Prompt and skill downloads

- [V3.9 Reference Images prompt skill](../write-h3-v39-reference-prompts/SKILL.md) | [ZIP](../write-h3-v39-reference-prompts.zip) — for fixed `@R1`–`@R9` image slots and per-chunk assignments. Use it with the V3.9 Reference Images node; it is separate from the general Continuum prompt skill below.
- [LLM system prompt ZIP](../H3-Continuum-LLM-System-Prompt-v1.zip) — system instructions and reference material for Continuum prompt authoring.
- [Continuum prompt skill ZIP](../H3-Continuum-Skill-v1.zip) — general chunk-aware prompt authoring for Codex and other compatible agents.
- [Continuum Dance Director skill ZIP](../minimax-h3-continuum-dance-director.zip) — long-form choreography prompts for one primary dancer, with body and camera continuity across chunks.

These are optional prompt-authoring resources, not ComfyUI custom nodes. Extract each ZIP and follow its included instructions. They do not change the sampler or guarantee generated motion or image quality.

## You can ask an AI to read this manual

This README is intentionally detailed. You do not have to memorize it. Give its GitHub URL or this file to a web-enabled AI, describe your target video, GPU/VRAM, available First Image/audio, and whether you want to review every chunk. Ask it to use the **exact V3.8 labels** below.

Example request:

```text
Read the current ComfyUI-H3-Continuum V3.8 README. I have a 16 GB GPU and want
to create a 30-second I2VA video, reviewing every chunk. Tell me exactly which
Continuum inputs and controls to use, what must stay fixed between Queue runs,
and what output length I should expect after each action. Do not use older V3.7 UI.
```

AI products, plans, and repository-reading behavior change frequently. If a URL is not read correctly, paste or upload this README instead. Do not send private workflows, local paths, tokens, or credentials to a public AI service. The README and the UI remain the source of truth; an AI summary can still be wrong.

## V3.8 supported surface

The V3.8X2 baseline registers ten node IDs, including two deprecated loader compatibility IDs; V3.9 adds a separate Sampler and Reference Images helper. Current official workflows use Core Load Audio and Core Load Video plus the Video Adapter.

- **H3 Continuum Sampler V3.8** — the Main sampler
- **H3 Continuum Finalize** — decoded Video/Audio assembly with optional seam handling
- **H3 Continuum Load Image**
- **H3 Continuum Load Audio** (legacy compatibility; new workflows use Core Load Audio)
- **H3 Continuum Load Video** (legacy compatibility; new workflows use Core Load Video + Video Adapter)
- **H3 Continuum Video Adapter** — Core VIDEO to H3 IMAGE/AUDIO, default 24fps, no Enable
- **H3 Continuum Second Pass** — the Advanced bridge for external latent processing or upscaling
- **H3 Continuum Reference Audios** — an ordered Reference Audio 1/2/3 bundle helper
- **H3 Continuum Reference Images** — optional additional Reference Images 4–9
- **Decode Cache Helper** — the existing optional decoded-result cache

The current frontend uses `Show Advanced Settings` / `Hide Advanced Settings` to change presentation without changing generation values. Saved drafts that still contain the former frontend-only `H3 Continuum View` property are migrated to the matching collapsed/expanded view and the legacy property is removed. If the frontend extension is unavailable, the complete Python-defined interface remains visible and executable.

The official V3.8X2 workflow uses the Helper path:

```text
H3 Continuum Sampler V3.8
  -> Decode Cache Helper
  -> H3 Continuum Finalize
  -> Create Video
  -> Save Video
```

The Helper delegates cache MISS entries to native Core Video/Audio Decode. A manually wired direct Core Decode path remains supported, but it has no decoded-result cache. Save and upscaling remain external. Hi-Res Fix is not part of the V3.8X2 standard workflow; use Second Pass as the bridge when an external latent processor or upscaler is needed. External processors may change only Video LATENT spatial geometry while preserving physical groups, B/C/T, finite values, first-pass Audio, and the original Assembly Plan. Finalize accepts public `IMAGE`/`AUDIO` outputs and does not require a specific decoder class. SageAttention, Sol-Attn, and Spectrum remain external MODEL wrappers. See the [V3.8 Open Integration Contract](V38_OPEN_INTEGRATION_CONTRACT.md).

## Complete V3.8 UI reference

This section covers every user-facing control and socket on the seven public V3.8 nodes. Names such as `Power Lora Loader (rgthree)`, Spectrum, SageAttention, Core VAE Decode, and Core Save Video belong to ComfyUI or another extension. They may be used in a supplied workflow, but they are not Continuum controls.

### H3 Continuum Sampler V3.8: required graph inputs

| Input | What it does | Normal use |
|---|---|---|
| `model` | MiniMax H3 diffusion model, including any upstream MODEL wrappers or selected LoRA | Required |
| `clip` | MiniMax H3 text encoder | Required |
| `video_vae` | Encodes connected image conditioning; Continuum does not use it for final decoding | Required by the node; unused by pure T2VA |
| `sampler` | ComfyUI sampling algorithm | Required |
| `sigmas` | Noise schedule and effective step count | Required |
| `Sequence Prompt` | Complete text, list, timeline, or JSON sequence prompt | Required |

The Sampler returns six outputs: a list of `video_latents`, a list of `audio_latents`, one `assembly_plan`, a text `status`, the selected `driving_audio` when used, and a `refine_context` for the Advanced Second Pass. Raw latent lists normally go through Core Video/Audio Decode before Finalize.

### H3 Continuum Sampler V3.8: optional media inputs

| Input | Role | Important distinction |
|---|---|---|
| `first_frame` | First Image for I2VA or FL2VA | Can also supply the output aspect ratio when `Size Source = First Image` |
| `last_frame` | Optional final-image constraint for FL2VA | Can trigger a Long Terminal Merge; the final pair may become one atomic review unit |
| `reference_image_1`–`reference_image_3` | Ordered appearance, identity, subject, or scene references | They never become the implicit size source |
| `Reference Images (Optional)` | Additional images 4–9 bundled by `H3 Continuum Reference Images` | Empty inputs are skipped; encoding remains in the Sampler |
| `Video Guide Frames` | A video loader's IMAGE frame batch, applied as a persistent guide | It does not carry the source video's audio; frames are interpreted at 24 fps |
| `Driving Audio` + `Driving Audio VAE` | Original audio timeline used as native guide conditioning | The selected source audio becomes final audio; generated audio and Audio Seam are bypassed |
| `Reference Audio (Optional)` + `Reference Audio VAE (Optional)` | Legacy single conditioning-only audio reference | Generated audio remains final audio |
| `Audio References (Optional)` | Ordered bundle from `H3 Continuum Reference Audios` | Do not connect this together with the legacy single Reference Audio path |
| `Still Image Guide (Optional)` | Compatibility socket inherited from the V3.7 guide contract | Experimental; not part of the V3.8X2 official workflow |

#### First Image, Last Image, and Reference Images

![First Image enabled and Last Image bypassed](images/v38-manual/first-last-image-bypass.png)

- **First Image** establishes the opening image and is the normal visual starting point for I2VA/FL2VA. It is also the only media input that can drive `Size Source = First Image`.
- **Last Image** constrains the sequence ending. Leave it `OFF` for T2VA and ordinary I2VA. With a connected Last Image, extending or regenerating the sequence may rebuild the terminal pair.
- **Reference Images 1–9** guide identity or appearance throughout generation. Inputs 1–3 remain on the Sampler; optional inputs 4–9 are on `H3 Continuum Reference Images`, connected to the Sampler's `Reference Images (Optional)` socket. The helper only bundles images: resizing, hashing, and VAE encoding remain in the existing Sampler path. Empty slots are skipped; Picture numbers follow active slot order after any First/Last Image. Existing three-loader templates still work unchanged.

Saved workflows with the earlier direct image 4/5 inputs migrate those links into a bundle after graph loading. Migration preserves the original source links and only removes a legacy input after its new link is verified. If a source is unavailable or its destination is occupied, the legacy link is retained with a warning. Old API prompts remain accepted; supplying both legacy and bundle images for the same slot is an explicit input conflict.

![Three optional Reference Image loaders](images/v38-manual/reference-images-three-bypass.png)

Every `H3 Continuum Load Image` has `Enable Image`. `ON` loads through ComfyUI Core. `OFF` uses native node bypass and makes that optional path behave as unconnected without deleting the node or cable. First, Last, and up to nine Reference Image inputs can therefore be connected without forcing every input to be active. An empty image bundle returns no reference and does not change the zero-to-three-image sampling/reuse contract.

| Public loader | Controls | Outputs |
|---|---|---|
| `H3 Continuum Load Image` | `Enable Image`, `image` file | `IMAGE`, `MASK` |
| `H3 Continuum Load Audio` | `Enable Audio`, `audio` file | `AUDIO` |
| `H3 Continuum Load Video` | `Enable Video`, `Video` file, `Force Rate` | `images`, `audio` |

#### Video, audio, and their bypass switches

![Continuum Video and Audio loaders with Enable controls](images/v38-manual/input-video-audio-bypass.png)

- `H3 Continuum Load Video`: `Enable Video`, `Video`, and `Force Rate`. `Force Rate = 0` uses source FPS; a positive value drops/duplicates frames to that rate while preserving nominal duration and audio. Connect `images` to `Video Guide Frames` when visual video guidance is wanted. Connect `audio` to `Driving Audio` only when the source audio should guide and become the final output.
- `H3 Continuum Load Audio`: `Enable Audio` and the audio file. Use it for Driving Audio or Reference Audio according to the socket you connect.
- The node titled `Audio Switch` in the example image is ComfyUI Core's `If/Else Switch` (`ComfySwitchNode`); `Fast Groups Bypasser (rgthree)` belongs to the rgthree extension. Neither is a Continuum node or a requirement of Continuum. The Continuum loaders already provide their own native ON/OFF controls.

`Audio Continuity` is different from both audio inputs: it passes the previously generated audio context into the next generated chunk. It does not import a source track. Driving Audio replaces final generated audio; Reference Audio only conditions generation.

### Main Sampler controls

| Displayed control | Meaning | Recommended starting point |
|---|---|---|
| `Prompt Format` | `Auto`, `Fixed`, `List`, or `Timeline` interpretation of `Sequence Prompt` | `Auto` unless you need to force one parser |
| `Continuity` | Prior Video context retained at each chunk boundary | `Balanced — 22 frames` for Standard audiovisual continuation |
| `Base Seed` | Base for deterministic per-chunk seed derivation | Keep the value unchanged when continuing, comparing, or selecting Takes |
| `Control After Generate` | What ComfyUI does to `Base Seed` after a Queue | `fixed` for `Review Each Chunk`, resume, and controlled comparisons |
| `Audio Continuity` | Carries generated-audio context across boundaries | `true` for normal audiovisual generation |
| `Chunks` | Planned total chunk count, from 1 to 16 | Enter the final total, not the number to add next |
| `Seconds per Chunk` | Duration shared by every chunk | 5–15 seconds is the validated range; see duration notes below |
| `Total Length` | Read-only `Chunks × Seconds per Chunk` | Check only; it never edits either input |
| `Size Source` | `First Image` or `Manual` output geometry | First Image for I2VA/FL2VA; Manual for T2VA or exact dimensions |
| `Resolution` | First-Image sizing preset | `Draft — 0.30 MP` for tests, `Balanced — 0.60 MP` for more detail, or `Native 768` for the H3-native short edge |
| `Custom MP` | Custom First-Image pixel budget | Visible only when `Resolution = Custom` |
| `Width` / `Height` | Exact output canvas in 32-pixel steps | Visible/editable only in Manual mode; 32–16384 is accepted |
| `Run` | `Generate Full Video` or `Review Each Chunk` | Use Review when you want a human decision after each physical group |
| `Progress` | Saved raw chunks, safe resume, and Take history | Review turns it On automatically; enable it for resume/regeneration |
| `Ready to Queue` | Plain-language summary of the next Queue | Read it before pressing ComfyUI's top-right blue `Run` button |
| `Show Advanced Settings` / `Hide Advanced Settings` | Shows or hides technical controls | Visibility only; it does not change their values |

`Continuity = Balanced — 22 frames` with `Continuation Backend = Standard` and `Audio Continuity = true` uses the current Masked AV route. `Fast — 5 frames`, `Strong — 39 frames (Experimental)`, and `Auto — conservative` safely resolve to the older Reference Context route while generated-audio continuity is on. With Audio Continuity off, Standard uses the Video-only masked route.

#### Choose First Image sizing or Manual sizing

![First Image sizing with Draft 0.30 MP](images/v38-manual/sampler-size-first-image-draft.png)

`Size Source = First Image` preserves the connected First Image aspect ratio. `Resolution` then chooses its pixel area:

| Preset | Target |
|---|---|
| `Draft — 0.30 MP` | Fastest and lowest-memory First Image starting point |
| `Balanced — 0.60 MP` | More detail with greater memory and processing cost |
| `Native 768` | 768 px short-edge target with a 1344 px long-edge cap |
| `Custom` | `Custom MP` selected by the user; separate from the Native 768 cap |

![Size Source First Image tooltip](images/v38-manual/size-source-first-image-tooltip.png)

`Size Source = Manual` ignores the preset and uses exact Width/Height values. Both must be multiples of 32. Manual is the normal choice for T2VA and also supports a 32×32 diagnostic canvas when only generated audio is being checked.

![Manual Size Source with explicit Width and Height](images/v38-manual/size-source-manual-640.png)

If First Image mode is selected but no usable First Image reaches the Sampler, V3.8 uses the stored Manual Width/Height as a safe fallback and reports the dimensions in `status`. Select `Size Source = Manual` to inspect or edit those values; Width/Height are hidden in the First Image facade. Reference Images and Video Guide never become implicit size sources. The historical `Auto / Landscape / Portrait / Square` values are migration/API compatibility values, not current Main choices.

Size selection is built into the V3.8 Sampler. A separate megapixel, empty-latent, or image-size node is not required for the normal Continuum workflow.

#### Choose a chunk duration

- **5 seconds** is a valid H3 duration and the fastest practical choice for workflow checks, Review UI checks, and quick Takes.
- **8–10 seconds** usually reduces the number of handoffs while keeping each Queue easier to review and rerun.
- **15 seconds** is the [upstream MiniMax H3 native maximum per generation](https://github.com/MiniMax-AI/cli/blob/main/skill/h3-video/SKILL.md) and minimizes the number of boundaries, but it increases per-chunk time and memory. Longer is not automatically higher quality.
- Continuum accepts 4–30 seconds for compatibility and experimentation. Values above 15 seconds are not the same as an upstream native-duration recommendation and can be expensive at high resolution.

For an audio-only listening diagnostic, use T2VA, `Size Source = Manual`, and a very small canvas such as 32×32, then play the saved video and ignore its picture. This is useful for hearing music or boundary continuity; it is not evidence of normal-resolution video quality.

### Advanced Sampler controls

| Control | When it appears | Meaning |
|---|---|---|
| `Continuation Backend` | Advanced open | `Standard` is the V3.8 path; `Compatibility` restores the older Reference Context route for comparison |
| `Regenerate From` | Advanced open and Progress On | `Auto` resumes the longest compatible prefix; `Chunk N` reuses earlier chunks and rebuilds N through the target |
| `Variation Nonce` | Explicit `Regenerate From = Chunk N` | `0`: automatic variation selection with interrupted-run resume; `1` or higher: a fixed variation value. Base Seed and the other generation settings stay unchanged |
| `Run Name (Optional Override)` | Advanced open and Progress On | Stable name for resume and Render History; blank uses the Sampler's automatic identity |
| `Reference Image Size` | Advanced open and a Reference Image connected | `Match Output` is practical; `Max Identity` preserves more reference detail and may use more memory |
| `Video Guide Size` | Advanced open and Video Guide connected | `Efficient — 0.4 MP`, `Balanced — 0.6 MP`, or `Match Output` |

Frontend-managed IDs, selected Take IDs, one-shot review actions, diagnostics, preview, and legacy compatibility values are deliberately not editable as ordinary node widgets. The corresponding settings or action buttons below are the supported interface.

### Review-state controls

When `Run = Review Each Chunk`, `Progress` is On, and a review unit is ready, the settings view changes to this action view:

| Button | What the next top-right ComfyUI `Run` does |
|---|---|
| `Use it and continue` | Accepts the current result, reuses it, and generates one next physical group |
| `Try this chunk again` | Keeps the earlier accepted prefix and creates another Take of the current review unit |
| `Start again from Chunk 1` | Selects a fresh branch from Chunk 1 with current settings and automatic variation; press Queue afterward. Saved Takes are kept. The selection resets to Auto after Queue |
| `Use it and finish the rest` | Accepts the current result and generates every remaining group without further review pauses |
| `Back to Settings` | Shows the normal settings; does not queue, reset, or discard the review |
| `Return to Review` | Returns from settings to the pending review; does not undo edited values |
| `Render History — N Takes` | Opens or closes stored Take browsing; N is Take count, not chunk count |
| `Previous Take` / `Next Take` | Changes the selected stored Take only |
| `Use This Take` | Makes the selected Take canonical on the next Queue; no new sampling is required |
| `Continue From Here` | Branches from the selected Take and generates the next review unit |

The action button selects intent and gains a `✓`; it does not start generation. Press ComfyUI's top-right blue `Run` button afterward. Full step-by-step examples begin in [Review, continue, and revise a chunked video](#review-continue-and-revise-a-chunked-video).

### H3 Continuum Reference Audios

`H3 Continuum Reference Audios` bundles up to three standalone audio references behind one `Audio References (Optional)` Sampler socket. Connect the references without gaps and use `<Audio 1>`, `<Audio 2>`, and `<Audio 3>` in the same order in the prompt. One shared Core Audio VAE encodes each reference independently. This path never replaces generated final audio and does not change the separate Driving Audio contract. Existing workflows may keep using the legacy single `Reference Audio (Optional)` socket; do not connect the legacy and bundled paths together.

Its complete interface is `Reference Audio 1 (Optional)`, `Reference Audio 2 (Optional)`, `Reference Audio 3 (Optional)`, one shared `Reference Audio VAE`, and the `audio_references` output. Leave no gap in the connected order: do not connect Audio 1 and Audio 3 while leaving Audio 2 empty.

The small arrow/triangle seen beside `audio_references` is ComfyUI's connection direction/cable rendering, not an additional option. Place this helper to the left of the Sampler or use a reroute node if the cable crosses the node body.

### H3 Continuum Finalize

Finalize is normally left wired in the workflow rather than operated repeatedly. It assembles the decoded physical groups into the exact requested timeline. Required inputs are decoded `images`, decoded `audio`, and their matching `assembly_plan` (the Sampler's plan for First Pass, or Second Pass `updated_assembly_plan` after refinement); optional `driving_audio` preserves the selected source track.

| Control | Meaning | Normal choice |
|---|---|---|
| `Audio Seam` | `Auto` corrects decoded audio boundaries only; `Off` leaves them unchanged | `Auto` unless diagnosing audio |
| `Video Seam` | `Auto`, experimental `Auto 2`, `Analyze Only`, or `Off` | Keep the supplied workflow value; use Analyze Only when measuring without altering frames |
| `Buffer Backend` | `Auto`, `RAM`, or `Disk-backed` storage for the assembled IMAGE buffer | `Auto` |

`Exact Total Duration` is managed as On and `Report Detail` is controlled from ComfyUI Settings. Driving Audio bypasses generated audio and Audio Seam, but Video Seam can still apply. Finalize outputs final `images`, final `audio`, and a text `report` for the downstream Save Video node.

### H3 Continuum Second Pass

Second Pass is the Advanced bridge for matching First Pass physical groups. See the current [diagram and connection checklist](SECOND_PASS_GUIDE.md) ([日本語](SECOND_PASS_GUIDE_JA.md)). It takes `model`, `clip`, `sampler`, low-denoise `sigmas`, externally processed `video_latents`, the matching first-pass `audio_latents`, the original `assembly_plan`, and a separate `refine_seed`. Optional `refine_context` restores the physical group's First/Last/Reference conditioning; optional `video_vae` is used only when that context requires image re-encoding.

Its outputs are `refined_video_latents`, bit-exact first-pass `audio_latents`, an `updated_assembly_plan`, and `status`. V3.8 requires a complete Review sequence for context inheritance. V3.9 can inherit validated context projected onto the actual partial-Review output groups; keep the matching latent lists, Plan and context together. Missing or unavailable context can produce a diagnostic prompt-only fallback; invalid typed context can fail validation. It is not an automatic Hi-Res button and does not include an upscaler.

### ComfyUI Settings added by Continuum

| Setting | Default | Effect |
|---|---:|---|
| `H3 Continuum: Sampling Preview` | On | Shows live sampling previews; Off only reduces preview overhead |
| `H3 Continuum: Developer Diagnostics` | Off | Enables developer-only logging/assertions; leave Off for normal use |
| `H3 Continuum: Detailed Report` | Off | Adds read-only detail to Sampler status and Finalize report; generated tensors are unchanged |

### Turbo LoRA and Spectrum in supplied workflows

![Example third-party LoRA selector with one LightX2V Turbo LoRA enabled](images/v38-manual/turbo-lora-choices.png)

The four MiniMax H3 Turbo files shown in the example come from the LightX2V MiniMax-H3-Turbo project: [GitHub](https://github.com/ModelTC/Minimax-H3-Turbo) and [Hugging Face files](https://huggingface.co/lightx2v/Minimax-h3-Turbo). `FL2VA` files are for T2VA/I2VA/first-last workflows; `Ref2VA` is for Reference-to-Video. `_768p` identifies the training-resolution family. Select **one LoRA matching the task**—do not enable all four together merely because they are listed.

| File shown | Intended path | Distilled target recorded by the file/repository |
|---|---|---|
| `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | FL2VA / T2VA, 544p family | 8-step; the upstream table also lists 4-step inference as an option for this checkpoint |
| `minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` | FL2VA / T2VA, 768p family | 8-step |
| `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` | Ref2VA, 768p family | 8-step |
| `minimax_h3_fl2v_turbo_4step_v1.2_768p_comfyui_bf16.safetensors` | FL2VA / T2VA, 768p family | 4-step |

The number in a Turbo filename is its distilled NFE target. Use the matching upstream recommendation unless a provided workflow explicitly documents a tested exception. In particular, using a 4-step LoRA with `Steps = 6` is a workflow-specific experiment, not the LightX2V default. `Euler`/`simple`, the actual Steps value, and the selected LoRA must be recorded together when comparing results.

`Power Lora Loader (rgthree)`, KJNodes SageAttention, and Spectrum are external components. Continuum does not install, enable, or tune them. The [V3.8X2 workflow](../examples/workflows/MiniMax_H3_Continuum_V38X2.json) is the supplied graph, distributed under two official filename aliases as matching JSON and ZIP pairs. Its saved default has Spectrum disabled and no Turbo LoRA enabled. These three custom-node packages are required to open the complete graph, including when switching it to Turbo. ComfyUI-Easy-Use is not required.

The supplied prompt, media selections, and node titles have deliberately been preserved. Choose files available on your computer, disable unused optional inputs, and enter your own prompt before generating. Models, LoRAs, images, and audio are not included. A custom title such as `Save 3x5s Video` is only a saved label: actual duration follows the Sampler's `Chunks` and `Seconds per Chunk`, not that title.

The same graph can be used as the quick Turbo path: disable Spectrum, enable exactly one task-matched LightX2V Turbo LoRA, then select the sampler and Steps intended for that LoRA or for a separately documented tested variation. The supplied graph lists the FL2VA Turbo 4-step v1.2 768p file but leaves it disabled in the Spectrum default. The previously tested `Euler` / `simple` / `Steps = 6` setup with that 4-step LoRA is a workflow-specific variation, not the LightX2V upstream default. Do not enable Spectrum and a Turbo LoRA together merely because both controls are present.

### Known long-continuation limitation: Issue #13

[Issue #13](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/13) remains open. Repeated continuation can increase contrast, edge energy, or apparent sharpness on some prompts and trajectories. V3.8 Standard has **no active production mitigation** for this issue; it preserves the accepted Masked AV behavior.

An experimental prefix-amplitude renormalization produced a strong improvement in one `6 × 5 s` run, but a later frozen `4 × 8 s` A/B/C gate did not reproduce the target drift and therefore applied gains of `1.0`; Standard and the experimental arm were bit-exact. The older Compatibility route did not justify replacing Standard and raised a separate boundary-audio concern. The accurate release statement is therefore: **the issue is not proven fixed, the current Standard path is unchanged, and experimental mitigation stays Default Off**. Report the first and worst affected chunk, workflow JSON, prompt, seed, model/LoRA, Steps/SIGMAS, size, Continuity, and Audio Continuity when reproducing it.

> **Support boundary:** The original V3.8 launch surface had seven IDs. V3.8X2 registers ten IDs including the Video Adapter and two deprecated loader compatibility IDs; V3.9 adds two more, for twelve. Some retain earlier IDs, including Finalize (`H3ContinuumAssembleSeamV35`) and Second Pass (`H3ContinuumSecondPassV35`); this does not make all older workflows compatible. Use the matching historical Release/tag for unsupported node IDs. See [V3.8 Release and Migration Policy](V38_RELEASE_AND_MIGRATION.md).

The accepted 16GB GPU gates reached about `15.5-15.6 GiB` in the most complex cases. Actual use varies by GPU, driver, backend, model precision, resolution, and connected nodes; this is not a universal 16GB guarantee.

### Review, continue, and revise a chunked video

> **Live UI verification:** The repaired Review flow was rechecked in ComfyUI on 2026-09-07. The current walkthrough used Turbo4, actual `Steps = 4`, Euler/simple, `Draft — 0.30 MP`, and Spectrum Off. Chunk 1 reached the three-action review screen; `Use it and continue` then reused the accepted first chunk, generated only Chunk 2, and reached `Saved sequence is complete`. `Try this chunk again` was also live-validated after the Review repair. Timings below are measurements from that machine, not speed guarantees.

Start here when you already have a working V3.8 workflow and want to keep good chunks, retry a result, or extend a sequence. These instructions use the labels displayed on **H3 Continuum Sampler V3.8**. The **blue `Run` button at the top right of ComfyUI** starts execution. It is different from the Sampler's `Run` setting (`Review Each Chunk` or `Generate Full Video`). Continuum's review messages still say “press Queue”; on the frontend shown here, that means clicking the top-right blue `Run` button. Older frontends may label that button `Queue`.

![ComfyUI's top-right blue Run button starts the selected action](images/v38-manual/live-execute-button.png)

Choose the task you need:

- [Prepare the settings for continuation](#1-prepare-the-settings-for-continuation)
- [Understand the first, shorter output](#2-generate-and-review-the-first-chunk)
- [Keep the result and generate the next chunk](#3-keep-the-result-and-generate-the-next-chunk)
- [Try the current chunk again](#4-try-the-current-chunk-again)
- [Keep the result and finish everything remaining](#5-keep-the-result-and-finish-everything-remaining)
- [Go back to settings without losing the review](#6-go-back-to-settings-without-losing-the-review)
- [Choose an earlier Take or branch from it](#7-choose-an-earlier-take-or-branch-from-it)
- [Regenerate from a particular chunk](#8-regenerate-from-a-particular-chunk)
- [Add more chunks to a completed sequence](#9-add-more-chunks-to-a-completed-sequence)
- [Understand continuation time and check reuse](#10-understand-continuation-time-and-check-reuse)
- [Troubleshoot a missing action or unexpected result](#11-troubleshoot-a-missing-action-or-unexpected-result)

#### Before you begin: total length is not the next Queue's output length

`Chunks` is the **total number of chunks you want**, not the number to add on the next Queue. `Seconds per Chunk` is the duration of each chunk. `Total Length` is the planned final duration; it is not a progress counter.

For example, `Chunks = 6` and `Seconds per Chunk = 5` means a 30-second target. With `Run = Review Each Chunk`, the first Queue normally creates only Chunk 1: a 5-second video. Continuing generates the next review unit. During review, the preview/save output is the **current review unit** (normally 5 seconds), not an accumulating preview. After the run reaches `complete`, or after `Use it and finish the rest` generates the remaining chunks, Finalize outputs the assembled completed sequence.

The screenshots show **two chunks as a small example**. The same controls apply to three, four, five, six, or another supported total.

> **Last Image exception:** The examples below assume ordinary, separately generated chunks. When Last Image uses Long Terminal Merge, the final pair is generated and reviewed together. Continuing or retrying that pair operates on both chunks as one unit. Do not expect a separate review stop between them.

#### 1. Prepare the settings for continuation

1. Find `Base Seed` and keep its current number. You do not need to copy the number in the screenshot.
2. Directly below it, set `Control After Generate` to `fixed`.

![Base Seed and Control After Generate set to fixed](images/v38-manual/seed-fixed.png)

3. Set `Chunks` to your intended **final total**. Use `2` for the screenshot's example, or your own total such as `6`.
4. Set `Seconds per Chunk` to the duration you want. The example uses `5`.
5. Check `Total Length`: two chunks of 5 seconds should show `10 seconds`; six should show `30 seconds`.
6. Set `Run` to `Review Each Chunk`.
7. Set `Progress` to `On — Resume and Takes available`.
8. If `Regenerate From` is visible under `Show Advanced Settings`, leave it at `Auto` for normal continuation.
9. Check that the green `Ready to Queue` card describes the total and says `Review each chunk`.

![Review settings with fixed seed, two 5-second chunks, Review Each Chunk, and Progress On](images/v38-manual/live-review-settings.png)

**Keep these settings while continuing:** `Base Seed`, `Control After Generate = fixed`, `Seconds per Chunk`, and `Progress = On — Resume and Takes available`. Keep the same workflow, prompt, input media, model, sampler, step schedule, size, and continuation settings too. Leave `Run Name (Optional Override)` unchanged. Changing generation inputs can make saved chunks incompatible; keeping the seed alone does not guarantee reuse.

For ordinary continuation, do not increase `Chunks` after every Queue. If the goal is six chunks, leave it at `6` until those six are complete.

#### 2. Generate and review the first chunk

1. Click the top-right blue `Run` button once.
2. Wait for the workflow, including video saving, to finish.
3. Play the resulting video. In the 5-second example, the first output is **5 seconds**, even though `Total Length` says 10 or 30 seconds.
4. Look at the Sampler. While more chunks remain, it should show `Chunk 1 is ready for review` and the actions below.

![Chunk 1 ready for review with continue, retry, finish, and Back to Settings buttons](images/v38-manual/live-review-actions-steps4.png)

The shorter output is intentional: Continuum is waiting for your decision before spending time on later chunks. If your total is only one chunk, it is already complete; there is no next chunk within that target.

`Render History — 68 Takes` in this screenshot is a count of stored Takes from that run's history. It does **not** mean the target is 68 chunks. Your count will differ.

#### 3. Keep the result and generate the next chunk

1. Click `Use it and continue` on the review panel.
2. Confirm the button now shows `✓ Use it and continue`. The card says `Selected: Use it and continue. Press Queue to run this action.`

![Use it and continue selected; Queue is still required](images/v38-manual/live-continue-selected-steps4.png)

3. Click the top-right blue `Run` button. Clicking the review button alone does not start generation.
4. Wait for completion and play the new output. The accepted chunks are reused; the next chunk is newly generated.
5. If the target is not yet complete, review the new chunk and repeat from step 1.

**Example:** With `Chunks = 6` and three 5-second chunks already completed, this action reuses Chunks 1–3 and generates Chunk 4. The saved video becomes 20 seconds, and you review Chunk 4 next. It does not immediately generate Chunks 5–6.

With the screenshot's `Chunks = 2`, continuing after Chunk 1 completes the target and produces a 10-second video. There is no third chunk unless you increase the target as described in [section 9](#9-add-more-chunks-to-a-completed-sequence).

![The two-chunk target is complete after only Chunk 2 is generated](images/v38-manual/live-sequence-complete-steps4.png)

At completion, `Try this chunk again` means “make another Take of the last reviewed chunk,” here Chunk 2. It does not mean that Continuum discarded Chunk 1. Use `Back to Settings` to change the target or `Render History` to inspect stored Takes.

#### 4. Try the current chunk again

Use this when the **chunk currently being reviewed** is the one you want to replace.

1. Keep `Base Seed` unchanged and `Control After Generate = fixed`. Do not switch to `randomize` to get another Take.
2. Click `Try this chunk again` on the review panel.
3. Confirm that this action has the `✓`, then click the top-right blue `Run` button.
4. Play the new result. Continuum keeps the earlier accepted chunks and creates another Take of the reviewed chunk, with its own variation managed internally.
5. If you like it, use `Use it and continue`. Otherwise, repeat `Try this chunk again` and the top-right blue `Run` button, or select an older Take from `Render History`.

**Example:** While reviewing Chunk 3 of a six-chunk target, retrying reuses Chunks 1–2 and generates a new Chunk 3. The output is still 15 seconds, not 20 or 30 seconds. Chunks 4–6 have not been generated on this path yet. The older Take remains in history.

![Try this chunk again selected; the top-right Run button executes the retry](images/v38-manual/live-retry-selected.png)

To replace an earlier chunk after moving past it, use [Render History](#7-choose-an-earlier-take-or-branch-from-it) or [Regenerate From](#8-regenerate-from-a-particular-chunk), not the current-chunk retry button.

If you change the seed, prompt, references or other generation inputs after a review, the panel shows **Settings changed** and withdraws the old Continue/Retry/Finish actions. Queue the current settings for the backend to decide compatible reuse, or select **Start again from Chunk 1** and then Queue for an explicit restart. This is non-destructive: existing Takes remain in Render History. If you manually select `Regenerate From = Chunk N`, press Queue directly; Review buttons no longer discard that boundary.

#### 5. Keep the result and finish everything remaining

1. Play and approve the chunk currently being reviewed.
2. Leave `Chunks` at the final total you want.
3. Click `Use it and finish the rest`.
4. Confirm its `✓`, then click the top-right blue `Run` button.
5. Wait for all remaining chunks and the final video to finish. This Queue does not pause for a review after each remaining chunk.

These three buttons are different even though all require `Queue`:

| While reviewing Chunk 3 of a six-chunk, 5-second-per-chunk target | Reused chunks | Newly generated chunks on the next Queue | Saved duration |
|---|---|---|---|
| `Use it and continue` | 1–3 | 4 | 20 seconds |
| `Try this chunk again` | 1–2 | A new Take of 3 | 15 seconds |
| `Use it and finish the rest` | 1–3 | 4–6 | 30 seconds |

For a two-chunk target after Chunk 1, `Use it and continue` and `Use it and finish the rest` produce the same remaining amount: only Chunk 2 is left. Their difference becomes clear with a larger target.

#### 6. Go back to settings without losing the review

1. On the review panel, click `Back to Settings`.
2. The normal controls appear again. You can inspect `Chunks`, `Run`, `Progress`, and the other settings.
3. Click `Show Advanced Settings` only if you need controls such as `Regenerate From` or `Run Name (Optional Override)`.
4. To go back without changing the operation, click `Return to Review`.

![Back to Settings keeps the completed sequence and exposes Return to Review](images/v38-manual/live-settings-complete-steps4.png)

![Return to Review above Regenerate From, Run Name, and Continuation Backend](images/v38-manual/return-to-review.png)

**Neither navigation button queues work, deletes a Take, resets the run, nor cancels a selected action.** `Return to Review` also does not undo settings you edited. Before the next Queue, select the action you actually want and check its `✓`.

`Show Advanced Settings` and `Hide Advanced Settings` only show or hide controls; they do not turn those settings on or off. `Back to Settings` is not a “start over” button.

#### 7. Choose an earlier Take or branch from it

A **Take** is a stored version of a generated result. A **branch** is an alternative continuation from a chosen result; the old history is retained.

1. On the review panel, click `Render History — … Takes`.
2. Use `Previous Take` and `Next Take` to choose a stored result. Read the displayed chunk and branch information; selecting an entry by itself does not replace your current sequence.

![Render History with Take navigation and the two explicit Take actions](images/v38-manual/live-render-history-steps4.png)

3. Choose one of the following actions, then click the top-right blue `Run` button:
   - `Use This Take`: make the selected stored result the active result. This action runs no new sampling; the output path can still decode and save the selected sequence.
   - `Continue From Here`: keep the sequence through the selected Take and generate the next review unit on a new continuation path.
4. Review the resulting output before continuing again.

**Example:** To keep an older Chunk 2 and make a new Chunk 3, select that Chunk 2 Take and use `Continue From Here`, then the top-right blue `Run` button. Do not select Chunk 3 if Chunk 3 is the part you want replaced. Later chunks from the old path are not automatically attached to the new one.

Keep `Regenerate From = Auto` when using Take actions. Do not combine an explicit `Regenerate From` selection with `Use This Take` or `Continue From Here`. If the selected Take already completes the configured total, `Continue From Here` has no next chunk to generate.

#### 8. Regenerate from a particular chunk

Use this when you know the **first chunk that must be redone**. Unlike retrying the current review, this can rebuild a longer section of an existing sequence.

1. Click `Back to Settings` if you are on the review panel.
2. Keep `Base Seed`, the total `Chunks`, and `Seconds per Chunk` unchanged. Keep `Control After Generate = fixed` and `Progress = On — Resume and Takes available`.
3. Click `Show Advanced Settings`.
4. Set `Regenerate From` to the first chunk to redo, such as `Chunk 3`. Earlier chunks can be reused only if their inputs remain compatible.
5. Set `Variation Nonce`, which appears for explicit regeneration. Keep `Base Seed` fixed. `0` selects a new variation automatically after a completed regeneration; a compatible interrupted regeneration resumes its existing variation instead. A value of `1` or higher fixes the variation: keep it to reproduce/resume that variation, or change it to request another. Repeating the same positive value with identical inputs does not request a different result. This is separate from `Try this chunk again`, which advances the review variation automatically.

![Regenerate From exposes Variation Nonce for an explicit regeneration](images/v38-manual/live-regenerate-from-chunk2.png)

6. Set `Run` to `Generate Full Video` to rebuild everything from the selected chunk through your target in one Queue.

![Run set to Generate Full Video while Progress stays On](images/v38-manual/full-video-progress.png)

7. Click the top-right blue `Run` button, wait for completion, and check the new full-length output.
8. Before ordinary continuation or review actions, set `Regenerate From` back to `Auto` so that the next Queue is not another explicit request to redo that section.

**Example:** With a completed six-chunk sequence, `Regenerate From = Chunk 3` and `Run = Generate Full Video` reuse compatible Chunks 1–2 and regenerate Chunks 3–6. This is **four newly generated chunks**, not only Chunk 3. Later chunks depend on the changed continuation and must follow the new path.

If you want a review pause instead, choose `Run = Review Each Chunk` in step 6. The next Queue generates the first requested review unit, not the whole remaining section. After reviewing it, select `Use it and continue` to proceed one unit at a time, or `Use it and finish the rest` to complete the section. Keep earlier-chunk inputs unchanged if you want those chunks reused.

#### 9. Add more chunks to a completed sequence

**You do not need Render History just to make a completed video longer.** For an ordinary extension, go back to the normal settings, increase the target `Chunks`, and Queue again. `Chunks` is the **final total number of chunks**, not the number you want to add next.

For the simplest and safest extension, keep the existing generation conditions unchanged: the same Sampler/workflow and run identity, `Base Seed`, `Control After Generate = fixed`, `Seconds per Chunk`, prompt, model/LoRA, media, dimensions, sampling schedule, Continuity, and Audio Continuity. Keep `Progress = On — Resume and Takes available` and `Regenerate From = Auto`.

**Example: extend a completed 2 × 5-second sequence to 3 × 5 seconds**

1. Finish the original two chunks. The completed target is `Chunks = 2`, so the saved video is 10 seconds.
2. Click `Back to Settings`. You do **not** need to open `Render History`.
3. Change `Chunks` from `2` to `3`. `Total Length` changes from 10 seconds to 15 seconds.
4. Keep `Progress = On — Resume and Takes available` and `Regenerate From = Auto`. Keep the prompt and the existing generation inputs unchanged for this ordinary extension.
5. Use `Run = Review Each Chunk` if you want to review the new chunk, or `Run = Generate Full Video` if you want all currently missing chunks generated in one Queue.
6. Click the top-right blue `Run` button.

With compatible saved progress, the expected work is:

- Chunk 1 → reused; no new Sampling
- Chunk 2 → reused; no new Sampling
- Chunk 3 → newly generated
- final saved sequence → 3 chunks / 15 seconds

The same rule applies to a larger extension. For example, changing `Chunks` from `3` to `5` means the new target is five total chunks; it does **not** mean “add five.” Review mode first generates Chunk 4, then Chunk 5 on the next accepted continuation. Full-video mode generates the missing Chunks 4–5 in one Queue.

Switching `Generate Full Video` ↔ `Review Each Chunk` by itself does **not** mean restart from Chunk 1. A Chunk 1 restart happens only when you explicitly choose `Start again from Chunk 1`, explicitly set Advanced `Regenerate From = Chunk 1`, or the backend determines that the stored prefix is incompatible with the current generation contract.

`Render History` is for a different job: browsing stored Takes, selecting an older Take, or branching with `Continue From Here`. Normal append-style extension does not require History. `Previous Take` / `Next Take` only browse stored results; they do not generate a new chunk.

**Do not assume append-only reuse with Last Image.** Extending a sequence changes where its final-image constraint belongs. The former last chunk, or a terminal pair, may need regeneration. Likewise, changing the prompt or other generation-contract inputs can invalidate saved progress. `Progress = On` enables compatibility checking; it does not force incompatible chunks to be reused.

The extension path is covered by CPU compatibility tests, including two-to-three chunks and Last Image invalidation. It is not the same GPU test as the two-chunk review timing example below; arbitrary extensions and media combinations have not all been GPU-verified.
#### 10. Understand continuation time and check reuse

Continuing does not mean saving only the new segment. With compatible saved progress, the normal workflow:

1. Reuses the accepted chunks' stored Video/Audio latents without sampling them again.
2. Samples the requested new chunk or remaining section.
3. Decodes the completed sequence so far, runs `H3 Continuum Finalize`, and saves the combined video again.

The full-output work grows as the sequence gets longer. Consequently, the next Queue can take as long as the first, or longer, even though earlier chunks are **not** being sampled again. Loading, preparation, decoding, assembly, saving, and other workflow overhead all contribute to total time.

The latest live GPU check used Turbo4, Euler/simple, actual `Steps = 4`, Spectrum Off, and `Draft — 0.30 MP` with `Chunks = 2`, `Seconds per Chunk = 5`, and Review enabled:

| Queue | Sampler work | H3 Continuum Sampler node time | Saved video |
|---|---|---:|---:|
| First | Generate Chunk 1 | 103.802 s | 5 seconds |
| After `Use it and continue` | Reuse Chunk 1; generate Chunk 2 | 43.738 s | 10 seconds |

Each Queue sampled one chunk with four steps. The second Queue did not sample Chunk 1 again; it sampled only the requested next chunk, then decoded, finalized, and saved the combined 10-second sequence. The first Queue also included cold-start/model preparation effects, so the difference must not be treated as a general speed ratio. Full-sequence decode and save work still occurs on continuation.

To inspect your own run:

1. Open ComfyUI Settings and search for `H3 Continuum: Detailed Report`.
2. Enable that setting before the Queue you want to inspect.
3. After completion, inspect the Sampler's `status` output through a text-display node in your workflow.
4. In the two-chunk example's second Queue, look for `1 reused, 1 generated, 2 total`. Detailed fields should show `sampled_physical_groups=1` and, with four steps, `sampling_steps_total=4`, not `8`.

The report field names are diagnostic text, not controls you need to set. For a larger target, use the reported reused/generated counts rather than timing alone. Terminal Merge can combine two chunks into one sampled group, so its group count differs from its chunk count.

#### 11. Troubleshoot a missing action or unexpected result

| What you see | What to check or do |
|---|---|
| A 5-second video despite a longer `Total Length` | In `Review Each Chunk`, this is the expected first output. Review it, select an action, then click the top-right blue `Run` button. |
| No next-chunk action | Check whether the configured total is already complete. Otherwise, wait for Queue completion and verify `Run = Review Each Chunk` and `Progress = On — Resume and Takes available`. If you opened settings, click `Return to Review`. |
| No review panel even though an incomplete Review run finished successfully | Inspect the Sampler's `status` and any ComfyUI error. This is not a reason to assume all chunks finished or to change `Base Seed`; the frontend must receive the saved review state. |
| Clicking an action appears to do nothing | Check its `✓`, then click ComfyUI's top-right blue `Run` button. The action button only selects what Queue will do. |
| `Set Control After Generate to fixed` | Set that exact control to `fixed` and retain the original `Base Seed` used for the saved chunks. |
| Settings disappeared behind the review panel | Click `Back to Settings`. Use `Return to Review` to come back; neither navigation button resets the run. |
| The next Queue takes as long as the first | Check reused/generated counts. Full-sequence decoding and saving still run; elapsed time alone cannot tell you whether chunks were resampled. |
| Earlier chunks are generated again | Check `Progress`, saved files, run identity, `Base Seed`, and changed generation inputs. Check that `Regenerate From` is `Auto` unless you intentionally requested regeneration. |
| Retrying changed more than one chunk | A terminal pair is one review unit. Also distinguish `Try this chunk again` from `Regenerate From`, which rebuilds the chosen chunk and its following section. |
| You want to stop choosing an action after every chunk | At the review panel, select `Use it and finish the rest`, then click the top-right blue `Run` button. Keep `Chunks` at your intended final total. |

Driving Audio can be used with Review and Smart Regenerate. The Continuum Image, Audio, and Video loaders support native bypass for optional media paths.

> **Second Pass version boundary:** V3.8 does not support partial-Review context inheritance. V3.9 supports validated context for the actual output groups, including partial Review. See the [current guide](SECOND_PASS_GUIDE.md).
