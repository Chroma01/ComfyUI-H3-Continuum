# Public development log

## 2026-10-15 — package 3.9.6 / regeneration intent and automatic variations

- Separate saved manual regeneration intent from the legacy stale Chunk 1 / nonce 0 state. Retain earlier unmarked later-chunk/fixed-nonce settings, and clear intent metadata when Auto or a one-shot restart consumes it. No widget order or API inputs change.
- Bypass Core output caching only for Full Run explicit regeneration with Run Storage on and automatic nonce 0. Run Storage remains the authority for compatible prefixes, interrupted variations and new completed variations; its Sampling v6 checks are unchanged.
- Add restored-workflow Queue cases for both public Samplers and a CPU-only real-Core cache lookup gate. Keep historical unsafe/v5 Takes read-only and official workflow bytes unchanged. Full CPU gate: 1,908 passed / 2 skipped / 2 known Inspector expected failures; zero unexpected failures and CUDA initialization attempts. Normal ComfyUI browser save/reload retained Chunk 2 / nonce 5 and Chunk 1 / nonce 0 after history loading. Five new-Run GPU queues passed continuation, Chunk 2 regeneration and two identical Full Run / nonce 0 submissions; earlier Chunk 1 bytes were preserved. GPU scope: PyTorch, Spectrum OFF, 512x512, 8-step Turbo; all five media outputs fully decoded. See docs/REGENERATE_INTENT_V396.md. GitHub main/tag CI, Release asset integrity and Registry status are verified separately during publication.

## 2026-10-15 — package 3.9.5 / Issue #31 publication

Main Linux/Windows CI passed. Correct the tag-presence probe to branch on the API exit status: a missing-ref error body must not be treated as an existing commit SHA. Product code and accepted GPU signatures are unchanged.

Consolidate the Attention fix and finite Spectrum binding adapter on the exact 3.9.4 public source tree. Add a separate audited upstream Spectrum 0.2.29 profile without changing existing local-provider identities. Keep old unsafe history, public node IDs, contracts and all official workflows. CPU/GPU and publication checks are recorded separately in docs/ISSUE31_SAMPLING_SIGNATURES.md.

## 2026-10-14 — Issue #31 Phase 1, unpublished

- Final standard CPU validation: 1,777 passed / 1 skipped / 2 existing Inspector expected failures; no failures. All three standard commands recorded zero CUDA initialization attempts. Native PackedLayout, prompt planning and twelve-node registration checks passed.
- Limit production edits to the MODEL attention signature adapter in run_storage.py. Use already-loaded Core registries and implementation bindings; never import Core/Kitchen or execute an attention kernel during observation.
- Include both container functions and provider implementations/state without persistent addresses. Keep unrelated v6 signatures and every existing reuse guard; do not rewrite old unsafe manifests or raw files.
- Add real-Core CPU signature, clone/recreation, separate-process/hash-seed, mutation detection, prefix reuse and history immutability regressions. Kernel registration in CPU fixtures is structural evidence, not INT8 execution acceptance.
- GPU Review continuity, Spectrum/KJ execution, browser behavior and reporter-exact reproduction remain separate. No public node, official workflow, installed runtime, package version, commit or release changes.

## 2026-10-14 — package 3.9.4 Registry packaging repair

- Reconcile the actual Registry ZIP with its declared Manifest: include the Review restoration guide and exclude prompt-authoring source files.
- Add an exact archive file-set, CRC and hash gate before Registry upload using the same pinned publishing CLI. Preserve runtime code, public node IDs, workflows and saved data.
- Publish 3.9.4 as a separate version; keep prior GitHub tags and assets unchanged. Registry scan approval and real Manager installation remain independent of upload success.


## 2026-10-13 - 3.9.3 storage panel failure handling

- Reproduce the initial panel failure with an empty HTTP 404. Startup logs identified a stale process retaining the configured address/port while the updated backend failed to bind; the new frontend could still be served from updated files.
- Keep Core's request address, base path and user/auth handling. Add explicit HTTP/invalid-response guidance, an initialized full-width storage candidate field, safe disabled mutation controls and manual recovery without reloading the page. Do not retry save or cleanup automatically.
- Keep the backend and generation contracts unchanged. Core 0.39.0 CPU regression passed 1,740 cases with 2 skips and 2 existing expected Inspector failures; CUDA attempts were zero. The frontend 1.53.10 browser gate passed empty-response diagnostics, manual recovery, save and cleanup at an alternate host/port. See PACKAGE_VALIDATION.txt for scope.

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


## 2026-10-13 — Prepare 3.9.3 versioned downloads

- Add 3.9.3 and retained 3.9.2 Release, custom-node ZIP and checksum links to the current English/Japanese guides. Update the installation heading to 3.9.3 and retain the implemented settings screenshot and historical validation records.
- Refresh Registry then development manifests from saved bytes. The existing release-metadata/public-surface CPU gate passes 8 tests with zero CUDA initialization attempts; all 25 tracked JSON/ZIP assets retain their bytes.
- Product code, package metadata, public schemas and saved-data contracts are unchanged. GitHub Release/asset and Registry publication are verified separately; no new GPU, long-form performance or physical SSD-write validation is claimed.


## 2026-10-15 — Issue #31 Spectrum binding identity candidate

Added a dedicated, fail-closed Spectrum binding adapter without changing the generic observer, Sampling v6, runtime signature v1, Graph v4, public nodes, workflows or package version. The immutable config fields and audited source/loaded-callable contract identify generation; reviewed runtime history, counters and profile caches do not change persistent identity. Unsupported structures, additional attributes and altered implementations remain non-reusable. Existing unsafe Takes are preserved without migration. CPU and GPU evidence are recorded separately; no commit or publication is authorized.


Issue #31 Phase 3 validation: the final standard CPU entry point passed 1,834 tests, 1 skip and 2 existing expected Inspector failures, with zero CUDA initialization attempts. The 57 new Spectrum tests cover all 27 config fields, transient-state/process stability, implementation/extra-state refusal, unaffected v6 contract identity and old unsafe Take protection; the 36 Phase 1 attention tests also pass. Under one audited local provider implementation, both PyTorch+Spectrum and Kitchen+Spectrum persisted new Chunk 1 Takes and reused them from a separate Queue to generate Chunk 2, with unchanged prefix hashes, identical safe contracts and fully decodable 10-second AV output. This is a targeted local GPU gate, not acceptance of other providers, KJ, browser behavior, subjective quality or benchmarks. No commit, push or publication occurred.
