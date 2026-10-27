---
type: raw-source
immutable: true
source: Google Public DNS (dns.google) — public lookups, not a scan
retrieved: 2026-10-26
---

# DNS email records — sloanslakedental.com

> REAL. Public DNS answers retrieved 2026-10-26 via Google Public DNS:
> [MX](https://dns.google/resolve?name=sloanslakedental.com&type=MX) ·
> [TXT](https://dns.google/resolve?name=sloanslakedental.com&type=TXT) ·
> [_dmarc TXT](https://dns.google/resolve?name=_dmarc.sloanslakedental.com&type=TXT).
> Anyone can look these up; this is not a security scan of the practice.

| Record | Value | What it means |
|---|---|---|
| MX | `0 mx.paubox.com.` | Inbound mail goes through **Paubox**, a HIPAA-focused encrypted email service. |
| TXT | `NETORGFT14230892.onmicrosoft.com` | A **Microsoft 365** tenant provisioned through **GoDaddy** (the "NETORGFT" naming). |
| TXT (SPF) | `v=spf1 include:_spf.paubox.com include:secureserver.net -all` | Only Paubox and GoDaddy servers may send as this domain; others **fail hard** (`-all`). Good. |
| TXT | `amazonses:…` | Amazon SES verified to send for the domain (typically a vendor's notification mail). |
| TXT | `google-site-verification=…` | Google Search Console ownership. |
| `_dmarc` TXT | **none (NXDOMAIN)** | **No DMARC policy.** Receivers aren't told what to do with mail that fails checks, and the practice gets no reports of who is sending as it. |
| NS / SOA | `ns03.domaincontrol.com`, `dns.jomax.net` | DNS hosted at **GoDaddy**. |
