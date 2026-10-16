# H3 Continuum — 日本語の更新履歴・実装資料

[現在の日本語README](../README_JA.md) · [日本語の詳細ガイド](USER_GUIDE_JA.md) · [CHANGELOG](../CHANGELOG.md)

正本`84899c1`（パッケージ3.9.8）の日本語READMEにあった更新説明・旧版画像・検証記録を保持しています。
「現行」「main上」などの表現、古い導入コマンド、版ごとの受入結果は当時の文脈です。
現在の導入案内や、未検証の条件を含む包括的な合格として読み替えないでください。
最新版の入手先と対応範囲は、日本語READMEを参照してください。

<!-- Preserved README sections begin. -->


**最新版パッケージは3.9.8です。** 固定版のGitHub配布は下表を参照してください。Registryの公開状態は別に確認します。

| バージョン | Release | カスタムノード本体ZIP | SHA-256チェックサム |
| --- | --- | --- | --- |
| 3.9.8 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.8) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/ComfyUI-H3-Continuum-v3.9.8.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.8/SHA256SUMS.txt) |
| 3.9.7 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.7) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.7/ComfyUI-H3-Continuum-v3.9.7.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.7/SHA256SUMS.txt) |
| 3.9.6 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.6) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.6/ComfyUI-H3-Continuum-v3.9.6.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.6/SHA256SUMS.txt) |
| 3.9.5 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.5) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.5/ComfyUI-H3-Continuum-v3.9.5.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.5/SHA256SUMS.txt) |
| 3.9.4 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.4) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.4/ComfyUI-H3-Continuum-v3.9.4.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.4/SHA256SUMS.txt) |
| 3.9.3 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.3) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.3/ComfyUI-H3-Continuum-v3.9.3.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.3/SHA256SUMS.txt) |
| 3.9.2 | [Release](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/tag/v3.9.2) | [ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.2/ComfyUI-H3-Continuum-v3.9.2.zip) | [SHA256SUMS.txt](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases/download/v3.9.2/SHA256SUMS.txt) |

## 3.9.8 — KJ Model Preview Overrideの継続修正

監査済みKJ Model Preview Overrideでは、プレビュー画像を保持しても新Runの保存署名を変えず、別QueueでChunk 1を再利用してChunk 2だけ生成できます。対応は固定したKJソース・Core helperと、**VAE／Audio VAE未接続・Tiny VAE `none`**、Core NoPreviews／Auto／Latent2RGBに限定します。KJNodes 1.5.2全般への対応ではありません。更新後はComfyUIを再起動し、ブラウザーを再読込して新Runを作成してください。旧Take・Workflowの削除は不要です。[対応条件・監査ハッシュ・検証範囲](KJ_PREVIEW_OVERRIDE_V398.md)を参照してください。

### 公開版v3.9.8のGPU再検証 — 2026-10-16：PASS

通常ComfyUIに公開タグ **`v3.9.8`／`58fbd855`** を反映して再起動し、公開版464ファイルとの一致、実ログの3.9.8読込、新しいSampling v6契約内のKJアダプターと固定監査プロファイルを確認しました。新Runを2つ使用した計4 Queueの結果です。

| KJ Preview Override併用構成 | 別QueueのChunk 1→2継続 |
| --- | --- |
| Model Attention Backend：PyTorch／Spectrum OFF | **PASS — 1再利用／1生成** |
| Model Attention Backend：Comfy Kitchen INT8＋監査済みローカルSpectrum | **PASS — 1再利用／1生成** |

両構成の2回目は画像を保持したKJ MODELをキャッシュ再利用（**8→16枚**）し、Samplerは実行。契約・revision・元Chunk 1 latentのSHA-256を維持し、`resume_safe=true`でした。映像・音声4本は全デコード成功（512×512／24fps、5秒120フレーム→10秒240フレーム）。保護対象170ファイル（保存Workflow 71件・既存Run／Take 46ファイルを含む）は全ハッシュ不変です。

