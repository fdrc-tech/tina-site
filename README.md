# Tina — public site

The website for the **Tina** iOS app: landing page, legal documents, usage
guide, and the invite-link landing page.

Live at **https://tinapantry.app**

## Layout

| Path | What it is |
|---|---|
| `public/` | the deployed site — everything under here is served at the domain root |
| `public/.well-known/apple-app-site-association` | universal-links association for `applinks:/join/*` and `webcredentials` |
| `public/join/index.html` | one page for every invite code, served for `/join/<CODE>` |
| `public/guide/` | usage guide in en/it/de/es/fr — **generated, do not edit by hand** |
| `public/_headers` / `public/_redirects` | Cloudflare Pages rules |
| `tools/build_guide.py` | regenerates the guide from the app's string catalog |
| `index.html`, `privacy.html`, `terms.html`, `style.css` at the repo root | the old GitHub Pages site at `fdrc-tech.github.io/tina-site`, kept alive as redirects because versions 1.0 to 1.3.1 of the app have that URL compiled in |

## Deploying

Pushing to `main` deploys `public/` to Cloudflare Pages via GitHub Actions.
Repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` drive it.

## Regenerating the guide

The guide is the same seven topics as `UsageGuideView.swift` in the app, in the
same five languages, read straight from `Localizable.xcstrings` so the two
cannot drift:

```sh
tools/build_guide.py ../Tina/Pantrio/Resources/Localizable.xcstrings
```

The English copy *is* the catalog key. If the English changes in Swift, the key
renames and this script stops with a clear error rather than publishing stale
text — update `TOPICS` in the script to match, then rerun.

## Legal text

`public/privacy.html` and `public/terms.html` are the canonical copies. The app
duplicates them in `LegalView.swift`, which needs a new build to change, so
update both together.
