// Preview-only runtime. The existing 3D renderer and puzzle mechanics are retained.
const V3_ROOMS=Array.from({length:10},(_,r)=>V3_DATA.filter(q=>q.room===r));
const V3_REVIEWED=V3_ROOMS.map(room=>room.filter(q=>q.reviewed));
const V3_PERIODS=[...new Set(V3_DATA.flatMap(q=>q.periods))].sort((a,b)=>a.localeCompare(b,'el'));
const V3_SEEN='literary-room-v3-preview-seen';
let v3Seen=new Set();
try{const old=JSON.parse(getStore(V3_SEEN)||'[]');if(Array.isArray(old))v3Seen=new Set(old.filter(id=>typeof id==='string'));}catch{}
bankFor=function(collection){return collection==='v3-all'?V3_ROOMS:V3_REVIEWED};
const v3PeriodMatches=(q,p)=>p==='all'||q.periods.includes(p);
available=function(){
 const bank=bankFor($('collection').value),p=$('period').value,a=$('author').value,w=$('work').value,d=$('level').value,n=$('count').value;
 return [...document.querySelectorAll('[data-room]:checked')].map(x=>+x.value).map(r=>({r,questions:bank[r].filter(q=>v3PeriodMatches(q,p)&&(a==='all'||q.author===a)&&(w==='all'||q.work===w)&&(d==='all'||q.level===+d))})).filter(x=>x.questions.length).map(x=>({...x,count:n==='all'?x.questions.length:Math.min(+n,x.questions.length)}));
};
filterValues=function(){
 const b=bankFor($('collection').value).flat().filter(q=>v3PeriodMatches(q,$('period').value)),prevA=$('author').value,prevW=$('work').value;
 const fill=(id,values,prev,label)=>{
  const el=$(id);el.replaceChildren(new Option(label,'all'));
  for(const v of [...new Set(values)].filter(Boolean).sort((a,b)=>a.localeCompare(b,'el')))el.add(new Option(v,v));
  if([...el.options].some(x=>x.value===prev))el.value=prev;
 };
 fill('author',b.map(q=>q.author),prevA,'Όλοι οι συγγραφείς');
 fill('work',b.filter(q=>$('author').value==='all'||q.author===$('author').value).map(q=>q.work),prevW,'Όλα τα έργα');
 updateMenu();
};
const legacyV3Passage=passage;
passage=function(q){
 if(!q.periods)return legacyV3Passage(q);
 const refs=q.sourceRefs?.length?q.sourceRefs:[{url:q.sourceUrl,locator:q.sourceLocator}];
 const links=refs.map(r=>{
  const safe=typeof r.url==='string'&&r.url.startsWith('https://ebooks.edu.gr/ebooks/');
  const title=esc(r.locator||'Σχολικό κείμενο');
  return '<li>'+(safe?'<a target="_blank" rel="noopener noreferrer" href="'+esc(r.url)+'">'+title+'</a>':title)+'</li>';
 }).join('');
 const body=q.category==='theory'?'<blockquote class="quote">«'+esc(q.text)+'»</blockquote>':'<p class="quote">'+esc(q.text)+'</p>';
 return body+'<p class="source">Πηγή: '+esc(q.source)+'</p><ul class="source">'+links+'</ul><p class="note">'+(q.category==='theory'?'Πρωτότυπο διδακτικό παράδειγμα θεωρίας.':q.reviewed?'Πρώτη επιμέλεια· απαιτείται τελική αξιολόγηση.':'Προσχέδιο προς φιλολογική επαλήθευση.')+'</p>';
};
const v3OldMenu=menu;
menu=function(){
 v3OldMenu();
 const el=$('collection');el.replaceChildren(new Option('Πρώτη επιμέλεια · '+V3_REVIEWED.flat().length+' γρίφοι','v3-reviewed'),new Option('Πλήρης υπό έλεγχο τράπεζα · '+V3_DATA.length+' γρίφοι','v3-all'));
 const periodEl=$('period');periodEl.replaceChildren(new Option('Όλες','all'));for(const p of V3_PERIODS)periodEl.add(new Option(p,p));
 const all=$('count').querySelector('option[value="all"]');if(all)all.textContent='Όλες οι διαθέσιμες';
 $('legacyImport')?.remove();
 const notice=document.createElement('p');notice.className='notice';notice.textContent='Δοκιμαστική έκδοση v3 — όχι οριστική σχολική δημοσίευση. Η πλήρης τράπεζα περιλαμβάνει ερωτήσεις που δεν έχουν ακόμη ελεγχθεί αναλυτικά. Για τα χωρία συμβουλεύσου το σχολικό ανθολόγιο από τους συνδέσμους.';
 $('dialogBody').prepend(notice);filterValues();
};
function selectV3Rooms(rows,level){
 const workCounts=new Map();
 const out=rows.map(({r,questions,count})=>{
  const pool=shuffle(questions),picked=[],used=new Set(),levelCounts={1:0,2:0,3:0};
  // Reset this eligible pool only when its previous cycle has ended.
  if(pool.every(q=>v3Seen.has(q.id)))for(const q of pool)v3Seen.delete(q.id);
  while(picked.length<count){
   const candidates=pool.filter(q=>!used.has(q.id));
   candidates.sort((a,b)=>Number(v3Seen.has(a.id))-Number(v3Seen.has(b.id))
    +(0) || (level==='all'?levelCounts[a.level]-levelCounts[b.level]:0)
    || (workCounts.get(a.work)||0)-(workCounts.get(b.work)||0));
   const q=candidates[0];if(!q)break;used.add(q.id);picked.push(q);levelCounts[q.level]++;workCounts.set(q.work,(workCounts.get(q.work)||0)+1);
  }
  for(const q of picked)v3Seen.add(q.id);
  if(level==='all')picked.sort((a,b)=>a.level-b.level);
  return {r,questions:picked};
 });
 putStore(V3_SEEN,JSON.stringify([...v3Seen]));return out;
}
const v3OldRestore=restore;
restore=function(data){
 const ids=new Set(V3_DATA.map(q=>q.id));
 if(!data?.s?.rooms?.every(r=>Array.isArray(r.questions)&&r.questions.every(q=>ids.has(q.id))))throw Error('Η αποθήκευση δεν ανήκει στη δοκιμαστική τράπεζα v3.');
 return v3OldRestore(data);
};
