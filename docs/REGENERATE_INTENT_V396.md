# Regeneration selections and automatic variations — 3.9.6

## Operation and compatibility

V3.8 and V3.9 retain explicit Regenerate From and Variation Nonce across workflow save/reload and Queue submission. The intent marker is stored in workflow properties; public inputs, widget order and node IDs are unchanged. Choosing Auto clears the marker. The existing one-shot restart remains one-shot.

With progress saving enabled, choose Full Run and an explicit Chunk. Nonce 0 lets Run Storage select an automatic variation: an interrupted compatible variation may continue, and queuing again after completion creates another variation. Fixed positive nonces and ordinary Full Run retain their existing deterministic identity and Core caching.

Restart ComfyUI and refresh the browser after updating. Older unmarked Chunk 1 / nonce 0 values cannot be distinguished from old restart residue; legacy cleanup still restores Auto. To retain a deliberate Chunk 1 / nonce 0, select it again in the updated UI and save once. Old unmarked later-chunk or fixed-positive-nonce selections are retained. Do not delete Runs/Takes to update.

Sampling v6, Graph v4, Run Storage v3 and State/Session formats are unchanged. This patch does not force resume_safe, relax reuse checks, rewrite unsafe/v5 history or migrate workflows. Run Storage decides whether a prefix is compatible. Earlier accepted chunks and previous Takes remain protected. All 25 distributed JSON/ZIP assets retain their bytes.

## Verified scope

Full real-Core CPU gate: 1,908 passed / 2 skipped / 2 existing Inspector expected failures / zero unexpected failures; CUDA initialization attempts 0. Production frontend fixtures cover 84 scenarios including 22 new restoration cases. Real-Core CPU cache checks cover ordinary Full Run, automatic nonce 0 and fixed positive nonces.

Actual normal ComfyUI (Core 0.40.0, frontend 1.55.17): save a separate test workflow, reload the browser, allow real Run history to load, and verify Chunk 2 / nonce 5 and Chunk 1 / nonce 0 remain selected. The saved JSON includes the matching intent marker. This browser test is distinct from actual GPU prompts submitted through the normal Core API.

| New-Run GPU Queue | Result |
| --- | --- |
| Review / Auto / nonce 0 | Generate Chunk 1 |
| Separate Queue, same Review input | Reuse Chunk 1, generate Chunk 2 |
| Full Run / Chunk 2 / nonce 5 | Keep Chunk 1, regenerate Chunk 2 |
| Full Run / Chunk 2 / nonce 0 | Keep Chunk 1, create automatic variation 6 |
| Identical Full Run / Chunk 2 / nonce 0 again | Keep Chunk 1, create automatic variation 7 |

GPU: RTX 5060 Ti, PyTorch attention, Spectrum OFF, 512x512, Euler/simple, 8-step Turbo, two 5-second chunks, no First/Last/Reference inputs. Earlier Chunk 1 SHA-256 stayed identical; every newly generated Chunk 2 differed. The last two prompts, including output prefix, were exactly identical and the Sampler was absent from execution_cached. All manifests recorded Sampling v6 and resume_safe=true. All five video/audio outputs (first: 5 seconds; others: 10 seconds) fully decoded at 24fps.

Existing saved workflows and reachable archived Run/Take files retained their recorded hashes. Older output paths unavailable before this repair were not counted as reverified; no missing-data diagnosis is inferred. Other attention/Spectrum combinations were not newly GPU-tested for this patch. Subjective audiovisual quality, mobile performance, full default-workflow acceptance and the known Inspector reconfigure issue remain separate. Previous Issue #31 coverage: ISSUE31_SAMPLING_SIGNATURES.md.

## 日本語

明示したRegenerate FromとVariation Nonceを保存・再読込後も保持します。保存ON／Full Run／明示Chunk／Nonce 0では、毎QueueでRun Storageが継続か新Variationかを判断します。完了後の同一入力でも再生成し、前のChunkと既存Takeは保持します。固定の正Nonceと通常Full Runのキャッシュは維持します。

ComfyUI再起動とブラウザー再読込が必要です。旧markerなしChunk 1／Nonce 0は、更新後にChunk 1を選び直して一度保存してください。旧unsafe履歴は自動修復しません。既存WorkflowやRun／Takeの削除は不要です。

実画面でChunk 2／5とChunk 1／0の保存再読込保持、実GPUでChunk 1→2継続・Chunk 2再生成・同一Full Run入力2回の自動Nonce 6→7、元Chunk 1保持、動画5本全デコードを確認しました。今回のGPU範囲はPyTorch／Spectrum OFFです。Sampling v6の安全判定、既存配布Workflow、旧Takeを保護しています。
