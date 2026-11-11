# plugin.video.stream-cinema-2

Zdrojový kód Kodi doplňku Stream Cinema Community (fork, GPL 2.0).

## Vydání nové verze
1. Zvyš `version` v `addon.xml`.
2. Push do `main` – workflow `.github/workflows/kodi-repo.yml` sestaví ZIPy a nahraje je do
   veřejného repozitáře [AnrielK/repository.anrielK](https://github.com/AnrielK/repository.anrielK)
   (GitHub Pages). Kodi pak nabídne aktualizaci.

Secret `KODI_REPO_TOKEN`: fine-grained token s Contents: Read and write pro `repository.anrielK`.

Závislosti dodávané z repozitáře (např. `script.module.yt-dlp`) leží jako hotové ZIPy v `extras/`.
Lokální sestavení: `python tools/kodi_repo.py build --out /tmp/repo`.
