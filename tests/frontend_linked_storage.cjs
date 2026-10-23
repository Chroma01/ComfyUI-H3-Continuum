// Use the existing lifecycle fixture and actual product JS, not copied guards.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = process.env.H3_TEST_ROOT || path.resolve(__dirname, '..');
const context = {require, __dirname:path.join(ROOT,'tests'), process, console,
  setTimeout, clearTimeout, setImmediate, structuredClone};
const harness = fs.readFileSync(path.join(ROOT,'tests/frontend_review_queue.cjs'),'utf8')
  .split('(async()=>{')[0]
  .replace('reviewSettingsChanged,synchronizeReviewQueue};',
    'reviewSettingsChanged,synchronizeReviewQueue,normalizeRunStorageState};');
vm.runInNewContext(harness+'\nglobalThis.fixture={environment,project};',context);
const results=[];
async function test(name, body) {
  const e=context.fixture.environment();
  try { await body(e);results.push({name,pass:true}); }
  catch(error) { results.push({name,pass:false,error:error.stack}); }
  finally { e.close(); }
}
function staleWidget(e,n,value) {
  if(value==='missing') n.widgets=n.widgets.filter(w=>w.name!=='run_storage');
  else e.w(n,'run_storage').value=value;
}
(async()=>{
for(const nodeClass of ['H3ContinuumSamplerV38','H3ContinuumSamplerV39']) {
 for(const widget of ['Save + Auto Resume','Off','missing']) {
  for(const storage of ['Save + Auto Resume','Off',['777',0]]) {
   for(const action of ['queue','normalize']) {
    await test(`${nodeClass} ${action}: widget ${widget}, API ${JSON.stringify(storage)}`,async e=>{
      const n=e.makeNode(312,'fixture',nodeClass);await e.load(n,context.fixture.project(3,3));
      const inputs=await e.inputs(n);
      staleWidget(e,n,widget);
      e.w(n,'reroll_from_chunk').value='Chunk 2';e.w(n,'reroll_from_chunk').callback?.('Chunk 2');
      e.w(n,'reroll_nonce').value=7;
      Object.assign(inputs,{run_storage:storage,reroll_from_chunk:'Chunk 2',reroll_nonce:7});
      let sent;
      if(action==='queue') {
        await e.api.queuePrompt(0,{output:{312:{class_type:nodeClass,inputs}},workflow:n.serialize()});
        sent=e.submissions.at(-1).data.output['312'].inputs;
      } else { e.f.normalizeRunStorageState(n,inputs);sent=inputs; }
      const off=storage==='Off';
      assert.deepEqual(sent.run_storage,storage);
      assert.equal(sent.reroll_from_chunk,off?'Auto':'Chunk 2');
      assert.equal(sent.reroll_nonce,off?0:7);
      assert.equal(e.w(n,'reroll_from_chunk').value,off?'Auto':'Chunk 2');
      assert.equal(e.w(n,'reroll_nonce').value,off?0:7);
    });
   }
  }
  await test(`${nodeClass}: connected socket ignores hidden ${widget}`,async e=>{
    const n=e.makeNode(312,'fixture',nodeClass);await e.load(n,context.fixture.project(3,3));
    staleWidget(e,n,widget);
    n.inputs.push({name:'run_storage',link:1,widget:{name:'run_storage'}});
    e.w(n,'reroll_from_chunk').value='Chunk 2';e.w(n,'reroll_from_chunk').callback?.('Chunk 2');
    e.w(n,'reroll_nonce').value=7;
    assert.equal(e.f.normalizeRunStorageState(n),true);
    assert.equal(e.w(n,'reroll_from_chunk').value,'Chunk 2');
    assert.equal(e.w(n,'reroll_nonce').value,7);
    assert.equal(n.properties.h3_continuum_regenerate_from,'Chunk 2');
  });
 }
}
console.log(JSON.stringify(results,null,2));if(results.some(r=>!r.pass))process.exitCode=1;
})();
