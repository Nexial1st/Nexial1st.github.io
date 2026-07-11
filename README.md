# Enzyme Consulting — Systems Maps & Strategic Intelligence

This repository powers the public site **[maps.enzyme.consulting](https://maps.enzyme.consulting)** via GitHub Pages.
Every `.html` file in the root of this repo is automatically published as a page — no build step, no configuration.

## What's on the site

| Page | Live URL |
|---|---|
| Landing page (all projects) | [/](https://maps.enzyme.consulting/) |
| Hotel Lifecycle Ecosystem | [/hotel-lifecycle-ecosystem.html](https://maps.enzyme.consulting/hotel-lifecycle-ecosystem.html) |
| Urak Lawoi Regenerative Hospitality | [/urak-lawoi-regen-hospitality-map.html](https://maps.enzyme.consulting/urak-lawoi-regen-hospitality-map.html) |
| City-Wide Reuse Ecosystem (Gold Coast) | [/muuse-ecosystem-map.html](https://maps.enzyme.consulting/muuse-ecosystem-map.html) |
| Cook Islands Fuel Supply System | [/cook-islands-fuel-system-map.html](https://maps.enzyme.consulting/cook-islands-fuel-system-map.html) |
| Hormuz Crisis — SE Asia Supply Chains | [/2026-04-25-hormuz-system-map.html](https://maps.enzyme.consulting/2026-04-25-hormuz-system-map.html) |
| Daily Intelligence Maps (23–25 Apr 2026) | [/2026-04-23-system-map.html](https://maps.enzyme.consulting/2026-04-23-system-map.html) etc. |
| Family Strategy Dashboard *(unlisted — direct link only)* | [/family-strategy-dashboard-final.html](https://maps.enzyme.consulting/family-strategy-dashboard-final.html) |

Every map is a **single self-contained HTML file** — all styling and interactivity is inline, with only Google Fonts loaded externally. This is deliberate: files are portable, never break from missing dependencies, and can be emailed or archived as-is.

## Password protection

All maps are **encrypted** (AES-256-GCM). Visiting a map shows an Enzyme-branded
login screen; the correct password decrypts the page in the browser. Without the
password the file contents are unreadable — this is real encryption, not a
cosmetic gate. One shared password unlocks every map, and the browser remembers
it for the rest of the tab session. The landing page stays public.

Because the files in this repo are encrypted, **keep unencrypted master copies
of every map on your own computer**. To publish or update a protected map:

```
pip install cryptography              # once
python3 tools/protect.py 'THE-PASSWORD' my-map.html
```

…then upload the resulting file. To change the site password, re-run the script
on all master copies with the new password and upload everything again.

## How to add a new map

1. Save your map as a single `.html` file. Name it in lowercase with hyphens, e.g. `client-name-system-map.html` (or `YYYY-MM-DD-topic.html` for dated briefings). Keep this master copy safe on your computer.
2. Optional but recommended: copy the block of `<meta name="description">` / `og:` tags from the top of any existing master into your new file's `<head>` and update the title, description, and URL — this gives links a proper preview when shared in LinkedIn, WhatsApp or Slack.
3. Encrypt it: `python3 tools/protect.py 'THE-PASSWORD' your-file.html` (skip this step only for pages that should be fully public).
4. On GitHub, click **Add file → Upload files**, drop the file in, and press **Commit changes**. It will be live at `https://maps.enzyme.consulting/your-file-name.html` within a minute or two.
5. To list it on the landing page: edit `index.html`, copy one of the existing `<a class="card">…</a>` blocks, and update the link, title, date and description.

## Housekeeping notes

- `index.html` is the landing page. Don't upload a project over it — give each project its own file.
- `404.html` is shown automatically for broken links.
- `robots.txt` and `sitemap.xml` help search engines index the site.
- Pages you'd rather keep semi-private: simply leave them out of `index.html` and `sitemap.xml`. They're still public to anyone with the exact link, so don't publish anything truly confidential here.

## Tips for working with this repo

- **Editing a file:** open it on GitHub, click the pencil icon, make changes, then **Commit changes**. Commit messages are notes to your future self — "Add Fiji water-security map" beats "Update file".
- **Branches and pull requests:** changes committed to `main` go live immediately. For bigger changes, GitHub can hold them on a *branch* (a parallel draft) and show you a *pull request* (a before/after review screen) — merge it when you're happy and only then does it go live.
- **History is your safety net:** every commit is kept forever. Click any file → **History** to view or restore old versions. You can't permanently break anything.
