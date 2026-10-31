# CROX Sec

Passive external security audits for web agencies and SMBs. Zero access needed — we measure exactly what an unauthenticated observer can see, then hand you the fix list.

## What we do

- **External posture audit** — DNS (SPF/DMARC/CAA/MX), TLS versions, HTTPS redirects, HSTS, exposed admin paths. No scanning, no payloads, no risk to production.
- **Email anti-spoofing** — from `p=none` to enforced `quarantine`/`reject`, with the reporting hooks to keep it that way.
- **20-minute fixes** — most findings close with a DNS record or a header, not a procurement cycle.

## Proof over promises

We ran our own methodology against **84 web agencies in 14 countries** and published everything: [the study](https://croxsec.surge.sh/estudio-2026.html).

Headline numbers: 51% DMARC `p=none` · 67% no HSTS · 26% `/wp-login.php` public · 4% CAA.

## Open source

- [`domain-posture`](https://github.com/croxsec/domain-posture) — the passive posture scanner we use (MIT, stdlib-only).

## Contact

- 🌐 https://croxsec.com
- 📧 crox@croxsec.com
