import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {runSelectionTests} from './selector.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url));
const files=fs.readdirSync(dir).filter(x=>/^bank-draft-\d+\.json$/.test(x)).sort();
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
 const entries=coverage.entries.filter(e=>q.entryId?e.id===q.entryId:(e.legacyBankTitle||e.work)===q.work);
 check(entries.length===1,q.id+' invalid anthology entry');
}
for(const entry of coverage.entries){
 const qs=questions.filter(q=>q.entryId?q.entryId===entry.id:q.work===(entry.legacyBankTitle||entry.work));
 check(entry.draftQuestions===qs.length,entry.id+' stale coverage');
}
const result=runSelectionTests(questions);
console.log(JSON.stringify({files,questions:questions.length,works:new Set(questions.map(q=>q.entryId||q.work)).size,choices:questions.length*3,coverage:coverage.summary,selection:result},null,2));
