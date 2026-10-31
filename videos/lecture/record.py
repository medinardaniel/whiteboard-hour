"""Record one lecture video, encode a web copy, and build a frame contact sheet for checking.

    python videos/lecture/record.py c02            # full: audio + recording + encode + sheet
    python videos/lecture/record.py c02 --audio    # narration only: prints speech length and the runtime estimate

Writes in videos/lecture/<id>/: raw.mp4 (ignored), <id>-lecture.mp4 + .jpg (web copies), raw_build/sheet.png.
The sheet holds one frame per step, 3 s after that step's narration starts. Each frame must show what its line says.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
MAKE = Path.home() / ".claude/skills/demo/scripts/make_demo.py"
CHECK = Path.home() / ".claude/skills/demo/scripts/check_frames.py"


def ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def main():
    vid = sys.argv[1]
    d = HERE / vid
    spec = json.loads((d / "cues.json").read_text(encoding="utf-8"))
    pauses = sum(c.get("post_ms", spec.get("gap_ms", 400)) for c in spec["cues"]) / 1000
    actions = sum(1 for c in spec["cues"] if c.get("do"))
    if "--audio" in sys.argv:
        out = subprocess.run([sys.executable, str(MAKE), "cues.json", "--only-audio"], cwd=d, capture_output=True, text=True).stdout
        speech = float(re.findall(r"total speech (\d+)s", out)[-1])
        est = speech + pauses + actions * 0.35 + spec.get("load_ms", 1200) / 1000 + spec.get("tail_ms", 1500) / 1000
        print(f"{vid}: speech {speech:.0f}s + pauses {pauses:.1f}s -> estimated {est:.0f}s ({'OK' if est <= 178 else 'TOO LONG, trim'})")
        return
    r = subprocess.run([sys.executable, str(MAKE), "cues.json", "--out", "raw.mp4"], cwd=d, capture_output=True, text=True)
    log = r.stdout + r.stderr
    clock = [l.strip() for l in log.splitlines() if "video clock" in l or "WARNING" in l]
    if r.returncode != 0 or not (d / "raw.mp4").exists():
        print(log[-2000:]); sys.exit(f"{vid}: recording failed")
    subprocess.run([ff(), "-y", "-loglevel", "error", "-i", "raw.mp4", "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", f"{vid}-lecture.mp4"], cwd=d, check=True)
    subprocess.run([ff(), "-y", "-loglevel", "error", "-ss", "9", "-i", "raw.mp4", "-frames:v", "1", "-vf", "scale=960:-2", "-q:v", "4",
                    f"{vid}-lecture.jpg"], cwd=d, check=True)
    subprocess.run([sys.executable, str(CHECK), "cues.json", "--out", "raw.mp4", "--offset", "3"], cwd=d, capture_output=True)
    import fitz
    fr = sorted((d / "raw_build" / "frames").glob("cue_*.png"))
    W, H, cols = 480, 270, 4
    doc = fitz.open(); pg = doc.new_page(width=W * cols, height=H * ((len(fr) + cols - 1) // cols))
    for k, f in enumerate(fr):
        pg.insert_image(fitz.Rect((k % cols) * W, (k // cols) * H, (k % cols + 1) * W, (k // cols + 1) * H), filename=str(f))
    pg.get_pixmap(dpi=72).save(str(d / "raw_build" / "sheet.png"))
    dur = re.findall(r"Duration: (\d+):(\d+):([\d.]+)", subprocess.run([ff(), "-i", str(d / "raw.mp4")], capture_output=True, text=True).stderr)[0]
    secs = int(dur[1]) * 60 + float(dur[2])
    print(f"{vid}: {secs:.0f}s ({'OK' if secs <= 180 else 'OVER 3 MIN'})  {'; '.join(clock)}")
    print(f"check: {d / 'raw_build' / 'sheet.png'}")


if __name__ == "__main__":
    main()
