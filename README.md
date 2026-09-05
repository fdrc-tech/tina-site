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

## The old GitHub Pages URLs

The repo-root `index.html`, `privacy.html` and `terms.html` are redirect stubs,
not content. Versions 1.0 to 1.3.1 of the app have
`fdrc-tech.github.io/tina-site` compiled into `LegalView`, so those URLs have to
keep working indefinitely. GitHub Pages cannot issue a real 301 for a project
site, so they use a meta refresh plus a canonical link and a visible link out.
**Never delete them.**

## Two traps when verifying a deploy

**Grepping the live site for the support address finds nothing.** Cloudflare's
Email Address Obfuscation (Scrape Shield, on by default) rewrites every `mailto:`
into `/cdn-cgi/l/email-protection#<hex>` and injects a decoder script. Real
visitors see the address; `curl | grep` does not. To check it, decode the hex:
the first byte is an XOR key applied to all the bytes after it. This looks
exactly like a deploy that did not land.

**`gh run list --limit 1` straight after a push can return the PREVIOUS run.**
GitHub has not created the new one yet, so watching that id reports success
instantly for work that never ran. Always select by commit:

```sh
SHA=$(git rev-parse HEAD)
gh run list --workflow deploy.yml --limit 10 --json databaseId,headSha \
  -q ".[] | select(.headSha==\"$SHA\") | .databaseId" | head -1
```

## Legal text

`public/privacy.html` and `public/terms.html` are the canonical copies. The app
duplicates them in `LegalView.swift`, which needs a new build to change, so
update both together.
