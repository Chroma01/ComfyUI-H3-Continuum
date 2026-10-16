# Issue #31 — Attention and Spectrum reuse signatures (3.9.5)

## 3.9.8 Preview Override Phase A (2026-10-16)

The new adapter is restricted to the KJ source profile in `preview_override_provider_v1.json`: Preview Override SHA-256 `d07c8e5ff7d7abd3e31acefe2cf29f618b5da5341b3b434e72ec2ac0953230b0`, audited sibling helpers and Core preview/dispatcher files. The complete profile digest is part of the persistent identity, so later dependency-profile upgrades cannot retain the same identity accidentally. It compares loaded functions, nested code, defaults and supported classes with the pinned source; it never imports KJNodes, executes a preview callback, loads a VAE or initializes CUDA during signature observation. Source line endings are normalized to LF for provider auditing.

After that audit, the exact builtin `frames` list is treated as execution-local display data. Max resolution, node ID, JPEG quality, suppression, frame count, FPS and supported Core preview settings remain part of the identity. Core's cross-key insertion order and each wrapper list's order are preserved explicitly, because the generic dictionary observer sorts keys. The ordinary non-KJ signature path is unchanged.

Phase A requires `vae is None`, `audio_vae is None`, KJ Tiny VAE `none`, and Core NoPreviews/Auto/Latent2RGB. Unknown files, replaced code/defaults/helpers, extra wrapper state, foreign classes and approximate-VAE previews keep reuse disabled; they are not promoted by an empty frame list. This profile does not claim support for every KJNodes 1.5.2 checkout or the different upstream Preview Override source. No general `frames` exclusion is added.

Existing normal non-KJ Sampling v6 identities remain exact. Earlier safe KJ identities may differ and cannot be assumed reusable; earlier unsafe/v5 histories remain preserved and read-only. Start a new Run after updating; old KJ history is not migrated. Full real-Core CPU gate: 1,995 passed / 3 skipped / 2 existing Inspector expected failures / zero unexpected failures and CUDA initialization attempts; the 48 dedicated KJ tests passed without skips. Normal ComfyUI GPU acceptance passed four Core-API Queues: PyTorch and Comfy Kitchen INT8 + the audited local Spectrum implementation, each with separate-Queue Chunk 1 to 2 continuation and held preview images. Both second Queues reused one chunk and generated one; original Chunk 1 bytes and contracts were unchanged. All four video/audio outputs fully decoded. See docs/KJ_PREVIEW_OVERRIDE_V398.md for exact support and limits. Product files used in this targeted GPU gate are byte-identical to the 3.9.8 repair. Browser Run-button behavior, subjective preview quality, reporter-exact reproduction and per-kernel return tracing are not newly accepted.

## Previous 3.9.5 Attention / Spectrum repair

With Model Attention Backend between a LoRA Loader and Spectrum, cyclic Attention closures and a slots-based SpectrumH3Binding could be unobservable. Generation still succeeded, but Sampling v6 correctly refused reuse with "Saved history is read-only". This update identifies the reviewed runtime implementations rather than forcing resume_safe.

Core PyTorch and Comfy Kitchen INT8 overrides are identified by their loaded functions, defaults, closures, both container paths and numerical/provider state. Spectrum identity includes all 27 effective immutable config fields and audited source/loaded-function contracts. Reviewed history, counters and statistics do not change persistent identity. Unknown sources, foreign module closures, extra runtime state and altered implementations remain non-reusable.

Two explicit Spectrum source profiles are included: upstream v0.2.29 at commit 806fe498d574a726fecb8818917f00a4b993fd77 (55 provider files), and the prior audited 44-file implementation. Versions/class names alone do not enable reuse. The loaded-function contract is environment-specific: validation uses Python 3.13.12, ComfyUI Core 0.40.0 and comfy-kitchen 0.2.37; other source/runtime combinations may remain read-only. BSA/Flow/Untwist and KJ/Sage patch-node combinations are outside this targeted acceptance.

Update the custom node and restart ComfyUI. Start a new Run. Existing unsafe/v5 Runs are preserved and are not repaired or promoted; normal unaffected Sampling v6 identities remain compatible. Sampling v6, Graph v4, Run Storage v3, public IDs/socket order and shipped workflow bytes stay unchanged.

The signature gate passed 152 CPU tests with one original-profile-only skip and no failures; CUDA initialization attempts were zero. Full standard validation passed 1,893 tests with 2 skips and 2 existing Inspector expected failures (zero unexpected failures and CUDA initialization attempts). Public upstream 0.2.29 PyTorch/Spectrum and Kitchen/Spectrum new-Run GPU gates both passed separate-Queue Chunk 1→2 continuation, prefix/contract preservation and complete 512x512 / 24fps / 10-second AV decoding. Actual CUDA backend returns were observed. Existing Inspector reconfigure expected failures, browser acceptance, visual/audio quality and benchmarks remain separate.

## 日本語

Model Attention BackendとSpectrumを併用したReview継続で、Attentionの循環参照とslots付きBindingを観測できず、生成後のTakeが再利用不可になる問題へ対応します。全27設定値・実ソース・読み込まれた関数を識別し、実行中の履歴や統計値は永続署名へ含めません。resume_safeを強制せず、未知の実装や追加状態は安全側で拒否します。

公式Spectrum v0.2.29の固定コミットと、以前に監査した44ファイルの実装を別プロファイルとして扱います。別のSpectrum版、別のPython/Core実装、BSA/Flow/UntwistやKJパッチの組合せ全般を保証するものではありません。更新・再起動後は新しいRunを作成してください。以前のunsafe履歴を自動修復せず、既存TakeとWorkflowは保持します。
