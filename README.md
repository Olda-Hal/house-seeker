# Hledání bytu pro 4–5 lidí v Brně

Skript každou hodinu stáhne nové inzeráty z **sreality.cz**, **bezrealitky.cz**
a **reality.idnes.cz**, stáhne k nim detail (popis, cena, zálohy, vybavení)
a pošle je LLM na [llm.ai.e-infra.cz](https://llm.ai.e-infra.cz/v1). Model
vyhodnotí, jestli má byt dost neprůchozích pokojů pro 2 páry (4 lidi), nebo
pro 2 páry + jednotlivce (5 lidí), a jestli se vejde do rozpočtu. Schválené
inzeráty posílá na Discord.

## Požadavky

- Python 3.10+
- `pip install -r requirements.txt`
- API token z <https://chat.ai.e-infra.cz> (Account → API keys)
- Discord webhook URL

## GitHub Actions

V nastavení repozitáře (Settings → Secrets and variables → Actions) přidej:

| Secret | Význam |
|---|---|
| `WEBHOOK_URL` | Discord webhook |
| `E_INFRA_API_TOKEN` | API klíč z chat.ai.e-infra.cz |

Workflow běží každou hodinu (`17 * * * *`) a lze ho spustit ručně přes
*Actions → House Scraper → Run workflow*. Změny v `seen.json` commituje sám.

## Lokální spuštění

```bash
pip install -r requirements.txt

# jen stáhnout a vypsat, bez AI a bez webhooku
python main.py --no-ai --limit 5

# plný běh, ale bez zápisu do seen.json a bez Discordu
WEBHOOK_URL=x E_INFRA_API_TOKEN=... python main.py --dry-run --limit 5
```

## Rozpočet a dispozice

- 5 lidí: max **30 000 Kč/měsíc** včetně energií (6 000 Kč/osobu)
- 4 lidé: max **30 000 Kč/měsíc** včetně energií (7 500 Kč/osobu)
- hledané dispozice: `3+kk`, `3+1`, `4+kk`, `4+1`
- vyžadovány 2 neprůchozí ložnice pro 4 lidi, 3 pro 5 lidí

## Volitelné proměnné prostředí

| Proměnná | Výchozí | Význam |
|---|---|---|
| `LLM_MODEL` | `deepseek` | název/alias modelu |
| `LLM_BASE_URL` | `https://llm.ai.e-infra.cz/v1` | OpenAI-kompatibilní endpoint |
| `MAX_TOTAL_CZK_4` | `30000` | strop pro 4 lidi |
| `MAX_TOTAL_CZK_5` | `30000` | strop pro 5 lidí |
| `MAX_AI_CALLS` | `120` | strop inzerátů poslaných do AI na jeden běh |
| `LLM_BATCH_SIZE` | `10` | inzerátů v jednom AI requestu |
| `LLM_BATCH_DELAY` | `1.0` | pauza (s) mezi dávkami |
| `LLM_MAX_RETRIES` | `6` | počet pokusů při 429/5xx |
| `MAX_WORKERS` | `4` | paralelní stahování detailů |
| `MAX_PAGES` | `3` | stránky sreality |
| `BEZREALITKY_PAGES` | `2` | stránky bezrealitky |
| `IDNES_PAGES` | `2` | stránky idnes |
| `SEEN_FILE` | `seen.json` | soubor s již viděnými inzeráty |
| `AI_MIN_CONFIDENCE` | `0.35` | minimální jistota modelu |

## Poznámky

- Selenium, Firefox ani geckodriver už nejsou potřeba.
- Inzeráty se do AI posílají **po dávkách** (výchozí 10) a dávky jdou
  sekvenčně, aby se vyhnulo limitům API (429). Při 429 se čeká podle
  `Retry-After`; když je dávka moc velká, automaticky se rozdělí.
- Stejný byt na více portálech se deduplikuje podle ulice, dispozice,
  nájmu a přibližné výměry.
- Pokud se inzerát nevyhodnotí (výpadek AI/stažení detailu), zůstane
  neuložený v `seen.json` a zkusí se znovu příští běh.
- `seen.json` drží posledních 5 000 položek.
