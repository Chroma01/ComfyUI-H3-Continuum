# 3.10.0 — Project / Take Manager V1.2

Validation date: 2026-10-23 JST. Package 3.10.0 adds the optional Manager V1.2
to the V3.9 workflow. Manager starts OFF and existing workflows remain usable.

## What changes

An optional, default-OFF right-side panel adds named Projects, independent
trials and named Take savepoints. Enable **Settings → H3Continuum → Project
Manager → Enabled**, then open **H3 Continuum → Project / Take**. English and
Japanese follow the ComfyUI locale.

Attach an existing Run, select a Take in Render History and name its savepoint.
Preparing that savepoint passes its fixed endpoint to the existing Review
controls. Inspect the selection and submit the normal Queue yourself. A new
trial uses an empty Run Name and a fresh Run UUID; it starts an independent Run.
Manager never automatically submits a Queue or restores model/prompt settings.

This release also repairs reopening when the host has detached the panel
DOM without its Close callback. Obsolete asynchronous work is cancelled before
a replacement panel is created.

## Preservation and safeguards

- Management JSON is separate from generated Run data, with short per-Project
  locks, atomic writes, revision conflict detection and idempotent operation IDs.
- Savepoints pin the endpoint and ancestry and verify raw hashes. Later appends
  do not move the saved endpoint. Saving or preparing does not rewrite Takes.
- A savepoint references existing data. It is not a backup, a cloned Run or a
  complete workflow restore; deleting its source data makes it unusable.
- Existing Sampling v6 reuse checks remain authoritative. Old v5 and unsafe v6
  Takes remain readable without being promoted to reusable history. Unknown
  code is not granted reuse by Manager.
- Busy targets, conflicting identities, connected identity controls and stale
  asynchronous selections are guarded. Capacity limits refuse further updates
  instead of silently discarding idempotency history.
- Manager OFF/unused retains normal generation and Review without Manager API
  requests or management metadata creation. No new graph node, Queue wrapper,
  Run marker or change to the sampling/storage engine is introduced.

Public node IDs, input/widget order, shipped workflows, Run Storage v3, Sampling
v6 and Graph v4 are unchanged. Separate test portability improvements keep the
production RAM safety checks intact.

## Final CPU and JavaScript regression

The final frozen source, including the reopening repair, passed **2,210 tests /
2 skipped / zero failures or expected failures** in 290.86 seconds. CUDA
initialization attempts were **zero** and CUDA stayed uninitialized. The test
harness used Windows, Python 3.13.12 and ComfyUI Core with CPU execution enforced.
Offline registration/native-layout verification also passed for all twelve
public nodes, without GPU generation.

Manager coverage comprises 62 pytest cases, including wrappers executing 57
distinct JavaScript cases: 32 bridge cases, one additional real saved-Take
integration case and 24 panel cases. Existing 90-case Review JavaScript coverage
also passed. JavaScript counts overlap pytest and must not be added to its total.

Coverage includes concurrent/atomic updates, operation retries, immutable
ancestry and hashes, read-only/unknown-code refusal, inactive behavior, Queue
guards, stale requests and panel reopening. The two skips concern an original
Spectrum descriptor fixture and an unavailable historical workflow template.
One existing pytest import-rewrite warning for an already imported dependency
was recorded.

## Separate Chrome and GPU acceptance

Chrome checks covered the initial OFF state, enabling/opening the panel, target
Sampler selection, named Project, attached Run, savepoint, independent trial,
and saving/reloading a dedicated workflow. Preparation used visible controls;
generation used the normal Run button.

GPU conditions: Windows, ComfyUI Core 0.42.1, frontend 1.55.18, Python 3.13.12,
PyTorch 2.14.1+cu130, RTX 5060 Ti 16 GB, Comfy Kitchen 0.2.39. The dedicated
T2VA test used an INT8 H3 model, BF16 Turbo model-only LoRA at 1.0, eight-step
Euler/simple, 512×512 at 24 fps and two five-second chunks. Spectrum, KJ preview
override and Second Pass were disabled; no First/Last or Reference images were
used.

