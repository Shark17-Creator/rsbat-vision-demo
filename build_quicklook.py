from pathlib import Path
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdUtils
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent

def build(name,w,h,d):
    src=ROOT/(name+'.usdc')
    s=Usd.Stage.CreateNew(str(src)); UsdGeom.SetStageMetersPerUnit(s,1); UsdGeom.SetStageUpAxis(s,UsdGeom.Tokens.y)
    root=UsdGeom.Xform.Define(s,'/Model'); s.SetDefaultPrim(root.GetPrim())
    def material(name,color):
        mat=UsdShade.Material.Define(s,'/Model/Materials/'+name)
        shader=UsdShade.Shader.Define(s,mat.GetPath().AppendChild('Surface')); shader.CreateIdAttr('UsdPreviewSurface')
        shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(color)
        shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.75)
        mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface'); return mat
    blue=material('Blue',(0.04,.38,.65)); yellow=material('Yellow',(1,.7,.015))
    def box(name,x0,y0,z0,x1,y1,z1,mat):
        mesh=UsdGeom.Mesh.Define(s,'/Model/'+name)
        mesh.CreatePointsAttr([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
        mesh.CreateFaceVertexCountsAttr([4]*6)
        mesh.CreateFaceVertexIndicesAttr([0,3,2,1,4,5,6,7,0,4,7,3,1,2,6,5,0,1,5,4,3,7,6,2])
        mesh.CreateSubdivisionSchemeAttr('none'); mesh.CreateExtentAttr([(x0,y0,z0),(x1,y1,z1)])
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
    t=.012 if w>.5 else .004
    box('Body',-w/2,0,-d/2,w/2,h,d/2,blue)
    # Yellow edge bars stay inside the exact model bounding box.
    for x in [-w/2,w/2-t]:
        for z in [-d/2,d/2-t]: box('Edge'+str(len(list(s.Traverse()))),x,0,z,x+t,h,z+t,yellow)
    for y in [0,h-t]:
        for z in [-d/2,d/2-t]: box('Edge'+str(len(list(s.Traverse()))),-w/2,y,z,w/2,y+t,z+t,yellow)
    s.GetRootLayer().Save()
    target=ROOT/(name+'.usdz')
    if target.exists(): target.unlink()
    assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(src)),str(target))
    reopened=Usd.Stage.Open(str(target)); assert reopened
    bound=UsdGeom.BBoxCache(Usd.TimeCode.Default(),['default']).ComputeWorldBound(reopened.GetDefaultPrim()).ComputeAlignedBox()
    size=bound.GetSize(); assert all(abs(a-b)<1e-6 for a,b in zip(size,(w,h,d))),size
    assert abs(bound.GetMin()[1])<1e-6
    assert UsdGeom.GetStageMetersPerUnit(reopened)==1
    import zipfile,struct
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        for item in archive.infolist():
            assert item.compress_type==zipfile.ZIP_STORED
            with open(target,'rb') as f:
                f.seek(item.header_offset+26); n,e=struct.unpack('<HH',f.read(4))
            assert (item.header_offset+30+n+e)%64==0
    print(name,'dimensions metres',tuple(size),'USD reopened / USDZ alignment OK',target.stat().st_size,'bytes')
    src.unlink()
    im=Image.new('RGB',(900,600),'#0d2137'); draw=ImageDraw.Draw(im)
    pts=[(210,430),(620,430),(620,135),(210,135)] if w>.5 else [(290,430),(570,430),(570,190),(290,190)]
    draw.polygon(pts,fill='#2277a4',outline='#f9c52a',width=7)
    a,b,c,e=pts
    draw.polygon([b,(b[0]+70,b[1]-45),(c[0]+70,c[1]-45),c],fill='#174e73',outline='#f9c52a',width=5)
    draw.polygon([e,c,(c[0]+70,c[1]-45),(e[0]+70,e[1]-45)],fill='#398db4',outline='#f9c52a',width=5)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
    label='3 m × 2,5 m × 20 cm' if w>.5 else '30 × 30 × 30 cm'
    draw.text((450,520),label,fill='white',font=font,anchor='mm')
    im.save(ROOT/(name+'.png'))
build('mur-quicklook',3,2.5,.2)
build('cube-quicklook',.3,.3,.3)
