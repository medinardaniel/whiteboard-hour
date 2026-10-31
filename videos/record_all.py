"""Record every component video, then shrink each for the web and grab a poster frame.

    python videos/record_all.py [--jobs 3] [--only 3,8]

Raw recordings go to videos/raw/ (not committed). Web copies: videos/cNN.mp4 (720p) and videos/cNN.jpg.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
MAKE = Path.home() / ".claude/skills/demo/scripts/make_demo.py"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def one(n):
    cue = HERE / "cues" / f"c{n:02d}.json"
    raw = HERE / "raw" / f"c{n:02d}.mp4"
    log = HERE / "raw" / f"c{n:02d}.log"
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run([sys.executable, str(MAKE), str(cue), "--out", str(raw)], stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
    if r.returncode != 0 or not raw.exists():
        return n, f"FAILED (see {log.name})"
    web, poster = HERE / f"c{n:02d}.mp4", HERE / f"c{n:02d}.jpg"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(raw), "-vf", "scale=1280:-2",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(web)], check=True)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-ss", "3", "-i", str(raw), "-frames:v", "1",
                    "-vf", "scale=960:-2", "-q:v", "4", str(poster)], check=True)
    clock = [l for l in log.read_text(encoding="utf-8", errors="replace").splitlines() if "clock" in l.lower()]
    return n, f"ok {web.stat().st_size / 1e6:.1f} MB  {clock[-1].strip() if clock else ''}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    (HERE / "raw").mkdir(exist_ok=True)
    nums = [int(x) for x in a.only.split(",") if x] or list(range(1, 24))
    with ThreadPoolExecutor(a.jobs) as ex:
        for n, msg in ex.map(one, nums):
            print(f"c{n:02d}: {msg}", flush=True)


if __name__ == "__main__":
    main()
