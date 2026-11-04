import math, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30; TOTAL=20.0
FD="/usr/share/fonts/opentype/inter/"
def F(s,w="Bold"): return ImageFont.truetype(FD+f"Inter-{w}.otf",int(s))
BG=(10,10,12); CARD=(28,28,32); TXT=(245,245,247); SUB=(152,152,160); BLUE=(10,132,255); YEL=(255,221,60); RED=(255,69,58); GRN=(48,209,88)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def cl(x): return max(0,min(1,x))
def tl(d,s,x,y,size,fill=TXT,w="Bold"): d.text((x,y),s,font=F(size,w),fill=fill)
def tc(d,s,x,y,size,fill=TXT,w="Bold"):
    f=F(size,w); bb=d.textbbox((0,0),s,font=f); d.text((x-(bb[2]-bb[0])/2-bb[0],y-(bb[3]-bb[1])/2-bb[1]),s,font=f,fill=fill)
def wraptxt(s,f,maxw):
    out,cur=[],""
    for wd in s.split():
        t=(cur+" "+wd).strip()
        if f.getlength(t)<=maxw: cur=t
        else: out.append(cur); cur=wd
    out.append(cur); return out
def nadie(d,cx,cy,r):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=YEL); fr=r*0.78; d.ellipse((cx-fr,cy-fr,cx+fr,cy+fr),fill=(17,17,17)); s=r/330
    d.rounded_rectangle((cx-170*s,cy-130*s,cx-90*s,cy+10*s),radius=30*s,fill=TXT)
    d.rounded_rectangle((cx+90*s,cy-50*s,cx+190*s,cy-20*s),radius=15*s,fill=TXT)
    d.rounded_rectangle((cx-60*s,cy+120*s,cx+60*s,cy+150*s),radius=12*s,fill=YEL)
random.seed(4)
FEED=[(random.choice([(255,94,58),(94,92,230),(48,176,199),(255,159,10),(191,90,242),(52,199,89),(255,55,95)]),random.random()) for _ in range(14)]
def timer(d,t):
    left=max(0,math.ceil(TOTAL-t-0.001))
    d.rounded_rectangle((W-250,250,W-70,330),radius=40,fill=(255,255,255,40) if False else (40,40,46))
    tc(d,f"0:{left:02d}",W-160,290,46,fill=YEL if left>5 else RED)
def phone(im,x0,y0,w,h,inner):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0-14,y0-14,x0+w+14,y0+h+14),radius=70,fill=(58,58,64))
    d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=58,fill=(0,0,0))
    scr=Image.new("RGB",(w,h),(0,0,0)); inner(scr); m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w,h),radius=58,fill=255)
    im.paste(scr,(x0,y0),m)
    d.rounded_rectangle((x0+w/2-90,y0+18,x0+w/2+90,y0+58),radius=20,fill=(0,0,0))
