#!/usr/bin/env python3
"""Petit Journal: baixa os episódios novos do feed e transcreve localmente.

Uso:  python3 tools/petit.py OUT_DIR [--days 2]
Para cada episódio publicado nos últimos N dias que ainda não aparece em
data/news/*.json (campo "pj_guid"), grava OUT_DIR/<guid>.txt (transcrição) e
OUT_DIR/<guid>.json (metadados). A transcrição é só material de trabalho:
NÃO vai para o repositório; o app publica apenas tópicos escritos com
palavras próprias + link para o episódio.

Requer: pip install --break-system-packages faster-whisper ; ffmpeg
"""
import glob, json, os, subprocess, sys, time, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

FEED = "https://www.spreaker.com/show/5659715/episodes/feed"
IT = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def done_guids():
    g = set()
    for f in glob.glob(os.path.join(ROOT, "data/news/*.json")):
        try:
            for c in json.load(open(f)).get("cards", []):
                if c.get("pj_guid"):
                    g.add(c["pj_guid"])
        except Exception:
            pass
    return g


def transcribe(mp3, model):
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = model.transcribe(a, language="pt", beam_size=1, vad_filter=True)
    return "\n".join(s.text.strip() for s in segs)


def main():
    out = sys.argv[1]
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 2
    os.makedirs(out, exist_ok=True)
    xml = urllib.request.urlopen(FEED, timeout=60).read()
    items = ET.fromstring(xml).iter("item")
    since = datetime.now(timezone.utc) - timedelta(days=days)
    seen = done_guids()
    todo = []
    for it in items:
        dt = parsedate_to_datetime(it.findtext("pubDate"))
        if dt < since:
            break
        guid = it.findtext("guid").rstrip("/").split("/")[-1]
        if guid in seen:
            continue
        todo.append(dict(guid=guid, titulo=it.findtext("title"), link=it.findtext("link"),
                         pub=dt.isoformat(), dur=int(it.findtext(IT + "duration") or 0),
                         mp3=it.find("enclosure").get("url")))
    if not todo:
        print("nenhum episódio novo")
        return
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("PJ_MODEL", "base"), device="cpu", compute_type="int8")
    for ep in todo:
        mp3 = os.path.join(out, ep["guid"] + ".mp3")
        urllib.request.urlretrieve(ep["mp3"], mp3)
        t = time.time()
        txt = transcribe(mp3, model)
        os.remove(mp3)
        open(os.path.join(out, ep["guid"] + ".txt"), "w").write(txt)
        json.dump(ep, open(os.path.join(out, ep["guid"] + ".json"), "w"), ensure_ascii=False, indent=1)
        print(f"ok {ep['guid']} {ep['titulo']} ({time.time()-t:.0f}s)")


if __name__ == "__main__":
    main()
