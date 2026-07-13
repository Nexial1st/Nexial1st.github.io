# Enzyme Consulting maps site — working notes for Claude

This repo publishes https://maps.enzyme.consulting via GitHub Pages (custom
domain via `CNAME`; every root `.html` file is a live page). It is Andrew's
portfolio of password-protected interactive systems maps for his consulting
work (regenerative hospitality, circular economies, supply chains).

## Standing workflow: publishing a new systems map

When Andrew provides a new map (HTML file), do ALL of the following unless he
says otherwise:

1. **Generate a fresh client password** for it (or reuse the client's existing
   one if the map belongs to a client who already has maps here). Format used
   so far: three capitalized words + 2-digit number, hyphen-separated, drawn
   from a nature/nautical wordlist — e.g. `Lagoon-Quartz-Lotus-11`. Generate
   with `secrets`, never `random`.
2. **Ask Andrew for the master password** if it isn't already in the
   conversation. Every map is encrypted with master + client password.
   NEVER write any password into this repo, commits, or PR text — passwords
   live only in chat with Andrew.
3. **Add share metadata** to the map's `<head>` before encrypting: meta
   description, `og:title/description/type/url/site_name`, `twitter:card`,
   using `https://maps.enzyme.consulting/<file>.html` as the URL (copy the
   pattern from any master/protected file).
4. **Encrypt it**:
   `python3 tools/protect.py 'MASTER-PW,CLIENT-PW' the-map.html`
   (envelope encryption; the tool replaces the file in place with a branded
   login shell). Needs `pip install cryptography` (+ `cffi` on this runner).
5. **Add it to the landing page** (`index.html`), unless Andrew wants it
   unlisted: a card in the grid (copy an existing `<a class="card">` block)
   AND a node in the hero constellation — one `<a class="pnode">` in the
   `.pweb` nav plus one extra anchor entry in BOTH `spots` arrays inside
   `placeProjects()` (they are positional; keep counts in sync with the
   number of `.pnode` elements).
6. **Update the README** page table.
7. **Verify before pushing**: serve locally (`python3 -m http.server`) and use
   Playwright + `/opt/pw-browsers/chromium` to check the login page renders,
   the correct passwords unlock it, a wrong password is rejected, and the
   landing page looks right (desktop + 390px mobile).
8. **Commit and push**, then tell Andrew the new client password and remind
   him to keep the unencrypted master copy on his own computer — the repo only
   holds encrypted versions, and this container is wiped after the session.
9. Andrew is a GitHub beginner: give him the PR link
   (`https://github.com/Nexial1st/Nexial1st.github.io/pull/new/<branch>`) and
   remind him to Create pull request → Merge to go live.

## Private client portals (currently: banyan/)

Per-client folders hold **unlisted** private engagements. NEVER add them to
the landing page, README, sitemap, or hero constellation. Everything in the
folder — including its `index.html` portal page — is encrypted with
master + that client's password.

**Banyan Group** (`banyan/`, portal at /banyan/): three dashboards regenerated
by Andrew's data pipeline, published here as encrypted copies. Source files
live in Andrew's Google Drive (use the Google Drive connector; IDs stable as
the pipeline overwrites in place):

| Repo file | Drive title | Drive file ID |
|---|---|---|
| banyan/procurement-dashboard.html | Procurement_Dashboard.html | 1zmQFN82j3t1axgPPMp42CYi72EVYFgZJ |
| banyan/data-coverage.html | Data_Coverage_Dashboard.html | 1yCOfQgDfaBjxmYR9IrbTDyjky5-QBcbF |
| banyan/sustainability-insights.html | Sustainability_Insights_Dashboard.html | 1aFcqVZpTMsctJf1gSH7dkn95vtGh37Qe |
| banyan/systems-map.html | banyan-spend-risk-map_map.html | 1HXABCKdE0Cli_RpFUTTxRyaWX8zDUNYC |

The systems map source is the **04_delivery** copy (a sibling exists in
03_build — do not publish that one). Its `<title>` is the generic framework
name; on publish, replace it with "Banyan Group — Procurement Spend & Risk
Systems Map" and insert the meta block in the same edit (see git history of
banyan/systems-map.html for the exact pattern).

**Auto-refresh is live**: an hourly Routine (bound to the session that set it
up) checks the Drive modifiedTime of each source against
`tools/banyan-sources.json`. When a source changed, it re-publishes that file,
updates the state JSON, pushes, opens a PR and merges it — Andrew authorised
fully automatic publishing for Banyan updates on 13 Jul 2026. When nothing
changed, it does nothing and stays silent.

**Refresh workflow** (manual, or executed by the Routine):
1. Get master + Banyan passwords from Andrew / conversation context.
2. Download the three files from Drive (`download_file_content`, base64).
3. Insert the meta block after `</title>` (description + og tags with the
   `https://maps.enzyme.consulting/banyan/<file>` URL — copy the pattern by
   running `--decrypt` on the current repo file first).
4. Encrypt: `python3 tools/protect.py 'MASTER,BANYAN' --home '/banyan/|Banyan portal' banyan/<file>.html`
5. Update the "Data through …" stat line on the portal: `--decrypt` the
   current `banyan/index.html`, edit, re-encrypt (no --home; default is fine).
6. Verify with Playwright (portal unlocks, click-through auto-unlocks), then
   commit, push, give Andrew the PR link.

A "Procurement Systems Map" slot (04) is reserved on the portal — when Andrew
provides it, publish as `banyan/systems-map.html`, same passwords, swap the
placeholder card for a real link.

## Facts to know

- **Master password opens everything**; each client password opens only that
  client's maps. `family-strategy-dashboard-final.html` is master-only and
  deliberately unlisted (personal). The three daily system maps
  (`2026-04-2{3,4,5}-system-map.html`) are live but unlisted.
- `sitemap.xml` lists ONLY the landing page (protected pages are noindex).
- Brand (matches www.enzyme.consulting): ivory `#F6F3EB`, cream `#EFE9DD`,
  pine `#1E3D31`, leaf `#2E5946`, sage `#9DB5A4`, olive `#75885F`,
  terracotta `#C9683C`, ink `#141F1A`. Fonts: Fraunces (serif headlines,
  italic accents), Inter (body), DM Mono (kickers/labels, letterspaced
  uppercase). Logo vector: `assets/enzyme-mark.svg` (trace of Andrew's mark).
- The hero on `index.html` is a living network: ambient canvas nodes plus the
  project maps as drifting clickable `.pnode` links; nodes freeze under the
  pointer; a wandering focus point animates when there's no pointer;
  `prefers-reduced-motion` gets a static frame.
- Interactive maps must keep touch support (one-finger pan, two-finger pinch)
  — see the touch handlers in the pre-encryption masters of
  hotel-lifecycle/cook-islands maps for the pattern.
- Unencrypted originals of maps published before protection exist in old git
  history (pre-`2dadce1`); Andrew knows. A history scrub is a pending
  offer/task, as is privacy-friendly analytics.
- This environment's proxy blocks most external domains (including
  enzyme.consulting) — use local Playwright screenshots for visual checks,
  and don't be fooled by 403s when checking external URLs.
