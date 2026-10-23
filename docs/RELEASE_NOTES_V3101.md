# 3.10.1 — Project / Take Manager refusal messages

Validation date: 2026-10-23 JST. This patch corrects HTTP 409 messages in the
optional Manager. Workflow V3.9 and Manager specification V1.2 are unchanged.

## What changes

In 3.10.0, every HTTP 409 was displayed as a Project changed in another tab,
hiding the actual reason for read-only Takes, raw size/SHA-256 mismatches,
queued/running Runs and management capacity limits.

The existing revision-mismatch exception now carries the optional API code
`project_revision_conflict`. Only HTTP 409 with that code receives the localized
conflict message. Other refusals display the server's `error` text, or the HTTP
status when no reason is supplied. Unknown future codes preserve their reason.
Other backend explanations remain in their original English in Japanese UI.

This repairs the explanation, not the condition that caused the refusal.
Read-only Takes do not become reusable. Integrity checks and reuse safety,
HTTP refusal status, explicit refresh and uncertain-write handling remain.
The repair does not automatically retry or submit a Queue.

## Validation

- Full real-Core CPU/JavaScript: **2,214 passed / 2 skipped / zero failures or
  expected failures**, with **zero CUDA initialization attempts**. Windows,
  Python 3.13.12, CPU enforced. The skips concern an older Spectrum descriptor
  fixture and an unavailable historical workflow. One existing pytest dependency
  import-rewrite warning was recorded.
- Manager subset: **66 pytest cases**, including wrappers executing **38 panel
  JavaScript cases** and existing bridge integration. Seven response variants
  are checked in each of English and Japanese: read-only, raw integrity, busy
  Run, journal limit, actual revision conflict, unknown code and missing reason.
  JavaScript counts overlap pytest and must not be added to its total.
- API checks verify the exact conflict code, unchanged refusal status and other
  server reasons. Existing valid continuation, old v5/unsafe v6 protection,
  unknown-code refusal and saved-data integrity regressions remain.
- Live Chrome/backend checks in **English and Japanese** used a dedicated
  Project. An actual stale revision displayed the localized conflict message;
  duplicate Run attachment displayed the server's actual reason. No Queue or
  automatic retry was submitted. Other refusal reasons used CPU/API/JavaScript
  fixtures; user data was not damaged to reproduce them.
- **184 existing Take/workflow/settings files** retained their hashes during the
  browser check. All **21 official workflow JSON/ZIP files** remain unchanged.

The browser check used the same three repaired product modules before the
package version bump. No new GPU generation is claimed for 3.10.1. The four
Manager GPU Queues in [3.10.0 notes](RELEASE_NOTES_V3100.md) are historical
evidence, not a new 3.10.1 run. Video/audio quality, speed and VRAM use are not
changed or newly validated. Public CI runs separately; its counts must not be
added to local results.

## Preservation and update

Sampling v6 / Graph v4, Run Storage and Take schemas, node IDs, widget order
and official workflows are unchanged. Manager is still optional/default-OFF.
Old v5 and unsafe v6 Takes stay readable without conversion. Compatible existing
Takes and workflows need no migration or new Run.

**GitHub-only release: Registry submission is held pending the manual review of
3.10.0.** The automatic release job only publishes and verifies GitHub assets.
The reviewed 3.10.0 Registry package is not replaced or resubmitted. This release
does not claim Registry approval or availability in its version selector.

- ComfyUI Manager: for a Git-tracked installation, use its repository update
  action and verify the version. A Registry-backed installation may not offer
  3.10.1 while submission is held; use the GitHub ZIP.
- Manual Git installation: open `custom_nodes/ComfyUI-H3-Continuum` inside your
  ComfyUI installation and update that checkout with `git pull`.
- ZIP installation: replace only the custom-node package files from the 3.10.1
  ZIP. Keep Run Storage, user workflows and management data. Avoid duplicate
  installed copies.
- Fully restart ComfyUI and hard-refresh the browser with **Ctrl+F5** so Python
  and JavaScript both use the repair. No Take deletion or new Run is needed.

## 日本語

HTTP 409を一律「別タブで更新された」と表示する不具合を修正しました。
本当の更新競合だけを専用コードで識別し、その他はサーバーの具体的な拒否理由を
表示します。日本語UIでもサーバー由来の理由は英語の原文です。読取専用・整合性検査・
実行中Runなどの拒否条件や、Sampling v6の安全判定は緩めていません。

CPU・JavaScriptは **2,214成功／2スキップ／失敗0**、CUDA初期化試行0。
Chromeの英語・日本語UIで実際の更新競合とRun重複登録を確認しました。
その他の理由はCPU・API・JavaScriptで確認し、既存データを壊して再現していません。
既存Take・Workflow・設定184ファイルと公式Workflow 21ファイルを保護しました。
今回の新しいGPU生成はありません。3.10.0の4 Queue検証とは別の結果です。

Registryへの送信は3.10.0の手動レビュー結果が出るまで保留し、今回はGitHubのみで配布します。
ManagerのRegistry版一覧に3.10.1が出ない場合はGitHub ZIPを使用してください。
Git導入ではComfyUI内の `custom_nodes/ComfyUI-H3-Continuum` で更新できます。
更新後はComfyUIを完全に再起動し、Ctrl+F5でブラウザーを更新してください。
既存Run／Takeの削除、Workflow変更、新規Runの作成は不要です。
