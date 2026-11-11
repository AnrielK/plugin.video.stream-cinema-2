#!/usr/bin/env python3
"""Sestaví Kodi repozitář (zips/ + addons.xml + addons.xml.md5) z tohoto doplňku.

  python tools/kodi_repo.py build --out DIR
      přidá ZIP aktuální verze doplňku do DIR a přegeneruje addons.xml + md5

  python tools/kodi_repo.py repo-addon --token TOKEN [--out repository.zip]
      vyrobí instalační ZIP repozitářového doplňku (token je v něm zapečený,
      proto se nikdy necommituje – generuje se lokálně)

Jen standardní knihovna.
"""
import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".github", "tools", "__pycache__", ".idea", ".vscode"}
EXCLUDE_FILES = {"dev-requirements.txt", ".gitignore", ".gitattributes"}
EXCLUDE_RE = re.compile(r"^addon\d+\.xml$|\.pyc$")  # addon16..21.xml jsou jen šablony

REPO_ID = "repository.scc-private"


def read_meta(xml_text):
    head = re.search(r"<addon\b[^>]*>", xml_text).group(0)
    return (re.search(r'\bid="([^"]+)"', head).group(1),
            re.search(r'\bversion="([^"]+)"', head).group(1))


def vkey(v):
    return [int(p) if p.isdigit() else p for p in re.split(r"[.\-]", v)]


def strip_decl(xml_text):
    return re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", xml_text).strip()


def build_zip(out):
    xml = (ROOT / "addon.xml").read_text(encoding="utf-8")
    addon_id, version = read_meta(xml)
    dest = out / "zips" / addon_id
    dest.mkdir(parents=True, exist_ok=True)
    zpath = dest / f"{addon_id}-{version}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob("*")):
            rel = p.relative_to(ROOT)
            if p.is_dir() or EXCLUDE_DIRS & set(rel.parts):
                continue
            if rel.name in EXCLUDE_FILES or EXCLUDE_RE.search(rel.name):
                continue
            z.write(p, f"{addon_id}/{rel.as_posix()}")
    # ikona/fanart vedle ZIPu (Kodi je zobrazí v seznamu repozitáře)
    for asset in ("icon", "fanart"):
        m = re.search(rf"<{asset}>([^<]+)</{asset}>", xml)
        if m and (ROOT / m.group(1)).exists():
            (dest / f"{asset}{Path(m.group(1)).suffix}").write_bytes((ROOT / m.group(1)).read_bytes())
    return zpath


def generate_index(out):
    parts = []
    for d in sorted((out / "zips").iterdir()):
        zips = list(d.glob("*.zip"))
        if not zips:
            continue
        latest = max(zips, key=lambda p: vkey(read_meta_from_zip(p)[1]))
        with zipfile.ZipFile(latest) as z:
            xml = z.read(f"{d.name}/addon.xml").decode("utf-8")
        parts.append(strip_decl(xml))
    body = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' \
           + "\n".join(parts) + "\n</addons>\n"
    (out / "addons.xml").write_text(body, encoding="utf-8")
    (out / "addons.xml.md5").write_text(
        hashlib.md5(body.encode("utf-8")).hexdigest(), encoding="utf-8")


def read_meta_from_zip(path):
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith("/addon.xml") and n.count("/") == 1)
        return read_meta(z.read(name).decode("utf-8"))


def cmd_build(a):
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    z = build_zip(out)
    generate_index(out)
    print(f"OK: {z.relative_to(out)}  ->  addons.xml, addons.xml.md5")


def cmd_repo_addon(a):
    base = f"https://{a.owner}:{a.token}@raw.githubusercontent.com/{a.owner}/{a.repo}/{a.branch}"
    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="{REPO_ID}" name="SCC privátní repozitář" version="{a.version}" provider-name="Jiří">
    <extension point="xbmc.addon.repository" name="SCC privátní repozitář">
        <dir>
            <info compressed="false">{base}/addons.xml</info>
            <checksum>{base}/addons.xml.md5</checksum>
            <datadir zip="true">{base}/zips/</datadir>
        </dir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>Privátní repozitář pro Stream Cinema (aktualizace z GitHubu)</summary>
        <platform>all</platform>
    </extension>
</addon>
'''
    out = Path(a.out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{REPO_ID}/addon.xml", xml)
    print(f"OK: {out}  (obsahuje token – nesdílej a necommituj)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("repo-addon")
    r.add_argument("--token", required=True)
    r.add_argument("--owner", default="AnrielK")
    r.add_argument("--repo", default="plugin.video.stream-cinema-2")
    r.add_argument("--branch", default="kodi-repo")
    r.add_argument("--version", default="1.0.0")
    r.add_argument("--out", default=f"{REPO_ID}-1.0.0.zip")
    r.set_defaults(fn=cmd_repo_addon)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
