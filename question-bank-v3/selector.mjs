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
 const rooms=[...new Set(bank.map(q=>q.room))];const signatures=new Set(),positions=[0,0,0];let checked=0;
 for(let s=1;s<=100;s++){const a=selectQuestions(bank,{rng:rngFor(s)});assert(a.length===30,"count");assert(new Set(a.map(q=>q.id)).size===a.length,"duplicate");for(const room of rooms)assert(a.filter(q=>q.room===room).length===3,"room");for(const q of a){assert(q.options.length===3&&q.options.includes(q.correct),"answer integrity");positions[q.options.indexOf(q.correct)]++;}signatures.add(a.map(q=>q.id).sort().join("|"));const b=selectQuestions(bank,{seenIds:a.map(q=>q.id),rng:rngFor(s+100)});assert(b.every(q=>!a.some(p=>p.id===q.id)),"repeat before exhaustion");checked+=a.length;}
 assert(signatures.size>90,"session variety");assert(positions.every(n=>n>0),"correct option positions");return{questions:bank.length,rooms:rooms.length,sessions:100,checkedSelections:checked,distinctQuestionSets:signatures.size,correctOptionPositions:positions,repeatBeforeExhaustion:false};
}
