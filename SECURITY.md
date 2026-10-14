# Security Policy

## Supported versions

Security fixes are applied to the latest version on the `main` branch. This project does not currently maintain older release branches.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's **Report a vulnerability** option in the repository Security tab to create a private security advisory.

Include a concise description, affected component, reproduction steps, expected impact, and any suggested mitigation. Remove API keys, personal data, and proprietary document content from the report.

A maintainer should acknowledge a complete report within five business days. Timelines for validation and remediation depend on severity and reproducibility. Please allow time for a fix before public disclosure.

## Deployment responsibility

The included defaults are intended for local development. Before an internet-facing deployment, replace all sample credentials, protect the API and n8n with authentication and TLS, restrict CORS and network exposure, use a secrets manager, configure backups, and review `docs/SECURITY.md`.
