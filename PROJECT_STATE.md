# Public source status

Updated: 2026-10-16 (Japan time).

## README organization (documentation only)

The English README is a compact entry point. Detailed operating instructions and
screenshots remain in docs/USER_GUIDE.md; release and older implementation notes
remain in docs/README_HISTORY.md. Version-specific acceptance statements retain
their historical context. Japanese README, product code, official workflows and
published v3.9.8 assets are unchanged; this is not a new runtime or release version.

## Published v3.9.8 GPU recheck (2026-10-16)

The exact published tag `58fbd855` was deployed and restarted in normal ComfyUI; all 464 release files and the live startup/adapter identity matched. Two new Runs / four Core-API Queues passed PyTorch/KJ and Kitchen INT8 + audited local Spectrum/KJ Chunk 1 to 2 continuation, unchanged prefix/contracts and complete AV decoding. Existing Takes/workflows stayed hash-identical. README and docs/RELEASE_NOTES_V398.md record conditions and unverified scope. The later documentation-only main commit does not replace the release tag, GitHub assets or Registry package.

## 3.9.8 — KJ Preview Override Phase A (2026-10-16)

A bounded adapter identifies the audited KJ Preview Override source and loaded helpers, preserves fixed settings and wrapper execution order, and excludes its reviewed transient image list. VAE/Audio VAE must be disconnected, KJ Tiny VAE must be `none`, and Core approximate-VAE preview is outside this phase. Unknown implementations remain non-reusable. Sampling v6, old Takes and official workflows are unchanged. Full real-Core CPU gate: 1,995 passed / 3 skipped / 2 existing Inspector expected failures / zero unexpected failures and CUDA initialization attempts; the 48 dedicated KJ tests passed without skips. Normal ComfyUI GPU acceptance passed four Core-API Queues: PyTorch and Comfy Kitchen INT8 + the audited local Spectrum implementation, each with separate-Queue Chunk 1 to 2 continuation and held preview images. Both second Queues reused one chunk and generated one; original Chunk 1 bytes and contracts were unchanged. All four video/audio outputs fully decoded. See docs/KJ_PREVIEW_OVERRIDE_V398.md for exact support and limits. Release and Registry state are verified separately.

## 3.9.7 — external-input regeneration cache

Fix automatic Full Run variations when Chunks or Variation Nonce come from external nodes. Unresolved linked inputs no longer let Core skip an explicitly requested regeneration. Earlier accepted chunks, existing Takes, public inputs and official workflows are preserved. Update the custom nodes, restart ComfyUI and refresh the browser; no workflow changes or history deletion are required. See docs/RELEASE_NOTES_V397.md for targeted validation and limits.

## 3.9.6 — regeneration selection and automatic variations

Package 3.9.6 preserves saved regeneration selections and routes explicit Full Run automatic variations through Run Storage on every Queue. The full CPU gate and targeted normal-runtime browser/GPU acceptance passed; scope and update steps are in docs/REGENERATE_INTENT_V396.md. Sampling v6 safety, public inputs, official workflows and stored Takes are preserved. Release assets and Registry service status are verified separately.

## 3.9.5 — Issue #31 Attention and Spectrum identity repair

Finite loaded-implementation signatures identify the Core PyTorch/Kitchen attention overrides and explicit Spectrum profiles, including upstream 0.2.29. Existing normal v6 contracts without the targeted override remain unchanged; original unsafe/v5 history and official workflows are preserved. Validation and compatibility limits are recorded in docs/ISSUE31_SAMPLING_SIGNATURES.md. GitHub assets and Registry service status are verified separately.

## GitHub and Registry publication status

**Latest package: 3.9.8.** Use the fixed-version GitHub downloads below. Registry publication is verified separately.

| Version | Release | Custom-node ZIP | SHA-256 checksum |
| --- | --- | --- | --- |
| 3.9.8 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.8) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/ComfyUI-H3-Continuum-v3.9.8.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/SHA256SUMS.txt) |
| 3.9.7 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.7) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.7/ComfyUI-H3-Continuum-v3.9.7.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.7/SHA256SUMS.txt) |
| 3.9.6 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.6) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.6/ComfyUI-H3-Continuum-v3.9.6.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.6/SHA256SUMS.txt) |
| 3.9.5 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.5) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.5/ComfyUI-H3-Continuum-v3.9.5.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.5/SHA256SUMS.txt) |
| 3.9.4 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.4) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.4/ComfyUI-H3-Continuum-v3.9.4.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.4/SHA256SUMS.txt) |
| 3.9.3 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.3) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.3/ComfyUI-H3-Continuum-v3.9.3.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.3/SHA256SUMS.txt) |
| 3.9.2 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.2) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.2/ComfyUI-H3-Continuum-v3.9.2.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.2/SHA256SUMS.txt) |

