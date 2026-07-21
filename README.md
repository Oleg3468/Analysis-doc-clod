# Analysis-doc-clod
# Agreement Analyzer

A tool that scans user agreements (terms of service, contracts) and flags
clauses that are unfavorable to the user: unilateral changes, silent
auto-renewals, third-party data sharing, hidden/non-refundable fees,
waivers of rights, and full liability limitations.

The project has two parts:
- **CLI** (`analyzer.py`) — scan a text file, an image, or a screenshot from the terminal.
- **API + mobile UI** (`app.py` + `IndexPage.vue`) — a FastAPI backend and a Quasar/Vue screen for a mobile app.

## Files
- `analyzer.py` — core detection logic (regex rules, OCR, CLI).
- `app.py` — FastAPI backend exposing `/analyze-text` and `/analyze-image`.
- `IndexPage.vue` — Quasar page that calls the backend and renders findings.
- `test_analyzer.py` — unit tests for the detection logic.
- `run_analyzer_json.py` — dev helper: analyze a file and print JSON.
- `test_agreement.txt` — sample agreement with several flagged clauses.

## Setup

```bash
pip install -r requirements.txt
```

OCR (image/screenshot scanning) additionally needs Tesseract installed on the system:
- Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng`
- macOS: `brew install tesseract tesseract-lang`
- Windows: install Tesseract and add it to PATH.

The CLI and API work without Tesseract too — text-file/text-payload scanning
doesn't need OCR at all; only `-i/--image` and `-s/--screenshot` do.

## Run the CLI

```bash
# Scan a text file
python3 analyzer.py -t test_agreement.txt

# Scan an image/screenshot from the gallery
python3 analyzer.py -i path/to/screenshot.png

# Capture and scan the active screen
python3 analyzer.py -s

# JSON output instead of colored text
python3 analyzer.py -t test_agreement.txt --json
```

## Run the API

```bash
python3 app.py
# or: uvicorn app:app --reload
```

Then `POST /analyze-text` with `{"text": "..."}` or `POST /analyze-image`
with a multipart image file.

## Run the mobile UI

`IndexPage.vue` is a Quasar page component. Drop it into a Quasar project's
`src/pages/` folder, set `API_BASE_URL` (env var `API_BASE_URL`) to point at
your deployed `app.py`, and run the Quasar dev server / build with Capacitor
as usual.

## Tests

```bash
python3 -m pytest -v
```
cd \~/Analysis-dok
cat >> README.md << 'EOF'

## Implementation Plan Template (адаптивный)

**Agent / Reasoning:** Claude Sonnet 4.6 / high reasoning  
**Роль:** Bounded implementation executor

**Goal:** Реализовать минимальный P7-shadow vertical slice...

(продолжи сюда полный шаблон)
