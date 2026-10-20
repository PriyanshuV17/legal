# Publish LegalBuddy AI on GitHub Pages

The `docs/index.html` file is a standalone, responsive project landing page. It uses inline CSS and SVG, so no build step is required.

## Option A — Upload through GitHub's website

1. Open <https://github.com/PriyanshuV17/legal>.
2. Choose **Add file → Upload files**.
3. Upload the `index.html` file into a folder named `docs` (create `docs` locally first, then upload `docs/index.html`).
4. Commit the change to `main`.
5. Open **Settings → Pages**.
6. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
7. Set the branch to **main** and the folder to **/docs**, then click **Save**.
8. Wait for the Pages deployment to complete. The project site should be available at <https://priyanshuv17.github.io/legal/>.

## Option B — Use Git from your local clone

Copy the supplied `docs` folder into the root of your local `legal` repository, then run:

```bash
git add docs/index.html
git commit -m "Add LegalBuddy AI GitHub Pages landing page"
git push origin main
```

Then configure **Settings → Pages → Deploy from a branch → main → /docs** as described above.

## Notes

- This landing page is a project overview; it does not host the Python API, Streamlit app, or model inference service. GitHub Pages serves static files only.
- The site is public. Review your repository and any files published from `/docs` before enabling Pages.
- GitHub may take several minutes to publish after the first deployment.