The original [3.9.2 GitHub source archive](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/archive/refs/tags/v3.9.2.zip) remains available from its unchanged tag. This custom-node package ZIP is distinct from the official workflow ZIPs.

Registry 3.9.3 was uploaded; its retrieved ZIP omitted one declared document and included three undeclared prompt-authoring files. Package 3.9.4 corrects the file selection. Registry scan status is reported by the service; source publication alone does not establish scan approval.

## 3.9.4 — Registry packaging repair (2026-10-14)

Include the declared Review restoration guide and exclude repository-only prompt-authoring files from the Registry ZIP. The publishing workflow now builds the actual package and checks its exact file set, CRC and every Registry Manifest hash before uploading. Runtime behavior, twelve public node IDs, workflows and saved Runs/Takes are unchanged. GitHub Releases 3.9.3 and 3.9.2 remain available.

## Package 3.9.3 — temporary storage settings

The current source adds a server-side scratch folder setting for Finalize and Decode Cache, storage usage/free-space reporting and conservative unused-file cleanup. Manual buffer capacity checks retain the existing Auto policy. Node schemas, official workflow bytes, generation identity and saved Runs/Takes are preserved.

Frontend follow-up improves missing/empty-response diagnostics and storage candidate initialization. The Core request address/profile handling is retained, and no automatic mutation retries are added.

The new setting is available under Settings → H3Continuum → Storage. Validation and platform limitations are recorded in PACKAGE_VALIDATION.txt. Source publication does not imply a new GitHub Release/tag or Registry publication.

## Previous package 3.9.2 — Issue #30 frontend hotfix

This package includes three minimal frontend changes: skip Review snapshots without a comparison baseline, notify connected Samplers once per Reference selection, and skip unchanged node dimensions when resizing. Review baseline monitoring, synchronous Take/Queue checks and generation/storage contracts are retained; package metadata is 3.9.2.

CPU/JavaScript regression checks passed 1,703 cases, with 2 skips and 2 explicit expected failures for the separate Inspector reconfigure bug. Offline twelve-node/runtime checks, isolated Chromium checks and the actual Core/frontend/LiteGraph desktop smoke passed without GPU generation. The live smoke covers native assignment graph serialization/reload and upstream edit/restore using synthetic nodes; UI file-save and stored-Take acceptance remain separate. DOM rebuilds remain; real ComfyUI browser save/reload, mobile freeze resolution and full workflow acceptance are still pending. No delayed update timer is added. See GitHub Releases for the published version; Registry publication is separate.

## Previous package 3.9.1 — generation stability history

This patch stabilizes V3.9 generation and Review without adding LoRA Plan or V4.0. Public V3.9 node IDs and official workflows remain unchanged. V3.8X2 stays available as a separate workflow; historical releases and tags remain available.

The included repairs cover:

- Second Pass audio-only and mixed keyframes, with video-only spatial adaptation.
- Conditioning and Reference inheritance for the actual Review output, including partial output and a single middle chunk.
- Take compatibility using Sampling Contract v6 and Graph Contract v4, including sampler closures and MODEL CFG/wrapper settings.
- Review Driving Audio cropped once from the physical group's natural frame range, sharing the PCM origin for Exact ON/OFF.
- Core-standard audio resampling with the legacy fallback when the API is unavailable.
- The documented Reference Encode Cache limitation for direct weight mutation inside the same VAE object.

## Compatibility

Original v5 Takes and history remain readable and are not deleted or converted. They cannot supply prefixes for v6 generation. Start a new Full Video or use Start again from Chunk 1 when moving an older Run to the repaired runtime.

Run Storage v3 and State/Session formats are retained. Unknown upstream settings can still generate; when their identity cannot be observed safely, automatic Take reuse is disabled.

## Validation and remaining limits

- Full CPU regression: 1,696 passed, 1 skipped, no failures; CUDA initialization attempts: zero.
- Offline verification: native PackedLayout and Fixed 3x5-second planning passed; twelve public nodes registered.
- Targeted GPU checks passed partial-prefix Review, single-middle-chunk Review and complete three-group reuse at 512x512 / 24 fps. Corresponding saved FLAC matched source PCM, and original Take/raw files were retained.
- Integrated generation and Take-reuse GPU checks passed for the repaired runtime.
- Browser save/reload acceptance and full acceptance of the unchanged default workflow remain pending. These targeted results do not establish every accelerator or quality combination.
- Optional latent-upscale doubled outlines are tracked separately in [Issue #27](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/27).
- Versioned source downloads are listed in GitHub Releases. Registry publication is separate, and Release publication does not complete the pending acceptance gates.

See README.md, README_JA.md and CHANGELOG.md for user instructions and repair details. Current package records are in PACKAGE_VALIDATION.txt and PACKAGE_INFO_JA.txt; docs/VALIDATION_JA.md separates the current acceptance procedure from historical V2 instructions. Follow-up documentation corrections on main retain the published v3.9.1 tag.
