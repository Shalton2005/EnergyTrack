# GitHub Daily Workflow (Beginner Friendly)

This guide is for daily, continuous updates to EnergyTrack.

## 1. Install Git (One Time)

If Git is not installed, install it first:
- Download: https://git-scm.com/download/win
- During install, keep default options
- Restart VS Code terminal after install

Verify:

```powershell
git --version
```

## 2. One-Time Git Setup

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Create repository on GitHub, then connect local project:

```powershell
git init
git add .
git commit -m "chore: initial project setup"
git branch -M main
git remote add origin https://github.com/<your-username>/EnergyTrack.git
git push -u origin main
```

## 3. Daily Update Flow

Run this every day when you make changes:

```powershell
git pull origin main
git status
git add .
git commit -m "type: short clear message"
git push origin main
```

Use commit message types:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation update
- `refactor:` code cleanup
- `chore:` maintenance

Examples:
- `feat: add tariff validation`
- `fix: prevent empty admin password bootstrap`
- `docs: simplify deployment steps`

## 4. Professional Branch Workflow (Recommended)

For safer team-style updates:

```powershell
git checkout -b feat/<short-name>
git add .
git commit -m "feat: your change"
git push -u origin feat/<short-name>
```

Then open a Pull Request on GitHub and merge to `main`.

## 5. What Not To Push

Never push:
- `.env`
- real passwords or API keys
- local database files with private data

If secret data is pushed by mistake:
1. Rotate/revoke the secret immediately.
2. Remove it from code.
3. Commit the fix and push.
4. If needed, rewrite git history.

## 6. Suggested Daily Routine

1. Pull latest code
2. Work on one small improvement
3. Run app locally and test
4. Commit with clean message
5. Push before ending the day

This creates continuous, professional progress with traceable history.

## 7. One-Command Daily Push (Windows)

Use the included script:

```powershell
powershell -ExecutionPolicy Bypass -File .\daily_github_update.ps1
```

It guides you through:
- status check
- add/commit
- push to current branch
