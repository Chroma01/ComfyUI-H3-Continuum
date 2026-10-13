# Public development log

## 2026-10-13 — package 3.9.3 temporary storage

- Re-review the scratch storage proposal against actual Finalize, Decode Cache and Core settings lifecycles. Implement server-side settings with revision checks, queue coordination, immutable directory identities and no silent disk fallback.
- Add read-only status and explicit cleanup paths. Preserve live aliases and unknown owners; track detached helper disk entries using only metadata and weak leases.
- Add a ComfyUI settings panel without draw-loop scans or periodic polling. Keep existing workflow controls and node registration.
- Add CPU, real HTTP and filesystem regressions plus a Windows-focused CI storage gate. The real-Core CPU candidate passed 1,740 cases with 2 skips and the 2 existing Inspector expected failures, without CUDA initialization. Standard compile/runtime and actual Core/frontend settings save/reload/cleanup checks passed. All 25 JSON/ZIP assets retain their bytes; see PACKAGE_VALIDATION.txt for scope and platform limits.

## 2026-10-13 — Issue #30 frontend hotfix, package 3.9.2

- Limit production changes to baseline-free Review snapshot skipping, one Reference selection notification per connected Sampler, and dimension checks before resizing the Reference helper. Align package metadata and current public guidance with 3.9.2; retain 3.9.1 records as history.
- Keep Review drawing-time upstream monitoring when a baseline exists and fresh synchronous Take/Queue checks. Preserve native callbacks, immediate saved assignment values, public widget/socket order and official workflow bytes.
- Add frontend regression coverage for upstream widget/link edits, rapid Reference selections, All/Off with future assignments, helper reconfiguration and independent helpers/Samplers. Track the independent Inspector reconfigure bug at 2 and 100 passes with explicit expected failures; one-pass refresh must succeed.
- Browser checks use isolated Chromium DOM and graph fixtures without generation. Full ComfyUI canvas, mobile performance and live workflow acceptance remain separate checks.
- Validation: 1,703 CPU/JavaScript regression cases passed, 2 skipped and 2 expected failures for the independent Inspector bug; zero CUDA initialization attempts. Offline runtime planning and twelve-node registration passed. In isolated Chromium, 600 baseline-free draw callbacks made zero snapshots (previously 600); 30 connected Reference checks notified the Sampler 30 times (previously 60), with zero same-dimension resize calls (previously 30). DOM rebuilds remain, and mobile freeze resolution is unconfirmed.

- Final 3.9.2 candidate CPU gate passed 1,703 cases with 2 skips and 2 explicit Inspector expected failures. The actual Core/frontend/LiteGraph browser smoke passed checkbox interactions, Prompt/link/Bypass edit/restore and native assignment graph reload without submitting a prompt. This desktop headless/model-free check is separate from UI file-save, mobile hardware and stored-Take acceptance.

## 2026-10-04 — V3.9 stability patch, package 3.9.1

- Preserve Second Pass audio/mixed-keyframe conditions and inherit the conditioning and References belonging to the selected Review output.
- Strengthen Take compatibility with Sampling Contract v6 / Graph Contract v4. Retain old v5 history without adopting its prefixes into new generation.
- Align Review Driving Audio with the original physical-group time range. Prefer Core audio resampling and document the same-object VAE mutation/cache limitation.
- Keep public V3.9 node IDs, official workflows and stored State/Session formats unchanged. LoRA Plan is not part of this patch.
- Full CPU validation: 1,696 passed / 1 skipped / no failures, with zero CUDA initialization attempts. Offline layout/planning and twelve-node registration passed.
- Targeted Review Second Pass and integrated generation/reuse GPU checks passed. Browser acceptance remains pending; optional latent-upscale artifacts remain a separate issue.
- Put the patch summary and v5-to-v6 restart instructions at the beginning of both language READMEs.
- Replace workstation paths and private operational history in public documentation with portable instructions and public validation summaries. Original development records are preserved outside the publication checkout.
- Mark the eighteen real-Core integration cases as dependency skips in standalone CI when ComfyUI Core is absent. They still execute with Core installed; broken Core dependencies remain test failures. Production code is unchanged.
- Release-preparation checks for the affected tests and package metadata: 66 passed with real Core; 48 passed / 18 dependency skips without Core. Both CPU gates had zero CUDA initialization attempts.
- GitHub Actions confirmed 1,676 passed / 21 skipped / no failures in standalone CI. Eighteen skips require real Core; the remaining three reflect existing platform/fixture limits. Prepare the versioned GitHub Release with English/Japanese repair and migration notes; Registry publication remains separate.
- Reconcile PACKAGE_VALIDATION.txt, PACKAGE_INFO_JA.txt and docs/VALIDATION_JA.md with package 3.9.1, the actual CPU/CI scopes, v5 migration and Release status. Retain the original V3.9.0/V2 text under explicit historical sections. Documentation corrections follow the fixed v3.9.1 release tag on main; runtime and official workflow bytes are unchanged.

Earlier product behavior is described in CHANGELOG.md and the historical Release/tag versions. This log contains public engineering summaries rather than private operational records.
