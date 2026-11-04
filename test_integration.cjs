const fs=require('fs'),vm=require('vm'),assert=require('assert'),T=require(process.env.THREE_TEST_MODULE||'three');
const {RSBatTracking}=require('./tracking.js');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const code=html.slice(html.indexOf('function runTracking('),html.indexOf("$('start').onclick="));
let now=0,queue=[];const status={};const ctx={_updatedAt:null};const root=new T.Group();const matrices=[new T.Matrix4().makeTranslation(0,0,-2),new T.Matrix4().makeTranslation(.6,0,-2)];
const controls=matrices.map(matrix=>({context:ctx,parameters:{size:.14},object3d:{visible:true,matrix}}));
const sc={object3D:root,_rsMarkers:controls.map(c=>({components:{'arjs-anchor':{_arAnchor:{controls:c}}}}))};
const env={RSBatTracking,T3:T,active:true,generation:1,scene:sc,makeHouse:()=>new T.Group(),performance:{now:()=>now},requestAnimationFrame:f=>queue.push(f),$:id=>status[id]||(status[id]={})};vm.createContext(env);vm.runInContext(code,env);env.runTracking(sc,{marker:.14,gap:.6},1);
function tick(stamp){now=stamp;ctx._updatedAt=stamp;queue.shift()();}
// No A-Frame loaded event or scene system required: controls provide the context.
for(let i=1;i<=8;i++)tick(i*33);
assert(sc._rsWall.visible);assert.equal(status.markerStatus.textContent,'A : détecté · B : détecté');assert.equal(sc._rsWall.position.z,-2);
controls[1].object3d.visible=false;tick(300);assert(!sc._rsWall.visible);assert.equal(status.markerStatus.textContent,'A : détecté · B : non détecté');
controls[1].object3d.visible=true;for(let i=1;i<=8;i++)tick(300+i*33);assert(sc._rsWall.visible);
now=1200;queue.shift()();assert(!sc._rsWall.visible);assert.equal(status.tracking.textContent,'Analyse caméra interrompue');
env.active=false;queue.shift()();assert.equal(queue.length,0);
new vm.Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);console.log('PASS : boucle réelle sans événement loaded, acquisition, états A/B, perte/reprise, image périmée, arrêt caméra, syntaxe.');
