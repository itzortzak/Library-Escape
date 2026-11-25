const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--enable-unsafe-swiftshader']});
 const context=await browser.newContext();const page=await context.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765');
 await page.selectOption('#count','all');await page.click('#go');
 assert.equal(await page.evaluate(()=>s.total),240);
 for(let i=0;i<240;i++){
   await page.evaluate(()=>ask());
   await page.evaluate(()=>{const q=room().questions[s.k];const b=[...document.querySelectorAll('[data-answer]')].find(b=>b.textContent===q.correct);if(!b)throw Error('Missing correct answer');b.click()});
   await page.click('#next');
   if(i===95){
     const before=await page.evaluate(()=>({right:s.right,pos:s.pos,k:s.k,target,cam}));
     await page.reload();await page.click('#resumeGame');
     const after=await page.evaluate(()=>({right:s.right,pos:s.pos,k:s.k,target,cam}));assert.deepEqual(after,before);
   }
   if(await page.evaluate(()=>isGate())){
     await page.evaluate(()=>gate());
     await page.fill('#gateCode',await page.evaluate(()=>s.marks.slice(-3).join('')));await page.click('#unlock');
     await page.evaluate(()=>hide());
   }
 }
 assert.equal(await page.evaluate(()=>s.right),240);assert.equal(await page.evaluate(()=>s.fragments.length),10);
 await page.evaluate(()=>finalGate());
 await page.evaluate(()=>{[...document.querySelectorAll('[data-frag]')].sort((a,b)=>parseInt(a.textContent)-parseInt(b.textContent)).forEach(b=>b.click())});
 await page.click('#finishGate');assert.equal(await page.evaluate(()=>s.done),true);
 assert.deepEqual(errors,[]);console.log('PASS: 240 answers, 10 gates, final escape, localStorage reload; renderer:',await page.evaluate(()=>renderer.mode));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
