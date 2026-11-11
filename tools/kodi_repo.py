#!/usr/bin/env python3
"""Sestaví Kodi repozitář (zips/ + addons.xml + addons.xml.md5) z tohoto doplňku.

  python tools/kodi_repo.py build --out DIR
      přidá ZIP aktuální verze doplňku (+ ZIPy z extras/ a repozitářový doplněk)
      do DIR a přegeneruje addons.xml + md5

  python tools/kodi_repo.py repo-addon [--base URL] [--out FILE]
      vyrobí jen instalační ZIP repozitářového doplňku

Jen standardní knihovna.
"""
import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", ".github", "tools", "extras", "__pycache__", ".idea", ".vscode"}
EXCLUDE_FILES = {"dev-requirements.txt", ".gitignore", ".gitattributes", "Readme.md", "README.md"}
EXCLUDE_RE = re.compile(r"^addon\d+\.xml$|\.pyc$")

REPO_ID = "repository.anrielK"
REPO_VERSION = "1.0.0"
# GitHub Pages repa AnrielK/repository.anrielK
DEFAULT_BASE = "https://anrielk.github.io/repository.anrielK"


def read_meta(xml_text):
    head = re.search(r"<addon\b[^>]*>", xml_text).group(0)
    return (re.search(r'\bid="([^"]+)"', head).group(1),
            re.search(r'\bversion="([^"]+)"', head).group(1))


def vkey(v):
    return [int(p) if p.isdigit() else p for p in re.split(r"[.\-]", v)]


def strip_decl(xml_text):
    return re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", xml_text).strip()


def read_meta_from_zip(path):
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith("/addon.xml") and n.count("/") == 1)
        return read_meta(z.read(name).decode("utf-8"))


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


def add_extras(out):
    """Přidá hotové ZIPy doplňků z extras/ (např. závislosti). Složku v ZIPu přejmenuje na id doplňku."""
    for src in sorted((ROOT / "extras").glob("*.zip")):
        with zipfile.ZipFile(src) as zin:
            names = [n for n in zin.namelist() if not n.endswith("/")]
            top = names[0].split("/")[0]
            xml = zin.read(f"{top}/addon.xml").decode("utf-8")
            addon_id, version = read_meta(xml)
            dest = out / "zips" / addon_id
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / f"{addon_id}-{version}.zip"
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
                for n in names:
                    zout.writestr(f"{addon_id}/{n.split('/', 1)[1]}", zin.read(n))
        print(f"OK: {target.relative_to(out)} (extras)")


def repo_addon_xml(base, version=REPO_VERSION):
    base = base.rstrip("/")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="{REPO_ID}" name="AnrielK repozitář" version="{version}" provider-name="AnrielK">
    <extension point="xbmc.addon.repository" name="AnrielK repozitář">
        <dir>
            <info compressed="false">{base}/addons.xml</info>
            <checksum>{base}/addons.xml.md5</checksum>
            <datadir zip="true">{base}/zips/</datadir>
        </dir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>AnrielK repozitář (Stream Cinema Community)</summary>
        <platform>all</platform>
    </extension>
</addon>
'''


def write_repo_addon_zip(path, base):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{REPO_ID}/addon.xml", repo_addon_xml(base))


def add_repo_addon(out, base):
    """Repozitářový doplněk jde i do repozitáře (samoaktualizace) a jako ZIP do kořene ke stažení."""
    name = f"{REPO_ID}-{REPO_VERSION}.zip"
    write_repo_addon_zip(out / "zips" / REPO_ID / name, base)
    for old in out.glob("repository.*.zip"):
        old.unlink()
    write_repo_addon_zip(out / name, base)
    print(f"OK: {name} (repozitářový doplněk)")


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


def cmd_build(a):
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    z = build_zip(out)
    add_extras(out)
    add_repo_addon(out, a.base)
    generate_index(out)
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"OK: {z.relative_to(out)}  ->  addons.xml, addons.xml.md5")


def cmd_repo_addon(a):
    out = Path(a.out)
    write_repo_addon_zip(out, a.base)
    print(f"OK: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", required=True)
    b.add_argument("--base", default=DEFAULT_BASE)
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("repo-addon")
    r.add_argument("--base", default=DEFAULT_BASE)
    r.add_argument("--out", default=f"{REPO_ID}-{REPO_VERSION}.zip")
    r.set_defaults(fn=cmd_repo_addon)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
