# Production journey audit

Method: HTTP probes against `https://kollio.memolabs.dev` with curl (status code, redirect target, body size, `<title>`, `html` lang, heading and landmark counts, `aria-label` inventory) plus inspection of the server-rendered HTML of the public screens. No credentials were used and no authentication was bypassed, weakened or invented, so every screen behind the sign-in gate is reported as NOT VERIFIED with the gate's own response cited as the evidence. Every step was attempted in French (`/`) and in English (`/en`).

Result: 1 finding (0 blocker, 0 major, 1 minor), 4 checks verified clean, and 9 journey steps not verified because they sit behind authentication.

## Finding

### JOURNEY-1 (minor) - an unknown path answers with a raw JSON error

URL: `https://kollio.memolabs.dev/nope` (same shape for any unknown path, including under `/en`).

Observed: HTTP 404 with a JSON body:

```
{"error":true,"url":"https://kollio.memolabs.dev/nope","statusCode":404,"statusMessage":"Page not found: /nope","message":"Page not found: /nope","data":{"path":"/nope"}}
```

Expected: a localized not-found page in the active locale with a way back to the landing. The product already ships localized screens in French and English, and the landing claims a private, well-kept space.

Repro: `curl -s https://kollio.memolabs.dev/nope`

Impact: a visitor who mistypes a path reads an English technical payload with no navigation and no product surface. It is the only public dead end this audit could reach.

## Checks verified clean

- Landing FR at `/`: HTTP 200, 64566 bytes, `html lang="fr-FR"`, one `h1` ("Confrontez vos initiatives au réel, gardez la trace de chaque décision et réunissez les bonnes personnes dans un espace privé"), one `main`, two `nav`, visible prose in French.
- Landing EN at `/en`: HTTP 200, 64217 bytes, `html lang="en-GB"`, one `h1`, one `main`, two `nav`, English prose.
- No raw translation keys on either landing: scanning the server-rendered HTML for `ideas.*` key paths returns nothing, so the blocker fixed in `de8b913` is absent from what production serves.
- The sign-in gate holds: `/workspace`, `/en/workspace`, `/workspace/ideas` and `/workspace/deposit` all answer 302 to `/sign-in`, which answers 302 to the Logto authorization endpoint (`kollio-auth.memolabs.dev`, `response_type=code`, `code_challenge_method=S256`, `resource=https://kollio.memolabs.dev/api`). `/sign-out` answers 302 to the Logto end-session endpoint with `post_logout_redirect_uri=/`.
- Cross-reference: production also serves two navigation landmarks with the same name (`Navigation principale` in French, `Main navigation` in English), which is the accessibility finding A11Y-3 in `a11y-report.md`, observed here on the deployed build.

## Journey grid

| Step | fr | en | Evidence |
| --- | --- | --- | --- |
| Landing | PASS | PASS | 200, titles and `html lang` correct, no raw keys |
| Sign-in gate | PASS | PASS | 302 to `/sign-in`, then 302 to Logto with PKCE S256 |
| Sign-out | PASS | PASS | 302 to the Logto end-session endpoint |
| Unknown path | FAIL | FAIL | JOURNEY-1, raw JSON 404 |
| Explorer | NOT VERIFIED | NOT VERIFIED | 302 to `/sign-in` |
| Deposit | NOT VERIFIED | NOT VERIFIED | 302 to `/sign-in` |
| Idea detail | NOT VERIFIED | NOT VERIFIED | reached only through the explorer, behind the gate |
| Person profile | NOT VERIFIED | NOT VERIFIED | reached only through an idea, behind the gate |
| Decision inbox | NOT VERIFIED | NOT VERIFIED | 302 to `/sign-in` |
| Decision space sections | NOT VERIFIED | NOT VERIFIED | reached only through the inbox, behind the gate |
| Settings | NOT VERIFIED | NOT VERIFIED | reached only through the navigation, behind the gate |

## Limits

- No credentials were requested, guessed or bypassed. The brief and `docs/12-delivery-workflow.md` forbid a production authentication bypass, so every authenticated step is marked NOT VERIFIED and the gate response is cited instead of a screenshot.
- Evidence is HTTP responses and server-rendered HTML, not screenshots.
- The audit only read the deployed site: it created, modified and deleted no data, and touched no database and no API with credentials.
- The 404 was probed once on an unknown path. A localized error route may exist elsewhere; that was not verified.
- The post-sign-in experience, the agent outputs and the provider quality are outside what an unauthenticated HTTP probe can prove.
