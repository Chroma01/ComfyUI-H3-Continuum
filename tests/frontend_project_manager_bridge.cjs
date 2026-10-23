// Reuse the existing real-frontend fixture, without changing its Queue adapter.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = process.env.H3_TEST_ROOT || path.resolve(__dirname, '..');
const context = {require, __dirname: path.join(ROOT, 'tests'), process, console,
    setTimeout, clearTimeout, setImmediate, structuredClone};
const harness = fs.readFileSync(path.join(ROOT, 'tests/frontend_review_queue.cjs'), 'utf8').split('(async()=>{')[0];
vm.runInNewContext(harness + '\nglobalThis.fixture = {environment, project};', context);
const {environment, project} = context.fixture;
const freshId = '650e8400-e29b-41d4-a716-446655440111';
const freshRun = `run_${freshId.replaceAll('-', '')}`;
const results = [];
const response = value => ({ok: true, status: 200, json: async () => structuredClone(value)});
const missing = () => ({ok: false, status: 404, json: async () => null});
const queueEmpty = () => response({queue_running: [], queue_pending: []});
const serialized = n => JSON.stringify(n.serialize());
const fetchSaved = (e, saved) => e.setFetchHook(url => String(url).startsWith('/queue')
    ? queueEmpty() : saved ? response(saved) : missing());
