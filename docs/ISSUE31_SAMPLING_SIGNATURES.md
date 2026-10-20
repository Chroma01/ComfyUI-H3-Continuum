# Issue #31 — Attention and Spectrum reuse signatures (3.9.5)

## 3.9.11 — stable supplemental loaded-code audit

Repeated imports of unchanged audited Spectrum source can produce different
marshal bytes for equivalent normalized code objects, observed with Python
3.13.12. This can mark a new Run read-only even though no source or settings
changed. It is a signature observation failure; the reporter's exact environment
has not been reproduced.

The original audit remains the first path. Only differences in function
`code_sha256` fields can trigger a supplemental audit. Fixed
`spectrum_code_audit_v1_py312.json` and `spectrum_code_audit_v1_py313.json`
profiles check all loaded provider module descriptors: typed code fields and
nested constants, defaults, keyword defaults, closures, class members and
provider references. Float/complex bits and constant types are preserved.
Source hashes, exact Python file sets, module provenance and runtime-state
checks remain required. Unknown constants or missing/invalid profiles reject
reuse; independent Attention failures remain failures.

The profiles are bound to the original metadata digest and complete audited
source set. They are generated offline with `tools/build_spectrum_code_audit.py`,
using explicit audited provider roots; opposite provider/module import orders
must produce identical bytes. The runtime never builds a profile, executes
provider functions, imports Spectrum or learns an approval from current code.

All four legacy provider metadata files and the returned persistent identity
remain unchanged. Normal pre-repair v6 Takes retain compatibility. Stored unsafe
Takes and v5 history stay readable and read-only; the repair never edits their
flags or manifests. Use a new Run when checking a previously rejected setup.
Sampling v6, Graph v4, Run Storage, public inputs and shipped workflows are
unchanged. Targeted browser/GPU Review continuation passed with the audited
local Spectrum provider and Kitchen Attention: Chunk 1 retained, Chunk 2
generated, one reused / one new, both AV outputs fully decoded. The supplemental
path is proven by CPU reproduction; its use during GPU execution is not traced.
See RELEASE_NOTES_V3911.md for environment, limits and the separate third-party
MP4 menu-thumbnail workaround.

CPU/JS validation: **2,139 passed / 2 skipped / 2 known Inspector expected
failures**, zero unexpected failures or CUDA initialization attempts. This
includes the existing 90-case Queue JS fixture. An additional 53 real-Core
observer/storage cases matched the production UI's read-only predicate: 30
reusable and 23 intentionally rejected. These use tiny CPU fixtures and actual
Core function references; no Attention kernel or H3 inference runs. Four normal
v6 Takes saved by pre-repair code kept identical full contracts and reused
Chunk 1 without changing their source files. Existing tests also preserve
unsafe/v5 history and reject reuse through the storage entry points.

Python 3.12 component coverage passed 155 tests with one skip; 21 tests tied to
the older Core's separate Attention limitation were excluded. The storage matrix
still checks that environment's eight Kitchen cases remain non-reusable for
its unobservable helper. This repair does not resolve that independent failure.

### 日本語 — 3.9.11の補助監査

同じ監査済みSpectrumを再読込した際、同等のコードでもmarshalの保存表現が変わり、
再利用不可になる条件へ対応します。旧監査を優先し、関数のコードハッシュだけが
異なる場合に限り、固定プロファイルでコードと読込済み記述全体を再検査します。
未知のコード・既定値やclosureの変更・追加状態の拒否は維持します。
旧署名を変更せず、正常な既存v6 Takeの互換性を保ちます。過去のunsafe／v5 Takeを
自動的に再利用可能にはしません。対象を限定したSpectrum＋Kitchenの実ブラウザー・GPU検証で、
Review操作とChunk 1保持／Chunk 2生成を確認しました。詳細と制約はRELEASE_NOTES_V3911.mdを参照。

## 3.9.10 — Spectrum audit portability

The repair treats source CRLF and LF line endings as equivalent
in both the provider-file audit and provider module closures. All other source
bytes and the exact supported Python file sets remain checked. The canonical
source hashes are unchanged, so existing valid Python 3.13 signatures retain
their identities.

Separate `spectrum_provider_v1_py312.json` and
`spectrum_provider_v029_py312.json` profiles identify the same audited source sets
under Python 3.12. They were generated and checked with Python 3.12.10; the
original profiles remain byte-identical for Python 3.13.12. Other Python runtimes,
altered implementations, foreign closures and unknown runtime fields remain
non-reusable. The adapter does not execute provider functions to approve reuse.

This repairs Spectrum observation, not every Core/Kitchen/KJ combination.
Independent Attention/provider checks must also pass. In particular, an older
Core/Kitchen environment can still fail its own Attention observation even when
Spectrum is recognized. Do not upgrade Python or replace Attention solely to
make an old Take reusable. Keep old history and start a new Run after updating.
No new GPU or reporter-exact acceptance is claimed for this repair.

The standard CPU/JS gate passed **2,096 tests / 2 skips / 2 known expected
Inspector failures**, with compile and offline registration checks passing.
Separate-process storage probes passed 16 Python 3.13 PyTorch/Kitchen cases and
eight Python 3.12 Spectrum/default-model cases; actual Take read-only JavaScript
matched all 24. The six previously valid full Sampling Contracts stayed exact.
These CPU checks execute no Attention kernel or H3 checkpoint inference.

### 日本語 — 3.9.10の局所修正

Spectrum監査でCRLF／LFの改行差を同一として扱い、対応済みソースにPython 3.12用の
固定プロファイルを追加します。既存3.13の正常な識別値と旧Takeは維持します。
未知のコード・追加状態の拒否は継続します。Spectrumが識別可能でも、Core／Kitchenなど
別の観測に失敗する環境は再利用不可のままです。適用後は新規Runで確認してください。
旧履歴を利用可能にする目的でPythonやAttentionを変更する必要はありません。

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
