import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30; TOTAL=22.0
def C(s,w=700):
    f=ImageFont.truetype("Caveat.ttf",int(s)); f.set_variation_by_axes([w]); return f
CH=(238,240,232); YEL=(255,226,90); PINK=(255,150,170); CY=(140,225,240); GRN=(150,235,150)
def board():
    im=Image.new("RGB",(W,H),(34,62,48)); random.seed(3); d=ImageDraw.Draw(im)
    for _ in range(9000):
        x,y=random.randint(0,W),random.randint(0,H); c=random.randint(-8,8); d.point((x,y),fill=(34+c,62+c,48+c))
    for _ in range(40):  # manchas de borrado
        x,y=random.randint(0,W),random.randint(0,H); r=random.randint(60,200)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).ellipse((x-r,y-r/3,x+r,y+r/3),fill=(255,255,255,3)); im.paste(ov,(0,0),ov)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,40),fill=(120,84,52)); d.rectangle((0,H-40,W,H),fill=(120,84,52))
    return im.filter(ImageFilter.GaussianBlur(0.6))
BASE=board()
def chalk(d,s,x,y,size,fill=CH,prog=1.0,center=False,w=700):
    f=C(size,w); n=max(0,int(len(s)*prog)); t=s[:n]
    if center:
        bb=d.textbbox((0,0),s,font=f); x=x-(bb[2]-bb[0])/2-bb[0]
    d.text((x,y),t,font=f,fill=fill)
def p(t,a,dur=0.9): return max(0,min(1,(t-a)/dur))
def nadie(d,cx,cy,r,col=CH):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=6)
    s=r/100
    d.rounded_rectangle((cx-50*s,cy-40*s,cx-26*s,cy+5*s),radius=10*s,outline=col,width=5)
    d.line((cx+25*s,cy-15*s,cx+55*s,cy-15*s),fill=col,width=6)
    d.line((cx-20*s,cy+45*s,cx+20*s,cy+45*s),fill=YEL,width=6)
REASONS=[(4.0,"1. Las lenguas cambian solas","cada generación pronuncia un pelín distinto",YEL),
         (7.6,"2. La distancia separa","montañas, mares... cada grupo cambia a su aire",CY),
         (11.2,"3. Los idiomas se mezclan","italiano en Argentina, árabe en el sur de España...",PINK),
         (14.8,"4. Hablas como tu gente","de pequeño copias el acento de tu barrio",GRN)]
def frame(t):
    im=BASE.copy(); d=ImageDraw.Draw(im)
    # cabecera
    chalk(d,"Lección de hoy para",W/2,180,62,prog=p(t,0,0.6),center=True,w=500)
    chalk(d,"@gstarr_4.7",W/2,250,96,fill=YEL,prog=p(t,0.5,0.6),center=True)
    if t<4.0:
        chalk(d,"¿Por qué hay",W/2,600,130,prog=p(t,1.2,0.7),center=True)
        chalk(d,"tantos acentos",W/2,740,130,prog=p(t,1.7,0.7),center=True)
        chalk(d,"en el mundo?",W/2,880,130,fill=YEL,prog=p(t,2.2,0.7),center=True)
        if t>2.9: d.line((260,1040,820,1040),fill=YEL,width=6)
        return im
    if t<18.6:
        y=430
        for a,tit,sub,col in REASONS:
            if t<a: break
            chalk(d,tit,90,y,80,fill=col,prog=p(t,a,0.9))
            chalk(d,sub,120,y+92,47,prog=p(t,a+0.8,1.4),w=500)
            y+=280
        return im
    # cierre
    k=t-18.6
    chalk(d,"Dato final:",W/2,520,88,fill=YEL,prog=p(k,0,0.4),center=True)
    chalk(d,"nadie habla",W/2,650,120,prog=p(k,0.3,0.5),center=True)
    chalk(d,"\"sin acento\".",W/2,780,120,prog=p(k,0.7,0.5),center=True)
    if k>1.3:
        nadie(d,W/2,1080,95)
        chalk(d,"(yo tengo acento de servidor)",W/2,1210,58,fill=CY,prog=p(k,1.4,0.7),center=True,w=500)
    if k>2.2:
        chalk(d,"¿Quieres salir en el próximo vídeo?",W/2,1380,58,prog=p(k,2.2,0.5),center=True,w=500)
        chalk(d,"Sígueme y comenta 🎲".replace(" 🎲",""),W/2,1450,70,fill=YEL,prog=p(k,2.4,0.4),center=True)
    return im
if __name__=="__main__":
    if sys.argv[1]=="still":
        for t in map(float,sys.argv[2:]): frame(t).save(f"s_{t}.png")
    else:
        pr=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","mudo.mp4"],stdin=subprocess.PIPE)
        for i in range(int(TOTAL*FPS)): pr.stdin.write(frame(i/FPS).tobytes())
        pr.stdin.close(); pr.wait()
