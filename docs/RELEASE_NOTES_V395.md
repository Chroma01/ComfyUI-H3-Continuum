# v3.9.5 — Issue #31 Attention and Spectrum Take reuse

Fix finite identity observation of Core Model Attention Backend and slots-based SpectrumH3Binding so compatible new Runs can continue Review Each Chunk. Core PyTorch and Comfy Kitchen INT8 overrides include loaded implementations, closures and both container paths. Spectrum includes every effective config value and an explicit loaded-implementation contract; transient history/counters do not change identity.

Includes a dedicated profile for upstream Spectrum v0.2.29 at 806fe498d574a726fecb8818917f00a4b993fd77, plus the prior audited implementation. Other source/runtime combinations remain non-reusable when their identity is unknown. Restart ComfyUI and start a new Run after updating; previously unsafe/v5 history is preserved and is not promoted or repaired.

Validation: full local CPU gate 1,893 passed / 2 skipped / 2 existing Inspector expected failures / 0 failures; CUDA initialization attempts 0. Targeted signature gate: 152 passed / 1 scope-specific skip. Upstream 0.2.29 PyTorch+Spectrum and Kitchen+Spectrum both persisted Chunk 1 and reused it from a separate Queue to generate Chunk 2, with matching revision/contract, unchanged prefix hashes and fully decoded 512x512, 24fps, 10-second audio/video output. Actual CUDA backend calls were observed in the isolated gate. Prior normal-user-runtime checks also passed for the original audited Spectrum implementation.

All 25 existing JSON/ZIP assets and 259 pre-existing Run/Take files were preserved. Sampling v6, Graph v4, Run Storage v3, twelve public IDs and official workflow bytes remain unchanged. This is targeted functional acceptance; browser interaction, subjective audiovisual continuity, BSA/Flow/Untwist, KJ/Sage patch-node combinations and benchmarks remain separate. See docs/ISSUE31_SAMPLING_SIGNATURES.md for environment-specific support.

GitHub and Registry archives are checked for exact file sets, CRC and complete Manifest hashes. Hosted main and tag tests must pass before publication. Registry scan approval and real Manager installation remain separate from upload/archive verification. Prior tags, Releases and assets are retained.

## 日本語

Model Attention BackendとSpectrumの署名を正確に識別し、新しいRunのReview Each Chunk継続を修正します。公式Spectrum v0.2.29も専用の監査済みプロファイルで対応します。更新・再起動後は新しいRunを作成してください。以前のunsafe／v5履歴は保持し、自動修復・再利用可能への昇格は行いません。

全CPU回帰は1,893成功・2スキップ・既知Inspector問題の期待失敗2件、失敗0・CUDA初期化0。公開Spectrum v0.2.29のPyTorch／Comfy Kitchen両条件で、別QueueからChunk 1を再利用してChunk 2へ継続しました。署名・元Takeのハッシュ保持・完成10秒動画の全デコードと実CUDA呼出しを確認しています。

既存25資産と259件のRun／Takeファイル、公開12ノード、Workflow、Sampling v6を保護しました。未知のSpectrumや異なる実行環境は安全側で再利用を拒否します。実画面・目視画質／音声・BSAやKJの組合せ全般の合格を主張するものではありません。

GitHub本体ZIP・チェックサム、Registry配布ZIPの整合性は公開工程で別々に確認します。Registry側の検査承認と実Manager導入は別判定です。3.9.4／3.9.3／3.9.2などの元タグ・Release・配布物は保持します。
