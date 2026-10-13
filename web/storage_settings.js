import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const words = {
    en: {
        title: "H3 Continuum — Temporary Storage", open: "Manage temporary storage", close: "Close",
        path: "Scratch folder on the ComfyUI server", default: "Blank: keep existing temporary folders",
        volumes: "Choose a server storage location…", validate: "Validate", save: "Save", refresh: "Refresh",
        cleanup: "Delete unused temporary files", free: "Free", total: "Temporary files", in_use: "In use",
        deletable: "Deletable", unknown: "Protected / unknown", current: "Current", previous: "Previous",
        loading: "Loading…", saved: "Saved. New files will use this location; existing files stay where they are.",
        valid: "The selected folder passed the write and memory-map checks.", removed: "Deleted",
        files: "files", busy: "Wait until the running and pending queues are empty to change or clean storage.",
        readonly: "Shared storage is read-only in multi-user mode. The server operator manages this setting.",
        note: "This is the server's storage, not the browser device. File sizes are logical sizes, not SSD write totals. Moving to another folder on the same physical disk does not reduce its writes.",
        modes: "Keep choosing Auto / RAM / Disk-backed in Finalize, and Auto / RAM / Off in Decode Cache Helper. They are independent. Deleting a cache can require decoding and writing it again.",
        memory: "Available CPU RAM", last: "Last Finalize allocation", never: "No Finalize allocation in this process yet",
        noVolumes: "No storage candidates found. Enter an absolute server folder above.",
        unavailable: "Storage service unavailable (HTTP {status}). The old ComfyUI process may still be running, or the updated process failed to start. Check the startup log for a port already in use.",
        invalidResponse: "Empty or invalid storage response (HTTP {status}). Click Refresh to retry; if it persists, check the ComfyUI startup log.",
        networkError: "Cannot reach ComfyUI at the current address. Click Refresh to retry.",
        unloaded: "Storage data unavailable — click Refresh",
    },
    ja: {
        title: "H3 Continuum — 一時ストレージ", open: "一時ストレージを管理", close: "閉じる",
        path: "ComfyUIサーバー側の一時保存先フォルダー", default: "空欄：従来の一時保存先を使用",
        volumes: "サーバーのストレージ候補を選択…", validate: "検証", save: "保存", refresh: "更新",
        cleanup: "未使用の一時ファイルを削除", free: "空き容量", total: "一時ファイル量", in_use: "使用中",
        deletable: "削除可能", unknown: "保護中／判定不能", current: "現在", previous: "以前",
        loading: "読み込み中…", saved: "保存しました。新規ファイルから適用し、既存ファイルは元の場所で保持します。",
        valid: "指定先の書き込みとメモリマップの検証に成功しました。", removed: "削除済み",
        files: "ファイル", busy: "保存先の変更・削除は、実行中と待機中のQueueが空になるまでお待ちください。",
        readonly: "マルチユーザー運用では閲覧のみです。共有保存先はサーバー管理者が管理します。",
        note: "対象はブラウザー端末ではなくComfyUIサーバーです。表示容量はファイルの論理サイズで、SSDの累計書き込み量ではありません。同じ物理ディスク内の移動では、そのディスクへの書き込みは減りません。",
        modes: "使用方式は従来どおりFinalizeのAuto／RAM／Disk-backedと、Decode Cache HelperのAuto／RAM／Offで選びます。両者は独立しています。キャッシュ削除後は再デコード・再書き込みが必要になる場合があります。",
        memory: "利用可能なCPU RAM", last: "直近のFinalize確保", never: "このプロセスではまだFinalizeを実行していません",
        noVolumes: "候補を取得できません。上の欄にサーバー側の絶対パスを入力できます。",
        unavailable: "一時ストレージ機能に接続できません（HTTP {status}）。旧ComfyUIが残っているか、更新後の起動に失敗した可能性があります。起動ログのポート使用中エラーを確認してください。",
        invalidResponse: "一時ストレージの応答が空か、不正な形式です（HTTP {status}）。更新で再取得し、続く場合はComfyUI起動ログを確認してください。",
        networkError: "現在のアドレスでComfyUIへ接続できません。更新で再取得してください。",
        unloaded: "保存先の状態を取得できません — 更新で再取得",
    },
};

function language() {
    const locale = app.ui?.settings?.getSettingValue?.("Comfy.Locale") || navigator.language || "en";
    return String(locale).startsWith("ja") ? words.ja : words.en;
}

