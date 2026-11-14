# Hledání bytu pro 4 lidi v Brně

Skript každou hodinu stáhne nové inzeráty z **sreality.cz**, **bezrealitky.cz**
a **reality.idnes.cz**, stáhne k nim detail (popis, cena, zálohy, vybavení)
a pošle je LLM na [llm.ai.e-infra.cz](https://llm.ai.e-infra.cz/v1). Model
vyhodnotí, jestli má byt dost neprůchozích pokojů pro 2 páry (4 lidi)
a jestli se vejde do rozpočtu. Schválené inzeráty posílá na Discord.

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
*Actions → House Scraper → Run workflow*. Ruční spuštění má volitelné
parametry `llm_model` (např. `deepseek`, `mini`, `qwen3.8-27b`),
`max_ai_calls` a `debug`. Změny v `seen.json` commituje sám.

## Lokální spuštění

```bash
pip install -r requirements.txt

# jen stáhnout a vypsat, bez AI a bez webhooku
python main.py --no-ai --limit 5

# plný běh, ale bez zápisu do seen.json a bez Discordu
WEBHOOK_URL=x E_INFRA_API_TOKEN=... python main.py --dry-run --limit 5
```

## Rozpočet a dispozice

- 4 lidé (2 páry): max **6 500 Kč/osobu**, tj. **26 000 Kč/měsíc** včetně energií
- hledané dispozice: `3+kk`, `3+1`, `4+kk`, `4+1`
- vyžadovány alespoň 2 neprůchozí ložnice

## Volitelné proměnné prostředí

| Proměnná | Výchozí | Význam |
|---|---|---|
| `LLM_MODEL` | `deepseek` | název/alias modelu |
| `LLM_BASE_URL` | `https://llm.ai.e-infra.cz/v1` | OpenAI-kompatibilní endpoint |
| `MAX_TOTAL_CZK` | `26000` | strop celkem pro 4 lidi včetně energií |
| `BEZREALITKY_PAGE_SIZE` | `50` | počet inzerátů na stránku GraphQL API |
| `MAX_AI_CALLS` | `120` | strop inzerátů poslaných do AI na jeden běh |
| `LLM_BATCH_SIZE` | `10` | inzerátů v jednom AI requestu |
| `LLM_BATCH_DELAY` | `1.0` | pauza (s) mezi dávkami |
| `LLM_MAX_RETRIES` | `6` | počet pokusů při 429/5xx |
| `LLM_DISABLE_THINKING` | `1` | vypne reasoning u DeepSeeku (`content` pak není null) |
| `LLM_JSON_MODE` | `1` | požádá API o `response_format=json_object` |
| `LLM_DEBUG` | `0` | vypíše surovou odpověď modelu |
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
