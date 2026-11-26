const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync(require('node:path').join(__dirname,'../dist/index.html'),'utf8');
const cut=(a,b)=>html.slice(html.indexOf(a),html.indexOf(b,html.indexOf(a)));
const sandbox={performance:{now:()=>0},Math,Set};vm.createContext(sandbox);
vm.runInContext(cut('const W=','function lineClear(')+cut('function translatePlayer(','function frame(t)')+`
let s={done:false},modal=false,opening=0,cam={x:11.5,z:21.5,a:0},layout=makeLayout(0),upperRooms=[],stairLock=0,lastStep=0;
let preferences={speed:'normal'};function room(){return {r:0}}function tone(){}
function atStair(){return false}function switchFloor(){throw Error('Unexpected floor transition')}
globalThis.api={makeLayout,isClear,archiveDoors,startPos,move,translatePlayer,
 get cam(){return cam},set cam(v){cam=v},get layout(){return layout},set layout(v){layout=v}};
`,sandbox);
const a=sandbox.api;let spots=0;
for(let r=0;r<10;r++)for(let floor=0;floor<2;floor++)for(let open of [false,true]){
 a.archiveDoors.clear();if(open)a.archiveDoors.add(r);const l=a.makeLayout(r,floor);a.layout=l;
 const start=Array.from(a.startPos),seen=new Set([start.map(Math.floor).join(',')]),q=[start];
 for(let i=0;i<q.length;i++)for(let [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]]){
  const [x,z]=q[i],nx=x+dx,nz=z+dz,k=[Math.floor(nx),Math.floor(nz)].join(',');
  if(seen.has(k)||!a.isClear(l,nx,nz,.22))continue;
  for(let t=.1;t<=1.001;t+=.1)assert(a.isClear(l,x+dx*t,z+dz*t,.18));
  seen.add(k);q.push([nx,nz]);
 }
 assert(l.spots.length>10);for(const p of l.spots){assert(seen.has(p.map(Math.floor).join(',')));spots++;}
 assert(seen.has('11,1'));for(let z=5;z<22;z++)for(let x=9;x<=13;x++)assert.equal(l.map[z][x],0);
 if([0,5,9].includes(r)){assert(seen.has(floor?'17,11':'17,16'));assert(a.isClear(l,17.5,floor?10.4:17.5));}
 if(open&&!floor){assert(seen.has('4,2'));assert(seen.has('5,4'));assert(seen.has('6,3'));}
}
a.layout=a.makeLayout(0);a.cam={x:11.5,z:20.5,a:-Math.PI/2};a.translatePlayer(1,0,.5);
assert(Math.abs(a.cam.z-18.3)<1e-8);
a.cam={x:11.5,z:20.5,a:-Math.PI/2};a.translatePlayer(1,1,.5);
assert(Math.abs(Math.hypot(a.cam.x-11.5,a.cam.z-20.5)-2.2)<1e-8);
a.cam={x:11.5,z:20.5,a:0};a.translatePlayer(0,0,1);assert.equal(a.cam.x,11.5);
a.cam={x:1.5,z:20.5,a:Math.PI};a.translatePlayer(1,0,2);assert(a.cam.x>=1.18);assert(a.isClear(a.layout,a.cam.x,a.cam.z,.18));
console.log(`PASS: 40 layouts, ${spots} reachable puzzle positions, stairs, archive passages, collision and diagonal movement.`);
