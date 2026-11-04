/* RS-BAT: rigid metric poses, independent from AR.js matrix smoothing. */
(function(root){
'use strict';
function createTracker(T){
 const pos=new T.Vector3(),rot=new T.Quaternion();let previous=null,filtered=null,count=0,last=0;
 function reset(){previous=null;filtered=null;count=0;last=0;}
 function candidate(matrix,offset){
  const p=new T.Vector3(),q=new T.Quaternion(),s=new T.Vector3();matrix.decompose(p,q,s);
  if(![...p.toArray(),...q.toArray(),...s.toArray()].every(Number.isFinite)||s.toArray().some(v=>Math.abs(v-1)>.05))return null;
  q.normalize();p.sub(new T.Vector3(offset,0,0).applyQuaternion(q));return {p,q};
 }
 function update(matrices,gap,time){
  if(matrices.length!==2||matrices.some(m=>!m)){reset();return {visible:false,reason:'Visez les deux repères'};}
  const a=candidate(matrices[0],0),b=candidate(matrices[1],gap);
  if(!a||!b||a.p.distanceTo(b.p)>.08||a.q.angleTo(b.q)>Math.PI/15){reset();return {visible:false,reason:'Ajustez les deux repères'};}
  const pose={p:a.p.clone().lerp(b.p,.5),q:a.q.clone().slerp(b.q,.5).normalize()};
  const dt=last?Math.min(.2,Math.max(.001,(time-last)/1000)):1/30;last=time;
  if(previous&&(pose.p.distanceTo(previous.p)>.08+dt*1.5||pose.q.angleTo(previous.q)>.15+dt*2)){previous=pose;filtered=null;count=0;return {visible:false,reason:'Recalage…'};}
  previous=pose;count++;
  if(!filtered)filtered={p:pose.p.clone(),q:pose.q.clone()};
  const alpha=1-Math.exp(-dt/.07);filtered.p.lerp(pose.p,alpha);filtered.q.slerp(pose.q,alpha).normalize();
  pos.copy(filtered.p);rot.copy(filtered.q);
  return {visible:count>=8,reason:count>=8?'Deux repères suivis':'Calage…',position:pos,quaternion:rot,scale:1};
 }
 return {update,reset};
}
root.RSBatTracking={createTracker};
})(typeof module==='object'?module.exports:window);
