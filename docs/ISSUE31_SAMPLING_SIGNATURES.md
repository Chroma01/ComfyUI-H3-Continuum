# Issue #31 — Attention and Spectrum reuse signatures (3.9.5)

With Model Attention Backend between a LoRA Loader and Spectrum, cyclic Attention closures and a slots-based SpectrumH3Binding could be unobservable. Generation still succeeded, but Sampling v6 correctly refused reuse with "Saved history is read-only". This update identifies the reviewed runtime implementations rather than forcing resume_safe.

Core PyTorch and Comfy Kitchen INT8 overrides are identified by their loaded functions, defaults, closures, both container paths and numerical/provider state. Spectrum identity includes all 27 effective immutable config fields and audited source/loaded-function contracts. Reviewed history, counters and statistics do not change persistent identity. Unknown sources, foreign module closures, extra runtime state and altered implementations remain non-reusable.

Two explicit Spectrum source profiles are included: upstream v0.2.29 at commit 806fe498d574a726fecb8818917f00a4b993fd77 (55 provider files), and the prior audited 44-file implementation. Versions/class names alone do not enable reuse. The loaded-function contract is environment-specific: validation uses Python 3.13.12, ComfyUI Core 0.40.0 and comfy-kitchen 0.2.37; other source/runtime combinations may remain read-only. BSA/Flow/Untwist and KJ/Sage patch-node combinations are outside this targeted acceptance.

Update the custom node and restart ComfyUI. Start a new Run. Existing unsafe/v5 Runs are preserved and are not repaired or promoted; normal unaffected Sampling v6 identities remain compatible. Sampling v6, Graph v4, Run Storage v3, public IDs/socket order and shipped workflow bytes stay unchanged.

The signature gate passed 152 CPU tests with one original-profile-only skip and no failures; CUDA initialization attempts were zero. Full standard validation passed 1,893 tests with 2 skips and 2 existing Inspector expected failures (zero unexpected failures and CUDA initialization attempts). Public upstream 0.2.29 PyTorch/Spectrum and Kitchen/Spectrum new-Run GPU gates both passed separate-Queue Chunk 1→2 continuation, prefix/contract preservation and complete 512x512 / 24fps / 10-second AV decoding. Actual CUDA backend returns were observed. Existing Inspector reconfigure expected failures, browser acceptance, visual/audio quality and benchmarks remain separate.

## 日本語

Model Attention BackendとSpectrumを併用したReview継続で、Attentionの循環参照とslots付きBindingを観測できず、生成後のTakeが再利用不可になる問題へ対応します。全27設定値・実ソース・読み込まれた関数を識別し、実行中の履歴や統計値は永続署名へ含めません。resume_safeを強制せず、未知の実装や追加状態は安全側で拒否します。

公式Spectrum v0.2.29の固定コミットと、以前に監査した44ファイルの実装を別プロファイルとして扱います。別のSpectrum版、別のPython/Core実装、BSA/Flow/UntwistやKJパッチの組合せ全般を保証するものではありません。更新・再起動後は新しいRunを作成してください。以前のunsafe履歴を自動修復せず、既存TakeとWorkflowは保持します。
