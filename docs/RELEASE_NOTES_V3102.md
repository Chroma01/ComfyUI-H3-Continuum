# 3.10.2 — Review history and regeneration hotfix

Validation date: 2026-10-24 JST. Five targeted repairs; workflow V3.9 and
Project / Take Manager V1.2 remain unchanged.

## Fixes

1. **Preserve finalized Take history.** Continuation previously changed a
   published revision to an unfinished state; an error could hide earlier Takes
   and named savepoints even though raw tensors remained. New work now uses a
   separate working revision with existing raw references. Final status and
   provenance are published atomically. Interrupted work cannot downgrade the
   earlier finalized revision; project indexes remain recoverable.
2. **Validate capped Review targets before sampling.** Unreachable manual
   regeneration targets are rejected before creating a sampling revision or
   doing expensive generation. Valid next groups, terminal pairs and uncapped
   Full Run behavior are retained.
3. **Preserve linked Run Storage requests.** Unknown/linked values no longer
   reset regeneration Chunk/Nonce to Auto/0. Only a direct literal Off resets
   them; ComfyUI Core still resolves and validates external inputs.
4. **Support Manager UUIDs on HTTP LAN pages.** If `crypto.randomUUID` is absent,
   use cryptographic `getRandomValues` for UUID v4. A clear English/Japanese error
   is shown when no secure random source exists. Retry operation IDs stay stable;
   no weak-random fallback is introduced.
5. **Keep accepted Second Pass video on CPU.** Move generated video tensors to
   CPU before retaining them in the output list, including with `--gpu-only`.
   Already-CPU tensors keep their identity. First Pass audio, unselected groups,
   dtype and metadata are preserved. Core device settings are not overridden.

## Validation and limits

- Full real-Core CPU/JavaScript: **2,248 passed / 2 skipped / zero failures**,
  with **zero CUDA initialization attempts**. Windows, Python 3.13.12, CPU
  enforced, in an isolated Git-free source copy. The skips concern an older
  Spectrum descriptor fixture and an unavailable historical workflow.
- Review Queue: 90 JavaScript cases; linked Run Storage: 42; Manager panel: 46.
  These execute through pytest wrappers and are included in the full count.
- Tests cover interruption before/after raw commits, atomic seal failure,
  project-index failure, abrupt process exit, saved endpoints, valid v6 reuse,
  legacy history, unknown-code refusal and storage integrity.
- Offline registration/layout: twelve public nodes and native PackedLayout.
- Official workflow JSON/ZIP bytes and existing protected Take/workflow/settings
  files were preserved. No saved schema or sampling-signature migration.
- **No new live-browser or GPU acceptance for this hotfix.** CPU device-ownership
  tests do not measure real VRAM peaks or prove OOM resolution. Video/audio
  quality, speed and all accelerator combinations are not newly validated.
  Public CI and tagged-package checks run separately from the local full gate.

This prevents future loss of finalized history. It does not automatically repair
previously interrupted Runs, rewrite stored manifests, convert old v5 Takes or
make unsafe/read-only v6 Takes reusable. Sampling v6 / Graph v4 and unknown-code
refusal remain unchanged. Manager remains optional/default-OFF.

## Update

**GitHub-only hotfix. Registry resubmission remains held pending the manual
review of 3.10.0.** That reviewed package is not replaced or resubmitted.

- ComfyUI Manager: update a Git-tracked installation through its repository
  update action and verify package 3.10.2. Registry-backed installations may
  not list this version while submission is held; use the GitHub ZIP.
- Manual Git installation: open your ComfyUI installation's
  `custom_nodes/ComfyUI-H3-Continuum` folder and update with `git pull`.
- ZIP installation: replace only custom-node package files from the 3.10.2 ZIP.
  Keep Run Storage, named Project data and user workflows; avoid duplicate copies.
- Fully restart ComfyUI and hard-refresh with **Ctrl+F5**. Existing compatible
  Takes and workflows need no migration, deletion or rewiring.

## 日本語

継続の失敗・中断で確定済みTakeや保存点が一覧から消える問題を優先して修正しました。
新しい処理は別の保存Revisionへ書き込み、元のraw参照と確定済み履歴を保護します。
Reviewの到達不能な再生成指定は計算前に拒否し、外部Run Storage接続による指定の
リセット、HTTP LAN接続でのManager UUID生成、Second Passの生成済み映像が
VRAMへ蓄積する経路も局所修正しました。First Pass音声は維持します。

CPU・JavaScriptは **2,248成功／2スキップ／失敗0**、CUDA初期化試行0。
12ノードのオフライン登録・Layoutを確認しました。**今回の実ブラウザー・GPU受入は
未実施**です。実VRAM使用量・OOM・画質改善を保証する結果ではありません。
過去の中断履歴の自動修復や旧v5／unsafe v6 Takeの再利用許可は行いません。

Registry再送信は3.10.0の手動レビュー待ちで保留し、GitHubのみで配布します。
ManagerでGit導入を更新するか、ComfyUIの `custom_nodes/ComfyUI-H3-Continuum` を
GitまたはZIPで更新してください。既存Take・Project管理データ・Workflowを保持し、
ComfyUIの完全再起動とCtrl+F5を行ってください。新規Runや履歴削除は不要です。
