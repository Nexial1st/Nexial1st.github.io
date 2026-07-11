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
