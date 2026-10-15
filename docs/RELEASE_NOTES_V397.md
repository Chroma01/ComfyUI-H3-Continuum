# v3.9.7 — External-input regeneration cache fix

Fix automatic Full Run variations when Chunks or Variation Nonce come from external nodes. Unresolved linked inputs no longer let Core skip an explicitly requested regeneration. Earlier accepted chunks, existing Takes, public inputs and official workflows are preserved. Update the custom nodes, restart ComfyUI and refresh the browser; no workflow changes or history deletion are required.

CPU: 1,948 passed / 2 skipped / 2 known Inspector expected failures; zero unexpected failures and zero CUDA initialization attempts. Targeted Core-API GPU queues verified external Chunks=2 / Nonce=0, repeated identical automatic variations 1 then 2, and 1 reused / 1 generated chunk per variation. Browser save/reload and Run-button submissions were checked separately. GPU scope: PyTorch attention, Spectrum OFF, 512x512, 8-step Turbo, two 5-second chunks. This is a targeted cache repair, not general image-quality or all-accelerator acceptance.

Known ordinary Full Run, storage OFF and directly specified fixed nonces retain stable caching. An unresolved externally connected nonce may reevaluate the Sampler even when fixed; Run Storage still decides safe prefix reuse. Sampling v6 / Graph v4 and existing unsafe/v5 history safeguards are unchanged.

Existing workflow JSON/ZIP assets remain byte-for-byte unchanged. GitHub asset integrity and Registry upload are verified by the publishing workflow; Registry scan approval and Manager installation remain separate checks.

## 日本語

ChunksやVariation Nonceを外部ノードから接続した際に、明示したFull Run再生成がCoreのキャッシュで省略される問題を修正しました。前の採用済みChunk、既存Take、公開入力、公式Workflowは維持します。更新後はComfyUIを再起動し、ブラウザーを再読込してください。Workflowの変更や履歴の削除は不要です。

CPU 1,948成功、2スキップ、既知の期待失敗2件。外部INT接続で同一入力から自動Variationが進み、Chunk 1を保持してChunk 2だけ再生成することをGPUで確認しました。ブラウザーの保存・再読込とRun操作も別途確認しています。画質・全アクセラレーター構成の新規合格は主張しません。外部接続の固定Nonceはキャッシュ判定時に値が未解決のためSamplerを再評価する場合がありますが、保存済みprefixの再利用は既存の安全判定に従います。
