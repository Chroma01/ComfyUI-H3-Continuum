# H3 Continuum — 日本語の詳細ガイド

[日本語README](../README_JA.md) · [英語の図解ガイド](USER_GUIDE.md) · [日本語の履歴資料](README_HISTORY_JA.md)

この資料は、正本`84899c1`（パッケージ3.9.8）の日本語READMEから、詳しい操作と画像を移したものです。
V3.8の表示名・操作説明は保持しているV3.8X2用であり、V3.9の導入・Reference説明とは区別してください。
過去の版表記、修正記録、測定条件は当時の記録として保持しています。
現在の配布・互換性・制約は[短縮版README](../README_JA.md)と[KJ対応条件](KJ_PREVIEW_OVERRIDE_V398.md)を参照してください。

- [V3.9とV3.8X2の導入](#最初にv39とv38x2)
- [Reference Images](#v39-reference-images)
- [Review・継続の手順](#10秒を5秒ずつ確認しながら作る)
- [Prompt・スキル配布](#プロンプトスキルのダウンロード)

<!-- Preserved README sections begin. -->

## 最初に：V3.9とV3.8X2

ComfyUIの **Templates → ComfyUI-H3-Continuum** には、今回選んだ[V3.9公式Workflow](../examples/workflows/MiniMax_H3_Continuum_V39.json)と、別の[V3.8X2 Workflow](../examples/workflows/MiniMax_H3_Continuum_V38X2.json)を2件表示します。[V3.8X2 Workflow ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip)には、**V3.8X2とV3.9の両JSON**を同梱しました。[V3.9単独ZIP](../examples/workflows/MiniMax_H3_Continuum_V39.zip)も残します。いずれもWorkflow用ZIPで、カスタムノード本体のインストーラーではありません。V3.8 Samplerは残るので既存のV3.8X2 Workflowは使えます。ただしV3.9へReference配線や保存済みRun／Takeは自動移行しません。旧Workflowを保存しておき、新しい作業ではV3.9専用Workflowを開いてください。

選択したV3.9テンプレートは32ノードです。画像Loader 1～6は新ヘルパーへ配線済み・初期Bypassです。7～9番の入力欄は残し、必要な人が画像Loaderを追加して接続します。使用する画像を選んで必要なLoaderだけ有効にしてください。保存済みサイズ設定は**First Image＋Draft — 0.30 MP**で、別のFirst Image Loaderは有効です。Queue前に自分のFirst Imageファイルを選び直してください。保存済みのWidth/Height 480×640はManual時だけ有効です。`Reference Image Size`は`Match Output`で、読み込み後のconditioningを縮小しますが元画像ファイル自体は縮小しません。チャンク別Referenceの効果を明瞭に試すなら、First ImageとLast ImageをOFFにし、Manualへ切り替えてReference Imagesだけを使うのが勧められます。First／Lastを入れるとそれ自体が動画を拘束し、Last Imageは最後の2つの論理チャンクを1つの生成groupに結合する場合があります。その場合、両チャンクの有効Reference集合は同じにしてください。Referenceを外しても、前チャンクの映像から人物が引き継がれることはあります。

ヘルパーの `All chunks` は接続画像を全チャンクに、`Per chunk` は画像×チャンクの表で指定します。このテンプレートは`Per chunk`で全チェックOFFから始まるため、Loaderを有効にした後、使用したいチャンクにもチェックしてください。空欄があっても番号はずれず、Image 1は常に`@R1`、Image 9は`@R9`です。Sequence Promptにはチャンクごとの動作を短く書き、そのチャンクで使う画像の`@R`タグを付けます。内部の`<Picture N>`番号はgroupごとに自動変換されます。使わないタグは警告しますが生成を止めません。まず短いチャンクと縮小済み画像で試してください。入力元画像はSamplerのReference Image Size設定より前にRAMを使うことがあります。

V3.9.3は`main`の現行ソースです。バージョンを固定したソースは[GitHub Releases](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/releases)から取得してください。ComfyUI Registryへの公開は別の作業です。過去のReleaseとtagも残します。設定済み1024×1024のReference-only GPU/APIテストは通っていますが、無改変の公式テンプレート初期設定とブラウザー保存・再読込は別の受入項目です。古い環境を厳密に再現するには対応する過去のRelease／tagとWorkflowを使用してください。現行mainにもV3.8 Samplerを残し、V3.8X2 Workflowを使えるようにしています。

`pyproject.toml`の宣言上はComfyUI `>=0.32.0`ですが、以前の実生成・GPU検証はComfyUI `0.34.2`、上記の限定したFixedキャッシュ比較は`0.38.0`で行いました。最低宣言版でV3.9の実機動作を確認済みという意味ではありません。以前のWindows CPU試験は`1696 passed / 1 skipped / 0 failed`、以前の別環境Linux再実行報告は`1534 passed / 3 skipped / 0 failed`で、新しいキャッシュ／外部INT試験は含みません。これらは無改変の公式テンプレートの実ブラウザー保存・再読込やGPU受入を代替しません。

## V3.9 Reference Images

### Reference Imagesノード：画像とチャンクを選ぶ

![H3 Continuum Reference Images V3.9ノードの固定スロットとチャンク別割り当て表](images/v39/v39-reference-images-node.png)

*この画像は操作例で、配布Workflowの初期割り当てではありません。* Image 1～9は固定スロットで、途中が空でもImage 1は常に`@R1`です。`Reference Use = Per chunk`にすると、使いたい画像とチャンクの交点をチェックできます。各行の`All`／`Off`は、その画像を全チャンクで選択／解除します。画像ではImage 1をChunk 1・2に割り当て、ほかの画像は別のチャンクに割り当てています。公式V3.9 Workflowは画像Loaderが初期Bypass、割り当てが全OFFです。実ファイルを選び、Loaderを有効化してから、使うチャンクにチェックしてください。

### Sampler V3.9：ヘルパーから1本で接続

![Reference Images Optional入力を1本持つH3 Continuum Sampler V3.9](images/v39/v39-sampler-node.png)

ヘルパーの緑色の`reference_images`出力を、Samplerの`Reference Images (Optional)`入力へ1本つなぎます。V3.8X2 Workflowは旧V3.8 Samplerと従来のReference接続を使用し、開くだけでV3.9配線へ変換されるわけではありません。この画像のサイズ設定は**Manual 480×640の操作例**で、公式V3.9 Workflowの保存値は**First Image＋Draft 0.30 MP**です。`Reference Image Size = Match Output`は画像読込後のReference conditioningサイズを決め、元ファイルを事前縮小したり、動画の出力解像度を直接決めたりはしません。

V3.9では、固定番号の参照画像1～9を新しい **H3 Continuum Reference Images V3.9** ノードにまとめます。ノード内の表で「All chunks」またはチャンク別のチェックを選び、Samplerへは1本だけ接続します。`Sequence Prompt`で`@R1`と書けば固定の画像1を指します。有効なタグは各生成groupの実際の`<Picture N>`へ変換されます。両モードとも同じチャンク別処理を通ります。

Promptは実行を止めません。明示的なTimelineでも解析できなければ元の入力をFixedとして扱い、診断`H3C-P100`を出します。Timelineで指定のないチャンクは前のPromptを再利用し、`H3C-P101`で知らせます。どの画像を各チャンクに使うかはReference Imagesノードで選び、Prompt中の`@R1`～`@R9`は接続画像の固定番号に対応させてください。

同梱の`2 × 10秒`Workflowでは、時間見出しを必ず単独行にし、各チャンクの動作だけを短く書きます。対応する画像LoaderをONにしてチャンク欄へチェックを入れた場合の書式例です。

```text
[0-10s]
@R1 walks forward through a quiet hallway. The camera follows smoothly.

[10-20s]
@R2 enters from the right. The camera turns to follow @R2.
```

人物や動作は実際の画像に合わせて書き換えてください。これは書式例で、配布WorkflowのPromptは空欄です。`[0-10s]`と本文を同じ行には書かないでください。チェックされた画像は、Prompt中に`@R`を書かなくてもそのチャンクのconditioningに入ります。

[公式V3.9 Workflow](../examples/workflows/MiniMax_H3_Continuum_V39.json)は、今回指定された添付JSONを無改変で採用しました。[単独ZIP](../examples/workflows/MiniMax_H3_Continuum_V39.zip)も用意しています。V38X2のモデル・LoRA、Decode Cache、Finalize、Saveのフル構成を維持し、画像Loaderは1～6だけを配線済み・初期Bypassにしています。7～9番を使う場合は`H3 Continuum Load Image`を追加し、ヘルパーの同じ番号の入力へ接続してください。Sequence Promptの入力ノードと配線は残し、文章は空欄です。Queue前に自分のプロンプトを入力してください。保存設定は`Timeline`、2×10秒、`Full Run`（画面表示はGenerate Full Video）、First Image＋Draft 0.30 MP、別Project IDです。従来の[V3.9 Reference Inline移行用Workflow](../examples/workflows/MiniMax_H3_Continuum_V39_Reference_Inline.json)は変更せず残します。チャンク別割り当て、First/Lastとの終端結合、保存・再読込、画像メモリの注意点は[操作ガイド](V39_REFERENCE_INLINE.md)を参照してください。Queue前にモデル・素材のファイル名を確認し、画像を有効化する場合は実ファイルを選択してください。7～9枚の参照は特に高負荷なので、最初は枚数と元画像サイズを抑えてください。新ノードを表示するにはComfyUI本体の完全再起動とブラウザーの強制再読込が必要です。無改変の公式テンプレートの実ブラウザー保存・再読込／GPU受入はまだ未実施です。GitHub Releaseの公開は、これらの受入やRegistry公開の完了を意味しません。

**互換性：** V3.8X2の既存Workflowは旧V3.8 Samplerと旧4～9ヘルパーで引き続き利用します。V3.9では新ヘルパーへの接続が必要です。旧Workflow上でSamplerの型だけ変えず、上記のV3.9専用Workflowを開いてください。以前のV3.9試作WorkflowにあったSampler直結1～3やSampler側の割り当て欄は配線と保存widgetの位置が異なります。V3.8の途中Run／Takeは自動移行しません。元Workflowを保存し、V3.9では別Run Nameを使ってください。

以前のV3.9操作系のブラウザー確認は、新しいヘルパーの保存・再読込確認とは別です。新ヘルパーは設定済みGPU/API実行の証拠がありますが、公式テンプレート初期設定の受入は別です。CPU／JS・Manifestも別に判定し、V3.9 GitHub Release／Registry公開はまだ行っていません。

**バージョン境界：** V3.8X2（package 3.8.3）とV3.9.0は別Workflowです。今回、新しいtag・GitHub Release・保守ブランチ・Registry版は作成せず、既存Releaseも削除しません。旧V3.8.0は既存の`v3.8.0` tagから取得できます。

## mainのLoader保存・復元修正（2026-09-21、3.8.3以降）

現行V3.8X2ワークフローは、音声を **Core Load Audio**、動画を **Core Load Video → H3 Continuum Video Adapter** に変更しました。Video Adapterは24fpsへの変換（Force Rate初期値24）とIMAGE/AUDIO出力だけを担当し、**Enableやファイル選択UIはありません**。動画を使わない場合はAdapter、または動画入力グループ全体をBypassしてください。Load VideoだけをBypassして必須入力のAdapterをONに残す構成は避けてください。

画像は **H3 Continuum Load ImageとEnable Imageを維持**します。Issue #23の継承されたmode setterへの委譲と、描画・保存中のwidget配列差し替え廃止を適用します。EnableはCoreの欄の後ろに配置し、画像ファイルとBypassの保存はCoreに委ねます。旧Audio/VideoノードIDは既存workflow用の非推奨互換ノードとして残します。V3.8X2の登録IDは互換用2個を含め10個で、V3.9では別IDのV3.9 SamplerとReference Imagesヘルパーを追加して計12個です。V3.8 Sampler設定・Sampling・Decode Cache・Finalize・既存Run Storage契約は変更しません。

更新後はComfyUI再起動と画面の再読み込みが必要です。既に保存JSONから消えたファイル名やOFF状態は推測で復元できないため、一度選び直して保存してください。既存ユーザーworkflowや保存済みTakeは自動変更しません。上流ノードの種類変更でRun Storageが新revisionになることはあるため、過去Runの再開には元workflowを保管してください。

検証範囲は[Loader修正記録](LOADER_PERSISTENCE_REPAIR.md)を参照してください。CPU回帰テストと実ブラウザ確認は別です。Windows Core 0.36.0 / frontend 1.53.6のタブ切替確認は未実施で、Release/tag・Registry公開も別作業です。以下の旧Loader画像は互換ノードの説明です。


## Timeline Video — main上のExperimental機能

従来の動画IMAGE入力を**`Timeline Video Frames`**と表示し、末尾に省略可能な設定**`Video Reference Mode`**を1項目追加しました。新しい設定を持たない既存Workflow／APIは、初期値の**`Repeat Reference`**で従来動作を維持します。

- **`Repeat Reference`**：従来のVideo Guide契約です。各physical生成groupで、同じ先頭側の上限付き参照を使います。短い素材を自動ループ／Stretchしません。
- **`Follow Timeline`**：各physical出力groupの時間位置に対応する24fps参照区間を使います。Continuationの過去prefixを二重消費しません。素材終了後は動画参照なしで続行し、利用可能な終端区間にはH3 frame-grid整列分だけ短いpaddingを行う場合があります。

これは`Prompt Format = Timeline`とは別の設定です。新しいsocketやLoaderは増やさず、元動画のAudioも自動使用しません。参照動画はsoft conditioningであり、motionをframe単位で完全コピーする機能ではありません。また、decode済みIMAGE batch全体をsystem RAMへ保持するため、長尺入力のRAM削減機能ではありません。

接続は既存のままです。

```text
Core Load Video → H3 Continuum Video Adapter → Timeline Video Frames
```

公式V3.8X2 Workflow本体は変更せず、比較用Experimental Workflowを別名で追加しています。

- [Follow Timeline JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Follow.json)／[ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Follow.zip)
- [Repeat Reference JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Repeat.json)／[ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2_Timeline_Experimental_Repeat.zip)

ローカル受入ではFull CPU `1424 passed / 1 skipped / 0 failed`、ブラウザ保存・再読込、Follow／Repeatの`2 × 5秒` GPUテストがPASSしました。両方とも704×416、24fps、240フレーム、映像10秒、32kHz stereo音声10秒で、OOM／NaN／allocation failure／crashはありません。FollowはChunk 2で後半区間へ切り替わり、Repeatは同じ先頭側参照を維持しました。RTX 5060 Ti 16 GBで観測した最大VRAMは約15.6～15.7 GiBで、16 GBの余裕は小さい条件です。これは機能・mode分離の受入結果であり、一般的な速度や主観画質の保証ではありません。詳細は[Timeline Video Experimental](TIMELINE_VIDEO_EXPERIMENTAL.md)を参照してください。

> **V3.8X2**はpackage `3.8.3`の製品名・Workflow名です。V3.8 Production Samplerを維持し、任意のReference Image 4～9と内蔵Decode Cache Helperを追加しています。旧V3.8.0は[`v3.8.0`タグ](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/tree/v3.8.0)から導入できます。

## V3.8X2 公式Workflow

- **標準名：** [JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2.json)／[ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip)
- **Helper明示名：** [JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.json)／[ZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2+Decode_Cache_Helper.zip)

V3.8X2の2つのJSON名は**同じ公式graph**を収録した配布上の別名で、異なる設定のWorkflowではありません。どちらも内蔵Decode Cache Helperと9枚Reference Image用の接続を含み、Helperの保存値は`Auto / RAM 256MB / Disk 8GB / reset_token 0`です。標準名のV3.8X2 ZIPには別のV3.9 JSONも同梱し、Helper明示名ZIPは対応するV3.8X2 JSONだけを収録します。既存projectでは従来のV3.8X Workflowも引き続き使用できます。

## Reference Image 9枚使用時のメモリ注意

Reference Image 1～3はSamplerへ直接接続し、任意の4～9は`H3 Continuum Reference Images`を経由して`Reference Images (Optional)`へ接続します。9枚すべてを使う構成は高負荷であり、通常の最低要件ではありません。

受入テストでは、**RTX 5060 Ti 16 GB／RAM 64 GB**環境で、9枚の元画像を各**約0.30 MP**に抑えた条件で完走しました。`512 × 608`出力、`3 × 5秒`、Spectrum Off、LoRA Off、Sage Attention、Balanced 22-frame continuityで、Sampling中のVRAMは`16,311 MiB`中の約**15.0～15.5 GiB**でした。16 GB環境では余裕がほとんどありません。

多数、特に9枚を使う場合は、読み込み・接続前に元画像のコピーを約0.30 MPへ縮小してください。Sampler内の通常のconditioning用Resizeは引き続き行われますが、小さい入力ファイルにすることで読み込み・前処理時の負荷を抑えられます。高解像度参照、大きな出力、追加wrapper、同時GPU処理では、より高性能なGPUと多いシステムRAMが必要になる可能性があります。9枚は任意であり、3枚より常に高画質になる保証はありません。

## 内蔵 Decode Cache Helper

### 重要：新規生成が一律に速くなる機能ではありません

**キャッシュの手動クリア**：普段は操作不要です。Helperの「キャッシュをクリア」ボタンを押すと、次回QueueでこのHelperのキャッシュを破棄し、通常Decodeからやり直します。ボタンは即時削除や自動Queueを行いません。内部の`reset_token`は保存・API互換用に残り、押すたびに1増えます（INT上限では0へ戻ります）。作成・読込・複製だけでは変更しません。JavaScriptが使えない環境やAPI版では、従来どおり`reset_token`の値を変更してください。

**短縮するのは、変更していないlatentを再びデコードする時間です。Sampling（生成計算）自体は高速化しません。** 初回は通常Decodeとキャッシュ保存を行うためMISSとなり、保存・照合の負荷で遅くなる場合があります。毎回ランダムシードで異なるlatentを新規生成する使い方では、基本的にMISSとなり、この機能による短縮は期待できません。

具体的に再利用できる場面：

- **Continueでチャンクを追加**：既存チャンクのlatentを保持し、出力時にもう一度Decodeする場合、保存済みの既存部分だけを再利用します。追加チャンクは初回MISSです。
- **Fix／部分再生成**：変更していないチャンクのlatentがそのまま再入力される場合、その部分だけを再利用します。再生成してlatentが変わった部分はMISSです。
- **Complete／Resumeで再出力**：Samplingをやり直さず、保存済みlatentから全体を再Decodeする場合に有効です。単なる既存動画ファイルの再生ではありません。
- **Decode以降のリトライ、Finalizeや出力設定の変更**：Helperへ同じlatent・Decode関連情報が再入力され、Decodeが再実行される場合に有効です。
- **固定シードで同条件を再生成**：生成後のlatentが完全に一致した場合だけ再利用できます。同じシードだけではHITを保証しません。

これらの操作名そのものが有効条件ではありません。**各Video／Audioの入力latentの内容・shape・dtype、Decode関連メタデータ、VAE識別情報が一致し、そのHelperにキャッシュが残っていること**がHITの条件です。ComfyUIが上流／出力をそのまま再利用してDecode自体を実行しない場合、Helperによる追加のDecode短縮はありません。Helperを接続し、`Auto`または`RAM`で使ってください。レポートの`hit`は再利用、`miss`は通常Decode、`off`／`bypass`はキャッシュ再利用なしを表します。

キャッシュはPythonプロセス内の利用に限られ、再起動後は再利用しません。上限による退避・破棄やVAE識別情報の変化でもMISSになります。モード、RAM／Disk予算、`reset_token`を変更すると、この実装ではHelperキャッシュをクリアします。`reset_token = 0`を維持することは、毎回リセットする意味ではありません。

`H3DecodeCacheHelper`をContinuumパッケージ内に収録し、UI上は`MiniMax H3/Continuum/Helpers`の独立公開ノードとして残します。インストール対象はContinuumだけです。V3.8X2の公開IDは、旧互換Loader 2件を含め計10件です。V3.9は別IDのSamplerとReference Imagesヘルパーを追加して計12件です。V3.8 Sampler、Finalize、Assembly Plan、Core Decode、保存済みwidget/socket契約は変更しません。

Samplerの`video_latents`／`audio_latents`と同じVideo／Audio VAEをHelperへ接続し、Helperの`images`／`audio`をFinalizeへ接続します。Samplerの`assembly_plan`はFinalizeへ直接接続したままです。[公式V3.8X2 Workflow](../examples/workflows/MiniMax_H3_Continuum_V38X2.json)は保存済みgraphと設定を維持します。このgraphにはCore VAE Decodeノードがないため、Core直結へ戻すにはCore Video／Audio Decodeを追加してFinalizeへ再配線するか、旧V3.8XのCore直結graphを開いてください。Helperを単に削除しても自動では戻りません。

`Auto`は全physical groupのVideo Decodeをプロセス専用Diskへ、小さなAudio Decodeを上限付きRAMへ保存します。`Off`はnative Decodeを使い、Helper Cacheを破棄します。Cache障害時はnative Decodeへ戻りますが、native DecodeのOOMやQueue中断は再試行しません。Python再起動後にCacheファイルを再利用しません。移行時は同じ`H3DecodeCacheHelper` IDを提供する旧単独addonと内蔵版を同時登録しないでください。内蔵版の導入確認後に旧addonを無効化または撤去します。

736×416（0.306MP）、3×5秒、Euler/simple 6 steps、Turbo FL2V v1.2、ウォーム、Video 3/3 HITの1条件では、Full Run Totalの**機構推定中心値は約47秒／約24.5%短縮**でした。直接A/Bの1ペアは50.887秒／26.46%、Samplingを伴わないComplete/Resumeの2ペアは平均46.309秒／79.826%短縮でした。これは限定条件の観測値で、反復された一般平均や無条件の20%以上高速化保証ではありません。初回MISSは遅くなる場合があり、新規Samplingは高速化せず、latentまたはVAE識別情報が変わればMISSになります。

MiniMax H3を複数チャンクで連続生成し、直前チャンク末尾の**映像latent / 音声latentを直接**次チャンクへ継承するComfyUIカスタムノードです。チャンク間でVideo/Audio VAEのDecode→Encodeは行いません。

## インストール・更新

新規導入：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum.git
```

既存のGit導入を更新：

```bash
cd ComfyUI/custom_nodes/ComfyUI-H3-Continuum
git pull --ff-only origin main
```

ComfyUIを再起動してください。Managerから導入した場合はManagerのUpdateを使い、同じノードを重複配置しないでください。

旧V3.8.0を別フォルダへ導入する場合：

```bash
cd ComfyUI/custom_nodes
git clone --branch v3.8.0 --single-branch https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum.git ComfyUI-H3-Continuum-v3.8.0
```

Continuumのcheckoutは同時に1つだけ有効にしてください。ComfyUI Managerの**Update**は`main`を更新するため、過去tagの選択には使いません。

V3.8X2 Workflow：[JSON](../examples/workflows/MiniMax_H3_Continuum_V38X2.json)／[V3.8X2・V3.9両JSONを含むZIP](../examples/workflows/MiniMax_H3_Continuum_V38X2.zip)。V3.8X2 JSONはSpectrum対応の1本で、保存状態ではSpectrumとTurbo LoRAはどちらもOFFです。[LightX2V Turbo](https://github.com/ModelTC/Minimax-H3-Turbo)にも切り替えられます。完全なgraphを開くにはSpectrum・rgthree・KJNodesが必要です。ComfyUI-Easy-Useは不要です。

## プロンプト・スキルのダウンロード

- [V3.9 Reference Images用プロンプトスキル本文](../write-h3-v39-reference-prompts/SKILL.md)／[ZIP](../write-h3-v39-reference-prompts.zip)：固定の`@R1`～`@R9`とチャンク別の画像割り当てに対応します。V3.9のReference Imagesノード用で、下記の汎用Continuumスキルとは別です。
- [LLM用システムプロンプトZIP](../H3-Continuum-LLM-System-Prompt-v1.zip)：Continuum向けプロンプト作成のシステム指示と詳細資料。
- [Continuum専用プロンプトスキルZIP](../H3-Continuum-Skill-v1.zip)：Codexなどで使う、チャンク構成に対応した汎用プロンプト作成スキル。
- [Continuum Dance DirectorスキルZIP](../minimax-h3-continuum-dance-director.zip)：主役のダンサー1人を対象に、チャンク間の身体動作とカメラの連続性を考慮した長尺ダンス用プロンプトを作成するスキル。

いずれも任意のプロンプト作成支援資料で、ComfyUIのカスタムノードではありません。ZIPを展開し、同梱の案内に従って利用してください。Samplerを変更するものではなく、生成動作や画質を保証するものでもありません。

## V3.8の公開範囲

H3 Continuumは、長尺映像を最初からやり直さずに生成・確認・部分再生成・再開するProduction Samplerです。V3.8は`Main / Production`と`Advanced`の2層に整理しました。

以下の9ノードに`H3 Continuum Video Adapter`を加えた計10 IDがV3.8X2の登録面です。旧Audio／Video Loaderは互換IDとして残ります。V3.9はさらにSampler V3.9とReference Images V3.9を追加した計12 IDです。

- `H3 Continuum Sampler V3.8`
- `H3 Continuum Finalize`
- `H3 Continuum Load Image`
- `H3 Continuum Load Audio`
- `H3 Continuum Load Video`
- `H3 Continuum Second Pass`
- `H3 Continuum Reference Audios`
- `H3 Continuum Reference Images`
- `Decode Cache Helper`

Main Sampler内の`Show Advanced Settings`／`Hide Advanced Settings`で詳細設定を開閉します。旧node property `H3 Continuum View`を含む保存Workflowは対応する開閉状態へ移行し、旧propertyを削除します。これは表示状態だけの変更です。Python input、widget順、保存済みwidget値、backend引数、Sampling identity、Run Storage identityは変更しません。Frontend extensionが読み込まれない場合も、Python定義の全widgetが表示された状態で実行できます。

V3.8X2公式Workflowの標準経路は`Sampler V3.8 -> Decode Cache Helper -> Finalize -> Create Video -> Save Video`です。HelperはMISSしたentryをCore Video／Audio Decodeへ委譲します。Core Decodeへ直接つなぐ手動構成も使用できますが、Decode結果のcacheはありません。Finalizeの`IMAGE`／`AUDIO`出力をCoreの`Create Video`で`VIDEO`へまとめてから保存します。Save、Upscalerは外付けとし、外部latent processorやupscalerはSecond Passをbridgeとして接続します。外部processorが変更できるのはVideo LATENTの空間解像度だけで、physical group、B/C/T、finite値、First Pass Audio、元のAssembly Planを維持する必要があります。Finalizeは公開`IMAGE`／`AUDIO`型を受け取り、特定decoder classへ依存しません。SageAttention、Sol-Attn、Spectrumは外部MODEL wrapperのままです。詳細は[V3.8 Open Integration Contract](V38_OPEN_INTEGRATION_CONTRACT.md)を参照してください。旧Hi-Res FixはV3.8X2標準Workflowに含めません。

### Reference Audio 1/2/3

`H3 Continuum Reference Audios`は、最大3本の単独Reference Audioを1本の`Audio References (Optional)` socketへまとめます。入力は間を空けずに接続し、Promptでは接続順どおりに`<Audio 1>`、`<Audio 2>`、`<Audio 3>`を使用します。共通のCore Audio VAEで各Audioを個別encodeします。生成後の最終Audioを置換せず、Driving Audio契約も変更しません。既存Workflowは従来の単数`Reference Audio (Optional)`をそのまま使用できますが、単数経路とbundle経路は同時接続しないでください。

> **対応範囲:** 元のV3.8公開面は7 ID、V3.8X2は互換Loaderを含め10 ID、V3.9は12 IDです。Finalizeの`H3ContinuumAssembleSeamV35`、Second Passの`H3ContinuumSecondPassV35`などは旧IDを維持しますが、すべての旧Workflowに互換性があるという意味ではありません。未対応のnode IDには対応するhistorical Release/tagを使用してください。詳細は[V3.8 Release／Migration Policy](V38_RELEASE_AND_MIGRATION.md)を参照してください。

複雑な16GB GPU受入Gateでは約`15.5～15.6 GiB`を使用しました。GPU、driver、backend、model精度、解像度、接続ノードで変動するため、すべての16GB GPUでの動作保証ではありません。

Reference Imageは最大9枚です。Samplerの直入力1～3を維持し、追加4～9は`H3 Continuum Reference Images`のoptional IMAGE入力へ接続して、出力をSamplerの`Reference Images (Optional)`へ渡します。補助ノードは画像を束ねるだけで、Resize・hash・VAE Encodeは既存Sampler経路で実行します。未接続を除き1→9の順に使い、Picture番号はFirst／Last Imageの後に連番で割り当てます。空のbundleは参照なしとなり、旧0～3枚の生成・再利用契約は変わりません。

以前の4・5直入力を含む保存Workflowは、グラフ読み込み後に元の画像接続をbundleへ移します。新接続を検証した後だけ旧接続口を削除し、接続元が不明・移行先が使用中の場合は警告して元の線を残します。旧API入力も維持しますが、同じ番号の画像を旧直入力とbundleの両方から指定すると入力競合として明示します。既存の3枚loaderテンプレートは上書きせず、そのまま利用できます。

### サイズの決め方を直接選択

| Preset | 目安 |
|---|---|
| `Draft` | 約0.30 MP |
| `Balanced` | 約0.60 MP |
| `Native 768` | 短辺768を目標。極端なAspectでは長辺1344 capを優先 |
| `Custom MP` | Megapixelを直接指定。Native 768のcapとは別 |

Mainの`Size Source`は次の2択です。

- `First Image`：接続したFirst Imageの縦横比を維持し、Presetの目標面積から最終Width／Heightを算出します。
- `Manual`：Width／Heightを32 pixel単位で直接指定します。この場合、Presetは適用しません。

MainのWidth／Heightは`Manual`のときだけ表示・編集できます。`First Image`ではResolutionを表示し、画像の縦横比からサイズを決めます。有効なFirst ImageがSamplerへ届かない場合は、保持しているManual Width／Heightへフォールバックし、その寸法をStatusへ表示します。手動寸法を確認・変更する場合は`Size Source = Manual`を選びます。Reference ImageやVideo Guideからサイズを暗黙取得することはありません。

旧V3.8の`Auto / Landscape / Portrait / Square`はWorkflow／API互換用として内部で受け付けます。FrontendはAutoをFirst Imageへ、3つの固定Aspectを同じ解決結果のManual Width／Heightへ移行します。

### 10秒を5秒ずつ確認しながら作る

ComfyUI上端の実行ボタンは、frontendにより`Queue`、`Run`、または`実行する`と表示されます。この手順内の`Queue`は、その実行ボタンを指します。

ここでは、画面に表示される名前だけを使って手順を説明します。

#### 最初に知っておくこと

`Chunks = 2`、`Seconds per Chunk = 5`は、完成目標が合計10秒という意味です。ただし、`Run = Review Each Chunk`では10秒を一度に生成しません。最初のQueueでは、確認用に**Chunk 1の5秒だけ**を生成します。これは正常動作です。

Chunk 1を確認した後に操作を選び、もう一度QueueするとChunk 2へ進みます。`Chunks = 1`では最初の5秒が最後なので、次へ進む操作はありません。

#### 手順1：生成前の設定

`H3 Continuum Sampler V3.8`で、上から次の順に設定します。

1. `Control After Generate`を`fixed`にします。`randomize`、`increment`、`decrement`では続きを再利用できません。
2. `Chunks`を`2`にします。
3. `Seconds per Chunk`を`5`にします。
4. `Total Length`が`10 seconds`になったことを確認します。`Total Length`は確認表示で、直接変更する項目ではありません。
5. `Run`を`Review Each Chunk`にします。
6. `Progress`を`On — Resume and Takes available`にします。
7. 緑色の`Ready to Queue`欄に、`2 × 5s = 10 seconds`と`Review each chunk`が表示されていることを確認します。`Set Control After Generate to fixed`と表示された場合は、Queueする前に手順1を直します。

#### 手順2：最初の5秒を作る

1. ComfyUIの`Queue`を押します。
2. Chunk 1だけが生成されます。出力動画が5秒でも正常です。
3. Queueの処理が完了すると、Samplerの表示が自動的に`Chunk 1 is ready for review`へ切り替わります。

#### 手順3：Chunk 1の動画を確認する

保存された5秒の動画を再生し、そのまま採用するか、作り直すかを決めます。この時点ではまだ合計10秒の動画は完成していません。

#### 手順4：次の操作を1つ選ぶ

| 画面上のボタン | 次のQueueで行うこと |
|---|---|
| `Use it and continue` | 現在の5秒を採用し、次のChunkを1つ生成します。 |
| `Try this chunk again` | 現在のChunkだけを別のTakeとして作り直します。 |
| `Use it and finish the rest` | 現在までを採用し、残りのChunkをまとめて生成します。 |

ボタンを選んだだけでは生成は始まりません。選択したボタンに`✓`が付いたことを確認してから、ComfyUIの`Queue`を押します。

`Try this chunk again`はContinuum側で別Takeを作るため、作り直しでも`Control After Generate`は`fixed`のままにしてください。

#### 手順5：2本目の5秒を作り、10秒を完成させる

1. `Use it and continue`を選びます。
2. ComfyUIの`Queue`をもう一度押します。
3. 採用済みのChunk 1を再利用し、Chunk 2を生成します。
4. Samplerから後ろのDecode、`H3 Continuum Finalize`、Save Videoまで通常どおり実行されると、合計10秒の完成動画が出力されます。

設定を確認し直したい場合は`Back to Settings`を押します。未処理のReviewへ戻る場合は`Return to Review`を押します。どちらも生成を自動開始せず、選択済みのTakeや保存済みChunkも削除しません。

#### 迷ったときの確認

- 最初のQueueで5秒だけ出た：`Review Each Chunk`の正常動作です。
- 次へ進むボタンが出ない：Queueが完了しており、`Progress = On — Resume and Takes available`、`Chunks = 2`以上であることを確認してください。正常なら完了後に自動表示されます。
- ボタンを押しても生成されない：操作を選んだ後、ComfyUIの`Queue`をもう一度押してください。
- `Set Control After Generate to fixed`と表示された：`Control After Generate`を`fixed`にしてください。別SeedのChunk 1が増えることを防ぐ安全チェックです。
- 1回で10秒すべて作りたい：`Run`を`Generate Full Video`にします。

Long Terminal Mergeのpairは分割せず、1つのReview単位として扱います。

Driving AudioはReview／Smart Regenerateと併用できます。Continuum Image／Audio／Video Loaderは任意入力向けのnative bypassに対応します。

> **V3.8 Reviewの制限:** Review途中のpartial sequenceでは、Second Pass／`refine_context`を正式対応範囲に含めません。Reviewを完了してsequenceを確定してからSecond Passを実行してください。V3.9では、上記のとおり検証済みの出力区間条件を継承できます。

### Take・Branch・安全な継続

Run Storageを有効にすると、Production表示に**Render History / Takes**が表示されます。
Takeを選択してもcanonical結果は変わりません。**Use This Take**でそのrevisionを
canonicalにし、**Continue From Here**で選択したTakeまでを保持して後続groupだけを
再生成します。どちらの操作も自動Queueは行いません。

## V3.9 Second Passの接続

現行版の[接続図・ソケット表・SIGMAS・外部拡大の説明](SECOND_PASS_GUIDE_JA.md)を参照してください。
FinalizeにはSecond Passの`updated_assembly_plan`を使います。V3.9では検証済みの実出力区間contextを
継承でき、旧V3.8の途中Review制約とは区別します。同解像度のRefinementも可能です。
