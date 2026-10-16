# ComfyUI-H3-Continuum 3.9.8 — V3.9

MiniMax H3の映像・音声をチャンクに分けて生成し、結果を確認しながら
一部分の再生成や、互換性のある保存Takeからの継続ができます。
**現在のWorkflowはV3.9です。V3.8X2も別のWorkflowとして保持しています。**

[v3.9.8本体ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/ComfyUI-H3-Continuum-v3.9.8.zip) ·
[Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.8) ·
[チェックサム](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/SHA256SUMS.txt) ·
[English](README.md)

## 基本操作を動画で見る

[H3 Continuum V3.9 — Chunks, Prompts & Reference Images](https://youtu.be/AKJxBXaiG6Q) — **12分26秒**、英語ナレーション・字幕・チャプター付き。

First Image、チャンク設定、Review・Takeの再試行、Timeline Prompt、Reference Imagesを説明しています。
画面写真と詳しい操作は[日本語の詳細ガイド](docs/USER_GUIDE_JA.md)を参照してください。

## インストール・更新

Continuumは`ComfyUI/custom_nodes`内に1つだけ配置してください。
モデル・外部カスタムノードは本体ZIPに含まれません。

### 固定バージョンのZIPを使う

1. 冒頭の**本体ZIP**を取得し、必要に応じてチェックサムを確認します。
2. パッケージフォルダーを`ComfyUI/custom_nodes`へ展開します。
   更新時は既存パッケージを置き換え、重複したコピーを残さないでください。
3. ComfyUIを再起動し、ブラウザーを**Ctrl+F5**で強制再読込します。
4. 下記のV3.9 Workflowを開き、導入したモデルと入力ファイルを選びます。

保存済みWorkflow、Run／Takeフォルダー、設定は保持してください。
**Workflow ZIPはグラフの配布物であり、カスタムノードのインストーラーではありません。**

### Git・ComfyUI-Managerを使う

Gitで新規導入する場合：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum.git
```

既存のGit導入を更新する場合：

```bash
cd ComfyUI/custom_nodes/ComfyUI-H3-Continuum
git pull --ff-only origin main
```

Managerで導入した場合は、そのコピーをManagerから更新してください。
更新後はComfyUIを再起動し、ブラウザーを再読込します。
Registry審査・Managerが選択する版・GitHub Releaseの状態は別です。
正確なv3.9.8を使う場合は、冒頭の固定版リンクを参照してください。

パッケージの宣言上の最低要件は**Python 3.10以降・ComfyUI 0.32.0以降**です。
この最低要件の宣言だけで、すべてのCore版でのGPU動作確認を意味するものではありません。

## 必要なモデル・拡張機能

重みは[Comfy-Org / MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)から別途取得します。
次の表は**保存されているV3.9テンプレートの選択値**です。配置先は`ComfyUI/`からの相対パスです。

| 用途 | ファイル・ダウンロード | 配置先 |
| --- | --- | --- |
| H3生成モデル | [minimax_h3_fl2va_pruned_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors) | `models/diffusion_models/` |
| テキストエンコーダー | [qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors) | `models/text_encoders/` |
| 動画VAE | [minimax_h3_video_vae_int8_convrot.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors) | `models/vae/` |
| 音声VAE | [minimax_h3_audio_vae_fp32.safetensors](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors) | `models/vae/` |

各Loaderで取得したファイルを選び、テキストエンコーダーのtypeは`minimax`にします。
保存済みの`minimax/`サブフォルダーが環境と異なる場合は、実際の配置先から選び直してください。
動画VAEの選択値はINT8版ですが、旧ダウンロード情報にFP16版が残っています。
実際に導入したVAEを選んでください。[別のモデル形式](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/main/diffusion_models)は生成用途とLoaderの対応に合わせて選択します。
量子化形式には対応するCore・GPUが必要であり、上表は全ハードウェアでの動作保証ではありません。

保持しているV3.8X2グラフでは、DasiwaMinimaxH3_dasiwaHybridV2_int8.safetensorsと
[FP16動画VAE](https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors)が選択されています。
このカスタムモデルは同梱されず、上表の配布元から取得するものでもありません。導入済みの互換H3モデルを選び直してください。

配布グラフ全体を使う場合は、次の外部ノードも必要です。

- [Spectrum](https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3)：任意の高速化機能。保存時は無効です。全バージョンでのTake再利用を保証しません。
- [KJNodes](https://github.com/kijai/ComfyUI-KJNodes)：テンプレートのH3 SageAttentionパッチを提供します。必要なAttention依存関係を導入するか、利用できないパッチを置換・Bypassしてください。
- [rgthree-comfy](https://github.com/rgthree/rgthree-comfy)：`Power Lora Loader (rgthree)`を提供します。

**Turboを使う場合のみ：** 用途に合う[LightX2V Turbo LoRA](https://huggingface.co/lightx2v/Minimax-h3-Turbo)を1つ選び、`models/loras/`へ配置します。
LoRAはすべて保存時に無効です。配布元のSampler・Steps指定に従ってください。
[ファイル一覧と設定の詳細](docs/USER_GUIDE.md#turbo-lora-and-spectrum-in-supplied-workflows)も参照できます。Continuumがこれらを自動導入することはありません。

## Workflowを選ぶ

| Workflow | ダウンロード | 用途 |
| --- | --- | --- |
| **V3.9** | [JSON](examples/workflows/MiniMax_H3_Continuum_V39.json) / [ZIP](examples/workflows/MiniMax_H3_Continuum_V39.zip) | 現行Samplerと固定Reference Imageスロット |
| **V3.8X2** | [JSON](examples/workflows/MiniMax_H3_Continuum_V38X2.json) / [統合ZIP](examples/workflows/MiniMax_H3_Continuum_V38X2.zip) | 既存Workflow用。統合ZIPにはV3.9も収録 |

ComfyUIの**Templates → ComfyUI-H3-Continuum**からも開けます。
V3.8X2のReference配線や保存履歴はV3.9へ自動変換されません。
元のグラフを保持し、新しい作業は専用のV3.9グラフで開始してください。
不足する外部ノードは導入・置換・削除してからQueueします。ComfyUI-Easy-Useは不要です。

V3.9テンプレートでは、自分の**First Image**を選んでください。
Reference Loader 1〜6はBypass、チャンク別割り当てはすべてOFFで保存されています。
Image 7〜9を使う場合はLoaderを追加・接続します。
[テンプレートの詳しい説明](docs/USER_GUIDE_JA.md#最初にv39とv38x2)。

## 最初の生成

長い動画を作る前に、短い2チャンクで確認してください。

1. H3モデル、テキストエンコーダー、Sampler、対応VAEを選びます。
2. `Sequence Prompt`を記入します。全チャンク共通なら`Prompt Format = Fixed`を使います。
3. 画像から作る場合は`Size Source = First Image`と解像度を選びます。
   初期値は**Draft — 0.30 MP**です。幅・高さを直接指定する場合は`Manual`にします。
4. `Chunks`を**2**、`Seconds per Chunk`を**5**にし、`Total Length`が**10秒**になることを確認します。
5. `Base Seed`を維持し、`Control After Generate`を`fixed`にします。
6. `Run`を`Review Each Chunk`、`Progress`を`On — Resume and Takes available`にします。
7. `Regenerate From = Auto`のまま`Ready to Queue`を読み、ComfyUI上端の**Run／実行ボタン**を押します。

`Chunks`は最終目標数であり、次のQueueで追加する数ではありません。
Reviewでは通常1単位ずつ生成するため、この例の最初の出力は**5秒**です。
Last ImageのTerminal Mergeでは、最後の2チャンクを1単位として扱う場合があります。

一括生成する場合は`Generate Full Video`を選びます。
保存Take・互換Resume・後からの再生成を使う場合はProgressをONにしてください。

## 確認・継続・再試行

Review操作を選ぶだけでは生成は始まりません。選択後にComfyUIの
**Run／実行ボタン（`Queue`）**を押してください。

| 操作 | 次のQueueで行うこと |
| --- | --- |
| `Use it and continue` | 採用済みチャンクを保持して、次のReview単位を生成 |
| `Try this chunk again` | 前のチャンクを保持して、確認中の単位を別Takeで再生成 |
| `Use it and finish the rest` | 採用済みの部分を保持して、残りをまとめて生成 |
| `Back to Settings` / `Return to Review` | 設定と確認画面の移動。生成開始・Take削除は行わない |
| `Use This Take` | 保存結果を採用。新しいSamplingは行わないがDecode・保存は実行され得る |
| `Continue From Here` | 選んだTakeまでを保持した分岐を作り、次の単位を生成 |

**2×5秒**の例では、Chunk 1を採用して継続すると、それを再利用してChunk 2を生成し、**10秒**の完成動画になります。
完了後に現在の単位をRetryすると、別のChunk 2 Takeを作ります。

継続時はモデル・LoRA・Seed・Prompt・入力素材・寸法・Sampling設定・継続設定・Run識別を維持します。
Seedを固定しただけで再利用が保証されるわけではありません。Statusと再利用数を確認してください。
完成動画を延ばす場合は条件を維持し、`Regenerate From = Auto`のまま最終目標の`Chunks`を増やしてQueueします。
[Review・Takeの詳細](docs/USER_GUIDE_JA.md#10秒を5秒ずつ確認しながら作る)。

## 指定チャンクから再生成する

1. 設定を開き、**Regenerate From = Chunk N**を選びます。
2. ProgressをONにし、前のチャンクの生成条件を維持します。
3. N以降をまとめて作るなら`Generate Full Video`、次の単位で確認するなら`Review Each Chunk`を選びます。
4. **Variation Nonce**を指定し、ComfyUIの実行ボタンを押します。
5. 通常の継続・Take操作へ戻る前に、`Regenerate From = Auto`へ戻します。

Nonce **0**は、再生成完了後の再実行で別Variationを自動選択します。
互換性のある中断処理では、同じVariationをResumeします。
正のNonceはVariationを固定します。同じ条件・同じ正数を繰り返しても別結果の要求にはなりません。
ReviewのRetryは、これとは別にVariationを管理します。

前の互換チャンク・以前のTakeは保持します。
後続は変更後の継続に従うため、Full RunのChunk 2指定は、目標数によってChunk 2以降をまとめて再生成します。
Terminal Mergeのpairは分割せず、チャンク内の任意フレームだけを変更することもできません。
[再生成・互換性の詳細](docs/REGENERATE_INTENT_V396.md)。

## Prompt・Reference Images

- **Fixed**は共通Prompt、**List**はチャンク別、**Timeline**は時間指定です。
- V3.9のReference Imagesは**Image 1〜9の固定スロット**を持ち、Samplerへ1本で接続します。
  `All chunks`は共通使用、`Per chunk`は画像とチャンクの交点を選択します。
- `@R1`は空きスロットに関係なくImage 1です。有効なReferenceだけをタグで参照してください。
  実際のPicture番号は物理groupごとに解決されます。
- First／Last Image、Reference Images、Reference Audio、Driving Audioは用途が異なります。
  Driving Audioは元の音声を保持し、Reference Audioは生成条件として使います。
- Reference単独を試す場合はFirst／Last ImageをOFF、サイズをManualにします。
  終端を結合するpairでは、両チャンクの有効なReferenceセットを揃えてください。
- 大きな入力画像は事前に縮小してください。条件付けのresizeだけでは元画像の読込RAMは減りません。
  割り当てを外した後も、映像の連続性により被写体が残る場合があります。

[Referenceガイド](docs/V39_REFERENCE_INLINE.md) ·
[Prompt例（英語）](docs/README_HISTORY.md#prompt-formats) ·
[V3.9用Promptスキル](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/tree/main/write-h3-v39-reference-prompts) ·
[Prompt・スキル配布](docs/USER_GUIDE_JA.md#プロンプトスキルのダウンロード)

## 保存・Decode・Second Pass

ProgressはRun／Takeを保存します。任意の**Decode Cache Helper**はデコード結果のキャッシュであり、保存履歴とは別です。
Finalizeで結合し、後段のCoreノードで動画を作成・保存します。

一時保存先は**設定 → H3Continuum → Storage → 一時ストレージを管理**で指定します。
ComfyUIサーバー側のフォルダーで、FinalizeとDecode Cacheに適用します。
Run／Takeや完成動画は移動しません。変更・削除は実行中／待機中Queueが空のときに行ってください。
同じ物理ドライブ内のフォルダー移動だけでは、書き込みを別機器へ逃がせません。
[保存方式・削除・制約](docs/TEMPORARY_STORAGE_JA.md)。

**Second Pass**は外部のRefinement・拡大処理へ渡す任意の機能です。
チャンク継続や通常のReview Retryとは別で、V3.8X2標準WorkflowにHi-Res Fixは不要です。
V3.8ではReview途中のpartial sequenceに対応しません。V3.9は検証済みの実出力groupの条件を継承できます。
[外部連携の仕様](docs/V38_OPEN_INTEGRATION_CONTRACT.md)。

## 互換性・v3.9.8の対応範囲

| 対象 | 対応条件 |
| --- | --- |
| 保存履歴 | 既存Takeは読取可能です。旧v5・unsafe履歴をSampling v6の再利用可能履歴へ自動修復・昇格しません。必要に応じて新Runを使います。 |
| 未知のMODEL wrapper | 新規生成は可能です。再利用には生成契約の完全な観測と一致が必要で、名前・版だけで許可しません。 |
| Attention／Spectrum | Core PyTorch／Kitchenと、公式v0.2.29を含む指定Spectrum実装の監査済みプロファイルに対応します。[厳密な範囲](docs/ISSUE31_SAMPLING_SIGNATURES.md)。 |
| KJ Model Preview Override | 固定したKJ／Core実装のみ。**VAE／Audio VAE未接続・Tiny VAE `none`**、Core NoPreviews／Auto／Latent2RGB。監査済みローカルソースはupstreamと異なり、KJNodes 1.5.2全般の合格ではありません。[対応ハッシュ](docs/KJ_PREVIEW_OVERRIDE_V398.md)。 |

公開版**v3.9.8**は、新Run・別QueueでのChunk 1→2継続を
**PyTorch＋KJ**と**Comfy Kitchen INT8＋監査済みローカルSpectrum＋KJ**で確認しています。
プレビュー画像を保持し、元Chunk 1と契約を維持、映像・音声4本は全デコード成功でした。
条件はRTX 5060 Ti 16 GB、512×512、24fps、2×5秒、8-step Turbo、Core API経由です。
別のKJ／Spectrum実装やPreview VAE接続を合格とするものではありません。
[詳しい条件・未確認範囲](docs/RELEASE_NOTES_V398.md)。

## 既知の問題・制約

- **Reference Plan Inspector：** Samplerの再configure後に古い表示が残る問題は未修正です。
  2件の期待失敗は修正済みを意味しません。
- **モバイル：** UI処理の削減は確認していますが、フリーズ解消は未確認です。
- **メモリ：** 大きなReference画像9枚や長尺の最終DecodeでVRAM／RAM不足になる場合があります。
  Disk-backed Finalizeでも、他ノードの大きなメモリ確保は防げません。
- **Refinement：** 高倍率のLatent Resizeでアーティファクトが残る場合があります。
  長いHi-Res／Hybrid条件と二重輪郭には制約・調査中の事項があります（[Issue #27](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/27)）。
- **連続性：** 完全な同一性・動作・口の同期・元動画の全フレーム再現は保証しません。長尺には既知の品質制約もあります。
- **検証範囲：** ブラウザー実行／保存再読込、報告者の完全一致グラフ、他実装、主観画質・音質、速度・VRAM比較は、今回の限定GPU再検証で確立していません。

## 詳細資料

| 内容 | 資料 |
| --- | --- |
| 導入・画像・詳細操作 | [日本語の詳細ガイド](docs/USER_GUIDE_JA.md) / [英語の図解ガイド](docs/USER_GUIDE.md) |
| 現行Reference Images | [V3.9 Referenceガイド](docs/V39_REFERENCE_INLINE.md) |
| V3.8X2からの更新 | [移行・保持する仕様](docs/V38_RELEASE_AND_MIGRATION.md) |
| 更新履歴・旧版画像・実装説明 | [日本語の履歴資料](docs/README_HISTORY_JA.md) / [CHANGELOG](CHANGELOG.md) |
| 最新版の検証記録 | [v3.9.8詳細](docs/RELEASE_NOTES_V398.md) / [配布検証](PACKAGE_VALIDATION.txt) |
| 不具合報告 | [GitHub Issues](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues) — Workflow、Status、`auto-resume disabled:`の理由を添えてください |

過去のRelease・タグは保持しています。mainの文書更新で、公開済みv3.9.8のタグや配布物を置き換えることはありません。
この整理は文書のみであり、公開ノード・公式Workflow JSON／ZIP・Sampling v6・既存Run／Takeは変更しません。

## ライセンス

[MIT](LICENSE)。外部コンポーネントの[ライセンス・表記](THIRD_PARTY_NOTICES.md)も参照してください。
