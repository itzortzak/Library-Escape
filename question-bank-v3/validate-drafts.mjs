import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {runSelectionTests} from './selector.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url));
const files=fs.readdirSync(dir).filter(x=>/^(bank|comparative|theory)-draft-\d+\.json$/.test(x)).sort();
const questions=files.flatMap(file=>JSON.parse(fs.readFileSync(path.join(dir,file),'utf8')).questions);
const coverage=JSON.parse(fs.readFileSync(path.join(dir,'anthology-coverage.json'),'utf8'));
const normalized=s=>s.normalize('NFC').trim().replace(/\s+/g,' ').toLocaleLowerCase('el');
const check=(value,msg)=>{if(!value)throw Error(msg)};
const unique=(values,label)=>check(new Set(values).size===values.length,'Repeated '+label);
unique(questions.map(q=>q.id),'ID');
unique(questions.map(q=>normalized(q.prompt)),'prompt');
unique(questions.flatMap(q=>q.options.map(normalized)),'answer choice');
for(const q of questions){
 check(q.options.length===3&&q.options.includes(q.correct),q.id+' invalid choices');
 check(q.prompt&&q.why&&q.sourceLocator&&q.sourceUrl,q.id+' missing reference or rationale');
 check(Number.isInteger(q.room)&&q.room>=0&&q.room<=9,q.id+' invalid room');
 check([1,2,3].includes(q.level),q.id+' invalid level');
 check(q.status!=='approved',q.id+' draft incorrectly marked approved');
 if(q.category==='comparative'){
 check(Array.isArray(q.comparisonEntryIds)&&q.comparisonEntryIds.length===2&&new Set(q.comparisonEntryIds).size===2,q.id+' invalid pair');
 check(Array.isArray(q.sourceRefs)&&q.sourceRefs.length===2,q.id+' invalid source references');
 check(q.comparisonEntryIds.every(id=>q.sourceRefs.some(r=>r.entryId===id&&r.locator&&coverage.entries.some(e=>e.id===id&&e.sourceUrl===r.url))),q.id+' invalid comparative source');
 }else if(q.category==='theory'){
 check(q.author==='Πρωτότυπο διδακτικό παράδειγμα'&&q.text&&q.work&&q.note,q.id+' missing original example metadata');
 check(!q.entryId&&!q.comparisonEntryIds,q.id+' theory incorrectly linked to anthology');
 check(/^https:\/\/ebooks\.edu\.gr\/ebooks\/v\/html\/8547\/(4716|2674)\//.test(q.sourceUrl),q.id+' invalid theory source');
 }else{
 const entries=coverage.entries.filter(e=>q.entryId?e.id===q.entryId:(e.legacyBankTitle||e.work)===q.work);
 check(entries.length===1,q.id+' invalid anthology entry');
 check(q.sourceUrl===entries[0].sourceUrl,q.id+' source URL differs from catalogue');
 }
}
for(const entry of coverage.entries){
 const qs=questions.filter(q=>q.category!=='comparative'&&q.category!=='theory'&&(q.entryId?q.entryId===entry.id:q.work===(entry.legacyBankTitle||entry.work)));
 check(entry.draftQuestions===qs.length,entry.id+' stale coverage');
}
check(files.length===31,'Expected 31 draft collections');
check(questions.length===1350,'Expected 1350 questions');
check(coverage.entries.length===115,'Expected 115 catalogue entries');
check(questions.filter(q=>q.category==='theory').length===100,'Expected 100 theory questions');
check(questions.filter(q=>q.category==='comparative').length===100,'Expected 100 comparative questions');
check(questions.filter(q=>q.category!=='comparative'&&q.category!=='theory').length===1150,'Expected 1150 anthology questions');
for(const room of Array.from({length:10},(_,i)=>i))for(const level of [1,2,3]){
 const pool=questions.filter(q=>q.room===room&&q.level===level);
 check(pool.length>=6,'Room '+room+' level '+level+' needs at least 6 questions for two complete sessions');
}
const result=runSelectionTests(questions);
console.log(JSON.stringify({files,questions:questions.length,works:coverage.entries.filter(e=>e.draftQuestions>0).length,anthology:questions.filter(q=>q.category!=='comparative'&&q.category!=='theory').length,comparative:questions.filter(q=>q.category==='comparative').length,theory:questions.filter(q=>q.category==='theory').length,choices:questions.length*3,coverage:coverage.summary,selection:result},null,2));
