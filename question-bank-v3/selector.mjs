// Experimental selector; not yet wired into the production game.
export function shuffle(items,rng=Math.random){const a=[...items];for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
export function selectQuestions(bank,{rooms=[...new Set(bank.map(q=>q.room))],perRoom=3,level=null,seenIds=[],rng=Math.random}={}){
 if(!Number.isInteger(perRoom)||perRoom<1)throw Error("Invalid perRoom");
 const seen=new Set(seenIds),used=new Set(),workCounts=new Map(),result=[];
 const unique=[...new Map(bank.map(q=>[q.id,q])).values()];
 const pools=new Map([...new Set(rooms)].map(room=>[room,unique.filter(q=>q.room===room&&(level===null||q.level===level))]));
 for(let round=0;round<perRoom;round++)for(const room of shuffle([...pools.keys()],rng)){
 const candidates=shuffle(pools.get(room).filter(q=>!used.has(q.id)),rng);
 const key=q=>`${q.author}\u0000${q.work}`;
 candidates.sort((a,b)=>Number(seen.has(a.id))-Number(seen.has(b.id))||(workCounts.get(key(a))||0)-(workCounts.get(key(b))||0));
 const q=candidates[0];if(!q)continue;used.add(q.id);workCounts.set(key(q),(workCounts.get(key(q))||0)+1);result.push({...q,options:shuffle(q.options,rng)});
 }
 return result;
}
export function runSelectionTests(bank){
 const assert=(x,msg)=>{if(!x)throw Error(msg);};
 const rngFor=s=>()=>{s=(Math.imul(s,1664525)+1013904223)>>>0;return s/4294967296;};
 const rooms=[0,1,2,3,4,5,6,7,8,9], results=[];
 for(const level of [null,1,2,3]){
  const eligible=bank.filter(q=>level===null||q.level===level);
  const pools=new Map(rooms.map(room=>[room,eligible.filter(q=>q.room===room)]));
  const minPool=Math.min(...[...pools.values()].map(p=>p.length));
  assert(minPool>=6,"insufficient level/room pool: "+level);
  const signatures=new Set(),positions=[0,0,0];let checked=0;
  for(let s=1;s<=100;s++){
   const a=selectQuestions(bank,{rooms,level,rng:rngFor(s+(level||0)*100)});
   assert(a.length===30,"count");assert(new Set(a.map(q=>q.id)).size===a.length,"duplicate");
   for(const room of rooms)assert(a.filter(q=>q.room===room).length===3,"room");
   for(const q of a){assert(q.options.length===3&&q.options.includes(q.correct),"answer integrity");assert(level===null||q.level===level,"wrong level");positions[q.options.indexOf(q.correct)]++;}
   signatures.add(a.map(q=>q.id).sort().join("|"));
   const b=selectQuestions(bank,{rooms,level,seenIds:a.map(q=>q.id),rng:rngFor(s+200+(level||0)*100)});
   assert(b.length===30,"second count");assert(b.every(q=>!a.some(p=>p.id===q.id)),"repeat before two full sessions");checked+=a.length;
  }
  assert(signatures.size>90,"session variety");assert(positions.every(n=>n>0),"correct option positions");
  const seen=new Set(),exhaustionSessions=Math.max(...[...pools.values()].map(p=>Math.ceil(p.length/3)));
  for(let s=0;s<exhaustionSessions;s++){
   const a=selectQuestions(bank,{rooms,level,seenIds:[...seen],rng:rngFor(s+800+(level||0)*100)});
   for(const room of rooms){const p=pools.get(room),selected=a.filter(q=>q.room===room),remaining=p.filter(q=>!seen.has(q.id)).length;assert(selected.length===3,"cycle room count");assert(selected.filter(q=>!seen.has(q.id)).length===Math.min(remaining,selected.length),"repeat before room exhaustion");}
   a.forEach(q=>seen.add(q.id));
  }
  assert(seen.size===eligible.length,"exhaustion coverage");
  results.push({level:level??"all",questions:eligible.length,minimumRoomPool:minPool,sessions:100,checkedSelections:checked,distinctQuestionSets:signatures.size,correctOptionPositions:positions,exhaustionSessions,distinctSeen:seen.size,repeatBeforeExhaustion:false});
 }
 return {questions:bank.length,rooms:rooms.length,results};
}
