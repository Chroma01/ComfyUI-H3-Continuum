# v3.9.8 — KJ Model Preview Override continuation

Fix saved-Take continuation after an explicitly audited KJ Preview Override retains preview images. The dedicated adapter separates reviewed transient frames from fixed settings and implementation identity, preserving cross-key/list wrapper execution order. A separate Queue can reuse Chunk 1 and generate only Chunk 2. Sampling v6 safety, existing Takes, public inputs and official workflow bytes are preserved.

**Limited Phase A support:** Preview Override VAE / Audio VAE disconnected, Tiny VAE `none`, Core NoPreviews/Auto/Latent2RGB, and only the exact provider/Core audit profile. KJNodes 1.5.2 alone is not sufficient; the audited local Preview Override source differs from upstream. Unknown or altered providers retain conservative non-reuse. See [the supported source hashes and update guide](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/blob/v3.9.8/docs/KJ_PREVIEW_OVERRIDE_V398.md).

Restart ComfyUI, refresh the browser and start a new Run. Do not delete old workflows or Takes. Earlier safe KJ identities may differ; unsafe/v5 history is not repaired or promoted. Non-KJ v6 signatures are unchanged.

CPU: 1,995 passed / 3 skipped / 2 existing Inspector expected failures; zero unexpected failures or CUDA initialization attempts. Dedicated real-provider tests: 48 passed, no skips. Four normal-runtime Core-API GPU Queues passed: PyTorch and Comfy Kitchen INT8 + audited local Spectrum, each saving Chunk 1 and continuing to Chunk 2 in a separate Queue with held previews. The KJ MODEL was cached on each second Queue, contracts stayed equal, and original Chunk 1 bytes were preserved. All four AV outputs fully decoded.

GPU scope: RTX 5060 Ti 16 GB, 512x512, 24fps, 8-step Turbo, 2x5-second chunks, Core Auto preview, no preview VAE. Product repair bytes are identical to the accepted candidate; this is not a fresh GPU run on the published tag. No new browser Run-button, per-kernel return trace, subjective-quality or performance acceptance is claimed. The Inspector issue remains. Source/tag CI and exact GitHub/Registry archive checks run in publication; Registry scan approval and real Manager installation are separate.

## 日本語

監査済みKJ Model Preview Overrideで画像を保持した後、保存Takeを継続できない問題を局所修正しました。一時画像と固定設定を分離し、実装識別とラッパー順序、Sampling v6の安全判定を維持します。

対応は固定した監査プロファイルと、VAE／Audio VAE未接続・Tiny VAE none・Core NoPreviews／Auto／Latent2RGBに限定します。KJNodes 1.5.2全般を保証するものではなく、監査したローカルソースは公開upstreamと異なります。未対応構成は安全側で再利用不可を維持します。

更新後はComfyUIを再起動し、ブラウザーを再読込して新Runを作成してください。既存Take・Workflowは保持し、旧unsafe履歴を自動修復しません。CPU 1,995成功（専用48件を含む）、PyTorchおよびKitchen＋ローカルSpectrumの4 Queueで別QueueのChunk 1→2継続、元Chunk 1保持、動画4本の全デコードを確認。画質・速度・全KJ構成の合格は主張しません。Registryの検査承認と実Manager導入は別確認です。
