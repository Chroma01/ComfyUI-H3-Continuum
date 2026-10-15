# v3.9.6 — Regeneration intent and automatic variations

Fix Regenerate From / Variation Nonce restoration in V3.8 and V3.9. Explicit Full Run regeneration with progress saving and nonce 0 now reaches Run Storage on every Queue, so repeating the same input after a completed variation creates another Take while preserving earlier accepted chunks. Ordinary Full Run and fixed positive nonces keep their caching behavior.

Restart ComfyUI and refresh the browser after updating. For an older unmarked Chunk 1 / nonce 0, select Chunk 1 again and save once. Existing Runs/Takes and official workflows do not need deletion or migration. Sampling v6 safety and unsafe/v5 history guards are unchanged.

Validation: 1,908 local CPU passed / 2 skipped / 2 known Inspector expected failures / zero unexpected failures and CUDA initialization attempts. Actual browser save/reload retained Chunk 2 / nonce 5 and Chunk 1 / nonce 0 after history loading. Five new-Run GPU queues passed Chunk 1 creation, separate-Queue Chunk 2 continuation, Chunk 2 regeneration and two identical Full Run / nonce 0 submissions (automatic variations 6 then 7). Earlier Chunk 1 bytes were unchanged; all five video/audio outputs fully decoded.

GPU scope: PyTorch attention, Spectrum OFF, RTX 5060 Ti, 512x512, 8-step Turbo, two 5-second chunks. Browser acceptance and Core-API GPU submissions are distinct checks. Subjective quality, other accelerators and the known Inspector issue are not newly accepted. Existing saved workflows, reachable archived Takes and all 25 JSON/ZIP distribution assets were hash-protected. Previously unavailable old output paths are not claimed as reverified. Details: docs/REGENERATE_INTENT_V396.md.

GitHub ZIP/checksums and Registry archive pass exact file-set, CRC and Manifest checks during publication. Registry upload, service scan approval and actual Manager installation are separate. Earlier Releases/tags/assets are retained.

## 日本語

V3.8／V3.9の再生成指定・Nonceを保存再読込後も保持します。保存ON／Full Run／明示Chunk／Nonce 0の同一入力でもRun Storageへ到達し、完了後は新Variationを生成できます。前のChunkと既存Takeを保持し、通常Full Runと固定Nonceのキャッシュは維持します。

更新後はComfyUIを再起動し、ブラウザーを再読込してください。旧markerなしChunk 1／Nonce 0は選び直して一度保存してください。既存WorkflowやRun／Takeの削除・移行は不要です。Sampling v6の安全判定と旧unsafe履歴の扱いは変更しません。

CPU 1,908成功・2スキップ・既知Inspector期待失敗2、失敗0・CUDA初期化0。実画面でChunk 2／Nonce 5とChunk 1／Nonce 0の保存再読込保持を確認。PyTorch／Spectrum OFFの新RunでGPU 5 Queueが成功し、Chunk 1→2継続・Chunk 2再生成・同一入力の自動Nonce 6→7・元Chunk 1保持・動画5本全デコードを確認しました。画質評価や他アクセラレーターの新規合格は主張しません。

GitHub配布物整合性とRegistryアップロードは公開工程で確認します。Registry検査承認・実Manager導入は別判定です。以前の元タグ・Release・配布物を保持します。
