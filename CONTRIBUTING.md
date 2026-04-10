# Contributing to EnergyTrack

Thanks for your interest in improving EnergyTrack.

## Development Setup

1. Create and activate a virtual environment.
2. Install dependencies from requirements.txt.
3. Copy .env.example to .env and set local values.
4. Run the app with python app.py.

## Branch Strategy

- main: stable production-ready branch
- feature branches: short-lived branches for isolated work

Naming examples:

- feat/device-dashboard
- fix/admin-login
- docs/readme-cleanup

## Commit Convention

Use clear commit prefixes:

- feat: user-visible feature
- fix: bug fix
- docs: documentation-only changes
- refactor: internal cleanup without behavior change
- chore: maintenance and tooling

Examples:

- feat: add billing history filters
- fix: prevent empty support ticket submission
- docs: clarify production environment variables

## Pull Request Checklist

- Keep PRs focused on one logical change.
- Add a clear summary of what changed and why.
- Include screenshots for UI changes.
- Verify no secrets are committed.
- Ensure app starts successfully before requesting review.

## Code Quality Guidelines

- Follow existing project style and naming.
- Avoid unrelated refactoring in feature PRs.
- Keep functions small and readable.
- Prefer configuration via environment variables.

## Security

Do not include API keys, passwords, or personal credentials in commits.
Refer to SECURITY.md for vulnerability reporting.
