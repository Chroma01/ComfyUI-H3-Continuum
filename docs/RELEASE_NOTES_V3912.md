# 3.9.12 — Reference Plan Inspector refresh

## Fix

After repeated Sampler UI configuration, including workflow save/reload, the
Reference Plan Inspector could keep an old verified result after Reference edits.
Use an explicit current refresh delegate and install event callbacks only once.
The Inspector now invalidates that result and accepts the next backend plan.
Align current installation commands and download links with 3.9.12; retain older
release records and their original validation counts.

## Validation

- Full local CPU/JavaScript regression: **2,148 passed, 2 skipped, zero failures
  or expected failures**. The two former Inspector expected failures are now
  required passing tests. The nine-case JS fixture also covers 100 configure
  passes, callback counts, new backend results and unchanged serialized values.
  JS cases are included in pytest totals, not additional tests to sum.
- Compile and offline registration/native-layout verification passed for all
  twelve public nodes. CPU checks prohibited CUDA initialization; none occurred.
- Chrome: saved and reopened a separate test workflow, then performed real GPU
  sampling. In the Review settings view, the Inspector showed the backend's
  `Reference Plan Inspector (last Queue, runtime verified)` heading. Unchecking
  Reference Image 1 / Chunk 1 changed it to
  `Configured only — Queue has not verified the effective Reference Plan.`
  without another Queue. The saved test workflow retained the edited assignment.
- Existing protected Take/workflow-related files: **140 hash-identical**.
  New Run project/manifest/raw-latent files: **3 hash-identical** before and
  after the Reference edit. The official workflow JSON/ZIP files are unchanged.

### GPU/browser scope and limits

Windows, Python 3.13.12, ComfyUI 0.42.1, frontend 1.55.18, torch 2.14.1+cu130,
Comfy Kitchen 0.2.39, RTX 5060 Ti 16 GB. INT8 FL2VA model, BF16 8-step Turbo
LoRA at 1.0, Euler/simple, one 5-second chunk, 512x512, fixed base seed
2026102201, one R1 Reference image; no Spectrum or Second Pass in this test.
Generation completed in Full Run mode. Its completed view hid the Inspector;
switching to Review Each Chunk settings exposed the retained verified heading.
The one-chunk Review configuration warning was expected; no further Queue ran.

The first attempt failed while Core/comfy_aimdo read model data with Windows
error 1450 (insufficient system resources). After unloading models, the same
configuration succeeded on one retry. This release does not fix that resource
error, and the entire test session was not error-free.

The browser assertion covers the visible Inspector heading transition.
It does not certify all multiline Plan rendering, video/audio quality,
performance, or all provider combinations. No final decode or MP4 export was
needed for this UI test. Previous Spectrum continuation results remain recorded
under 3.9.11; they are not counted as new 3.9.12 GPU tests.

## Update

- ComfyUI Manager: update H3 Continuum to 3.9.12 when the Registry entry is
  available. GitHub release and Registry scan/Manager availability are separate.
- Manual: open your ComfyUI installation's `custom_nodes/ComfyUI-H3-Continuum`
  folder. For a Git checkout, update it with `git pull`; for a ZIP installation,
  replace the package files using this release's ZIP. Do not create duplicate
  installed copies or delete Run Storage/workflows.
- Fully restart ComfyUI and hard-refresh the browser with Ctrl+F5.
  No workflow rewiring or new Run is required for this Inspector fix.

Sampling v6, Graph v4, Run Storage, generation, public node IDs and input/widget
order are unchanged. Existing safe Takes keep their compatibility; old unsafe/v5
Takes remain readable without being promoted to reusable history.

## 日本語

保存・再読込などでSamplerのUIが再構成された後、参照変更でも古い検証済みPlanが
残る問題を局所修正しました。CPU/JSは2,148成功・2スキップ・失敗/期待失敗0。
実GPU生成後、Chrome上で参照割り当てを外すと未検証表示へ戻ることを確認しました。
既存保護対象140ファイルと新規Runの3ファイルはハッシュ不変です。
初回はモデル読み込み時のリソース不足で失敗し、モデル解放後の同条件再試行は成功。
この検証はInspector表示の確認であり、動画品質全般の評価ではありません。
Managerまたは既存custom-nodeフォルダーを更新後、ComfyUI再起動とCtrl+F5を実施してください。
既存Take・Workflowの削除、配線変更、この修正のための新規Runは不要です。
