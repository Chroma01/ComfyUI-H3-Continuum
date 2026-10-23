# Project / Take Manager V1.2 — package 3.10.0

Package 3.10.0 adds this optional feature to the V3.9 workflow. It provides a
right-side management panel for the V3.9 Sampler; it adds no graph node or socket.
The feature is OFF by default. Existing workflows, generation and Render History
can be used without enabling or opening it.

## Use

For the illustrated walkthrough, see the [English README](../README.md#manager-walkthrough-with-actual-screenshots)
or [日本語README](../README_JA.md#managerの使い方--実画面で順番に操作).

1. Enable **Settings → H3Continuum → Project Manager → Enabled**.
2. Open **Project / Take** from the H3 Continuum menu or the same settings section.
3. Select the target V3.9 Sampler and create a named Project.
4. **Add current Run** attaches its existing history. Alternatively, **New trial**
   allocates a fresh independent Run identity; **Prepare new trial** explicitly
   applies that identity to the selected Sampler. It does not copy an old prefix.
5. Select a Take in the Sampler's Render History, then **Name selected Take**.
   The savepoint pins that Take's endpoint and ancestor chain. Later generation
   does not move it to the latest Take.
6. Select a named savepoint and **Prepare from savepoint**. Inspect the existing
   Review controls, then use the ordinary Queue button to generate.

The panel follows ComfyUI's English/Japanese locale. Names are display labels;
renaming or archiving never renames, moves or deletes a Run. Archive is an
organizational action, not a Queue cancellation or generation lock.

Savepoints are references, not additional backups. They require the original
Run metadata and raw data. They do not restore models, prompts, images or the
whole workflow. Keep the intended generation settings in the workflow; the
existing Sampling v6 checks remain the final authority for reuse when queued.
Old read-only Takes are not made reusable. Runs without immutable provenance
remain available through their original history view.

Preparation refuses a queued/running target, conflicting Run identity in the
graph, externally connected identity/action controls, missing/corrupt saved
data and obsolete responses after the workflow changes. Browsing, naming and
archiving do not need to stop normal generation.

## Storage and recovery contract

- One JSON per Project in the validated ComfyUI user profile:
  `h3_continuum/project_manager/projects/<UUID>.json`.
- Existing data stays in `output/h3_continuum/runs/`. Management reads it without
  adding markers, acquiring a sampling lock or rewriting manifests/raw files.
- A short OS lock protects each management JSON. Updates check operation ID and
  revision before an atomic replace. A conflicting tab must refresh and review
  the new state. Unknown network outcomes can be retried with the same ID.
- The operation journal retains up to 4,096 operations without evicting old IDs.
  At the limit, further edits are refused; create another Project. Existing
  Projects and savepoints remain readable. Each Project also limits trials and
  savepoints to 4,096, and its JSON to 16 MiB.
- Corrupt metadata is reported and preserved. Manager registration or operation
  failure does not disable the original generator, Review or temporary storage.
- Run Storage v3, Sampling v6, Graph v4, node IDs, widget order and official
  workflow files remain unchanged. Chunk LoRA switching is a separate feature.

## Validation gates

CPU tests cover atomic storage, concurrent updates, idempotent retry, immutable
savepoints, raw-data integrity, legacy/read-only rejection, append-after-save,
and continued operation of the original storage API without Manager.
JavaScript tests execute the actual panel and Review bridge, including inactive
mode, graph changes during requests, Queue guards and existing Review behavior.
Fixed-source full CPU/JavaScript regression: **2,210 passed / 2 skipped / zero failures**;
CUDA initialization attempts: zero. Manager-specific coverage is 62 pytest
cases, with 57 distinct JavaScript cases included through its wrappers. Existing
90-case Review coverage also passed. These counts overlap and must not be added.
The final full run includes the host-detached panel reopening repair and all
24 panel JavaScript cases. Two skips cover an original Spectrum profile fixture
and an unavailable historical workflow template. One pytest import-rewrite
warning is recorded; no expected failures remain.

Separate Chrome acceptance passed: default OFF, enable/open, target Sampler,
Project/Run attachment, savepoint preparation, independent trial, workflow save
and reload. Four dedicated GPU Queues also passed: Chunk 1 with Manager OFF →
saved-prefix Chunk 2 → another Chunk 2 from the same Chunk 1 savepoint → a fresh
independent trial. The original Chunk 1 raw hash and previous Takes were retained;
Chunk 2 Variation advanced from 1 to 2. All four AV files fully decoded.
See [test conditions and limitations](RELEASE_NOTES_V3100.md). These checks
do not establish broad video quality, speed or VRAM performance.

## 日本語

パッケージ3.10.0の追加機能です。**初期OFFの右側管理パネル**で、ノードや接続口は
増えません。使わない場合は従来どおり生成・Review・履歴を利用できます。

設定の **H3Continuum → Project Manager** で有効にし、**Project / Take** を
開きます。対象Samplerを選び、Projectを作成して「現在のRunを追加」します。
別案を試す場合は「新しい試行」を作成し、「新しい試行へ切替準備」で切り替えます。
新しい試行は独立Runで、前のチャンクを自動複製しません。

Render HistoryでTakeを選び、「選択Takeに名前を付ける」で保存点を作成します。
「前半採用・Chunk 2まで」のように、保存した時点の終点を固定します。
「保存点から再開準備」の後、既存Reviewで確認して通常のQueueで生成します。
再開準備だけでは生成しません。

保存点は元データへの参照です。バックアップやモデル・プロンプト・Workflow全体の
復元ではありません。元Runやrawを削除すると使用できなくなります。再利用の
互換性確認は既存Sampling v6に委譲し、旧read-only Takeを再利用可能にはしません。

表示名の変更・アーカイブは管理情報だけを更新します。元Takeの変更・削除や
Queue停止は行いません。複数タブの競合は上書きせず、更新後の内容確認を求めます。
通信結果が不明な更新は、同じ操作IDで再確認できます。

再表示修正を含む最終CPU・JavaScript回帰は2,210成功・2スキップ・失敗0、
CUDA初期化試行0です。Chromeの保存・再読込と、専用Runでの4 Queueも別途成功しました。
元Chunk 1と以前のTakeを保持し、Chunk 2のVariationは1から2へ進み、独立試行は
新しいRunのChunk 1から開始しました。画質全般・長尺・速度・VRAMの合格とは区別します。
詳しい条件は[検証結果と制限](RELEASE_NOTES_V3100.md)を参照してください。
