#!/usr/bin/env python3
"""Render a 30s vertical motion-graphic video without paid APIs or stock assets."""
from pathlib import Path
import math, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
TMP = OUT / "work"
W, H, FPS = 1080, 1920, 30
DURATION = 30
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

def run(cmd):
    subprocess.run(cmd, check=True)

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def centered(draw, xy, text, fnt, fill, anchor="mm", stroke=0):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0,0,0,180))

def base_scene(index, title, subtitle):
    im = Image.new("RGB", (W,H), (4,13,29))
    px = im.load()
    # Deep navy vertical gradient with restrained red-white highlights.
    for y in range(H):
        t = y / H
        c = (int(4+7*t), int(14+10*t), int(31+22*t))
        for x in range(0,W,4):
            for xx in range(x,min(x+4,W)): px[xx,y] = c
    d = ImageDraw.Draw(im, "RGBA")
    # Horizon / soft light beams
    for k in range(7):
        x = 120 + k*145
        d.polygon([(x,0),(x+28,0),(x+260,H),(x+180,H)], fill=(35,115,170,12))
    # Grid and stars
    for x in range(60,W,120): d.line((x,150,x,H-180), fill=(100,170,210,18), width=1)
    for y in range(160,H-180,120): d.line((35,y,W-35,y), fill=(100,170,210,16), width=1)
    for i in range(85):
        x=(i*137+index*71)%W; y=(i*251+index*103)%H
        r=2+(i%3)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(255,220,160,90))
    # Flag-colored light ribbons
    d.arc((-250,250,W+250,1550), 195, 345, fill=(220,35,55,100), width=8)
    d.arc((-250,280,W+250,1580), 195, 345, fill=(235,240,250,90), width=5)
    centered(d,(W//2,150),title,font(54,True),(255,255,255,255),stroke=2)
    centered(d,(W//2,220),subtitle,font(28,True),(235,190,105,255))
    return im

def island_shapes(d, yoff=0, scale=1.0):
    # Stylized archipelago silhouettes: decorative, not a navigational map.
    shapes = [
      [(120,650),(190,610),(250,625),(300,670),(260,705),(180,700)],
      [(330,720),(400,680),(485,700),(530,745),(470,770),(380,760)],
      [(520,650),(590,610),(690,625),(735,680),(670,710),(580,700)],
      [(690,800),(760,770),(850,800),(900,850),(830,875),(750,860)],
      [(240,850),(290,820),(330,850),(315,890),(270,895)],
      [(420,920),(460,900),(485,940),(460,970),(430,950)],
      [(830,1020),(880,990),(930,1020),(920,1060),(870,1065)],
      [(560,1080),(610,1050),(655,1085),(640,1120),(590,1125)]
    ]
    for pts in shapes:
        pts2=[(int(x*scale),int(y*scale+yoff)) for x,y in pts]
        d.polygon(pts2, fill=(15,95,112,255), outline=(235,185,95,255), width=5)
        d.line(pts2+[pts2[0]], fill=(255,220,150,150), width=3)

def ship(d, cx, cy, scale=1.0):
    # Generic illustrative patrol ship silhouette; no weapon detail.
    pts=[(cx-210*scale,cy),(cx+205*scale,cy),(cx+150*scale,cy+55*scale),(cx-155*scale,cy+55*scale)]
    d.polygon(pts,fill=(165,190,198,255),outline=(255,225,165,255))
    d.rectangle((cx-85*scale,cy-72*scale,cx+65*scale,cy),fill=(205,218,220,255))
    d.rectangle((cx-35*scale,cy-120*scale,cx+20*scale,cy-72*scale),fill=(225,230,226,255))
    d.line((cx-5*scale,cy-120*scale,cx-5*scale,cy-205*scale),fill=(235,235,220,255),width=max(2,int(5*scale)))
    d.line((cx-5*scale,cy-195*scale,cx+75*scale,cy-165*scale),fill=(235,235,220,255),width=max(2,int(4*scale)))
    for i in range(3):
        yy=cy+75*scale+i*24*scale
        d.arc((cx-250*scale,yy-25*scale,cx+250*scale,yy+40*scale),0,180,fill=(90,190,220,170),width=4)

def jet(d, cx, cy, scale=1.0):
    # Generic aircraft silhouette, intentionally non-specific.
    pts=[(cx,cy-170*scale),(cx+35*scale,cy-25*scale),(cx+190*scale,cy+50*scale),
         (cx+185*scale,cy+85*scale),(cx+35*scale,cy+50*scale),(cx+20*scale,cy+160*scale),
         (cx-20*scale,cy+160*scale),(cx-35*scale,cy+50*scale),(cx-185*scale,cy+85*scale),
         (cx-190*scale,cy+50*scale),(cx-35*scale,cy-25*scale)]
    d.polygon(pts,fill=(190,205,215,240),outline=(255,220,160,255))

def soldier(d, cx, cy, scale=1.0):
    col=(175,195,185,255)
    d.ellipse((cx-38*scale,cy-190*scale,cx+38*scale,cy-114*scale),fill=col)
    d.rectangle((cx-54*scale,cy-110*scale,cx+54*scale,cy+65*scale),fill=col)
    d.line((cx-25*scale,cy+55*scale,cx-75*scale,cy+190*scale),fill=col,width=max(8,int(28*scale)))
    d.line((cx+25*scale,cy+55*scale,cx+85*scale,cy+190*scale),fill=col,width=max(8,int(28*scale)))
    d.line((cx-45*scale,cy-75*scale,cx-125*scale,cy+20*scale),fill=col,width=max(8,int(24*scale)))
    d.line((cx+45*scale,cy-75*scale,cx+120*scale,cy+10*scale),fill=col,width=max(8,int(24*scale)))

def radar(d,cx,cy):
    d.line((cx,cy,cx,cy+220),fill=(220,225,220,255),width=10)
    d.arc((cx-230,cy-230,cx+230,cy+230),180,360,fill=(100,210,230,220),width=7)
    d.arc((cx-150,cy-150,cx+150,cy+150),180,360,fill=(100,210,230,180),width=5)
    d.line((cx,cy,cx+190,cy-170),fill=(255,210,120,255),width=8)
    d.ellipse((cx-18,cy-18,cx+18,cy+18),fill=(255,220,145,255))

def monas(d,cx,cy):
    d.polygon([(cx-100,cy+260),(cx+100,cy+260),(cx+65,cy-20),(cx-65,cy-20)],fill=(210,215,210,255))
    d.rectangle((cx-75,cy-90,cx+75,cy-20),fill=(225,225,215,255))
    d.polygon([(cx-28,cy-90),(cx+28,cy-90),(cx+16,cy-270),(cx-16,cy-270)],fill=(235,230,210,255))
    d.ellipse((cx-24,cy-300,cx+24,cy-250),fill=(220,55,55,255))
    d.rectangle((cx-150,cy+260,cx+150,cy+300),fill=(180,190,195,255))

def create_scenes():
    scenes=[]
    titles=[
      ("KEKUATAN MILITER INDONESIA","SIAP MENJAGA NUSANTARA"),
      ("TIGA MATRA, SATU TUGAS","DARAT • LAUT • UDARA"),
      ("PENJAGA LAUT NUSANTARA","338 ASET ANGKATAN LAUT*"),
      ("KESIAPSIAGAAN PERTAHANAN","PERSONEL & TEKNOLOGI"),
      ("INDONESIA KUAT","TNI SIAP • NUSANTARA TEGAK")
    ]
    for i,(title,sub) in enumerate(titles):
        im=base_scene(i,title,sub); d=ImageDraw.Draw(im,"RGBA")
        if i==0:
            island_shapes(d)
            d.ellipse((140,500,940,1300),outline=(255,205,115,100),width=5)
            centered(d,(W//2,1390),"SABANG  —  MERAUKE",font(36,True),(255,255,255,240))
        elif i==1:
            soldier(d,260,1050,0.9); soldier(d,540,1050,1.0); soldier(d,820,1050,0.9)
            ship(d,540,1430,0.85); jet(d,540,570,0.65)
            centered(d,(W//2,1640),"ANGKATAN DARAT  •  LAUT  •  UDARA",font(27,True),(245,245,245,255))
        elif i==2:
            island_shapes(d,yoff=-30,scale=1.0); ship(d,540,1320,1.0)
            for x in [160,920]:
                d.ellipse((x-55,800-55,x+55,800+55),outline=(255,210,120,180),width=5)
                d.line((x,800,x+120,690),fill=(255,210,120,180),width=4)
            centered(d,(W//2,1660),"ESTIMASI GLOBAL FIREPOWER 2026",font(27,True),(235,195,120,255))
        elif i==3:
            soldier(d,280,1120,1.05); soldier(d,540,1120,1.05); soldier(d,800,1120,1.05)
            radar(d,540,650)
            d.ellipse((200,430,880,1110),outline=(75,185,215,80),width=4)
            centered(d,(W//2,1540),"DISIPLIN  •  LATIHAN  •  KESIAPSIAGAAN",font(27,True),(245,245,245,255))
        else:
            monas(d,540,1040)
            # Generic heraldic bird silhouette, not official insignia.
            d.ellipse((420,570,660,790),fill=(210,180,105,255))
            d.polygon([(440,650),(250,560),(370,730),(540,700),(710,730),(830,560),(640,650)],fill=(210,180,105,255))
            d.polygon([(520,770),(560,770),(540,850)],fill=(210,180,105,255))
            centered(d,(W//2,1510),"MERAH PUTIH MENJAGA NUSANTARA",font(30,True),(255,255,255,255))
        # vignette
        mask=Image.new("L",(W,H),0); md=ImageDraw.Draw(mask)
        md.ellipse((-250,-100,W+250,H+150),fill=180)
        mask=mask.filter(ImageFilter.GaussianBlur(180))
        dark=Image.new("RGB",(W,H),(0,0,0))
        im=Image.composite(im,dark,Image.eval(mask,lambda p: 255-p//2))
        p=TMP/f"scene_{i}.png"; im.save(p,optimize=True); scenes.append(p)
    return scenes

def make_voice():
    script=("Dari Sabang sampai Merauke, Indonesia menjaga setiap inci kedaulatan. "
            "TNI hadir di darat, laut, dan udara. "
            "Dengan sekitar tiga ratus tiga puluh delapan aset angkatan laut menurut Global Firepower dua ribu dua puluh enam, Indonesia berdiri kokoh di tengah kepulauan Nusantara. "
            "Lebih dari empat ratus ribu personel aktif, menurut estimasi Global Firepower dua ribu dua puluh enam, siap menjaga kedaulatan bangsa. "
            "Indonesia kuat. TNI siap. Nusantara tegak.")
    espeak=shutil.which("espeak-ng") or shutil.which("espeak")
    if not espeak:
        raise RuntimeError("eSpeak NG tidak ditemukan. Install espeak-ng terlebih dahulu.")
    wav=TMP/"narration.wav"
    # Voice id is preferred; fallback to Indonesian-capable default if unavailable.
    cmd=[espeak,"-v","id","-s","178","-p","34","-a","165","-w",str(wav),script]
    try: run(cmd)
    except subprocess.CalledProcessError:
        print("Peringatan: voice 'id' tidak tersedia; memakai voice default eSpeak.",file=sys.stderr)
        run([espeak,"-s","178","-p","34","-a","165","-w",str(wav),script])
    return wav

def make_subtitles():
    # ASS subtitles: readable, moderate size, bottom safe-zone.
    lines=[
      (0,4,"Dari Sabang sampai Merauke,\nIndonesia menjaga setiap inci kedaulatan."),
      (4,10,"TNI hadir di darat, laut, dan udara."),
      (10,17,"Sekitar 338 aset angkatan laut menurut\\NGlobal Firepower 2026."),
      (17,24,"Lebih dari 400 ribu personel aktif*\\Nsiap menjaga kedaulatan bangsa."),
      (24,30,"Indonesia kuat. TNI siap.\\NNusantara tegak.")
    ]
    def ts(s):
        h=int(s//3600); m=int((s%3600)//60); sec=s%60
        return f"{h}:{m:02d}:{sec:05.2f}"
    ass=TMP/"subtitles.ass"
    with ass.open("w",encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        f.write("Style: Default,DejaVu Sans,48,&H00FFFFFF,&H0000FFFF,&H00101825,&H99000000,-1,0,0,0,100,100,0,0,1,3,1,2,90,90,210,1\n\n")
        f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a,b,t in lines:
            f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{t}\n")
    return ass

def main():
    scenes=create_scenes()
    voice=make_voice()
    ass=make_subtitles()
    segments=[]
    durations=[4,6,7,7,6]
    for i,(img,dur) in enumerate(zip(scenes,durations)):
        seg=TMP/f"segment_{i}.mp4"
        frames=dur*FPS
        vf=(f"scale=1200:2134:force_original_aspect_ratio=increase,"
            f"crop=1200:2134,zoompan=z='min(zoom+0.0007,1.10)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
            f"setsar=1,format=yuv420p")
        run(["ffmpeg","-y","-loop","1","-i",str(img),"-vf",vf,"-t",str(dur),
             "-r",str(FPS),"-an","-c:v","libx264","-preset","ultrafast","-crf","21",str(seg)])
        segments.append(seg)
    concat=TMP/"concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments),encoding="utf-8")
    silent=TMP/"picture.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    final=OUT/"indonesia-military-video.mp4"
    # Synthesized low drone + pulse bed, no third-party music.
    music_expr="sine=frequency=55:sample_rate=48000,volume=0.10"
    run(["ffmpeg","-y","-i",str(silent),"-i",str(voice),"-f","lavfi","-i",
         "sine=frequency=110:sample_rate=48000:duration=30",
         "-filter_complex",
         f"[1:a]atempo=1.12,volume=1.45,apad,atrim=0:30,adelay=250|250[vo];"
         f"[2:a]volume=0.08,afade=t=in:st=0:d=2,afade=t=out:st=27:d=3[bed];"
         f"[vo][bed]amix=inputs=2:duration=longest:normalize=0,"
         f"loudnorm=I=-16:TP=-1.5:LRA=11[a]",
         "-vf",f"subtitles={ass.as_posix()}:fontsdir=/usr/share/fonts/truetype/dejavu",
         "-map","0:v:0","-map","[a]","-t","30","-r",str(FPS),
         "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",str(final)])
    probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,r_frame_rate","-of","default=noprint_wrappers=1",str(final)],text=True)
    print(probe)
    duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(final)],text=True).strip())
    if abs(duration-30.0)>0.05:
        raise RuntimeError(f"Durasi akhir bukan 30 detik: {duration}")
    print(f"Berhasil: {final} ({final.stat().st_size} bytes)")

if __name__=="__main__":
    main()
