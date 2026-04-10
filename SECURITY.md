# Security Policy

## Supported Versions

Security fixes are applied to the latest main branch.

## Reporting a Vulnerability

If you discover a security issue, please do not open a public issue first.

Use one of these channels:

1. Open a private security advisory on GitHub for this repository.
2. If private advisories are unavailable, contact the maintainer directly and share reproduction steps.

Please include:

- A clear description of the issue
- Steps to reproduce
- Potential impact
- Suggested remediation (if known)

## Response Process

- Acknowledgement target: within 72 hours
- Initial triage: within 7 days
- Fix timeline: based on severity and complexity

## Security Best Practices for Contributors

- Never commit .env or credentials
- Use strong random SECRET_KEY values
- Keep FLASK_DEBUG disabled in production
- Rotate secrets immediately if exposure is suspected
