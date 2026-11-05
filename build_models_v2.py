from pathlib import Path
import math, zipfile
from pxr import Usd, UsdGeom, UsdShade, Sdf, UsdUtils
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import qrcode
R=Path(__file__).resolve().parent
class Model:
 def __init__(self,name):
  self.name=name; self.src=R/(name+'.usdc'); self.s=Usd.Stage.CreateNew(str(self.src)); UsdGeom.SetStageMetersPerUnit(self.s,1); UsdGeom.SetStageUpAxis(self.s,'Y'); self.root=UsdGeom.Xform.Define(self.s,'/Model'); self.s.SetDefaultPrim(self.root.GetPrim()); self.faces=[]; self.colors=[]; self.n=0
  self.mats=[]
  for label,col in [('Gold',(1,.65,.025)),('Steel',(.13,.23,.32))]:
   mat=UsdShade.Material.Define(self.s,'/Model/Materials/'+label); sh=UsdShade.Shader.Define(self.s,mat.GetPath().AppendChild('Surface')); sh.CreateIdAttr('UsdPreviewSurface'); sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(col); sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.4); mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface'); self.mats.append((mat,col))
 def prism(self,poly,lo,hi,axis='z',mat=0):
  # convex polygons; all caps have explicit outward winding
  if sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))<0: poly=list(reversed(poly))
  conv=lambda p,t:(p[0],p[1],t) if axis=='z' else (p[0],t,-p[1])
  p=[conv(v,t) for t in [lo,hi] for v in poly]; n=len(poly); faces=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
  self.n+=1; m=UsdGeom.Mesh.Define(self.s,f'/Model/Part{self.n}'); m.CreatePointsAttr(p); m.CreateFaceVertexCountsAttr([len(f) for f in faces]); m.CreateFaceVertexIndicesAttr([j for f in faces for j in f]); m.CreateSubdivisionSchemeAttr('none'); m.CreateExtentAttr([tuple(min(v[k] for v in p) for k in range(3)),tuple(max(v[k] for v in p) for k in range(3))]); UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(self.mats[mat][0]); self.faces += [[p[j] for j in f] for f in faces]; self.colors += [self.mats[mat][1]]*len(faces)
 def finish(self,expect=None):
  self.s.GetRootLayer().Save(); dst=R/(self.name+'.usdz'); dst.unlink(missing_ok=True); assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(self.src)),str(dst)); s=Usd.Stage.Open(str(dst)); b=UsdGeom.BBoxCache(Usd.TimeCode.Default(),['default']).ComputeWorldBound(s.GetDefaultPrim()).ComputeAlignedBox(); size=tuple(b.GetSize()); assert abs(b.GetMin()[1])<1e-6
  if expect: assert all(abs(a-b)<1e-5 for a,b in zip(size,expect)),size
  assert zipfile.ZipFile(dst).testzip() is None; self.src.unlink(); print(self.name,size)
  fig=plt.figure(figsize=(9,6),facecolor='#0d2137'); ax=fig.add_subplot(111,projection='3d',facecolor='#0d2137'); ax.add_collection3d(Poly3DCollection([[(x,z,y) for x,y,z in f] for f in self.faces],facecolors=self.colors,edgecolors='#334454',linewidths=.2)); allp=[p for f in self.faces for p in f]; mins=[min(p[k] for p in allp) for k in range(3)]; maxs=[max(p[k] for p in allp) for k in range(3)]; ax.set_xlim(mins[0]-.1,maxs[0]+.1); ax.set_ylim(mins[2]-.1,maxs[2]+.1); ax.set_zlim(0,maxs[1]+.1); ax.set_box_aspect((size[0],max(size[2],.3),size[1])); ax.view_init(elev=15,azim=-72); ax.set_axis_off(); fig.savefig(R/(self.name+'.png'),dpi=100,bbox_inches='tight',pad_inches=.15); plt.close(fig)
m=Model('imer-quicklook')
# Four geometric capital letters, overall 2 m wide x 1.50 m high, depth 20 cm.
def stroke(x,poly): m.prism([(x+a,b) for a,b in poly],-.1,.1)
def rect(x,a,b,c,d): stroke(x,[(a,b),(c,b),(c,d),(a,d)])
w=.44; t=.095
for x in [-1,-.48,.04,.56]:
 if x==-1:
  rect(x,0,0,w,t); rect(x,0,1.5-t,w,1.5); rect(x,(w-t)/2,0,(w+t)/2,1.5)
 elif x==-.48:
  rect(x,0,0,t,1.5); rect(x,w-t,0,w,1.5); stroke(x,[(t,1.5),(.22,.93),(.22,.64),(t,1.18)]); stroke(x,[(.22,.93),(w-t,1.5),(w-t,1.18),(.22,.64)])
 elif x==.04:
  rect(x,0,0,t,1.5)
  for y in [0,.70,1.5-t]: rect(x,0,y,w,y+t)
 else:
  rect(x,0,0,t,1.5); rect(x,t,1.5-t,w-t,1.5); rect(x,w-t,.82,w,1.5-t); rect(x,t,.725,w-t,.82); stroke(x,[(t,.82),(w,0),(w-t,0),(t,.58)])
m.finish((2,1.5,.2))
m=Model('escalier-quicklook'); n=16; rise=2.8/n
for i in range(n):
 a=i*math.pi*2/n; b=a+math.pi*2/n*.94
 # split annular step into convex quads
 for j in range(6):
  u=a+(b-a)*j/6; v=a+(b-a)*(j+1)/6
  m.prism([(r*math.cos(t),r*math.sin(t)) for r,t in [(.1,u),(1,u),(1,v),(.1,v)]],(i+1)*rise-.06,(i+1)*rise,axis='y')
 a=(a+b)/2; cx=.94*math.cos(a); cz=.94*math.sin(a)
 m.prism([(cx+.018*math.cos(t*math.pi/6),cz+.018*math.sin(t*math.pi/6)) for t in range(12)],(i+1)*rise,(i+1)*rise+.9,axis='y',mat=1)
 # handrail short segments as closed prisms between rail sample endpoints
 for j in range(4):
  u=i*2*math.pi/n+(j/4)*2*math.pi/n; v=u+2*math.pi/n/4
  y=(i+1+j/4)*rise+.9
  m.prism([(.92*math.cos(u),.92*math.sin(u)),(.96*math.cos(u),.96*math.sin(u)),(.96*math.cos(v),.96*math.sin(v)),(.92*math.cos(v),.92*math.sin(v))],y,y+.04,axis='y',mat=1)
m.prism([(.1*math.cos(t*math.pi/16),.1*math.sin(t*math.pi/16)) for t in range(32)],0,3.7,axis='y',mat=1); m.finish()
for key in ['imer','escalier','mur','cube']:
 qrcode.make('https://shark17-creator.github.io/rsbat-vision-demo/quicklook.html?model='+key).save(R/('qr-'+key+'.png'))