async function test(name, fn) {
    const e = environment();
    try {
        const n = e.makeNode(312, 'fixture', 'H3ContinuumSamplerV39');
        await e.load(n, project(1));
        await fn(e, n, n.__h3ContinuumManagerBridge);
        results.push({name, pass: true});
    } catch (error) { results.push({name, pass: false, error: error.stack}); }
    finally { e.close(); }
}
(async () => {
await test('dormant bridge does not alter workflow, Queue adapter or listeners', async (e,n,b) => {
    const before = serialized(n), fetches = e.getFetchCount(), queue = e.api.queuePrompt;
    const widgets = n.widgets.length;
    for (let i = 0; i < 100; i++) b.describe();
    assert.equal(serialized(n), before);
    assert.equal(n.widgets.length, widgets);
    assert.equal(e.getFetchCount(), fetches);
    assert.equal(e.api.queuePrompt, queue);
    assert.equal(Object.keys(n).includes('__h3ContinuumManagerBridge'), false);
    assert.equal(b.describe().revision_id, 'r1-g1');
    assert.equal(b.describe().takes[0].read_only, false);
});
await test('new trial clears Run Name and prior Take as one explicit preparation', async (e,n,b) => {
    e.w(n,'take_action').value = 'Continue From Here'; e.w(n,'take_revision_id').value = 'r1-g1';
    e.w(n,'reroll_from_chunk').value = 'Chunk 2'; e.w(n,'reroll_nonce').value = 7;
    const seed = e.w(n,'base_seed').value;
    fetchSaved(e, null);
    const result = await b.prepareRun({run_name:'', project_id:freshId});
    assert.equal(result.prepared, true); assert.equal(result.queued, false);
    assert.equal(result.busy, false);
    assert.equal(e.w(n,'run_name').value, ''); assert.equal(e.w(n,'project_id').value, freshId);
    assert.equal(b.describe().run_name, freshRun);
    assert.equal(e.w(n,'take_action').value, 'Automatic'); assert.equal(e.w(n,'take_revision_id').value, '');
    assert.equal(e.w(n,'reroll_from_chunk').value, 'Auto'); assert.equal(e.w(n,'reroll_nonce').value, 0);
    assert.equal(e.w(n,'base_seed').value, seed); assert.equal(e.submissions.length, 0);
    assert.equal(n.__h3ContinuumTakeProject, null);
});
await test('savepoint uses existing Continue action without Queue or history mutation', async (e,n,b) => {
    const saved = project(2), original = JSON.stringify(saved); fetchSaved(e,saved);
    const result = await b.prepareRun({run_name:'fixture',project_id:'',revision_id:'r1-g1',group:{physical_group:1,start:1,end:1}});
    assert.equal(result.prepared,true); assert.equal(e.submissions.length,0);
    assert.equal(e.w(n,'take_action').value,'Continue From Here');
    assert.equal(e.w(n,'take_revision_id').value,'r1-g1'); assert.equal(e.w(n,'take_group').value,1);
    assert.equal(e.w(n,'generation_mode').value,'Review Each Chunk');
    assert.equal(n.__h3ContinuumHistoryOpen,true);
    assert.equal(JSON.stringify(saved), original);
    await e.queue(n);
    assert.equal(e.submissions[0].data.output['312'].inputs.take_revision_id,'r1-g1');
});
await test('other named Run can be prepared without inventing generation settings', async (e,n,b) => {
    fetchSaved(e,project(1,3,'other','other-run'));
    await b.prepareRun({run_name:'other-run',project_id:'',revision_id:'other-g1'});
    assert.equal(e.w(n,'run_name').value,'other-run');
    assert.equal(e.w(n,'take_revision_id').value,'other-g1');
    assert.equal(n.__h3ContinuumReviewedSettings,undefined);
    assert.equal(n.__h3ContinuumReviewedSettingsKey,undefined);
});
await test('same Run edited settings guard is not bypassed', async (e,n,b) => {
    e.w(n,'base_seed').value++; const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g1'}),/Settings changed/);
    assert.equal(serialized(n),before);
});
for (const version of [5,6]) await test(`read-only v${version} is never promoted`,async(e,n,b)=>{
    const p=project(1); p.group_revisions[0].sampling_contract_version=version;
    p.group_revisions[0].generation_reusable=false; fetchSaved(e,p); const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g1'}),/cannot be reused/);
    assert.equal(serialized(n),before);
});
for (const name of ['run_name','project_id','take_action','reroll_from_chunk']) await test(`external ${name} is preserved and rejected`,async(e,n,b)=>{
    n.inputs.push({name,link:99}); const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/local widgets/);
    assert.equal(serialized(n),before); assert.equal(n.inputs[0].link,99);
});
await test('other Sampler duplicate Project ID is rejected',async(e,n,b)=>{
    const other=e.makeNode(900,'other','H3ContinuumSamplerV39'); e.w(other,'project_id').value=freshId;
    const before=serialized(n); await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/Another Sampler/);
    assert.equal(serialized(n),before);
});
await test('other Sampler duplicate resolved Run is rejected',async(e,n,b)=>{
    e.makeNode(900,'FIXTURE','H3ContinuumSamplerV39');
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g1'}),/Another Sampler/);
});
await test('existing Run cannot be mistaken for a new trial',async(e,n,b)=>{
    fetchSaved(e,project(1,3,'existing',freshRun)); const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/already exists/);
    assert.equal(serialized(n),before);
});
for(const kind of ['queue_running','queue_pending']) await test(`${kind} blocks preparation without widget mutation`,async(e,n,b)=>{
    const queued=[0,'queued',{312:{class_type:n.comfyClass,inputs:{run_name:'fixture'}}},{},['312']];
    e.setFetchHook(()=>response({queue_running:[],queue_pending:[],[kind]:[queued]})); const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/queued or running/);
    assert.equal(serialized(n),before);
});
await test('a different Sampler queue leaves this new trial available',async(e,n,b)=>{
    const queued=[0,'unrelated',{999:{class_type:n.comfyClass,inputs:{run_name:'unrelated'}}},{},['999']];
    e.setFetchHook(url=>String(url).startsWith('/queue')?response({queue_running:[queued],queue_pending:[]}):missing());
    await b.prepareRun({run_name:'',project_id:freshId}); assert.equal(b.describe().run_name,freshRun);
});
await test('Queue appearing after history read is rejected',async(e,n,b)=>{
    let checks=0; e.setFetchHook(url=>{
        if(!String(url).startsWith('/queue'))return missing();
        checks++; return response({queue_running:[],queue_pending:checks===1?[]:[[0,'late',{312:{class_type:n.comfyClass,inputs:{run_name:'fixture'}}},{},['312']]]});
    });
    const before=serialized(n); await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/queued or running/);
    assert.equal(serialized(n),before);
});
for(const [label,accepted,blocked] of [
    ['empty accepted outputs',[],false],
    ['unrelated output accepted',['other-output'],false],
    ['downstream output accepted',['target-output'],true],
])await test(`actual Queue output boundary: ${label}`,async(e,n,b)=>{
    const output={
        312:{class_type:n.comfyClass,inputs:{run_name:'fixture'}},
        'other-output':{class_type:'SaveImage',inputs:{}},
        'target-output':{class_type:'SaveImage',inputs:{images:['312',0]}},
    };
    e.setFetchHook(url=>String(url).startsWith('/queue')
        ?response({queue_running:[],queue_pending:[[0,'partial',output,{},accepted]]}):missing());
    const before=serialized(n), pending=b.prepareRun({run_name:'',project_id:freshId});
    if(blocked){await assert.rejects(pending,/queued or running/);assert.equal(serialized(n),before);}
    else {await pending;assert.equal(b.describe().run_name,freshRun);}
});
for(const edit of ['settings','selection','graph','removed']) await test(`${edit} change during request cancels preparation`,async(e,n,b)=>{
    let release; e.setFetchHook(()=>new Promise(resolve=>{release=resolve;}));
    const pending=b.prepareRun({run_name:'',project_id:freshId});
    if(edit==='settings')e.w(n,'base_seed').value++;
    if(edit==='selection')n.__h3ContinuumBrowseRevision='a-different-take';
    if(edit==='graph')e.app.graph={_nodes:[]};
    if(edit==='removed')n.graph._nodes=[];
    const before=serialized(n); release(await queueEmpty());
    await assert.rejects(pending,/changed|loading/); assert.equal(serialized(n),before);
});
await test('invalid Queue information fails closed',async(e,n,b)=>{
    e.setFetchHook(()=>response({})); const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/Could not verify/);
    assert.equal(serialized(n),before);
});
await test('same panel action cannot overlap itself',async(e,n,b)=>{
    let release; e.setFetchHook(()=>new Promise(resolve=>{release=resolve;}));
    const first=b.prepareRun({run_name:'',project_id:freshId});
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId}),/already in progress/);
    release(response({})); await assert.rejects(first,/Could not verify/);
    assert.equal(b.describe().busy,false);
});
await test('changed group and missing ancestry are rejected',async(e,n,b)=>{
    fetchSaved(e,project(2));
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g1',group:{physical_group:2,start:2,end:2}}),/group changed/);
    const p=project(2);p.group_revisions.shift();fetchSaved(e,p);
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g2'}),/cannot be reused/);
});
await test('Run response identity must match the requested history',async(e,n,b)=>{
    fetchSaved(e,project(1,3,'r1','wrong-run'));
    await assert.rejects(b.prepareRun({run_name:'fixture',revision_id:'r1-g1'}),/identity or provenance/);
});
await test('closed Manager cannot begin preparation',async(e,n,b)=>{
    const before=serialized(n), count=e.getFetchCount();
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId,isCurrent:()=>false}),/cancelled/);
    assert.equal(serialized(n),before);assert.equal(e.getFetchCount(),count);
});
for(const at of ['history','final-queue'])await test(`closing Manager during ${at} prevents application`,async(e,n,b)=>{
    let current=true, checks=0;
    e.setFetchHook(url=>{
        if(!String(url).startsWith('/queue')) {
            if(at==='history')current=false;
            return missing();
        }
        if(++checks===2 && at==='final-queue')current=false;
        return queueEmpty();
    });
    const before=serialized(n);
    await assert.rejects(b.prepareRun({run_name:'',project_id:freshId,isCurrent:()=>current}),/cancelled/);
    assert.equal(serialized(n),before);assert.equal(b.describe().busy,false);
});
if(process.argv[2])await test('actual Python Manager savepoint prepares the real producer Take',async(e,n,b)=>{
    const fixture=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
    const saved=fixture.history, target=fixture.target;
    e.w(n,'run_name').value=saved.run_name;
    await e.load(n,saved);
    fetchSaved(e,saved);
    const original=JSON.stringify(saved), beforeQueue=e.submissions.length;
    assert(b.describe().takes.some(item=>item.revision_id===target.revision_id));
    const prepared=await b.prepareRun(target);
    assert.equal(prepared.prepared,true);assert.equal(prepared.queued,false);
    assert.equal(e.submissions.length,beforeQueue);
    assert.equal(e.w(n,'take_revision_id').value,target.revision_id);
    assert.equal(e.w(n,'take_group').value,target.group.physical_group);
    assert.equal(e.w(n,'take_action').value,'Continue From Here');
    assert.equal(JSON.stringify(saved),original);
    await e.queue(n);
    const inputs=e.submissions.at(-1).data.output['312'].inputs;
    assert.equal(inputs.take_revision_id,target.revision_id);
    assert.equal(inputs.take_group,target.group.physical_group);
    assert.equal(inputs.take_action,'Continue From Here');
    assert.equal(inputs.reroll_from_chunk,'Auto');
});
console.log(JSON.stringify(results,null,2));
if(results.some(item=>!item.pass))process.exitCode=1;
})();
