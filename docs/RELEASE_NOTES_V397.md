# v3.9.7 — External-input regeneration cache fix

Fix automatic Full Run variations when Chunks or Variation Nonce come from external nodes. Unresolved linked inputs no longer let Core skip an explicitly requested regeneration. Earlier accepted chunks, existing Takes, public inputs and official workflows are preserved. Update the custom nodes, restart ComfyUI and refresh the browser; no workflow changes or history deletion are required.

CPU: 1,948 passed / 2 skipped / 2 known Inspector expected failures; zero unexpected failures and zero CUDA initialization attempts. Targeted Core-API GPU queues verified external Chunks=2 / Nonce=0, repeated identical automatic variations 1 then 2, and 1 reused / 1 generated chunk per variation. Browser save/reload and Run-button submissions were checked separately. GPU scope: PyTorch attention, Spectrum OFF, 512x512, 8-step Turbo, two 5-second chunks. This is a targeted cache repair, not general image-quality or all-accelerator acceptance.

Known ordinary Full Run, storage OFF and directly specified fixed nonces retain stable caching. An unresolved externally connected nonce may reevaluate the Sampler even when fixed; Run Storage still decides safe prefix reuse. Sampling v6 / Graph v4 and existing unsafe/v5 history safeguards are unchanged.

Existing workflow JSON/ZIP assets remain byte-for-byte unchanged. GitHub asset integrity and Registry upload are verified by the publishing workflow; Registry scan approval and Manager installation remain separate checks.

## 日本語

ChunksやVariation Nonceを外部ノードから接続した際に、明示したFull Run再生成がCoreのキャッシュで省略される問題を修正しました。前の採用済みChunk、既存Take、公開入力、公式Workflowは維持します。更新後はComfyUIを再起動し、ブラウザーを再読込してください。Workflowの変更や履歴の削除は不要です。

CPU 1,948成功、2スキップ、既知の期待失敗2件。外部INT接続で同一入力から自動Variationが進み、Chunk 1を保持してChunk 2だけ再生成することをGPUで確認しました。ブラウザーの保存・再読込とRun操作も別途確認しています。画質・全アクセラレーター構成の新規合格は主張しません。外部接続の固定Nonceはキャッシュ判定時に値が未解決のためSamplerを再評価する場合がありますが、保存済みprefixの再利用は既存の安全判定に従います。


## Post-release verification on the published v3.9.7 tag

**Published v3.9.7 GPU recheck (2026-10-15): PASS.** After restarting with the published tag (`18df80d`), external Core INT nodes supplied Chunks=2 and Nonce=0. Two completely identical Chunk 2 regeneration prompts advanced automatic Nonce **1 → 2**; both reused Chunk 1 and generated only Chunk 2. Earlier Takes and raw latents were retained. All three outputs (baseline plus two variations) fully decoded with 240 frames and 10-second video/audio. Existing 60 workflows, one settings file, 30 Run/Take files and all 459 release files remained hash-identical. Scope: RTX 5060 Ti 16 GB, 512×512, 24 fps, 2×5 seconds, 8-step Turbo, PyTorch attention, Spectrum OFF, Core API submissions. No CUDA/OOM/execution errors were observed; this does not extend browser, subjective-quality or other-accelerator acceptance.

| Queue | Reused chunks | Generated chunks | Automatic Nonce | Elapsed |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0 | 2 | 0 | 177.8 s |
| Regenerate Chunk 2, first run | 1 | 1 | 1 | 90.4 s |
| Same input, second run | 1 | 1 | 2 | 90.5 s |

### 公開版での追加GPU検証

**公開版3.9.7でのGPU再検証（2026-10-15）：PASS。** 公開タグ（`18df80d`）で再起動後、外部Core INTからChunks=2・Nonce=0を入力し、完全に同一のプロンプトでChunk 2を2回再生成しました。自動Nonceは**1→2**へ進み、両回ともChunk 1を再利用してChunk 2だけを生成。以前のTake・raw latentも保持しました。基準生成を含む動画3本は240フレーム・映像／音声各10秒で全デコード成功。既存Workflow 60件・設定1件・Run／Take 30ファイル・公開版459ファイルのハッシュは不変です。条件はRTX 5060 Ti 16 GB、512×512、24fps、2×5秒、8-step Turbo、PyTorch attention／Spectrum OFF、Core API経由。CUDA／OOM／実行エラーは確認されず、ブラウザー・主観画質・他アクセラレーターの受入範囲は拡張していません。
