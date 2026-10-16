# v3.9.8 — KJ Model Preview Override continuation

Fix saved-Take continuation after an explicitly audited KJ Preview Override retains preview images. The dedicated adapter separates reviewed transient frames from fixed settings and implementation identity, preserving cross-key/list wrapper execution order. A separate Queue can reuse Chunk 1 and generate only Chunk 2. Sampling v6 safety, existing Takes, public inputs and official workflow bytes are preserved.

**Limited Phase A support:** Preview Override VAE / Audio VAE disconnected, Tiny VAE `none`, Core NoPreviews/Auto/Latent2RGB, and only the exact provider/Core audit profile. KJNodes 1.5.2 alone is not sufficient; the audited local Preview Override source differs from upstream. Unknown or altered providers retain conservative non-reuse. See [the supported source hashes and update guide](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/blob/v3.9.8/docs/KJ_PREVIEW_OVERRIDE_V398.md).

Restart ComfyUI, refresh the browser and start a new Run. Do not delete old workflows or Takes. Earlier safe KJ identities may differ; unsafe/v5 history is not repaired or promoted. Non-KJ v6 signatures are unchanged.

CPU: 1,995 passed / 3 skipped / 2 existing Inspector expected failures; zero unexpected failures or CUDA initialization attempts. Dedicated real-provider tests: 48 passed, no skips. Four normal-runtime Core-API GPU Queues passed: PyTorch and Comfy Kitchen INT8 + audited local Spectrum, each saving Chunk 1 and continuing to Chunk 2 in a separate Queue with held previews. The KJ MODEL was cached on each second Queue, contracts stayed equal, and original Chunk 1 bytes were preserved. All four AV outputs fully decoded.

GPU scope: RTX 5060 Ti 16 GB, 512x512, 24fps, 8-step Turbo, 2x5-second chunks, Core Auto preview, no preview VAE. The initial GPU gate used candidate product bytes; the subsequent published-tag recheck is recorded below. No new browser Run-button, per-kernel return trace, subjective-quality or performance acceptance is claimed. The Inspector issue remains. Source/tag CI and exact GitHub/Registry archive checks run in publication; Registry scan approval and real Manager installation are separate.

## 日本語

監査済みKJ Model Preview Overrideで画像を保持した後、保存Takeを継続できない問題を局所修正しました。一時画像と固定設定を分離し、実装識別とラッパー順序、Sampling v6の安全判定を維持します。

対応は固定した監査プロファイルと、VAE／Audio VAE未接続・Tiny VAE none・Core NoPreviews／Auto／Latent2RGBに限定します。KJNodes 1.5.2全般を保証するものではなく、監査したローカルソースは公開upstreamと異なります。未対応構成は安全側で再利用不可を維持します。

更新後はComfyUIを再起動し、ブラウザーを再読込して新Runを作成してください。既存Take・Workflowは保持し、旧unsafe履歴を自動修復しません。CPU 1,995成功（専用48件を含む）、PyTorchおよびKitchen＋ローカルSpectrumの4 Queueで別QueueのChunk 1→2継続、元Chunk 1保持、動画4本の全デコードを確認。画質・速度・全KJ構成の合格は主張しません。Registryの検査承認と実Manager導入は別確認です。

## Post-release verification on the published v3.9.8 tag

### Published v3.9.8 GPU recheck — 2026-10-16: PASS

After restarting the normal ComfyUI installation with the published tag **`v3.9.8` / `58fbd855`**, all 464 installed release files matched the tag. The startup log confirmed 3.9.8, and new saved Sampling v6 contracts contained the KJ adapter and pinned audit-profile digest. Two brand-new Runs passed four Core-API GPU Queues:

| KJ Preview Override configuration | Separate-Queue Chunk 1 → 2 |
| --- | --- |
| Model Attention Backend: PyTorch, Spectrum OFF | **PASS — 1 reused / 1 generated** |
| Model Attention Backend: Comfy Kitchen INT8 + audited local Spectrum | **PASS — 1 reused / 1 generated** |

On both second Queues, the KJ MODEL stayed cached with preview images retained (**8 → 16**), while the Sampler executed. The contract/revision and original Chunk 1 latent hashes stayed unchanged; `resume_safe=true`. All four video/audio outputs fully decoded (5 seconds / 120 frames, then 10 seconds / 240 frames, 512×512 at 24fps). Existing workflows and Takes were preserved: 170 protected files, including 71 saved workflow files and 46 pre-existing Run/Take files, retained their hashes.

**Scope:** only the exact audited KJ/Core profile; the local KJ source differs from upstream, so KJNodes 1.5.2 alone is insufficient. Preview Override VAE / Audio VAE were disconnected, Tiny VAE was `none`, Core preview was Auto. GPU: RTX 5060 Ti 16 GB, 8-step Turbo, Euler/simple, 2×5-second chunks. Spectrum used the audited local offline-replay implementation, system-RAM history/archive and model-aware OFF. **Unverified:** browser Run-button/save-reload behavior, the reporter's exact complete graph, other KJ/Spectrum builds, SolAttn/preview VAE paths, per-kernel return tracing, subjective quality and speed/VRAM benchmarks. Retained PNGs were 32×32, not high-resolution preview-quality evidence. The known Inspector issue remains; old unsafe/v5 Takes are not repaired or promoted. [Issue #31 result](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/31#issuecomment-6209571261).

### 公開版v3.9.8のGPU再検証 — 2026-10-16：PASS

通常ComfyUIに公開タグ **`v3.9.8`／`58fbd855`** を反映して再起動し、公開版464ファイルとの一致、実ログの3.9.8読込、新しいSampling v6契約内のKJアダプターと固定監査プロファイルを確認しました。新Runを2つ使用した計4 Queueの結果です。

| KJ Preview Override併用構成 | 別QueueのChunk 1→2継続 |
| --- | --- |
| Model Attention Backend：PyTorch／Spectrum OFF | **PASS — 1再利用／1生成** |
| Model Attention Backend：Comfy Kitchen INT8＋監査済みローカルSpectrum | **PASS — 1再利用／1生成** |

両構成の2回目は画像を保持したKJ MODELをキャッシュ再利用（**8→16枚**）し、Samplerは実行。契約・revision・元Chunk 1 latentのSHA-256を維持し、`resume_safe=true`でした。映像・音声4本は全デコード成功（512×512／24fps、5秒120フレーム→10秒240フレーム）。保護対象170ファイル（保存Workflow 71件・既存Run／Take 46ファイルを含む）は全ハッシュ不変です。

**対応範囲：** 固定したKJ／Core監査プロファイルのみ。ローカルKJソースはupstreamと異なり、KJNodes 1.5.2全般の合格ではありません。Preview OverrideのVAE／Audio VAE未接続・Tiny VAE `none`・Core Auto、RTX 5060 Ti 16 GB、8-step Turbo／Euler/simple、2×5秒。Spectrumは監査済みローカル版のoffline replay、履歴・archiveはsystem RAM、model-aware OFFです。**未確認：** ブラウザーRunボタン／保存再読込、報告者の完全一致graph、別KJ／Spectrum版、SolAttn／preview VAE、カーネル単位の戻り値、主観画質・音質、速度・VRAM比較。保持PNGは32×32で、高解像度プレビュー品質の証明ではありません。既知Inspector問題は残り、旧unsafe／v5 Takeを自動修復・昇格しません。[Issue #31への結果返信](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/31#issuecomment-6209571261)。