def frame(t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    # ---------- 0-3.4 notificación
    if t<3.4:
        k=ease(t/0.5); y=420+(-300)*(1-k)
        d.rounded_rectangle((70,y,W-70,y+250),radius=44,fill=CARD)
        d.rounded_rectangle((110,y+40,190,y+120),radius=20,fill=YEL); nadie(d,150,y+80,34)
        tl(d,"COMENTARIO NUEVO",215,y+42,30,SUB,"SemiBold"); tl(d,"ahora",W-200,y+42,30,SUB,"Regular")
        tl(d,"mako_pk ha comentado:",215,y+86,38,TXT,"Bold")
        f=F(36,"Regular"); 
        for i,l in enumerate(wraptxt("«De porque estos tipo de videos se hacen tan virales»",f,W-330)): d.text((215,y+136+i*44),l,font=f,fill=(220,220,226))
        if t>1.1:
            q=ease((t-1.1)/0.4); tc(d,"Te lo explico",W/2,960,int(96*(0.8+0.2*q)),w="Black")
            tc(d,"en 20 segundos.",W/2,1080,int(96*(0.8+0.2*q)),fill=YEL,w="Black")
        if t>2.0: timer(d,t)
        return im
    timer(d,t)
    # ---------- 3.4-8.6 razón 1: el primer segundo
    if t<8.6:
        k=t-3.4
        tl(d,"1",80,400,150,YEL,"Black"); tl(d,"El primer segundo",200,420,62,TXT,"Black"); tl(d,"lo decide todo",200,495,62,SUB,"Black")
        def feed(scr):
            sd=ImageDraw.Draw(scr); sw,sh=scr.size
            # scroll rápido que frena
            pos=min(k,3.0); off=(1-(1-pos/3.0)**3)*sh*6
            for i,(c,r) in enumerate(FEED):
                y=i*sh-off
                if y>sh or y+sh<0: continue
                sd.rectangle((0,y,sw,y+sh),fill=tuple(int(v*0.55) for v in c))
                sd.ellipse((sw*0.2,y+sh*0.25,sw*0.8,y+sh*0.25+sw*0.6),fill=tuple(min(255,int(v*0.9)) for v in c))
                sd.rounded_rectangle((40,y+sh-260,sw*0.65,y+sh-225),radius=10,fill=(235,235,235)); sd.rounded_rectangle((40,y+sh-205,sw*0.45,y+sh-178),radius=10,fill=(170,170,170))
                for j in range(4): sd.ellipse((sw-95,y+sh*0.45+j*120,sw-45,y+sh*0.45+j*120+50),fill=(235,235,235))
        phone(im,250,640,580,1000,feed); d=ImageDraw.Draw(im)
        if k>3.1:
            q=ease((k-3.1)/0.35)
            d.rounded_rectangle((110,1500-30*q,W-110,1640),radius=34,fill=(0,0,0))
            tc(d,"Si no te engancha ya,",W/2,1540,50,TXT,"Black"); tc(d,"deslizas. Y adiós.",W/2,1600,50,YEL,"Black")
        return im
    # ---------- 8.6-13.6 razón 2: retención
    if t<13.6:
        k=t-8.6
        tl(d,"2",80,400,150,YEL,"Black"); tl(d,"Que lo veas",200,420,62,TXT,"Black"); tl(d,"hasta el final",200,495,62,SUB,"Black")
        x0,y0,x1,y1=130,760,W-110,1300
        d.rounded_rectangle((x0-50,y0-110,x1+50,y1+120),radius=40,fill=CARD)
        tl(d,"Retención de audiencia",x0,y0-80,38,TXT,"SemiBold")
        for i,p in enumerate((100,75,50,25,0)):
            y=y0+(y1-y0)*i/4; d.line((x0+70,y,x1,y),fill=(52,52,58),width=2); tl(d,f"{p}%",x0-10,y-18,28,SUB,"Regular")
        def curve(fn,col,prog):
            pts=[(x0+70+(x1-x0-70)*s/100, y0+(y1-y0)*(1-fn(s/100))) for s in range(0,int(100*prog)+1)]
            if len(pts)>1: d.line(pts,fill=col,width=10,joint="curve")
        p=cl(k/2.2)
        curve(lambda s: math.exp(-6*s)*0.9+0.05,RED,p)
        curve(lambda s: 1-0.35*s,GRN,cl((k-0.6)/2.2))
        if k>0.8: tl(d,"aburrido",x0+180,y1-110,34,RED,"Bold")
        if k>1.6: tl(d,"enganchado",x1-260,y0+60,34,GRN,"Bold")
        if k>3.0:
            tc(d,"Cuanto más lo ve la gente,",W/2,1520,50,TXT,"Black"); tc(d,"más se lo enseña Instagram.",W/2,1585,50,YEL,"Black")
        return im
    # ---------- 13.6-17.4 razón 3: comentar y compartir
    if t<17.4:
        k=t-13.6
        tl(d,"3",80,400,150,YEL,"Black"); tl(d,"Comentar y",200,420,62,TXT,"Black"); tl(d,"compartir",200,495,62,SUB,"Black")
        n_c=int(3+ (1-(1-cl(k/2.5))**3)*1244); n_s=int(1+(1-(1-cl((k-0.3)/2.5))**3)*867)
        for i,(lab,val,col) in enumerate((("Comentarios",n_c,BLUE),("Envíos",n_s,GRN))):
            y=760+i*300
            d.rounded_rectangle((110,y,W-110,y+240),radius=40,fill=CARD)
            tl(d,lab,170,y+40,40,SUB,"SemiBold"); tl(d,f"{val:,}".replace(",","."),170,y+100,100,col,"Black")
        if k>1.5:
            tc(d,"Cada uno empuja el vídeo",W/2,1440,50,TXT,"Black"); tc(d,"a gente nueva.",W/2,1505,50,YEL,"Black")
        return im
    # ---------- 17.4-20 cierre
    k=t-17.4
    tc(d,"Como acabas",W/2,560,92,TXT,"Black"); tc(d,"de hacer tú.",W/2,670,92,YEL,"Black")
    nadie(d,W/2,1000,150*(0.85+0.15*ease(k/0.4)))
    if k>0.8: tc(d,"Gracias por hacerme un poco",W/2,1270,48,SUB,"Bold"); tc(d,"más viral, @mako_pk",W/2,1335,48,TXT,"Bold")
    return im
if __name__=="__main__":
    if sys.argv[1]=="still":
        for t in map(float,sys.argv[2:]): frame(t).save(f"s_{t}.png")
    else:
        p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","mudo.mp4"],stdin=subprocess.PIPE)
        for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); p.wait()