function size(bytes) {
    if (!Number.isFinite(bytes)) return "—";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(2)} KiB`;
    if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(2)} MiB`;
    return `${(bytes / 1024 ** 3).toFixed(2)} GiB`;
}

function element(tag, text, parent) {
    const result = document.createElement(tag);
    if (text != null) result.textContent = text;
    parent?.append(result);
    return result;
}

async function request(operation, body) {
    const path = `/h3-continuum/storage/${operation}`;
    const options = body === undefined
        ? { cache: "no-store" }
        : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    const t = language();
    let response;
    try {
        // Core retains the UI address, base path and user/auth handling.
        // Never replay a save or cleanup after an empty/failed response:
        // it may already have run on the server.
        response = await api.fetchApi(path, options);
    } catch {
        throw new Error(t.networkError);
    }
    let value;
    try { value = JSON.parse(await response.text()); } catch { /* Report HTTP status instead of a JSON parser exception. */ }
    if (!response.ok) {
        const fallback = response.status === 404 ? t.unavailable : `HTTP ${response.status}`;
        throw new Error(typeof value?.error === "string" ? value.error : fallback.replace("{status}", response.status));
    }
    if (!value || typeof value !== "object" || Array.isArray(value)
        || (operation === "status" && (typeof value.path !== "string" || !Number.isInteger(value.revision)
            || !Array.isArray(value.roots) || !Array.isArray(value.volumes) || !value.memory))) {
        throw new Error(t.invalidResponse.replace("{status}", response.status));
    }
    return value;
}

let opened = null;

