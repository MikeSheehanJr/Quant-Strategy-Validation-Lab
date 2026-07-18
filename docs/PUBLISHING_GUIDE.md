# Safe publishing, sharing, and submission guide

This is the release playbook for turning the local work-in-progress project into a public GitHub repository, a live Streamlit app, a LinkedIn project, and a resume entry.

The local safety sweep is automated. The remaining sequence is:

1. Run the one-command release gate.
2. Create a private GitHub repository.
3. Let CI repeat the gate while the repository is private.
4. Make the repository public and run the remote-security configurator.
5. Deploy the app with no secrets.
6. Verify both public URLs while logged out.
7. Add the prepared GitHub, LinkedIn, and resume copy.

## 1. Final local safety audit

Open a terminal in this project directory—not in the larger private research workspace.

### Install and test with Python 3.12

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install --requirement requirements.txt
python scripts/release_gate.py
```

Expected results:

- Python compilation, the public-release scanner, all tests, and `pip-audit` pass.
- The dependency audit reports no known vulnerabilities.
- The scan reports no prohibited artifact, raw/trade-level field, secret, PII, local path, unsafe PNG metadata, runtime connection surface, or unpinned GitHub Action.

### What is now checked automatically

You do not need to manually search the project tree for the common leak classes. The gate checks every candidate file, requires `data/` to contain exactly one aggregate JSON snapshot, blocks symlinks and unsupported binary types, rejects metadata-bearing PNGs, validates source hashes, scans for common credentials and email addresses, and verifies the deployed Python surface has no upload, secret, connection, network, or process-spawning path.

The only judgment the scanner cannot make is whether you personally intend to publish the prose and historical claims. That is a content decision, not a security sweep.

### Regenerate only when necessary

The checked-in snapshot is already built. If the private research changes, regenerate it only from the licensed workspace:

```bash
python scripts/build_public_snapshot.py --source-root /path/to/private/research
python scripts/release_gate.py
```

Never commit the value passed to `--source-root` into a script, config file, or screenshot.

## 2. Create a separate local Git repository

The larger research workspace is intentionally not the public repository. Initialize Git from this project directory only:

```bash
git init -b main
python scripts/release_gate.py
git add .
git diff --cached --stat
```

Do not use a broad parent directory as the repository root. The project-level `.gitignore` and release gate are designed to make `git add .` safe inside this isolated directory.

After the staged diff is clean:

```bash
git commit -m "Build public quant validation lab MVP"
```

GitHub’s official instructions warn against committing sensitive information and document both GitHub CLI and ordinary Git workflows: [Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## 3. Publish to GitHub safely

### Recommended: private-first launch

Authenticate with GitHub CLI, then create a private repository:

```bash
gh auth status
gh repo create quant-strategy-validation-lab \
  --private \
  --source=. \
  --remote=origin \
  --push
