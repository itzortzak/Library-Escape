const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--enable-unsafe-swiftshader']});
 try{
  const context=await browser.newContext({viewport:{width:1280,height:800}});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8766');
  await page.locator('#collection').waitFor();
  assert.equal(await page.locator('#collection').inputValue(),'v3-reviewed');
  assert.equal(await page.evaluate(()=>V3_DATA.length),1350);
  assert.equal(await page.evaluate(()=>V3_REVIEWED.flat().length),968);
  assert.equal(await page.evaluate(()=>available().reduce((n,r)=>n+r.count,0)),30);
  // Validate rendering of every school reference, not just a random session.
  const missingSources=await page.evaluate(()=>V3_DATA.filter(q=>{const div=document.createElement('div');div.innerHTML=passage(q);const links=[...div.querySelectorAll('a[href]')];const refs=q.sourceRefs?.length?q.sourceRefs:[{url:q.sourceUrl}];return links.length!==refs.length||links.some(a=>!v3SafeSource(a.href))}).map(q=>q.id));
  assert.deepEqual(missingSources,[]);
  assert.equal(await page.evaluate(()=>v3SafeSource('https://dev.old.ebooks.edu.gr/modules/ebook/show.php/DSGL-A111/262/1917,6376/')),true);
  assert.equal(await page.evaluate(()=>v3SafeSource('https://ebooks.edu.gr.example.org/ebooks/')),false);
  await page.selectOption('#count','all');
  assert.equal(await page.evaluate(()=>available().reduce((n,r)=>n+r.count,0)),968);
  await page.selectOption('#collection','v3-all');
  assert.equal(await page.evaluate(()=>available().reduce((n,r)=>n+r.count,0)),1350);
  await page.selectOption('#period','Ξένη λογοτεχνία');
  assert(await page.evaluate(()=>available().flatMap(r=>r.questions).every(q=>q.periods.includes('Ξένη λογοτεχνία'))));
  await page.selectOption('#period','all');
  await page.selectOption('#author',{label:'Δημήτριος Βικέλας'});
  assert(await page.evaluate(()=>available().flatMap(r=>r.questions).length>0&&available().flatMap(r=>r.questions).every(q=>q.author==='Δημήτριος Βικέλας')));
  await page.selectOption('#author','all');
  await page.selectOption('#work','all');
  await page.selectOption('#count','3');
  for(const level of ['1','2','3']){
   await page.selectOption('#level',level);
   assert.equal(await page.evaluate(()=>available().reduce((n,r)=>n+r.count,0)),30);
   assert(await page.evaluate(l=>available().flatMap(r=>r.questions).every(q=>q.level===+l),level));
  }
  await page.selectOption('#level','all');
  // Two short sessions from the actual game selection function, not its replica.
  const selection=await page.evaluate(()=>{
   v3Seen.clear();delStore(V3_SEEN);
   const a=selectV3Rooms(available(),'all').flatMap(r=>r.questions);
   const b=selectV3Rooms(available(),'all').flatMap(r=>r.questions);
   return {a:a.map(q=>q.id),b:b.map(q=>q.id),levels:a.reduce((o,q)=>(o[q.level]=(o[q.level]||0)+1,o),{})};
  });
  assert.equal(selection.a.length,30);assert.equal(selection.b.length,30);
  assert.equal(new Set([...selection.a,...selection.b]).size,60);
  assert.deepEqual(selection.levels,{1:10,2:10,3:10});
  await page.evaluate(()=>{v3Seen.clear();delStore(V3_SEEN)});
  await page.selectOption('#collection','v3-reviewed');
  await page.click('#go');
  assert.equal(await page.evaluate(()=>s.total),30);
  const positions=[0,0,0];
  for(let i=0;i<30;i++){
   await page.evaluate(()=>ask());
   const answer=await page.evaluate(()=>{
    const q=room().questions[s.k],buttons=[...document.querySelectorAll('[data-answer]')];
    const idx=buttons.findIndex(b=>b.textContent===q.correct);
    if(idx<0)throw Error('Correct answer missing');
    const links=[...document.querySelectorAll('#dialogBody a[href]')];
    if(!links.length||links.some(a=>!v3SafeSource(a.href)))throw Error('Missing source link');
    buttons[idx].click();return idx;
   });positions[answer]++;
   await page.click('#next');
   if(i===10){
    const before=await page.evaluate(()=>({right:s.right,pos:s.pos,k:s.k,target,cam}));
    await page.reload();await page.click('#resumeGame');
    assert.deepEqual(await page.evaluate(()=>({right:s.right,pos:s.pos,k:s.k,target,cam})),before);
   }
   if(await page.evaluate(()=>isGate())){
    await page.evaluate(()=>gate());
    await page.fill('#gateCode',await page.evaluate(()=>s.marks.slice(-3).join('')));
    await page.click('#unlock');await page.evaluate(()=>hide());
   }
  }
  assert.equal(await page.evaluate(()=>s.right),30);
  assert.equal(await page.evaluate(()=>s.fragments.length),10);
  await page.evaluate(()=>finalGate());
  await page.evaluate(()=>{[...document.querySelectorAll('[data-frag]')].sort((a,b)=>parseInt(a.textContent)-parseInt(b.textContent)).forEach(b=>b.click())});
  await page.click('#finishGate');assert.equal(await page.evaluate(()=>s.done),true);
  assert.deepEqual(errors,[]);
  // Mobile viewport: choose and answer via the visible puzzle controls.
  const phone=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const p=await phone.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:8766');
  await p.selectOption('#count','1');await p.click('#go');await p.evaluate(()=>ask());
  const mobile=await p.evaluate(()=>{
   const q=room().questions[s.k],buttons=[...document.querySelectorAll('[data-answer]')],idx=buttons.findIndex(b=>b.textContent===q.correct);
   return {idx,kind:puzzleKind(),scroll:document.documentElement.scrollWidth,width:innerWidth};
  });assert(mobile.idx>=0);assert(mobile.scroll<=mobile.width+2,'mobile horizontal overflow');
  if(mobile.kind===0)await p.locator('[data-answer="'+mobile.idx+'"]').click();
  else if(mobile.kind===1||mobile.kind===4){await p.locator('[data-pick="'+mobile.idx+'"]').click();await p.click('#confirmPick')}
  else{for(let i=0;i<mobile.idx;i++)await p.click('#dialNext');await p.click('#dialSelect')}
  assert.equal(await p.evaluate(()=>s.right),1);
  assert.deepEqual(errors,[]);
  console.log('PASS: v3 menu, 1350/968 counts, period and level filters, 60 unique selections, 30-answer 10-room escape, source links, save/resume, mobile visible controls. Correct positions:',positions);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
