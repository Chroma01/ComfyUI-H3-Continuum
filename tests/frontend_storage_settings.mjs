import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

class Element extends EventTarget {
    constructor(tag) { super(); this.tag = tag; this.children = []; this.style = {}; this.dataset = {}; this.attributes = {}; this.value = ""; this.disabled = false; this.textContent = ""; }
    append(child) { child.parentElement = this; this.children.push(child); }
    replaceChildren() { for (const child of this.children) child.parentElement = null; this.children = []; }
    setAttribute(name, value) { this.attributes[name] = value; }
    get isConnected() { return this === document.body || !!this.parentElement?.isConnected; }
    closest() { let node = this; while (node) { if (node.tag === "dialog" || node.attributes.role === "dialog") return node; node = node.parentElement; } return null; }
    remove() { this.parentElement.children = this.parentElement.children.filter(x => x !== this); this.parentElement = null; }
    showModal() { this.open = true; }
    close() { this.open = false; this.dispatchEvent(new Event("close")); }
    focus() {}
    click() { if (!this.disabled) this.dispatchEvent(new Event("click")); }
}
const all = [];
globalThis.document = { createElement: tag => { const e = new Element(tag); all.push(e); return e; }, body: new Element("body") };
Object.defineProperty(globalThis, "navigator", { value: { language: "en" }, configurable: true });
let definition;
globalThis.__app = { ui: { settings: { getSettingValue: () => "en", addSetting: d => { definition = d; } } }, registerExtension: d => d.setup() };
const api = globalThis.__api = new EventTarget();
const requests = [];
let state = { path: "", revision: 0, busy: false, read_only: false, memory: { available_bytes: 8 * 1024 ** 3 }, roots: [], volumes: [], last_backend: null };
api.fetchApi = async (path, options) => {
    const action = path.split("/").at(-1);
    const body = options.body ? JSON.parse(options.body) : undefined;
    requests.push({ action, body });
    let value = structuredClone(state), ok = true;
    if (action === "settings") { assert.equal(body.revision, state.revision); state = { ...state, path: body.path, revision: state.revision + 1 }; value = state; }
    if (action === "validate") {
        ok = !body.path || body.path.startsWith("/");
        value = ok ? { path: body.path, roots: [{ free_bytes: 10 * 1024 ** 3 }] } : { error: "absolute path required" };
    }
    if (action === "cleanup") { assert.deepEqual(body, {}); value = { roots: [] }; }
    return { ok, status: ok ? 200 : 400, json: async () => value };
};
const source = fs.readFileSync(new URL("../web/storage_settings.js", import.meta.url), "utf8")
    .replace('import { app } from "../../scripts/app.js";', "const app = globalThis.__app;")
    .replace('import { api } from "../../scripts/api.js";', "const api = globalThis.__api;")
    .replace("export function openStorageDialog", "function openStorageDialog");
vm.runInThisContext(source);
const settings = new Element("section"); settings.setAttribute("role", "dialog"); document.body.append(settings);
const row = definition.type(); settings.append(row);
const launch = row.children[0].children[0];
const connected = tag => all.filter(x => x.tag === tag && x.isConnected);
const dialog = () => connected("dialog")[0];
const control = name => all.find(x => x.tag === "button" && x.isConnected && x.textContent === name);
const settle = () => new Promise(resolve => setImmediate(resolve));

launch.click(); await settle();
assert.equal(dialog().parentElement, settings, "preserve Core's settings dialog during native-modal interactions");
assert.equal(connected("input")[0].value, "");
assert.equal(requests.filter(r => r.action === "status").length, 1);
launch.click(); assert.equal(connected("dialog").length, 1, "no duplicate modal");
const input = connected("input")[0];
input.value = "relative"; input.dispatchEvent(new Event("input"));
control("Validate").click(); await settle();
assert.ok(all.some(x => x.isConnected && x.textContent === "absolute path required"));
input.value = "/scratch"; input.dispatchEvent(new Event("input"));
control("Save").click(); control("Save").click(); await settle();
assert.equal(requests.filter(r => r.action === "settings").length, 1, "one save while request is pending");
assert.equal(state.path, "/scratch");
const status = new Event("status"); status.detail = { exec_info: { queue_remaining: 1 } }; api.dispatchEvent(status);
assert.equal(control("Save").disabled, true);
assert.equal(control("Delete unused temporary files").disabled, true);
status.detail.exec_info.queue_remaining = 0; api.dispatchEvent(status);
control("Delete unused temporary files").click(); await settle();
assert.equal(requests.filter(r => r.action === "cleanup").length, 1);
control("Close").click(); assert.equal(connected("dialog").length, 0);
const before = requests.length;
for (let n = 0; n < 100; n++) {
    launch.click(); await settle();
    assert.equal(connected("input")[0].value, "/scratch");
    control("Close").click();
}
await settle();
assert.equal(requests.length - before, 100, "one fetch per open and no periodic polling");
assert.equal(connected("dialog").length, 0);
// A disposed dialog's handler must not receive later status events.
api.dispatchEvent(status);
assert.equal(requests.length - before, 100);
state.read_only = true;
launch.click(); await settle();
assert.equal(control("Save").disabled, true);
assert.equal(control("Delete unused temporary files").disabled, true);
assert.equal(connected("input")[0].disabled, true);
control("Close").click();
console.log("Temporary storage frontend: settings nesting, deduplication, errors, save, busy/read-only gates, cleanup, and 100 reopen cycles passed");