```

Why private first:

- CI can rerun the entire release gate before public exposure.
- README rendering and links can be checked without search indexing.
- The public transition remains a deliberate authorization step.

Do not make it public until all of the following are true:

- CI is green.
- `data/` contains one aggregate JSON file.
- The Security, Insights, and commit-history views contain nothing private.
- The README does not link to a local path or unfinished private resource.
- Repository description says “Work-in-progress robustness-first quant research dashboard.”

### Security automation

The repository already contains:

- Commit-pinned CI actions
- Weekly Dependabot checks for Python and GitHub Actions
- Pull-request dependency review that rejects moderate-or-higher vulnerabilities
- CodeQL with the extended Python security query suite
- A live `pip-audit` during every CI release gate

After the repository is public, run one command:

```bash
python scripts/configure_github_security.py OWNER/quant-strategy-validation-lab
```

It enables dependency alerts, automated security fixes, secret scanning, push protection, and private vulnerability reporting, then reads the repository settings back. CodeQL and dependency review intentionally skip the private-first stage when GitHub Code Security is unavailable, and activate after the repository becomes public.

GitHub explains that push protection blocks supported secrets before they enter repository history: [Push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection). Public repositories are automatically covered by supported secret scanning patterns: [Secret scanning patterns](https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns).

### Make the repository public

After the private review:

1. Open **Settings → General → Danger Zone → Change repository visibility**.
2. Select **Public**.
3. Read the visibility consequences carefully.
4. Confirm the repository name.
5. Immediately open the repository in a logged-out/private browser window.
6. Run the remote-security command above.
7. Open **Actions → Security review → Run workflow** once so CodeQL runs immediately rather than waiting for the next push or weekly schedule.

If a secret is discovered after publishing, rotate it immediately. Deleting the file in a later commit is insufficient because it remains in history; use GitHub’s [sensitive-data removal procedure](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

### Pin the repository

On your GitHub profile:

1. Click **Customize your pins**.
2. Select `quant-strategy-validation-lab`.
3. Move it into the first three positions.

GitHub allows an owned public repository to be pinned to the profile: [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference).

## 4. Deploy to Streamlit Community Cloud

### Deployment settings

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Connect the GitHub account that owns the repository.
3. Click **Create app**.
4. Choose the repository.
5. Branch: `main`.
6. Entrypoint: `streamlit_app.py`.
7. Open **Advanced settings**.
8. Python version: **3.12**.
9. Secrets: **leave empty**. This app does not require secrets.
10. Choose a memorable subdomain such as `quant-validation-lab` if available.
11. Deploy.

Streamlit recommends a single dependency file and explains how Community Cloud installs it: [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies). The deployment flow and Python-version selector are documented here: [Deploy an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

### Post-deployment checks

Open the live app and verify:

- Research brief loads before any click.
- All four hero metrics display.
- Monthly and yearly charts render.
- Robustness → Monte Carlo renders the percentile fan plus terminal and drawdown distributions.
- Robustness → Parameters renders all three surfaces, reward:risk curve, gate chart, and cutoff chart.
- Robustness → Validation renders the execution heatmap, validation table, and failure journal.
- Implementation renders the Pine version ledger, aggregate path, tables, and downloads.
- Forward validation visibly states that collection has not started and shows no performance chart.
- No Python traceback appears.
- No private file path is visible in the UI or browser source.
- No app secret exists in Streamlit settings.
- The app works in a logged-out/private window.
- The app is readable at a narrow browser width.

Use **Manage app → Analytics** after launch to monitor usage. Streamlit documents app settings, including URL, access, and secrets, here: [App settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-settings).

### Search-indexing warning

A public Streamlit Community Cloud app can be indexed by search engines. If you are not ready for broad discovery, keep it private. Streamlit’s current behavior is described in [SEO and search indexability](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app/indexability).

## 5. Create safe project screenshots

Use only screenshots from the completed app. Do not upload the original dashboard reference images.

Recommended screenshots:

1. Research brief at approximately 1440×900.
2. Robustness → Monte Carlo showing the percentile fan and simulation caveat.
3. Robustness → Parameters showing a frozen-cell heatmap.
4. Implementation showing the version ledger or reviewed aggregate path.
5. Forward validation showing the not-started evidence state and source lock.

Before capturing:

- Use a fresh browser window with no personal tabs visible.
- Hide bookmarks, profile avatars, extensions, notifications, and operating-system menu details when possible.
- Confirm no local URL includes a username in the visible crop.
- Use the public app URL for final launch screenshots.
- Do not add simulated balances, wallet cards, broker logos, or profit claims.

Suggested image caption:

> Work-in-progress research dashboard: historical results, execution stress testing, validation evidence, and open limitations.

## 6. Post to LinkedIn as a work in progress

### Safe wording rules

Use:

- “historical research sample”
- “cost-adjusted simulation”
- “observed in the June 2021–June 2026 sample”
- “work in progress”
- “paper forward-test remains outstanding”
- “research and engineering demonstration”

Avoid:

- “proven strategy”
- “guaranteed edge”
- “live returns”
- “production trading system”
- “risk-free”
- “this will make…”
- any annualized return forecast derived from the backtest

### Recommended launch post

Copy the current draft from [PROFILE_AND_RESUME_COPY.md](PROFILE_AND_RESUME_COPY.md). Before posting:

1. Replace the GitHub and app placeholders with the actual public URLs.
2. Open both links while logged out.
3. Use one real screenshot from the live app.
4. Set post visibility intentionally. Choose **Anyone** only when you want public search and off-network sharing.
5. Keep the WIP and research-only sentences above the “see more” fold.
6. After publishing, open the post from a logged-out/private window.
7. Reply to early comments with methodology or limitations—not performance promises.

## 6A. Post the plain-English GitHub announcement

Use [GITHUB_LAUNCH_COPY.md](GITHUB_LAUNCH_COPY.md) for the repository description, profile-pin summary, launch post, first-release notes, and social-preview caption. Replace the URL placeholders only after the logged-out link test passes.

## 7. Add the LinkedIn Projects section

LinkedIn’s current path is:

1. **Me → View Profile**.
2. **Add profile section**.
3. **Recommended → Projects**.
4. Project name: **Quant strategy validation lab — work in progress**.
5. Associate it with the most relevant education or experience entry only if that relationship is accurate.
6. Add the description from [PROFILE_AND_RESUME_COPY.md](PROFILE_AND_RESUME_COPY.md).
7. Use **Add media → Add a link** for the GitHub repository or live app.
8. Save.

LinkedIn notes that newly added Projects do not have a dedicated Project URL field; use **Add media → Add a link** instead: [Add sections to your profile](https://www.linkedin.com/help/linkedin/answer/a540837/add-sections-to-your-profile?lang=en).

Use the GitHub repository as the project’s durable source link. Put the live app URL in the description or as an additional media link if the UI permits it.

## 8. Add to the LinkedIn Featured section

If the Featured section and desired item type are available on your account:

1. Open **Me → View Profile**.
2. Add or scroll to **Featured**.
3. Click the **Add** icon.
4. Feature the launch post first.
5. Add the live app or GitHub repository as a link if available.
6. Reorder items so the launch post or live app appears first.

LinkedIn’s Featured section can showcase posts, external links, documents, and media, although current availability and controls may vary by account: [Manage featured samples](https://www.linkedin.com/help/linkedin/answer/a550399/feature-samples-of-your-work-on-your-linkedin-profile).

## 9. Review LinkedIn visibility

Before sharing a resume link to your profile:

1. Open **Settings & Privacy → Visibility**.
2. Review public-profile visibility.
3. Review discoverability by email and phone.
4. Review contact-info visibility.
5. Open your public profile while logged out.
6. Confirm that the intended project information is visible and personal information is not overexposed.

LinkedIn explains that public profile sections may appear to logged-out viewers and search engines, and lets you control eligible sections: [LinkedIn public profile visibility](https://www.linkedin.com/help/linkedin/answer/a518980/linkedin-public-profile-visibility?lang=en).

## 10. Add the project to a resume

### Placement

Use a **Projects** section near Technical Skills or Experience. If you are applying directly to quant roles and this is your strongest relevant work, place Projects above less relevant employment.

### Title line

```text
Quant Strategy Validation Lab (Work in Progress) | Python, pandas, Altair, Streamlit, pytest
GitHub: [repository] | Live demo: [app]
```

### Bullet rules

- Use “historical” and the sample window with any performance statistic.
- Lead with research and engineering actions, not profit.
- Include one or two validated numbers, not a wall of metrics.
- State the safety architecture if applying to engineering-oriented roles.
- Keep the WIP status until forward validation is complete.

Copy the role-specific bullet options from [PROFILE_AND_RESUME_COPY.md](PROFILE_AND_RESUME_COPY.md).

### Resume link QA

1. Export the resume to PDF.
2. Open the PDF outside the editor.
3. Click every GitHub, app, and LinkedIn link.
4. Confirm links open in a private browser window.
5. Use full HTTPS destinations behind descriptive labels; avoid URL shorteners.
6. Confirm the PDF text is selectable and ATS-readable.
7. Ensure the displayed project title matches GitHub and LinkedIn exactly.

## 11. Submit through job portals

When an application has separate fields:

| Field | Recommended value |
|---|---|
| Portfolio website | Live Streamlit app |
| GitHub | Repository URL |
| LinkedIn | Public LinkedIn profile |
| Work sample description | Copy the 300-character summary from the copy sheet |
| Attachment | Resume PDF; do not attach raw data or the private workspace |

If only one project link is allowed, use the GitHub repository because it has the most durable context and can link to the live app from the README. If the role is design/data-visualization heavy, use the live app and ensure the app links back to GitHub after launch.

## 12. Final public-launch checklist

### Repository

- [ ] One-command release gate passes
- [ ] Dependency audit reports no known vulnerabilities
- [ ] Private-first remote review complete
- [ ] CI green
- [ ] Remote-security configurator passes
- [ ] CodeQL and dependency review are active after public visibility
- [ ] Repository public and visible while logged out
- [ ] Repository pinned on GitHub profile

### App

- [ ] Python 3.12 selected
- [ ] No secrets configured
- [ ] Research brief, all Robustness subviews, Implementation, and Forward validation work
- [ ] Desktop and narrow layouts reviewed
- [ ] Public URL works while logged out
- [ ] Search-indexing choice understood

### LinkedIn

- [ ] WIP language appears above the fold
- [ ] Only real app screenshots used
- [ ] GitHub and app links tested
- [ ] Project added through Projects section
- [ ] Featured item added if available
- [ ] Visibility reviewed while logged out

### Resume and applications

- [ ] WIP project title used
- [ ] Historical window qualifies performance metrics
- [ ] GitHub and live-demo links included
- [ ] Exported PDF links tested
- [ ] No raw data or private workspace attached
