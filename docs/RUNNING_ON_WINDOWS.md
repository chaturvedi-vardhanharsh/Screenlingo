# Running ScreenLingo on your Windows PC

This guide is for running ScreenLingo on **Windows 10 or 11** (including your current machine).

## What you need

| Requirement | Details |
|-------------|---------|
| OS | Windows 10 or 11 (64-bit) |
| Python | 3.10, 3.11, 3.12, or 3.13 recommended (3.14 works if dependencies install) |
| Internet | Required for translations (not for OCR) |
| Display | Any resolution; use **Select screen area** for best accuracy |

Check Python:

```powershell
python --version
```

If `python` is not found, install from [python.org](https://www.python.org/downloads/) and enable **“Add python.exe to PATH”** during setup.

---

## Option A — Quick start (recommended)

1. **Open PowerShell** (Win + X → Terminal or Windows PowerShell).

2. **Go to the project folder** (adjust if you cloned elsewhere):

   ```powershell
   cd C:\Users\LSWKQ\screenlingo
   ```

3. **Run the launcher** (creates a virtual environment and installs dependencies on first run):

   ```powershell
   .\run.bat
   ```

4. The ScreenLingo window should open.

---

## Option B — Manual install

```powershell
cd C:\Users\LSWKQ\screenlingo

# Create isolated Python environment
python -m venv .venv

# Activate it (PowerShell)
.\.venv\Scripts\Activate.ps1

# If activation is blocked, run once:
# Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

pip install --upgrade pip
pip install -r requirements.txt

# Start the app
python main.py
```

### Install as a command (optional)

```powershell
pip install -e .
screenlingo
```

---

## Option C — After cloning from GitHub

```powershell
git clone https://github.com/chaturvedi-vardhanharsh/Screenlingo.git
cd Screenlingo
.\run.bat
```

---

## First-time setup in the app

1. **Live Translate** tab → pick **source** and **target** language.
2. **Select screen area** → drag a box over the window you want translated (browser, PDF, subtitles, etc.).
3. **Start live translation** → use the floating overlay.
4. Use **Learn Words** after a few minutes of live mode to review words you see often.

---

## Windows language for OCR

ScreenLingo reads text with **Windows OCR**. For non-English source text:

1. Open **Settings → Time & language → Language & region**.
2. **Add a language** matching your source (e.g. Spanish, Japanese).
3. Under that language, install the **Language pack** / OCR if offered.
4. Restart ScreenLingo.

---

## Hotkeys

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+T` | Translate now (one capture) |
| `Ctrl+Shift+L` | Start / stop live translation |

If hotkeys do nothing:

- Run PowerShell **as Administrator**, then start the app again, **or**
- Use the in-app buttons only.

---

## Where your data is saved

| File | Purpose |
|------|---------|
| `%USERPROFILE%\.screenlingo\config.json` | Languages, region, interval |
| `%USERPROFILE%\.screenlingo\vocabulary.db` | Words and learning progress |

Uninstalling the repo folder does **not** delete this data. Remove `.screenlingo` manually if you want a clean slate.

---

## Troubleshooting

### `No text detected`

- Select a smaller region with clear, high-contrast text.
- Zoom the source app (125–150%) so text is larger.
- Avoid semi-transparent overlays.

### Translation shows an error

- On a **work PC**, enable **Use Windows certificates** in the app. If it still fails, check **Relax SSL check**.
- Connect to company **VPN** if your network routes Google through an internal proxy.
- Use **Select screen area** so OCR does not capture login pages and long URLs.
- Check internet connection and try again in a minute.

### App closes when I close PowerShell

- Use **`ScreenLingo.vbs`** (double-click) or **`run.bat`** — both start the app detached.
- Do not run `python main.py` directly in PowerShell unless you keep that window open.

### `ModuleNotFoundError` for `winrt`

- You must be on Windows.
- Re-run: `pip install -r requirements.txt`

### App won’t start after Python upgrade

```powershell
cd C:\Users\LSWKQ\screenlingo
Remove-Item -Recurse -Force .venv
.\run.bat
```

---

## Running at login (optional)

Create a shortcut:

1. Right-click Desktop → **New → Shortcut**.
2. Target: `C:\Users\LSWKQ\screenlingo\run.bat`
3. Start in: `C:\Users\LSWKQ\screenlingo`
4. Place the shortcut in `shell:startup` if you want it when Windows starts.

---

## System summary (your machine)

- **Project path:** `C:\Users\LSWKQ\screenlingo`
- **Launcher:** `run.bat`
- **Python venv:** `C:\Users\LSWKQ\screenlingo\.venv`
- **Config/data:** `C:\Users\LSWKQ\.screenlingo\`