| Queue | Operation | Observed result |
| --- | --- | --- |
| 1 | Generate Chunk 1 with Manager OFF | No prefix reused; one new chunk; 5-second output |
| 2 | Attach Run, save Chunk 1 and prepare continuation | Chunk 1 reused; Chunk 2 generated with Variation 1; 10-second output |
| 3 | Prepare the same Chunk 1 savepoint again | Chunk 1 reused; alternate Chunk 2 with Variation 2; 10-second output |
| 4 | Prepare a new independent trial | Fresh Run with no parent; new Chunk 1; 5-second output |

All four Queues completed without execution errors. The original Chunk 1 raw
SHA-256 remained identical across both continuations. Previous Chunk 2 Takes
and their metadata remained available. The independent trial did not reuse the
original Run. All four MP4s fully decoded, with matching audio/video stream
durations of 5, 10, 10 and 5 seconds. The final Queue was empty.

Protected existing Takes and workflow files were unchanged. The explicit Manager
enable preference and new dedicated test assets were the expected local additions.

These are targeted management-function checks. They do not establish subjective
video/audio quality, long-form stability, peak VRAM, speed, Spectrum/Second Pass
GPU compatibility or every model/provider combination. The final reopening
guard received the full CPU/JavaScript regression; no additional GPU run was
needed for that UI-only repair.

## 日本語要約

初期OFFの右側パネルでProject・独立試行・名前付きTake保存点を管理します。
保存点からの準備は既存Reviewに渡し、生成は通常のQueueで行います。保存点は
元データへの参照で、バックアップやWorkflow全体の復元ではありません。
使わない場合は従来どおり動作し、既存Take・公式Workflow・生成契約を維持します。

再表示修正を含む最終CPU・JavaScript回帰は **2,210成功／2スキップ／失敗0**、
CUDA初期化試行0。Chromeで保存・再読込を確認しました。専用GPUテストの
「Chunk 1生成 → Chunk 2継続 → 同じ保存点から別Chunk 2 → 独立試行」も4 Queueすべて成功。
元Chunk 1のrawハッシュは不変で、以前のTakeを保持し、Variationは1から2へ進みました。
4本とも正常にデコードでき、映像・音声の尺が一致しました。

今回の合格は管理機能の対象動作についてです。長尺・総合画質・速度・VRAM・
SpectrumやSecond PassとのGPU組合せは今回の受入対象に含めません。
パッケージ3.10.0で追加する機能です。Managerの仕様名はV1.2、Workflowは引き続きV3.9です。

## Test portability included in this release

Small assembly/buffer correctness tests use fixed test-only memory probe values.
Explicit low-memory tests still verify the production RAM guard. A historical
model-signature fixture replaces a test-time Git/HEAD lookup, allowing tests to
run from a source ZIP. Production RAM checks and dependency requirements are
unchanged.

## Update and first use

- ComfyUI Manager: update H3 Continuum to 3.10.0 when the Registry entry is
  available. Registry moderation and GitHub publication are separate states.
- Manual Git installation: open `custom_nodes/ComfyUI-H3-Continuum` in your
  ComfyUI installation and update that checkout with `git pull`. For a ZIP
  installation, replace only the package files from this release. Avoid duplicate
  installed copies and keep existing Run Storage and workflow files.
- Fully restart ComfyUI and hard-refresh the browser with Ctrl+F5.
- Existing workflows work without Manager. To use it, enable Settings →
  H3Continuum → Project Manager, then open H3 Continuum → Project / Take.
- The README includes six actual screenshots and a complete walkthrough in
  English and Japanese. Existing safe Takes remain compatible; unsafe/v5 Takes
  are preserved without conversion. No new Run is required just to update.
