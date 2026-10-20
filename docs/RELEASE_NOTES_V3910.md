# 3.9.10 — Spectrum reuse and Reference assignment display

Fix two causes of false **Sampling v6 read-only** in the supported Spectrum
configurations: Windows CRLF source line endings and Python 3.12 implementation
signatures. Also correct the Reference Images assignment table when Chunks comes
from an external INT node.

## Changes

- Audit Spectrum CRLF and LF source line endings identically, including module
  closures. All other source bytes and the exact supported file sets stay checked.
- Add separate audited Python 3.12 profiles for upstream Spectrum 0.2.29 at
  `806fe498d574a726fecb8818917f00a4b993fd77` and the existing audited local
  implementation. Retain the original Python 3.13 profiles byte-for-byte.
- With external Chunks inputs, display **assignment range 1–16** instead of a
  stale Sampler widget count. All/Off actions identify their range. This range
  does not set generation length or automatically expand saved selections.
- Preserve public node IDs, input/widget order, Sampling v6, Graph v4, existing
  Takes and official workflow files. No chunk-LoRA or Project Manager feature is
  included.

## Update

Update Continuum, restart ComfyUI and refresh the browser. Existing workflows need
no rewiring. Keep saved Runs/Takes. For a newly supported configuration, start a
**new Run**: older unsafe/v5 Takes remain readable and are not automatically made
reusable. Normal supported Python 3.13 generation identities stay unchanged.

## Verification and limits

- Full local CPU/JS gate: **2,096 passed / 2 skipped / 2 known Inspector expected
  failures**; compilation and offline registration of all twelve nodes passed.
- Targeted Spectrum/Attention: **169 passed / 1 skip**. Python 3.12 component:
  **112 passed / 1 skip**, with 21 independent older-Core/Attention cases excluded.
- Separate-process storage: **24 cases**, comprising 16 PyTorch/Kitchen cases on
  Python 3.13 and eight Spectrum/default-model cases on Python 3.12. All matched
  the actual Take read-only JavaScript. Original raw data was retained, and all
  six previously valid full Sampling Contracts stayed identical.
- Reference table browser checks passed external INT and KJ Set/Get routing,
  selection controls, disconnect/restore, save/reload and workflow tab switching.
- **No new GPU acceptance is claimed for 3.9.10.** These are CPU and UI checks,
  not Attention-kernel, H3 inference, image-quality or performance measurements.

Unknown source, changed functions, foreign closures and additional runtime state
remain non-reusable. The repair does not guarantee every Core/Kitchen/KJ/Sage or
Python combination. An independent Attention-observation failure in an older
Core/Kitchen environment can still disable reuse even when Spectrum is recognized.
The reporting user's exact environment has not been reproduced.

See the [compatibility guide](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/blob/v3.9.10/docs/ISSUE31_SAMPLING_SIGNATURES.md) for audit details.

## 日本語

対応済みSpectrum構成で、WindowsのCRLF改行とPython 3.12の実装識別によって
新規Takeまで「Sampling v6 read-only」になる判定を修正しました。外部INTでChunksを
指定したときのReference Images割り当て表も修正し、範囲1–16で設定できるようにしました。
生成チャンク数や既存の選択内容を自動変更する機能ではありません。

更新後はComfyUIを再起動し、ブラウザーを更新してください。Workflowの配線変更や
履歴削除は不要です。新しく対応した構成は新規Runで確認してください。
既存3.13の正常な識別値と、旧unsafe/v5 Takeの閲覧を維持します。

CPU/JS全回帰2,096成功、Python 3.12対象112成功、独立した保存・継続24ケースと
実JS照合、Reference表示のブラウザー操作を確認しました。
**今回の修正としてのGPU受入は未実施です。** 未知の実装や追加状態の拒否は維持し、
すべてのCore／Kitchen／KJ／Sage構成への対応や、報告者本人の環境再現を保証しません。
4.0はメジャーアップデート用として温存し、SemVer互換の3.9.10で公開します。
