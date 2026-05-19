# Publishing ScreenLingo to GitHub (soft launch)

Follow these steps once to publish the project and share it with others.

## 1. Prepare the repository locally

From PowerShell:

```powershell
cd C:\Users\LSWKQ\screenlingo

# Initialize git (skip if already a repo)
git init

# Review what will be committed (.venv is ignored)
git status
```

## 2. Update repository URLs (one-time)

Edit `pyproject.toml` and replace `chaturvedi-vardhanharsh` in the `[project.urls]` section with your GitHub username or org.

Optional: add a screenshot to `docs/screenshots/` and reference it in `README.md`.

## 3. Create the GitHub repository

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `Screenlingo`
3. Description: *Real-time screen translation and vocabulary learning for Windows*
4. Choose **Public** (or Private for a private soft launch)
5. Do **not** add README, .gitignore, or license (this repo already has them)
6. Click **Create repository**

## 4. Push your code

Replace `chaturvedi-vardhanharsh` with your GitHub username:

```powershell
cd C:\Users\LSWKQ\screenlingo

git add .
git commit -m "Initial release: ScreenLingo v1.0.0 soft launch"

git branch -M main
git remote add origin https://github.com/chaturvedi-vardhanharsh/Screenlingo.git
git push -u origin main
```

If you use SSH:

```powershell
git remote add origin git@github.com:chaturvedi-vardhanharsh/Screenlingo.git
git push -u origin main
```

## 5. Create a release (recommended for soft launch)

On GitHub:

1. **Releases → Create a new release**
2. Tag: `v1.0.0`
3. Title: `ScreenLingo 1.0.0 — Soft launch`
4. Paste the **1.0.0** section from `CHANGELOG.md`
5. Publish release

## 6. What to tell early users

Share the repo link and these install steps:

```powershell
git clone https://github.com/chaturvedi-vardhanharsh/Screenlingo.git
cd Screenlingo
.\run.bat
```

Full Windows guide: [docs/RUNNING_ON_WINDOWS.md](RUNNING_ON_WINDOWS.md)

## 7. Optional next steps

- Add topics on GitHub: `translation`, `ocr`, `language-learning`, `windows`
- Enable **Issues** for feedback
- Add a `SECURITY.md` if you plan a wider launch
- CI (GitHub Actions) can be added later; not required for soft launch

## Checklist before making the repo public

- [ ] No secrets in the repo (`.env`, API keys, tokens)
- [ ] `chaturvedi-vardhanharsh` replaced in `pyproject.toml`
- [ ] README and `docs/RUNNING_ON_WINDOWS.md` reviewed
- [ ] Tested `.\run.bat` on a clean machine or after deleting `.venv`
