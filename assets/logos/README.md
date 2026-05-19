# ScreenLingo logo options

Four icons in the same style (dark blue + teal accent). Default: **A — Globe**.

| File | Style |
|------|--------|
| `logo_a_globe.png` | Globe with SL — **default** (`app_icon.ico`) |
| `logo_b_speech.png` | Speech bubble with translation arrow |
| `logo_c_monogram.png` | SL monogram badge |
| `logo_d_screen.png` | Monitor with text lines |

## Switch icon in the app

**Live Translate** tab → **App icon (taskbar)** dropdown → pick A, B, C, or D. Restart is not required; the taskbar icon updates immediately on Windows.

## Regenerate icons

```powershell
python scripts\generate_logos.py
```

This rebuilds all PNGs and `assets/app_icon.ico`.
