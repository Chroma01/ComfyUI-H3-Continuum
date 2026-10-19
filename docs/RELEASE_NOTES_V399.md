# 3.9.9 — Public KJ Preview Override and Review continuation

Some new Runs were marked **Sampling v6 read-only** when using the upstream KJ
Model Preview Override implementation, even though generation completed. This
release adds a separately audited upstream profile and explains saved reuse
failures in Review and Render History. The original supported local profile and
unaffected generation identities are retained; the safety checks are not relaxed.

## Update

Update Continuum, restart ComfyUI and hard-refresh the browser. Existing workflows
need no rewiring. Keep all saved Runs/Takes. After correcting an unsupported
configuration, start a **new Run**: old unsafe/v5 Takes remain readable and are
not automatically promoted to reusable history.

Supported upstream KJ commit: `17195fcfa8a05f601b766a0f09c9733284f47416`.
On **Model Preview Override**, leave its optional VAE and Audio VAE disconnected,
set Tiny VAE to `none`, and use Core NoPreviews, Auto or Latent2RGB. Keep the
normal generation VAEs connected. This is not blanket support for every KJ/Core
version or unknown wrapper. See [the exact profiles and recovery steps](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/blob/v3.9.9/docs/KJ_PREVIEW_OVERRIDE_V398.md).

## Validation

- CPU: **2,075 passed / 2 skipped / 2 known Inspector expected failures**, zero
  unexpected failures. The 90 production-JS cases and eight actual Run Storage
  vectors passed; these overlap the pytest total. Offline twelve-node,
  PackedLayout and Fixed 3x5s checks passed with zero recorded CPU CUDA
  initialization attempts.
- Upstream KJ GPU: two separate Queues, **512x512 / 24fps / 2 x 5 seconds**,
  FL2VA INT8 convrot, Qwen3VL NVFP4 AWQ, 8-step Turbo/Euler/simple and explicit
  PyTorch attention. Chunk 1 paused for Review; the next Queue reused it and
  generated only Chunk 2. The same cached KJ wrapper held eight real preview
  images before Continue, while MODEL and sampling signatures remained equal.
- Browser on normal ComfyUI: with the pre-existing audited local KJ profile,
  restart and frontend reload succeeded. **Use This Take** and **Continue From
  Here** were visibly enabled. Continue From Here followed by the browser Run
  button completed Chunk 2: **one reused / one generated**. Core execution times
  were approximately 100 and 92 seconds, including decode/save; they are not a
  speed comparison. Opening Render History involved one manual click; the
  subsequent Continue selection and Run submission were automated browser actions.
- Both GPU pairs preserved the original Chunk 1 raw SHA-256, original Take and
  correct parent link. All four 5s/10s video/audio outputs fully decoded. The
  upstream GPU pair also passed saved-latent finite-value checks. No execution
  errors or OOM occurred. The observed upstream system VRAM maximum was 15,446
  MiB at roughly six-second intervals, not an instantaneous per-process peak.
- All 21 existing workflow JSON/ZIP files remain byte-identical. Existing user
  Take/workflow files were preserved; there is no storage or schema migration.

These are targeted continuation/Review checks on Core 0.42.1, frontend 1.55.18,
Python 3.13.12, torch 2.14.1+cu130 and RTX 5060 Ti 16GB. Full CPU validation also
uses real Core/provider imports. They do not establish visual/audio quality,
long-video quality, all accelerators, all KJ versions, or save/reload acceptance
of every shipped workflow. The separate Turbo Sample already present on main is
included unchanged; its six-step/4-step-LoRA pairing has no new GPU acceptance.

## 日本語

公開KJ Preview Overrideを接続した新規Runまで「v6 read-only」になる対応漏れを修正し、
再利用不可のTakeには保存時の理由と対処法を表示します。安全判定は緩めていません。

更新後はComfyUIを再起動し、ブラウザーを強制再読込してください。既存Workflowの配線変更や
Run／Take削除は不要です。旧unsafe／v5 Takeは保持されますが、自動的に再利用可能には
なりません。設定修正後は新Runで開始してください。Preview Override側の任意VAE／Audio VAEは
未接続、Tiny VAEはnoneが条件です。通常の生成用VAEは接続したまま使用します。

CPU 2,075成功、公開KJでの実GPU継続、既設KJを維持した実ブラウザーでのボタン有効化と
Continue From Here→Run→Chunk 2完了を確認しました。両GPU構成でChunk 1を保持し、
1再利用・1新規生成、Takeの親子関係、映像・音声全デコードを確認しています。
対象修正の検証結果であり、全KJ構成や画質・長時間品質への包括的な合格ではありません。