export function openStorageDialog(event) {
    if (opened?.isConnected && opened.open) { opened.focus(); return; }
    const t = language();
    const dialog = element("dialog");
    opened = dialog;
    dialog.dataset.h3Storage = "true";
    dialog.setAttribute("aria-label", t.title);
    Object.assign(dialog.style, {
        width: "min(760px, 92vw)", maxHeight: "88vh", overflow: "auto", padding: "20px",
        background: "var(--comfy-menu-bg, #222)", color: "var(--fg-color, #ddd)",
        border: "1px solid var(--border-color, #666)", borderRadius: "10px",
    });
    const abort = new AbortController();
    element("h2", t.title, dialog);
    element("p", t.note, dialog);
    const label = element("label", t.path, dialog);
    const input = element("input", null, label);
    input.type = "text"; input.placeholder = t.default; input.setAttribute("aria-label", t.path);
    Object.assign(input.style, { display: "block", width: "100%", margin: "8px 0", padding: "8px", boxSizing: "border-box" });
    const volumeLabel = element("label", t.volumes, dialog);
    const select = element("select", null, volumeLabel);
    select.setAttribute("aria-label", t.volumes);
    Object.assign(select.style, { display: "block", width: "100%", minHeight: "34px", margin: "8px 0", boxSizing: "border-box" });
    const placeholder = element("option", t.loading, select); placeholder.value = "";
    const actions = element("div", null, dialog);
    Object.assign(actions.style, { display: "flex", gap: "8px", flexWrap: "wrap", margin: "12px 0" });
    const buttons = {};
    for (const action of ["validate", "save", "refresh", "cleanup", "close"]) {
        const button = element("button", t[action], actions);
        button.type = "button"; button.style.padding = "6px 10px"; buttons[action] = button;
    }
    const notice = element("p", null, dialog);
    const message = element("p", t.loading, dialog); message.setAttribute("role", "status");
    const memory = element("p", null, dialog);
    const last = element("p", null, dialog);
    const roots = element("div", null, dialog);
    element("p", t.modes, dialog);
    let state = null, pending = true, dirty = false, closed = false;

    function controls() {
        for (const name of ["validate", "save", "cleanup"]) buttons[name].disabled = pending || !state || state.busy || state.read_only;
        buttons.refresh.disabled = pending;
        input.disabled = pending || !state || !!state.read_only;
        select.disabled = input.disabled || !state?.volumes?.length;
        notice.textContent = state?.read_only ? t.readonly : state?.busy ? t.busy : "";
    }
    function render(value) {
        state = value;
        if (!dirty) input.value = value.path;
        select.replaceChildren();
        const option = element("option", value.volumes.length ? t.volumes : t.noVolumes, select); option.value = "";
        for (const volume of value.volumes) {
            const option = element("option", `${volume.path} (${t.free}: ${size(volume.free_bytes)})`, select);
            option.value = volume.path;
        }
        memory.textContent = `${t.memory}: ${size(value.memory.available_bytes)}`;
        last.textContent = value.last_backend
            ? `${t.last}: ${value.last_backend.backend}, ${size(value.last_backend.image_bytes)}${value.last_backend.path ? ` — ${value.last_backend.path}` : ""}`
            : t.never;
        roots.replaceChildren();
        for (const root of value.roots) {
            const section = element("section", null, roots);
            Object.assign(section.style, { borderTop: "1px solid #666", padding: "10px 0", overflowWrap: "anywhere" });
            element("strong", `${root.kind === "finalize" ? "Finalize" : "Decode Cache"} — ${root.current ? t.current : t.previous}`, section);
            element("div", root.path, section);
            element("div", `${t.total}: ${size(root.bytes)} · ${t.free}: ${size(root.free_bytes)}`, section);
            element("div", `${t.in_use}: ${size(root.in_use_bytes)} · ${t.deletable}: ${size(root.deletable_bytes)} · ${t.unknown}: ${size(root.unknown_bytes)}`, section);
            for (const error of root.errors) element("p", error, section);
        }
    }
    async function refresh() {
        try {
            const value = await request("status");
            if (!closed) render(value);
        } catch (error) {
            if (!closed) {
                state = null;
                select.replaceChildren();
                const option = element("option", t.unloaded, select); option.value = "";
            }
            throw error;
        }
    }
    async function perform(action) {
        if (pending) return;
        pending = true; controls(); message.textContent = t.loading;
        try {
            if (action === "refresh") { await refresh(); message.textContent = ""; }
            if (action === "validate") {
                const result = await request("validate", { path: input.value });
                message.textContent = result.path
                    ? `${t.valid} ${result.path} (${t.free}: ${size(result.roots[0]?.free_bytes)})`
                    : t.default;
            }
            if (action === "save") {
                await request("settings", { path: input.value, revision: state.revision });
                dirty = false; await refresh(); message.textContent = t.saved;
            }
            if (action === "cleanup") {
                const result = await request("cleanup", {});
                const files = result.roots.reduce((sum, root) => sum + root.removed_files, 0);
                const bytes = result.roots.reduce((sum, root) => sum + root.removed_bytes, 0);
                const errors = result.roots.flatMap(root => root.errors);
                await refresh(); message.textContent = `${t.removed}: ${files} ${t.files}, ${size(bytes)}${errors.length ? ` — ${errors.join("; ")}` : ""}`;
            }
        } catch (error) { if (!closed) message.textContent = error.message; }
        finally { pending = false; if (!closed) controls(); }
    }
    input.addEventListener("input", () => { dirty = true; });
    select.addEventListener("change", () => { if (select.value) { input.value = select.value; dirty = true; } });
    for (const name of ["validate", "save", "refresh", "cleanup"]) buttons[name].addEventListener("click", () => perform(name));
    buttons.close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("close", () => { closed = true; abort.abort(); dialog.remove(); if (opened === dialog) opened = null; }, { once: true });
    dialog.addEventListener("keydown", event => { if (event.key === "Escape") event.stopPropagation(); });
    api.addEventListener("status", event => {
        const remaining = event.detail?.exec_info?.queue_remaining;
        if (state && typeof remaining === "number") { state.busy = remaining > 0; controls(); }
    }, { signal: abort.signal });
    // Keep the native modal inside the settings dialog's DOM so Core's
    // outside-click handling does not dismiss the underlying settings page.
    const parent = event?.currentTarget?.closest?.('[role="dialog"], dialog') || document.body;
    parent.append(dialog); dialog.showModal(); controls();
    refresh().then(() => { if (!closed) message.textContent = ""; })
        .catch(error => { if (!closed) message.textContent = error.message; })
        .finally(() => { pending = false; if (!closed) controls(); });
}

app.registerExtension({
    name: "H3Continuum.TemporaryStorage",
    setup() {
        app.ui.settings.addSetting({
            id: "H3Continuum.Storage.Manager",
            name: "H3 Continuum: Temporary Storage",
            category: ["H3Continuum", "Storage", "Temporary Storage"],
            type: () => {
                const row = element("tr");
                const cell = element("td", null, row); cell.colSpan = 2;
                const button = element("button", language().open, cell);
                button.type = "button"; button.addEventListener("click", openStorageDialog);
                return row;
            },
            defaultValue: null,
        });
    },
});
