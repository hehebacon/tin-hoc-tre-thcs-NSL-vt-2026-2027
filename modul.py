from build123d import *
from pathlib import Path
import math

OUT=Path("out")
OUT.mkdir(exist_ok=True)

# ---------- helpers ----------
def rb(x,y,z,r=6):
    s=Box(x,y,z,align=(Align.CENTER,Align.CENTER,Align.CENTER))
    try: return fillet(s.edges(),r)
    except: return s

def scale(w,d,t,a=0):
    s=rb(w,d,t,min(t*.45,6))
    return s.rotate(Axis.X,a)

def cyl(r,h):
    return Cylinder(r,h,rotation=(0,90,0),align=(Align.CENTER,Align.CENTER,Align.MIN))

# ---------- body ----------
def body():
    s=rb(300,170,82,22)
    s=s.fuse(Sphere(70).translate((-75,0,8)))
    s=s.fuse(Sphere(62).translate((82,0,8)))
    s=s.fuse(rb(205,62,34,12).translate((15,0,53)))
    return s

# ---------- chibi angry dragon head ----------
def head():
    s=Sphere(62)
    s=s.fuse(Sphere(40).translate((38,-38,-2)))
    s=s.fuse(Sphere(40).translate((38,38,-2)))
    s=s.fuse(rb(58,84,45,15).translate((72,0,-10)))
    s=s.fuse(Sphere(23).translate((106,0,-3)))
    s=s.fuse(rb(48,72,23,9).translate((73,0,-38)))

    # angry brows / eyes
    for y,ang in [(-40,-15),(40,15)]:
        brow=rb(43,18,12,5).translate((45,y,38)).rotate(Axis.X,ang)
        s=s.fuse(brow)
    for y in (-48,48):
        s=s.cut(Sphere(18).translate((54,y,18)))

    # nostrils
    for y in (-12,12):
        s=s.cut(Sphere(5).translate((116,y,-2)))

    # small horns
    for y,ang in [(-43,-18),(43,18)]:
        h=Cone(17,5,42,align=(Align.CENTER,Align.CENTER,Align.MIN))
        s=s.fuse(h.translate((7,y,43)).rotate(Axis.Y,ang))
    return s

# ---------- neck ----------
def neck():
    return cyl(42,70).translate((-5,0,0))

# ---------- layered dragon frill ----------
def neck_frill():
    out=None
    levels=[(58,30,7,30,20),(68,34,7,36,9),(76,38,8,40,-3),(68,34,7,35,-18),(56,29,6,27,-31)]
    for i,(w,d,t,a,z) in enumerate(levels):
        x=-34+i*17
        p=scale(w,d,t,a).translate((x,0,z))
        l=scale(w*.66,d*.58,t,a+8).translate((x,-d*.62,z-3))
        r=scale(w*.66,d*.58,t,a-8).translate((x,d*.62,z-3))
        out=p if out is None else out.fuse(p)
        out=out.fuse(l).fuse(r)
    return out

# ---------- body scales ----------
def body_scales():
    out=None
    for i in range(9):
        x=-108+i*27
        w=42+18*math.sin(i/8*math.pi)
        p=scale(w,32,7,18).translate((x,0,62+i*1.5))
        l=scale(w*.72,27,6,12).translate((x,-71,37))
        r=scale(w*.72,27,6,12).translate((x,71,37))
        out=p if out is None else out.fuse(p)
        out=out.fuse(l).fuse(r)
    return out

# ---------- segmented tail + chunky scales ----------
def tail():
    out=None
    for i in range(9):
        r1=max(9,34-i*3.2); r2=max(7,27-i*2.8)
        seg=Cone(r1,r2,45,rotation=(0,90,0),align=(Align.CENTER,Align.CENTER,Align.MIN))
        x=145+i*38
        seg=seg.translate((x,0,8-i*1.5))
        out=seg if out is None else out.fuse(seg)
    return out

