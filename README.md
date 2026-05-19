# ScreenLingo

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows-0078D6)](https://www.microsoft.com/windows)

Real-time **screen translation** for Windows, plus a built-in **vocabulary learner** that tracks words you see often and helps you memorize them.

> **Soft launch (v1.0.0)** — Windows desktop app. Feedback welcome via [Issues](https://github.com/chaturvedi-vardhanharsh/Screenlingo/issues).

## Features

- **Live translate** — Captures your screen (full screen or a selected region), reads text with OCR, and shows translations in a floating overlay.
- **Translate now** — One-shot capture with `Ctrl+Shift+T`.
- **Vocabulary tracking** — Words you encounter repeatedly are saved automatically (after appearing twice).
- **Learn mode** — Flashcard reviews with spaced repetition for your most common words.
- **20+ languages** — Powered by Google Translate (via `deep-translator`).

## Quick start

**Windows only.** Requires [Python 3.10+](https://www.python.org/downloads/).

```powershell
git clone https://github.com/chaturvedi-vardhanharsh/Screenlingo.git
cd Screenlingo
.\run.bat
```

Or download the ZIP from GitHub, extract, open PowerShell in that folder, and run `.\run.bat`.

The first run creates a virtual environment and installs dependencies automatically.

## Install (manual)

```powershell
cd screenlingo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Optional — install as a CLI command:

```powershell
pip install -e .
screenlingo
```

## How to use

1. Open **Live Translate** and choose source/target languages.
2. Click **Select screen area** and drag over the content you want translated.
3. Click **Start live translation** — the overlay shows detected text and translation.
4. Use **Learn Words** after some live sessions to review frequent words.
5. Browse **My Vocabulary** for your word list and stats.

## Hotkeys

| Key | Action |
|-----|--------|
| `Ctrl+Shift+T` | Translate now |
| `Ctrl+Shift+L` | Toggle live translation |

Global hotkeys may require running as Administrator on some systems.

## Documentation

| Guide | Description |
|-------|-------------|
| [Running on Windows](docs/RUNNING_ON_WINDOWS.md) | Full install and troubleshooting for your PC |
| [Publish to GitHub](docs/GITHUB_PUBLISH.md) | Maintainer guide for releases and pushing the repo |
| [Changelog](CHANGELOG.md) | Version history |

## Requirements

- Windows 10/11 (64-bit)
- Python 3.10–3.13 recommended
- Internet connection for translations

## Data & privacy

- Screen captures are processed **locally** (OCR uses Windows built-in engine).
- Only **detected text** is sent for translation (not screen images).
- Settings: `%USERPROFILE%\.screenlingo\config.json`
- Vocabulary: `%USERPROFILE%\.screenlingo\vocabulary.db`

## Project structure

```
screenlingo/
├── main.py              # Entry point
├── run.bat              # Windows launcher
├── requirements.txt
├── pyproject.toml       # Package metadata
├── screenlingo/         # Application code
│   ├── app.py           # Main UI
│   ├── engine.py        # Live translation loop
│   ├── ocr.py           # Windows OCR
│   ├── translator.py
│   └── vocabulary.py
└── docs/
```

## Troubleshooting

- **No text detected** — Use a smaller, high-contrast region; zoom the source app.
- **OCR language** — Add your source language in Windows **Settings → Time & language → Language**.
- **Hotkeys don't work** — Run as Administrator or use in-app buttons.
- **Broken venv after Python upgrade** — Delete `.venv` and run `.\run.bat` again.

See [docs/RUNNING_ON_WINDOWS.md](docs/RUNNING_ON_WINDOWS.md) for more.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

This is a soft launch. Open an issue with bugs or ideas; pull requests welcome for small, focused changes.