**対応範囲：** 固定したKJ／Core監査プロファイルのみ。ローカルKJソースはupstreamと異なり、KJNodes 1.5.2全般の合格ではありません。Preview OverrideのVAE／Audio VAE未接続・Tiny VAE `none`・Core Auto、RTX 5060 Ti 16 GB、8-step Turbo／Euler/simple、2×5秒。Spectrumは監査済みローカル版のoffline replay、履歴・archiveはsystem RAM、model-aware OFFです。**未確認：** ブラウザーRunボタン／保存再読込、報告者の完全一致graph、別KJ／Spectrum版、SolAttn／preview VAE、カーネル単位の戻り値、主観画質・音質、速度・VRAM比較。保持PNGは32×32で、高解像度プレビュー品質の証明ではありません。既知Inspector問題は残り、旧unsafe／v5 Takeを自動修復・昇格しません。[Issue #31への結果返信](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/31#issuecomment-6209571261)。

## 3.9.7 — 外部入力接続時の再生成キャッシュ修正

ChunksやVariation Nonceを外部ノードから接続した際に、明示したFull Run再生成がCoreのキャッシュで省略される問題を修正しました。前の採用済みChunk、既存Take、公開入力、公式Workflowは維持します。更新後はComfyUIを再起動し、ブラウザーを再読込してください。Workflowの変更や履歴の削除は不要です。 [Release notes](RELEASE_NOTES_V397.md).

**公開版3.9.7でのGPU再検証（2026-10-15）：PASS。** 公開タグ（`18df80d`）で再起動後、外部Core INTからChunks=2・Nonce=0を入力し、完全に同一のプロンプトでChunk 2を2回再生成しました。自動Nonceは**1→2**へ進み、両回ともChunk 1を再利用してChunk 2だけを生成。以前のTake・raw latentも保持しました。基準生成を含む動画3本は240フレーム・映像／音声各10秒で全デコード成功。既存Workflow 60件・設定1件・Run／Take 30ファイル・公開版459ファイルのハッシュは不変です。条件はRTX 5060 Ti 16 GB、512×512、24fps、2×5秒、8-step Turbo、PyTorch attention／Spectrum OFF、Core API経由。CUDA／OOM／実行エラーは確認されず、ブラウザー・主観画質・他アクセラレーターの受入範囲は拡張していません。

元の[3.9.2 Source ZIP](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/archive/refs/tags/v3.9.2.zip)は従来のタグから取得できます。本体ZIPと公式Workflow ZIPは別の配布物です。

## 3.9.6 — 再生成指定・Nonce保持と自動Variationの再実行

V3.8／V3.9の**Regenerate From・Variation Nonceを保存・再読込後も保持**します。保存ONで**Full Run＋明示Chunk＋Nonce 0**を指定すると、QueueごとにRun Storageが処理し、完了後の再実行で新Variationを作成できます。前のChunkと既存Takeは保持します。更新後はComfyUIを再起動し、ブラウザーを再読込してください。旧markerなしChunk 1／Nonce 0は、Chunk 1を選び直して一度保存してください。[操作・互換性・検証範囲](REGENERATE_INTENT_V396.md)を参照してください。

## 3.9.5 — Issue #31：Attention／Spectrumの保存Take継続

CoreのModel Attention Backend（PyTorch／Comfy Kitchen INT8）と監査済みSpectrum Bindingを正確に識別し、新しいRunのReview Each Chunk継続を可能にします。公式Spectrum v0.2.29も専用プロファイルで対応します。以前のunsafe履歴は保持し、再利用可能へ自動変換しません。更新後は新しいRunで生成してください。公開ノード・Workflow・Sampling v6は維持します。[対応実装・更新手順・検証範囲](ISSUE31_SAMPLING_SIGNATURES.md)を参照してください。

## 3.9.4 — Registry配布の梱包修正（2026-10-14）

Manifestに記載したReview復元ガイドを収録し、配布対象外のプロンプト作成資料を除外します。公開前に実際のRegistry ZIPを作り、全収録ファイル・CRC・Manifestの全ハッシュを照合します。生成動作・12公開ノード・公式Workflow・保存済みRun／Takeは変更しません。3.9.3と3.9.2のGitHub Releaseは保持します。

## 3.9.3 — 一時ストレージの保存先設定（2026-10-13）

未圧縮フレームなどの一時データを、指定したストレージへ保存できるようになりました。**設定 → H3Continuum → Storage → 一時ストレージを管理**を開き、**ComfyUIサーバー側**の絶対パスを入力するかストレージ候補を選択して、検証・保存してください。空欄なら従来の保存先を使用します。ワークフローの変更は不要で、V3.9ノードと3.9.1／3.9.2のワークフローを引き続き使用できます。

- **FinalizeとDecode Cache Helperの両方**が対象です。指定先の`h3-continuum-scratch`専用領域へ保存します。Run／Takeや完成動画の保存先は別です。
- 現在・以前の保存先、一時ファイル量、空き容量、使用中／削除可能な容量を表示します。**未使用の一時ファイルを削除**は、参照中の出力・Tensorのview・生存プロセス・所有者不明のファイルを保護します。キャッシュ削除後は再デコード・再書き込みが必要になる場合があります。
- 保存・削除は実行中と待機中のQueueが空のときに行います。新しいファイルから保存先を切り替え、既存出力は元の場所で保持します。指定先が使えない場合、元のSSDへ黙って戻しません。マルチユーザー運用では共有保存先のUIは閲覧のみです。
- 使用方式は既存ノードで選びます。**Finalize：Auto／RAM／Disk-backed、Decode Cache Helper：Auto／RAM／Off**。Autoの4 GiB境界とRAM安全余裕は維持します。手動RAMは確保前に空きメモリを、手動Disk-backedは空き容量を確認します。ただし、実行中のメモリ・容量変動やドライブ切断まで防ぐ保証はありません。VRAMを保存領域にする機能は追加していません。

**保存先変更は書き込み先を変える機能で、総書き込み量を減らすものではありません。** 物理ストレージが1台なら、同じ機器の別フォルダー・別パーティションへ移しても書き込みを逃がせません。別のSSDは速度を保ちやすく、HDDも使用できますがDecode・結合・保存が遅くなる場合があります。十分なCPU RAMがあればRAM方式で一時書き込みを避けられますが、余裕がなければページファイルへの書き込みやOOMが起こり得ます。CacheをOffにするだけではFinalizeのDisk-backedを無効にしません。容量表示は論理ファイルサイズであり、物理占有量やSSDの累計書き込み量ではありません。対応先はローカルファイルシステムで、ネットワーク共有は正式対応外です。

更新時はカスタムノードを更新し、ComfyUIを再起動してブラウザーを強制再読込してください。その後の保存先設定の変更には再起動は不要です。空欄時はFinalizeがComfyUIのtemp、Decode Cacheが既存の`H3_DECODE_CACHE_TEMP_DIR`指定またはOSのtempを使います。フォルダーを指定した場合、その指定がキャッシュ用環境変数より優先します。

映像のdtype、動画・音声の結合計算、生成条件の識別は維持します。[実装仕様](TEMPORARY_STORAGE_JA.md)と[検証記録](../PACKAGE_VALIDATION.txt)も参照してください。設定画面のスクリーンショットは[英語README](../README.md)の冒頭にあります。Releaseの公開状態は上表を参照してください。Registry公開は別に確認します。

画面にHTTP 404が出る場合は、ComfyUI起動ログを確認してください。旧プロセスが同じアドレス・ポートを占有していると、更新後の起動が失敗し、新しい画面だけが表示される場合があります。残っている旧環境を終了するか別のポートを選んで、新しいComfyUIを起動してください。**Refresh（更新）**は保存先の状態を再取得するボタンで、ComfyUIの再起動ではありません。取得失敗時はHTTP結果と対応方法を表示し、状態を取得できるまで保存・削除を無効にします。

## 3.9.2 — Issue #30 Frontend hotfix（2026-10-13）

ReviewとReference Imagesの不要なUI処理を削減します。

- Review比較基準がない場合、上流設定snapshotの作成を省略。
- Reference選択時のSampler通知を1回へ整理。native値の即時更新と元widget callbackを維持。
- Referenceノードの目標寸法と実寸が同じ場合、不要なサイズ変更を省略。

比較基準がある場合の監視と、Take／Queue時の最新設定確認を維持します。Sampling、保存済みRun／Take、公開Node ID、公式Workflowのbytesは変更しません。引き続きV3.9ノードを使用してください。

Frontend修正で**CPU／JavaScript回帰1703件成功・2件スキップ**、独立したInspector再configure問題の**2条件を期待失敗として記録**しました。Coreのオフライン登録・計画確認と隔離Chromium検証も通過しています。このパッケージの実ComfyUIブラウザー確認は[PACKAGE_VALIDATION.txt](../PACKAGE_VALIDATION.txt)に記録します。モバイルでのフリーズ解消は未確認です。Reference表の再構築と、比較基準がある場合のReview走査は残ります。今回のhotfixで新たなGPU生成は行っていません。

更新後は**ブラウザーを強制再読込（Ctrl+F5）**してください。表示するパッケージ番号も更新する場合は、通常の手順でComfyUIを再起動してください。3.9.1のRun／Takeは、このUI修正のために移行する必要はありません。固定版は[GitHub Releases](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases)を参照してください。Registry公開は別作業です。

## 3.9.1で変わった点（2026-10-04）

Second Pass、Takeの再利用、Review音声に関するバグを修正しました。

- **Second Pass**：音声のみ／複合キーフレームを保持し、途中Reviewや中間Chunk単独でも、その出力区間のconditioningとReference割当を照合して引き継ぎます。
- **Takeの再利用**：Samplerのclosure、MODELのCFG／wrapperも互換性判定に含め、異なる生成設定のTakeを誤って再利用しないようにしました。
- **ReviewのDriving Audio**：物理groupの自然時間に合わせて元PCMを1回だけ切り出します。Exact ON/OFFで開始位置を揃えます。
- **音声resample**：ComfyUI Core標準APIを優先し、古いCoreでは従来方式へ戻します。同じVAE内部の重みを直接変更する場合のReference Encode Cacheの制約も下記に明記しました。

**3.9.0から更新する場合**：更新後にComfyUIを再起動し、ブラウザーも更新してください。旧v5 Takeと履歴は読めて、削除されませんが、新しいv6生成の前半として再利用できません。新規Full Video、または **Start again from Chunk 1** で開始してください。公開Node ID・widget順・公式Workflowは維持し、引き続き **V3.9ノード** を使います。

修正済みコードは **CPU 1,696成功・1スキップ**、対象を絞ったReview Second PassのGPU検証、生成／Take再利用の統合GPU検証に合格しています。ブラウザー受入は未完了です。任意のLATENT拡大で出る二重輪郭は別課題の [Issue #27](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/issues/27) として管理し、今回の修正の必須Gateには含めません。今回もmainソースの更新で、GitHub Release／Registry公開ではありません。

![H3 Continuum V3.9：固定の参照画像番号、チャンク別割り当て、Samplerへの1本の接続](images/v39/v39-feature-summary.png)

*現在の`main`はV3.9です。Image 1～9の固定番号、チャンク別のReference選択、V3.9 Samplerへの1本の接続が新しい操作です。*

## 3.9.1の修正詳細

Second Passで音声のみのキーフレームを保持し、複合キーフレームでは映像だけを空間適応します。ReviewのDriving Audioは、区間選択前の物理decode groupの自然時間から元PCMを切り出します。Exact ON/OFFの開始位置は共通です。完全に空のReview音声だけは選択映像の尺に合う無音を補い、部分的に短い音声はExact OFFで引き延ばしません。

新しい生成はSampling Contract v6／Graph Contract v4を使用します。Samplerのコード・closureとMODELのCFG／wrapper等の設定も再利用判定へ含めます。旧v5のTake・raw・生成履歴は読めますが、v6生成へ継ぎ足せません。新規Full Video、またはReviewの「Start again from Chunk 1」で新しいrevisionを作成してください。旧Takeは残ります。署名を観測できない外部設定でも新規生成は可能ですが、自動再利用は無効になります。明示した不適合TakeやRetryを別Takeへ置き換えません。

Reference／DrivingのresampleはCore標準APIを優先し、そのAPIがない旧Coreだけ従来のTorchAudioを使います。最終出力へ渡す元PCMの波形とsample rateは保持します。

**Reference Encode Cacheの制約**：同じVAEオブジェクトの内部重みを直接書き換えた場合、その変更を自動検知しません。変更後は`v3.ref_encode_cache.clear_ref_encode_cache()`を呼ぶか、新しいVAEオブジェクトへ再ロードしてください。通常の同一VAE・同一入力ではcache HITを維持します。Decode Cache Helperのresetは別のcacheを対象とし、Reference Encode Cacheを消しません。

この修正はV3.9内の変更です。公開Node ID・socket・widget順、公式Workflow、Run Storage v3、State／Session形式を維持し、LoRA Planは追加しません。CPU検証と実ブラウザー・GPU受入は別です。

V3.9では、Second Passへ渡す条件を実際のReview出力区間へ対応させます。途中までの出力や中間Chunk単独でも、条件の照合に成功すれば、その区間自身のconditioningとReference割当を継承します。全体の完了状態や保存済みTakeは変更しません。条件が不足・不一致の場合は、従来の診断付きprompt-only fallbackを維持します。

修正済みランタイムは**CPU 1696成功・1スキップ**、**512×512・24fpsのGPU 3ケース**（途中2区間、Chunk 2単独、完了済み3区間の再利用）で合格しました。全区間の条件継承を確認し、保存FLACと元PCMの対応区間は完全一致、既存Takeとrawファイルも保持しています。合格対象は修正対象の動作です。ブラウザー受入は未完了で、任意のLATENT拡大時の二重輪郭はIssue #27で別途調査します。過去のV3.8 Release／tagはそのまま利用できます。

## V3.9の基本操作を動画で見る

[H3 Continuum V3.9 — Getting Started: Chunks, Prompts & Reference Images](https://youtu.be/AKJxBXaiG6Q)（12分26秒）

First Imageの基本設定、チャンクの設定、Review／Takeでの再試行、Timeline形式のプロンプト、Reference Imagesの使い方を紹介します。英語のナレーションと字幕、7つのチャプターがあり、バージョンを明記したUIの静止画と実際の生成例で説明します。

![公開当時のH3 Continuum V3.8X2機能紹介画像](images/v39/v38x2-feature-summary-historical.png)

*V3.8X2の画像も比較用に残しています。画像内の「CURRENT MAIN」は作成当時の表記で、現在の`main`はV3.9です。V3.8 SamplerとV3.8X2 Workflowは利用できますが、Reference配線はV3.9へ自動変換されません。*

## main更新：外部INTによるWidth／Height入力の修正（2026-10-01）

V3.8／V3.9のWidth／Height入力と表示コントロールの対応を修正しました。外部INTの接続位置をWorkflow保存・再読込やタブ切替後も維持します。接続中の欄は編集不可になり、表示する数値は保存済みのManual予備値です。上流ノードが実行時に出す値を推測して表示するものではありません。接続を外すと手動編集に戻ります。

Coreの **Int** ノードから正確な幅・高さを指定する場合は、**Size Source = Manual**にしてWidth／HeightのINT入力へ接続してください。**First Image**は引き続き画像とResolution設定からサイズを決めます。INTを接続しても優先順位やSize Sourceは自動で変わりません。有効なFirst Imageがない場合は従来のManualフォールバックを使います。寸法検証、Backend入力順序・初期値は変更していません。

確認済み：**全CPU試験1569 PASS／1 skipped**（新Frontend試験22/22・既存Review試験60/60を含む）、両バージョンのChrome保存・再読込とタブ5往復。外部INTを使ったV3.9のGPUテスト1回では、**480×640・24fps・96フレーム・映像／音声とも4秒**を正確に出力しました。20ステップ、全体**107.3秒**で、保存動画の全フレームを正常にデコードできました。短い単一条件の確認であり、長時間継続や全モデルでの受入確認ではありません。Sampling、Run Storage、先行するReview／キャッシュ修正、公式Workflow JSON／ZIP、過去Releaseは変更していません。

Continuumを`main`から更新し、**ブラウザーをCtrl+F5で強制更新**してください。このJavaScript修正だけならComfyUI本体の再起動は不要です。同時にPython修正や新ノード定義も更新された場合は通常どおり再起動してください。今回もmainのソース修正で、新Release／Registry公開ではありません。

## main更新：V3.9の条件付け準備の速度修正（2026-10-01）

**Prompt Format = Fixedかつ有効なReference Imagesがない場合**に、V3.9で余分なプロンプト条件付けの準備が繰り返される経路を修正しました。入力が同じ場合に既存の上限付きconditioningキャッシュを再利用します。First Imageは利用できます。List／Timeline、有効なReference Images、Reference Audio、Timeline Video、終端ペアのgroupは従来の経路を維持します。Decode Cache Helperとは別の修正で、Samplingは省略しません。

検証した`2 × 5秒`・480×640・First Imageの条件では、group準備が約**10.76秒から0.013秒**へ短縮しました。修正後の同セッション比較（warm-up後、各版3回）では、全体時間の中央値は**V3.8が273.58秒、V3.9が273.78秒**で測定範囲も重なり、以前の約6％差は見られなくなりました。全Workflow／モデル／GPUでの解決や、GPU演算そのものの高速化を確認したという意味ではありません。

Continuumを`main`から更新し、Python修正を読み込むため**ComfyUIを完全に再起動**してください。確認済み：**CPU 1558 PASS／1 skipped、GPU生成8回すべて成功**（ComfyUI 0.38.0／RTX 5060 Ti 16 GB）。Seed、チャンク／フレーム契約、Run Storage、V3.8X2／V3.9公式Workflow・ZIP、過去Releaseは変更していません。今回もmainのソース修正で、新Release／Registry公開ではありません。

## main更新：Review表示の復元修正（2026-10-01）

別のWorkflowタブへ切り替えて戻ると、保存済みTakeが残っていてもReview操作が消える問題を修正しました。Workflowの復元完了後に履歴を取得し、古い画面の非同期結果は反映しません。実際に生成設定を変えた場合のReview／Take適用ガードは維持し、元の設定に戻すと操作が復帰します。

カスタムノードを`main`から更新後、ブラウザーを更新して新しいJavaScriptを読み込んでください。確認済み：Frontend回帰60/60、関連CPU試験108件、Chromeのタブ5往復とBase Seed変更／復元。Take管理データは不変です。Sampling、Run Storage契約、V3.8X2／V3.9のWorkflowファイルと過去Releaseは変更していません。この修正のGPU継続生成は未検証です。[詳細と検証範囲](REVIEW_RESTORATION_REPAIR.md)。

## アーカイブされた実装・受入記録（V3.8現行ガイドではありません）

以下は一時的にsource historyとして残る旧リリース記録です。V3.8の標準経路・公開範囲・推奨配線を示すものではありません。旧WorkflowにはMigration Policyと対応するhistorical Release/tagを使用してください。

### V3.7 高解像度Refinement基盤

V3.7では`H3 Continuum Sampler V3.7`を追加し、解像度を変更するSecond Passに必要な2つの基盤を完成させました。V3.6のProduction初期値と既存SIGMAS socketは変更していません。

### 解像度変更後もConditioningを再構築

Conditioning Adapterは、First／Last Image、Continuation context、Still Image Guideの元画像をtarget latent geometryに合わせて再構築します。Physical group ownership、Long Terminal Merge、Core側のPackedLayout／RoPE再構築、First Pass Audioのpassthroughは維持します。704×704と1152×1152のCorrectness GateはPASSしていますが、大きなcanvasほどmemory使用量と処理時間は増えます。

### RefineScheduleでRefinement範囲を明示

内部のversioned contractである`RefineSchedule`は、`External`、`Full`、`Tail`、`Partial`に対応します。`External`は入力SIGMAS tensorをそのまま維持し、`Tail`と`Partial`は同じsource scheduleから範囲を正確に切り出します。内部Tail 6 Gateでは、6 evaluationのsuffix再現とdecoded Audio PCMのbit-exact passthroughを確認しました。現時点では実装基盤として内部で扱い、公開widgetは追加していません。Production初期値も変更していません。

### Still Image GuideはExperimental

V3.7では、Still Image Guide 1枚をabsolute frameからowner physical groupへ割り当て、高解像度Second Passでも元画像から再encodeできます。位置変換、Terminal Merge ownership、Run Storage identity、non-owner groupの非干渉はCorrectness PASSです。一方、Core Add Guideはhard anchorとして働くため、anchor位置で急なtrajectory変化が起き、その後のmotionも別の軌道へ分岐する場合があります。**Still Image GuideはExperimentalで、Production昇格はHOLDです。** 滑らかなtransition制御としては扱わないでください。

### V3.6.1 Maintenance Hotfix

V3.6.1は、受入済みBalanced 22 Masked AV経路を変更せず、限定的なfail-open／互換性問題を修正します。Timeline/List記法が混在したPromptは`H3C-P105`を表示し、Timeline解析ではstandalone `---`行だけを除去します。未指定Chunkの既存fallbackとFixed Promptのfail-open動作は維持し、Prompt構文だけを理由に生成を停止しません。

`Continuation Backend = Standard`かつAudio Continuity ONでは、`Balanced — 22 frames`が引き続きMasked AVを使用します。`Fast — 5 frames`、`Strong — 39 frames`、`Auto — conservative`はRun Storage identity作成前に、受入済みReference Contextへ解決します。UIの選択値は書き換えず、status reportへ解決結果と理由を表示します。Audio Continuity OFFのStandardはMasked Video、Compatibilityは常にReference Contextのままです。

Run Storageは、Last Frame未接続を表す値をすべて同じ空identityとして扱います。通常のLast Frameなし2チャンク生成を3チャンクへ延長すると、旧最終Chunkが`none`だったV3.6.1 cacheを含めて`2 reused, 1 generated`になります。実Last Frame接続時とLong Terminal Mergeのatomic pairは従来どおり厳密です。Run StorageをOffへ変更した場合は、Queue前にhiddenのRegenerate FromとVariation Nonceも`Auto`と`0`へ戻します。

### V3.6 Masked AV Continuation

V3.6では`H3 Continuum Sampler V3.6`を追加しました。標準backendは、前Chunkで確定したVideo／Audio latent prefixを次のH3 Target内へ直接配置し、CoreのNoise Maskで保持します。V3.5のReference Context方式のように、同じ過去フレームを別Reference blockとして追加しないため、H3が処理するpacked sequenceを短縮できます。

| Continuation Backend | 用途 |
|---|---|
| `Standard` | 推奨V3.6経路。Balanced 22＋Audio ContinuityはMasked AV、Fast 5／Strong 39／Autoは安全にReference Contextへfallbackします。Audio Continuity OFF時はMasked Videoです。 |
| `Compatibility` | 受入済みV3.5 Reference Context動作へ戻すAdvanced fallbackです。 |

内部transport識別子はUIへ表示しません。Run Storage identityは実行前に解決したtransportへ従います。Balanced 22 Masked AVはReference Contextと分離し、非Balanced Standard fallbackは同一動作のReference contractを安全に共有します。`Regenerate From`でもLong Terminal Mergeのlogical `[2,3]`を1つのphysical sampleとして再利用・再生成します。

### 受入結果

- T2VA、I2VA、Reference Image＋Reference Audio、Balanced 22-frame Joint AV、3×5秒FL2VA Long Terminal MergeのGPU GateをPASS。
- 保護Video／Audio prefixは最終的にbit-exact。生成領域はSamplerの出力を維持します。
- Reference Image＋Reference Audio代表出力は実聴PASSで、click、dropout、定位異常の報告なし。
- 実測したFL2VA Terminal Group 2では、StandardがCompatibilityよりpacked rowsを2,874行（`8.01%`）削減し、Sampling中央値を`4.06%`短縮。速度はmodel、hardware、workflowで変わります。
- `chunk_seconds`は4.0～30.0秒、初期値5.0秒、step 0.1です。5～15秒を推奨・検証済み範囲として維持し、長時間・高解像度ChunkはVRAMと処理時間が大きく増える場合があります。

V3.5.3、V3.5、V3.4のNode IDと保存済みWorkflowは維持します。V3.5.3は従来Reference Contextのままで、V3.6標準backendへ暗黙に切り替えません。

## V3.5.3 Maintenance Hotfix

V3.5.3は配布整合性だけを修正するメンテナンス版です。公開Conditioning Bridge WorkflowのWidth／Height接続、V3.4／V3.5テンプレート内の孤立link ID、Hybridの`<Picture N>`警告番号、厳密な画像decoderで読めなかった旧PNG 1件を修正しました。

生成動作、Node、socket、Sampling、Conditioning payload、Terminal Merge、Assembly、Seam、Run Storage、Prompt/CLIP cache、Video Guide最適化、V3.4互換性は変更していません。既存V3.5.x Workflowはそのまま読み込めます。

## V3.5.2 Stabilization & Optimization Update

V3.5.2は新しい生成モードを追加する版ではありません。V3.5.xを安定化し、安全な条件で繰り返しPrompt/CLIP処理を省略し、長いVideo Guide入力の一時メモリを削減します。既存Workflowと生成契約は維持します。

![H3 Continuum V3.5.2の安定化・最適化結果](images/v352-stabilization-optimization.png)

画像は受入済み最適化の実測値です。最終パッケージゲートでは、さらにComfyUI 0.33.3と、この画像を含む172項目のManifestでPASSを確認しています。

### 主な変更

1. **繰り返し実行Prompt/CLIP cache**: 条件が変わらないT2VA、I2VA、FL2VAではCPU上のPrompt/CLIP結果を再利用できます。Reference、schedule、tokenizer option、hook変更CLIPは安全側でbypassします。Sampling自体は通常どおり再実行します。
2. **Video Guideメモリ最適化**: source全体をfinite検査とSHA-256 identityへ含めたまま、VAE/conditioningに必要なprefixだけを保持します。
3. **安定化監査**: Sampling、Decode、Assembly、保存、任意機能の負荷、保持memoryを実測しました。根拠のないSampling、Driving Audio、Audio hash、Assembly、Seam、Session、V3.4最適化は採用していません。

### 実測結果

| 項目 | 変更前 | V3.5.2 | 結果 |
|---|---:|---:|---:|
| T2VA繰り返しPrompt/CLIP | 5.898398秒 | 0.000028秒 | Cache HIT、`encode_calls=0` |
| FL2VA繰り返しPrompt/CLIP | 21.642687秒 | 0.007128秒 | Cache HIT、`encode_calls=0` |
| Video Guide Peak追加RSS | 396.8 MiB | 114.7 MiB | 約71%削減 |
| Video Guide保持Storage | 225 MiB | 93 MiB | 約59%削減 |

Prompt/CLIPの数値はconditioning区間だけで、総生成時間ではありません。Video Guideメモリ比較は300×256×256 RGB入力／必要prefix 124 framesの固定CPU条件です。別のGPU A/Bでは実際の15秒／360-frame Video Guideを使い、decoded videoとaudio PCMの完全一致を確認しています。

RTX 5060 Ti 16 GB／RAM 64 GBの検証環境で測定したSage-only Production baselineは、576×576 T2VA 1×5秒が168.069秒、640×640 FL2VA Long Terminal Merge 3×5秒が379.765秒です。環境・設定固有の測定値であり、すべての環境に対する速度保証ではありません。Samplingが最大コストで、Continuum Assemble + Seamは1%未満でした。

**V3.8.0はhistorical release baselineです。V3.8X2はpackage 3.8.3の別Workflowとして維持し、V3.9はmainの現行ソースです。** V3.8X2が内部利用する旧module/classはsourceへ維持します。現在の登録面はV3.8X2の10 IDとV3.9追加の2 IDです。一部は旧IDを維持しますが、それ以外のIDを必要とする旧保存Workflowは対応するhistorical Release/tagを使用してください。Still Image Guideは引き続きExperimentalです。

## V3.5.1 Reference Audio／互換性更新

V3.5.1ではV3.4のSampling、Conditioning、Terminal Merge、Assembly、Seam、Run Storage契約を変更せず、次の2点を追加しました。

1. **Reference Audio（任意）**: 生成音声を置換しない、H3 nativeの音声conditioningです。Workflowの保存・再読込互換を守るため、2つのsocketは常時表示します。
2. **Conditioning Bridge V3.5**: Continuumのphysical groupごとに、完全なCore互換`MODEL`と`CONDITIONING`を外部Samplerへ公開します。

Reference Audio socketはPython `INPUT_TYPES`で常設し、保存・再読込時の値ずれを防ぐため動的socket変更とUI-onlyの`Hidden`／`Show` controlを削除しました。V3.4のNode IDとbackend socket keyは保存済みWorkflow互換のため維持しており、既存V3.4/V3.5 Workflowの接続は変わりません。

### Reference系入力の違い

表示名は役割の違いを示しています。名前が似ていても同じ組み合わせではありません。

| 表示入力 | 接続元 | 用途 | 最終音声 |
|---|---|---|---|
| `reference_image_1`～`reference_image_3` | 静止画`IMAGE` | 人物、被写体、外観などの継続参照 | 音声なし |
| `Video Guide Frames` | Video loaderの`IMAGE`フレームbatch | 全chunkでmotion、framing、timing、appearanceをガイド | 元動画の音声は含まない |
| `Driving Audio` + `Driving Audio VAE` | Audio loader、またはVideo loaderの`AUDIO`と対応Audio VAE | 音声で生成をガイドし、入力音声を最終出力へ維持 | 生成音声を選択した元音声へ置換 |
| `Reference Audio (Optional)` + `Reference Audio VAE (Optional)` | 単独Audioと対応Audio VAE | H3 native conditioning専用 | 生成音声をcopy・置換しない |

音声付き動画を使う通常の接続は、loaderの`IMAGE`を`Video Guide Frames`へ、`AUDIO`を`Driving Audio`へ接続します。conditioning専用動作が目的でない限り、動画の音声を`Reference Audio (Optional)`へ接続しないでください。

![Sampler V3.5の常設Reference Audio、Video Guide Frames、Driving Audio、Reference Image入力](images/v351-video-guide-frames.png)

`Reference Audio (Optional)`と`Reference Audio VAE (Optional)`は、Pythonのinput schemaどおり常時表示します。V3.5.1ではこの2 socketをFrontendで動的に追加・削除せず、UI-onlyの`Hidden`／`Show` widgetも使用しません。これによりWorkflowを保存・再読込した際のwidget値の位置ずれを防ぎます。backend input keyと既存接続は変更しません。

![常設Reference Audio socketと正常なwidget配置](images/v351-reference-audio-permanent.png)

### Conditioning Bridge V3.5

`H3 Continuum Conditioning Bridge V3.5`は外部sampling用のAdvanced接続点です。`model`、`clip`、外部処理後の`video_latents`、`assembly_plan`、`refine_context`を接続し、選択したconditioning経路で必要な場合だけ`video_vae`を接続します。出力`group_models`と`conditioning`はphysical group数と同数で、各要素は完全なComfyUI objectのままです。CONDITIONING内部entryをphysical-group listへflattenしません。

```text
H3 Continuum Sampler V3.5.video_latents
  → LBH等の外部H3 latent処理
  → H3 Continuum Conditioning Bridge V3.5
  → Core BasicGuider + 外部Sampler
  → Core Video / Audio VAE Decode
  → H3 Continuum Assemble + Seam V3.5
```

AV LATENTの組、Noise、SIGMAS、Audio Lock、sampling、audio passthroughは外部workflow側の責任です。Bridgeは準備済み`MODEL`と`CONDITIONING`、更新済みAssembly Planだけを公開します。

![V3.5.1 LBH＋Conditioning Bridge外部sampling接続図](images/v351-lbh-conditioning-bridge-flow.svg)

退役したV3.5.1 LBH＋Conditioning Bridgeの接続例は、対応するhistorical Release/tagでのみ参照できます。これはV3.8 Workflowではありません。

接続例ではCore標準名の`BasicGuider`、`BasicScheduler`、`SamplerCustomAdvanced`を変更していません。公開サンプルではCoreノードを独自タイトルへ変更せず、Continuumノードや外部カスタムノードと直感的に区別できる状態を維持します。LBH latent upscaler、AV LATENTの結合／分離、load／save、任意accelerationは外部ノードなので、各ComfyUI環境に合わせて導入または置換してください。

LBHはlatent geometryだけを変更し、Continuumのdenoise強度は持ちません。拡大後latentをどれだけ再生成するかは外部`BasicScheduler`のSIGMASで調整します。1.5x等へ上げても高速な場合がありますが、target canvasに応じてmemory、decode、sampling負荷は増加します。

## V3.5の主な追加機能

V3.5の大きな追加は2点です。

1. **Continuum対応Second Pass / Hi-Res Fix**: physical group構造を維持した再Samplingと、標準Pixel/VAE 2x経路。
2. **低メモリAssemble + Seam**: Exact Duration、Seam、Terminal Merge、Audioを維持したRAM / Disk-backed / Auto出力。

### 1. Second Pass / Hi-Res Fix

`H3 Continuum Hi-Res Fix V3.5`はVideo VAE Decode → pixel resize → Encode → low-denoise Second Passを1ノード化したMain経路です。長尺2xではVRAM上限に達する場合があるためExperimentalです。

![H3 Continuum Hi-Res Fix V3.5 node](images/v35-hires-fix-node.png)

通常のHi-Res Fix接続:

```text
H3 Continuum Sampler V3.5
  → H3 Continuum Hi-Res Fix V3.5
  → Core Video / Audio VAE Decode
  → H3 Continuum Assemble + Seam V3.5
```

`H3 Continuum Second Pass V3.5`は外部加工したH3 video latentをphysical group構造のまま再Samplingする安定版Advanced入口です。Issue #8への本体回答です。

![H3 Continuum Second Pass V3.5 node](images/v35-second-pass-node.png)

外部latent upscaler接続:

```text
H3 Continuum Sampler V3.5.video_latents
  → LBH等の外部H3 latent処理
  → H3 Continuum Second Pass V3.5
  → Core Video / Audio VAE Decode
  → H3 Continuum Assemble + Seam V3.5
```

画像では`BasicScheduler`を省略していますが、Second Pass用`SIGMAS`の接続は必要です。GPU受入済み基準は`res_multistep`、`simple / 10 steps / denoise 0.35`、Lanczos pixel resize、FL2VA 1×5秒・576→1152です。Hybrid FL2VA + Referenceも1×5秒で、統合2x Hi-Res FixとAdvanced Second Pass直結の両方を受入しました。

Hi-Res Fixを接続しなければV3.4 Sampling経路は変わりません。強制CPU offloadや低VRAM samplerは追加していません。`enabled=false`ではResize、VAE、Second Passを評価せず、元のVideo／Audio LATENTとAssembly Planをそのまま返します。

### 2. 低メモリAssemble + Seam

`H3 Continuum Assemble + Seam V3.5`はRAM / Disk-backed / Autoを選択できます。Disk-backedでは完成Video IMAGEをWindows対応mapped fileへ直接writeし、AudioはRAMに維持します。

1536×1536・360 frames・完成IMAGE 9.49 GiBの実測では、RAM版とDisk-backed版の映像／音声hashが完全一致しました。

| Windows process指標 | RAM | Disk-backed | 削減 |
|---|---:|---:|---:|
| Private memory | 12.41 GiB | 2.91 GiB | **9.50 GiB** |
| USS | 10.29 GiB | 0.80 GiB | **9.49 GiB** |

これはContinuum Assembly時の**システムRAM／private commitment削減**であり、SamplerのGPU VRAM削減値ではありません。Disk I/Oにより最終Assemblyが遅くなる可能性はありますが、前段のモデルSampling速度は変えません。

### GPU受入範囲

| 経路 | 条件 | 結果 |
|---|---|---|
| Main Hi-Res Fix | FL2VA 1×5秒、576→1152 | PASS |
| Main Hi-Res Fix | Hybrid FL2VA + Reference 1×5秒、576→1152 | PASS |
| Advanced Second Pass | Hybrid／Reference 1×5秒、576×576 | PASS |
| Main Hi-Res Fix | FL2VA 3×5秒、576→1152、RTX 5060 Ti 16 GiB | **Terminal 77TでCUDA OOM** |

3×5秒2xではFirst Passと37T groupのSecond Passは完了し、最後のlogical `[2,3]`を維持した77T physical groupが1152×1152の最初の推論でVRAM上限に達しました。group構造の破損ではなく、16 GiB実機でのリソース上限です。

詳しいsocket接続・OFF時のpassthrough・既知の制限は[英語版V3.5接続ガイド](V35_HIRES_FIX.md)を参照してください。

## 公開テンプレートワークフロー

- [V3.9 Workflow JSON](../examples/workflows/MiniMax_H3_Continuum_V39.json)／[単独ZIP](../examples/workflows/MiniMax_H3_Continuum_V39.zip) — 現行V3.9 graph。ZIPにはこのJSONだけを収録
- [V3.8X2 Workflow JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2.json) — 併存する旧系公式graph。Spectrumは初期状態でOFF
- [V3.8X2 Workflow ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip) — V3.8X2とV3.9の両JSONを格納。カスタムノードのインストーラーではありません
- [V3.8X2 Helper明示名JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.json)／[ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.zip) — 同じgraphを説明的な配布名で収録

Registry配布予定の対象はV3.9とV3.8X2のJSON／ZIPです。依存なしのテンプレートではなく、Spectrum・rgthree・KJNodesが必要です。ComfyUI-Easy-Useは不要です。Turboへ切り替えてもgraph内の外部ノードは残ります。SpectrumをOFFにし、用途に合うLightX2V Turbo LoRAを1本だけONにしてsampler／Stepsを合わせます。保存状態はSpectrum OFF、Turbo LoRA OFF、res_multistep／simple／20 Stepsです。

配布元のprompt、画像・音声名、ノード表示名、設定は変更していません。手元にあるファイルを選び、不要な入力をOFFにし、promptを入力してください。モデルやメディアは同梱しません。`Save 3x5s Video`などの保存済み表示名は生成時間を決めません。実際の長さはSamplerのChunksとSeconds per Chunkで決まります。

旧Workflowは開発履歴としてsource repositoryへ保持しますが、V3.8 Registry packageからは除外します。旧保存Workflowは[Migration Policy](V38_RELEASE_AND_MIGRATION.md)に従い、対応するhistorical Release/tagで開いてください。Registryの正式pack検証・公開はGitHub sourceの更新とは別工程です。

## V3.4互換

V3.4の実装moduleは内部継承とhistorical testのためsourceへ保持しています。現行の登録面は上記12 IDに限定します。それ以外のIDを必要とするV3.4保存Workflowは、対応するhistorical packageを使用してください。

## V3.4.0 Stable

V3.4.0は、最大3枚のReference Image、Run Storage、Spectrum Interop、Decode後のAudio / Video Seam補正を維持し、`Driving Audio`と`Video Guide Frames`を正式な入力として追加します。

`Driving Audio`は入力音声を絶対時間で各Chunkのガイドに使い、最終出力には元音声を維持します。`Video Guide Frames`はVideo loaderが出力したIMAGE frame batchを全Chunkで継続使用し、`Efficient - 0.4 MP`、`Balanced - 0.6 MP`、`Match Output`から処理解像度を選択できます。青いIMAGE socketですが、通常の1枚の静止画参照ではなく動画フレーム列を接続します。

### Size項目の条件付き表示と内部Resize

V3.5のCompact UIでは、対応する入力を接続した時だけSize項目を表示します。

- `reference_image_1`～`reference_image_3`のいずれかを接続すると、`Reference Size`を表示します。
- `Video Guide Frames`を接続すると、`Video Guide Size`を表示します。以前のWorkflowやIssueで`Video Reference Size`と記載されている項目と同じもので、V3.5.1では表示名だけを`Video Guide Size`へ明確化し、既存のbackend keyと保存済みWorkflowの互換性を維持しています。

したがって、新規ノードで見えないSize項目は欠落ではなく、未接続のため非表示になっています。Reference ImageとVideo Guide FramesはVAE Encode前に内部Resizeされます。Video Guide Framesはアスペクト比を維持してH3 canvasへ整列し、縮小が必要な場合はLanczosを使用します。小さい入力を自動的に拡大はしません。通常は外部Resizeノードを必要としませんが、意図的なcrop、小さい素材の強制upscale、独自のresize／upscale方式を使う場合には外部処理を利用できます。動画のdecodeとframe-rate変換は引き続きloader側の責任です。

Reference入力のバイパスされたソケットは無視され、有効な画像だけがPicture 1から連続採番されます。空欄や不完全なプロンプトも停止せず、警告とFixed fallbackで生成を続行します。未知のモデル、ノード、プロンプト形式を独自判断で拒否する制限も撤廃しました。

## Run Storage：第2部分だけを再生成

通常のT2VA／I2VAを`2 chunks x 5 seconds`にした場合、Chunk 1が最初の5秒、Chunk 2が次の5秒です。

初回生成前に次を設定します。

1. `Run Storage`を`Save + Auto Resume`にします。
2. 固定の`Run Name`を選び、Base Seedも固定します。
3. まず10秒全体を一度生成します。Continuumは完了した各Chunkのraw Video／Audio latentを保存します。

最初の5秒を保持して、第2部分だけを作り直す手順は次のとおりです。

1. Run Name、Base Seed、model、LoRA、解像度、sampler、SIGMAS／steps、Reference、Continuity設定を初回と同じに保ちます。
2. `Regenerate From`を`Chunk 2`にします。
3. `Variation Nonce = 0`なら、完了済みの再生成に対して新しいバリエーションを自動選択します。互換性のある未完了runを再開する場合は、既存のバリエーションを引き継ぎます。`1以上`は指定値を固定するため、同じ入力で別の結果を求める場合は別の正の値へ変更します。Base Seedは固定のままにします。
4. Workflowをもう一度Queueします。

Review画面の`Try this chunk again`は、この手動指定とは別に、内部のバリエーションを自動で進めます。

Continuumは保存済みChunk 1を再Samplingせずに読み込み、その確定済み末尾をContinuation contextとして新しいChunk 2をSamplingします。Reportの目安は`1 reused, 1 generated`です。その後、10秒全体を再Decode／Assemblyします。第1ChunkのSampling結果は再利用され、境界のSeam処理は新しいAssembly時に再評価されます。

第1部分と第2部分で異なる指示を使う場合は、初回生成前にListまたはTimeline Promptとして分けておきます。保存後にPrompt Planや生成Contractの入力を変更すると新しいRevisionになり、以前のChunk 1を再利用できない場合があります。初回を`Run Storage = Off`で生成した場合も、後から遡って再利用することはできません。`Regenerate From`はChunk境界単位であり、1つのChunk内部の任意領域を編集する機能ではありません。

FL2VA Long Terminal Mergeは重要な例外です。最後の2つのlogical Chunkを1つのatomicなphysical Samplingとして扱うため、その2つは一緒に再生成されます。

Run Storageの保存契約にはDriving AudioとVideo Guide Framesのidentityを含め、入力変更後に古いChunkを誤再利用しないようにしています。

## Driving Audio / Video Guide Frames / Seam

Driving Audioだけを使う、Video Guide Framesだけを使う、Video Guide Framesと別音声を組み合わせる、という3通りの接続に対応します。Video Guide Framesは24 fps入力を基準とし、異なるfpsの素材はLoad Video側で24 fpsへ設定してください。

H3 Continuum Assemble + SeamはAudio Seam AutoとVideo Seam Autoを既定とし、フレーム削除を行わずに境界の一時的な露出・色変化を補正します。Auto 2は露出ランプ向けの実験的な追加モードです。

## Legacy V2.1.7 Stable Facade UI

V2.1.7では、V2.1.6の動的表示制御を廃止し、標準ComfyUI描画だけを使用する静的Facadeへ移行しました。生成処理は互換用`H3ContinuumSamplerV2`を再利用し、State、Session、Prompt Plan、Spectrum Interop、保存Schemaは変更していません。

通常表示は次を中心にします。

```text
model / clip / video_vae / audio_vae / sampler / sigmas
Sequence Prompt
first_frame
prompt_overrides（任意pack）
advanced（任意pack）

Prompt Format
chunks
chunk_seconds
width / height
continuity
base_seed
control after generate
Seam Correction
Seam Correction

outputs: images / audio / result
```

### 補助ノード

- `H3 Continuum Clip Overrides`: Clip別Promptを1本のpackへまとめます。
- `H3 Continuum Advanced`: resume/session入力と低頻度設定をまとめます。
- `H3 Continuum Result`: resultから`last_state / session / report`を展開します。
- 補助ノードを使わない通常生成では、Sampler本体だけで動作します。

### Legacy互換

当時のV2.1.7では、旧`H3ContinuumSamplerV2`をLegacy/Coreノードとして登録し、既存WorkflowのノードID、入力順、出力順を維持していました。これはV3.8の公開範囲を示す説明ではありません。このIDを使う旧Workflowは対応するhistorical Release/tagで開いてください。

## Continuity

- `Auto — conservative`
- `Balanced — 22 frames`（標準）
- `Fast — 5 frames`
- `Strong — 39 frames (Experimental)`

5/22/39フレームはH3の時間latent周期`1,4,4,4,4`に対して、それぞれ2/7/12 temporal latent stepsです。

## Spectrum

Continuumは有効な前チャンクContextがある場合だけ`h3_continuum` Interop API v1をMODEL optionsへ付与し、対応Spectrumへ`min_actual_prefix_steps=2`を要求します。初回チャンクにはInterop keyを付与しません。未知・未対応Spectrumでは通常Spectrumとしてfail-openします。

## 推奨配線

```text
UNET -> SageAttention -> Sol-Attn -> LoRA -> Spectrum -> H3 Continuum Sampler
```

まず`chunks=2 / chunk_seconds=5 / Balanced 22f / Seam Correction=Off`でNative Continuityを確認し、その後`Seam Correction=Auto`を比較してください。

## インストール

V3.8はComfyUI 0.34.2で検証しています。以下の歴史的な受入記録には旧ComfyUI版も登場しますが、現在のインストール目標ではありません。V3.8の依存を満たす限り、ComfyUIの最新版は必須ではありません。

ZIPを展開して、`ComfyUI-H3-Continuum`フォルダーを`ComfyUI/custom_nodes/`へ置き、ComfyUIを再起動します。

再起動後はV3.8X2 Workflowで`H3 Continuum Sampler V3.8`、V3.9 Workflowで`H3 Continuum Sampler V3.9`と`H3 Continuum Reference Images V3.9`を確認してください。現行の登録面は計12 IDです。

旧`ComfyUI-H3-Continuum-Join`が残っている場合は同時ロードを避けるため削除または退避してください。同梱`install_windows.bat`は旧名・新名の既存フォルダーを日時付きでバックアップします。

## 検査

Public Surface suiteはV3.8X2の10 IDとV3.9を含む計12 ID、公式Workflowと各ZIP内JSONの同一性、外部依存、Registry除外、既存V3.8 widget/socket順、`Show Advanced Settings`／`Hide Advanced Settings`による表示切替を確認します。Registry配布対象のハッシュは`REGISTRY_MANIFEST.sha256`、source側の整合性は`MANIFEST.sha256`で管理します。

**過去のV3.8X2準備証拠：** Full CPU suiteは**1,367 passed / 1 skipped / 0 failed**です。従来の最終GPU Functional Gateでは`3 × 5秒`のReview Each Chunkを実行し、Q1～Q3はphysical groupを1つずつ生成、Q4は`3 reused / 0 generated`で3 groupすべてを再利用しました。Q3とQ4の復号後RGBおよびPCM SHA-256は一致しています。9枚Reference Imageの別Gateは下記に記録しています。これは実行、prefix再利用、AV再構築、テストした9枚経路の確認であり、画像・音声の総合的な主観品質評価ではありません。

### 9枚Reference Image入力Gate（0.3 MP参照画像）

テストしたNVIDIA GeForce RTX 5060 Ti 16 GB／RAM 64 GB環境では、Reference Image 1～9、`512 × 608`出力、`3 × 5秒` Full Run、Spectrum Off、LoRA Off、Sage Attention、Balanced 22-frame continuity、各約`0.30 MP`のテスト参照画像で完走しました。Sampling中のVRAM使用量は、利用可能な`16,311 MiB`のうち約`15.0～15.5 GiB`であり、16 GB GPUでは余裕の小さい高負荷構成です。

9枚bundleは、追加の外観・ポーズ情報が必要で、十分なVRAM余裕を確保できる環境で使用してください。このsingle-seed Gateは実行と基本的な視覚的連続性を確認したものです。9枚が3枚より常に高画質であること、高解像度参照・大きな出力・別model・同時GPU負荷でも動作することを保証するものではありません。

16 GB GPUで9枚を使う場合は、読み込む前に元画像のコピーを約0.30 MPへ縮小してください。内部のconditioning用Resizeは継続しますが、9枚の大きな元画像によるメモリ負荷を管理する代わりにはなりません。

検証結果はテストしたローカルsourceと環境に限られます。導入済み環境が最新版であること、すべてのmodel／wrapperが任意のGPUに収まること、別のpromptでも同じ画質になることを保証するものではありません。

```text
python -m compileall -q .
pytest -q
```

MIT License。
