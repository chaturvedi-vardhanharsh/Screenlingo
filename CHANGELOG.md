# Changelog

All notable changes to ScreenLingo are documented in this file.

## [1.0.2] - 2026-05-19

### Fixed

- SSL certificate errors on corporate networks (uses Windows certificate store via `truststore`)
- Translation failures from oversized OCR text (chunking + URL/noise filtering)
- App closing when PowerShell closes (`run.bat` and `ScreenLingo.vbs` launch detached via `pythonw`)

### Added

- Network settings: Windows certificates toggle and optional relaxed SSL for strict proxies
- MyMemory fallback if Google Translate is unavailable

## [1.0.1] - 2026-05-19

### Fixed

- Screen capture crash on mss 10.x (`'ScreenShot' object has no attribute 'bgr'`) — now uses `rgb` API with fallback for older mss
- Use primary monitor by default instead of all monitors combined (faster, more stable)

## [1.0.0] - 2026-05-19

### Added

- Live screen translation with draggable capture region
- Floating translation overlay
- One-shot translate (`Ctrl+Shift+T`) and live toggle (`Ctrl+Shift+L`)
- Windows built-in OCR for text detection
- Vocabulary tracking for frequently seen words
- Flashcard learning mode with spaced repetition
- 20+ target languages via Google Translate
- Local settings and vocabulary database in `%USERPROFILE%\.screenlingo\`
