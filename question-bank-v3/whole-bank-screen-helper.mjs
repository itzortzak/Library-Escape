// Whole-bank screening helper. Heuristics are not a philological certification.
function screenBatch(files,coverage){
const norm=s=>String(s??"").normalize("NFC").trim().replace(/\s+/g," ").toLocaleLowerCase("el");
const hash=s=>{let a=2166136261,b=0x9e3779b9;for(const c of norm(s)){let n=c.codePointAt(0);a=Math.imul(a^n,16777619);b=Math.imul(b^n,0x85ebca6b)}return (a>>>0).toString(16).padStart(8,"0")+(b>>>0).toString(16).padStart(8,"0")};
const words=s=>[...new Set(norm(s).replace(/[^\p{L}\p{N} ]/gu," ").split(/\s+/).filter(x=>x.length>=4))];
const rows=[],errors=[],collections=[];
for(const f of files){const qs=JSON.parse(f.content).questions;collections.push({file:f.name,sha:f.sha,count:qs.length,works:[...new Set(qs.map(q=>q.work))]});for(const q of qs){
const fail=issue=>errors.push({id:q.id,file:f.name,issue});const cat=q.category||"anthology";let entry=q.entryId||null;
if(!Array.isArray(q.options)||q.options.length!==3||q.options.filter(x=>x===q.correct).length!==1)fail("invalid choices");
if(!["id","prompt","why","sourceLocator","sourceUrl","text","work","author","genre","theme"].every(k=>typeof q[k]==="string"&&q[k].trim()))fail("missing fields");
if(!Number.isInteger(q.room)||q.room<0||q.room>9||![1,2,3].includes(q.level))fail("room/level");
if(q.status==="approved")fail("draft incorrectly approved");
if(cat==="comparative"){if(q.comparisonEntryIds?.length!==2||new Set(q.comparisonEntryIds).size!==2||q.sourceRefs?.length!==2||!q.comparisonEntryIds.every(id=>q.sourceRefs.some(r=>r.entryId===id&&r.locator&&coverage.entries.some(e=>e.id===id&&e.sourceUrl===r.url))))fail("comparative reference");}
else if(cat==="theory"){if(q.author!=="Πρωτότυπο διδακτικό παράδειγμα"||!q.note||q.entryId||q.comparisonEntryIds||!/^https:\/\/ebooks\.edu\.gr\/ebooks\/v\/html\/8547\/(4716|2674)\//.test(q.sourceUrl))fail("theory metadata");}
else{const es=coverage.entries.filter(e=>q.entryId?e.id===q.entryId:(e.legacyBankTitle||e.work)===q.work);if(es.length!==1||es[0].sourceUrl!==q.sourceUrl)fail("catalogue reference");if(es.length===1){entry=es[0].id;if(norm(es[0].author)!==norm(q.author))fail("author differs from catalogue");}}
const wrong=q.options.filter(x=>x!==q.correct), lengths=wrong.map(x=>x.length);
rows.push({id:q.id,file:f.name,category:cat,entry,group:cat==="comparative"?[...(q.comparisonEntryIds||[])].sort().join("|"):cat==="theory"?q.work:entry||q.work,room:q.room,level:q.level,promptHash:hash(q.prompt),optionHashes:q.options.map(hash),correctIndex:q.options.indexOf(q.correct),pWords:words(q.prompt),cWords:words(q.correct),longest:q.correct.length>Math.max(...lengths),shortest:q.correct.length<Math.min(...lengths),bothAbsolute:wrong.every(x=>/(?:^|[^\p{L}])(?:αποκλειστικά|πάντοτε|ποτέ|μόνο|κάθε|όλα|οριστικά)(?:$|[^\p{L}])/u.test(x))});
}}
return {collections,errors,rows};
}
export {screenBatch};