def tail_scales():
    out=None
    for i in range(9):
        x=150+i*38
        w=max(20,56-i*4)
        p=scale(w,25,6,23).translate((x+5,0,27-i*2))
        l=scale(w*.60,18,5,14).translate((x,-21,13-i))
        r=scale(w*.60,18,5,14).translate((x,21,13-i))
        out=p if out is None else out.fuse(p)
        out=out.fuse(l).fuse(r)
    return out

# ---------- spider-mech legs ----------
def joint():
    j=cyl(30,34)
    try: j=j.cut(cyl(6,44).translate((-5,0,0)))
    except: pass
    return j

def upper_leg():
    L=150
    s=cyl(18,L)
    s=s.fuse(joint()).fuse(joint().translate((L,0,0)))
    s=s.fuse(rb(90,44,32,11).translate((75,0,0)))
    return s

def lower_leg():
    L=165
    s=cyl(15,L)
    s=s.fuse(joint()).fuse(joint().translate((L,0,0)))
    s=s.fuse(rb(88,40,30,10).translate((82,0,0)))
    s=s.fuse(Sphere(25).translate((82,0,4)))
    return s

def foot():
    s=rb(72,48,16,11)
    for y in (-14,14):
        try: s=s.cut(Cylinder(2,30).translate((7,y,-15)))
        except: pass
    return s

# ---------- accessories / future cover mounts ----------
def shoulder():
    return Sphere(48).cut(Sphere(36).translate((8,0,10)))

def sensor_pod():
    p=rb(58,46,30,9)
    for y in (-14,14):
        try: p=p.cut(Cylinder(3,40).translate((0,y,-20)))
        except: pass
    return p

def cover_rail():
    rail=rb(210,16,12,4).translate((0,0,42))
    for x in range(-90,91,30):
        try: rail=rail.cut(Cylinder(1.7,25).translate((x,0,42)))
        except: pass
    return rail

def foot_claw():
    base=rb(58,42,10,7).translate((10,0,0))
    for y in (-13,0,13):
        toe=rb(38,8,9,3).translate((42,y,0))
        base=base.fuse(toe)
    return base

# ---------- assembly ----------
def assembly():
    b=body()
    h=head().translate((-175,0,50))
    n=neck().translate((-145,0,43))
    nf=neck_frill().translate((-145,0,43))
    bs=body_scales()
    t=tail()
    ts=tail_scales()
    rail=cover_rail()
    sensor=sensor_pod().translate((-10,0,86))

    # four mirrored spider legs
    parts=[b,h,n,nf,bs,t,ts,rail,sensor]
    for sx in (-1,1):
        for sy in (-1,1):
            y=sy*78
            x=sx*105
            sh=shoulder().translate((x,y,10))
            up=upper_leg().translate((x,y,-5))
            lo=lower_leg().translate((x+sx*145,y,-5))
            ft=foot().translate((x+sx*300,y,-25))
            parts += [sh,up,lo,ft]
    result=parts[0]
    for p in parts[1:]:
        result=result.fuse(p)
    return result

# ---------- exports ----------
if __name__=="__main__":
    parts={
        "body":body(),
        "head":head(),
        "neck":neck(),
        "neck_frill":neck_frill(),
        "body_scales":body_scales(),
        "tail":tail(),
        "tail_scales":tail_scales(),
        "upper_leg":upper_leg(),
        "lower_leg":lower_leg(),
        "foot":foot(),
        "shoulder":shoulder(),
        "sensor_pod":sensor_pod(),
        "cover_rail":cover_rail(),
        "foot_claw":foot_claw(),
    }
    for name,p in parts.items():
        try: export_stl(p,OUT/f"{name}.stl")
        except Exception as e: print("[STL]",name,e)
        try: export_step(p,OUT/f"{name}.step")
        except Exception as e: print("[STEP]",name,e)

    full=assembly()
    try: export_stl(full,OUT/"dragon_spider_full.stl")
    except Exception as e: print("[FULL STL]",e)
    try: export_step(full,OUT/"dragon_spider_full.step")
    except Exception as e: print("[FULL STEP]",e)

    print("\n=== DRAGON-SPIDER CAD DONE ===")
    print("Output:",OUT.resolve())
