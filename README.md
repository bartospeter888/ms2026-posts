# MS 2026 – FPL Addicted Výsledkové karty

Každé ráno (08:30 SELČ) se automaticky vygeneruje stránka s výsledky včerejších zápasů.
Na každé kartě nahraješ fotku hráče, naaranžuješ prstem a stáhneš PNG na Instagram.

---

## Jednorázový setup (udělej jednou před 11. 6.)

### 1. Vytvoř GitHub repozitář

1. Přejdi na [github.com/new](https://github.com/new)
2. Název: `ms2026-posts`
3. Visibility: **Public** (GitHub Pages je zdarma jen pro public repo na free účtu)
4. Klikni **Create repository** — NEZaškrtávej žádné volby (prázdné repo)

### 2. Pushnout projekt na GitHub

Otevři PowerShell v `Desktop\ms2026-posts\` a spusť:

```powershell
git init
git add .
git commit -m "init: MS 2026 post generator"
git branch -M main
git remote add origin https://github.com/TVOJE_UZIVATELSKE_JMENO/ms2026-posts.git
git push -u origin main
```

### 3. Zapnout GitHub Pages

1. V repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/docs`
4. Uložit → stránka bude za ~1 min na `https://TVOJE_JMENO.github.io/ms2026-posts/`

### 4. Přidat API klíč jako secret

1. V repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. Name: `FOOTBALL_DATA_API_KEY`
4. Value: tvůj API klíč z [football-data.org](https://www.football-data.org)
5. Uložit

### 5. Stáhnout vlajky (dělá CI automaticky, ale můžeš i lokálně)

```powershell
cd Desktop\ms2026-posts
pip install -r requirements.txt
python scripts/download_flags.py
git add docs/assets/flags/
git commit -m "feat: add all WC 2026 flags"
git push
```

---

## Každodenní workflow

| Čas         | Co se děje |
|-------------|------------|
| **08:30 SELČ** | GitHub Actions stáhne výsledky z football-data.org |
| | Vygeneruje `docs/index.html` se všemi kartami |
| | Commitne a pushne — GitHub Pages stránka se aktualizuje |
| **Kdykoli ráno** | Otevřeš stejný odkaz na mobilu |
| | Nahraješ fotku, naaranžuješ prstem, stáhneš PNG |
| | Zkopíruješ caption → doplníš top fantasy hráče → postuješ |

---

## Manuální spuštění (testování / nouzový run)

GitHub → repo → **Actions** → **MS 2026 – Daily Match Cards** → **Run workflow**

Volitelně zadej datum ve formátu `YYYY-MM-DD` (např. `2026-06-12`) pro konkrétní den.

---

## Struktura projektu

```
ms2026-posts/
├── .github/workflows/daily.yml   ← GitHub Actions cron
├── docs/
│   ├── index.html                ← generovaná stránka (GitHub Pages)
│   └── assets/
│       ├── flags/                ← PNG vlajky všech WC týmů
│       ├── logos/wc2026.png      ← FIFA WC 2026 logo
│       ├── logos/fpl_addicted.png← FPL Addicted logo
│       ├── style.css             ← styly karet
│       └── app.js                ← foto interakce + PNG export
├── scripts/
│   ├── fetch_matches.py          ← stáhne výsledky → matches.json
│   ├── generate_page.py          ← matches.json → docs/index.html
│   ├── download_flags.py         ← jednorázové stažení vlajek
│   └── flag_map.py               ← FIFA TLA → ISO kód mapping
├── matches.json                  ← poslední stažená data
└── requirements.txt
```

---

## Poznámky

- **API free tier**: Střelci a asistence jsou na higher tieru. Pokud API vrátí prázdný seznam, v captionech
  bude prázdné pole — nebojí se, skripty s tím počítají.
- **Vlajky**: Máš lokálně CZ, KR, MX, ZA. Ostatní stáhne `download_flags.py` z flagcdn.com.
- **Fonty**: Anton + Barlow Condensed z Google Fonts — potřebuješ internet při generování PNG.
