# Houston TCG Storefront

This is a standalone static website for Houston TCG.

## Files

- `index.html` contains the page structure.
- `styles.css` contains the full design and responsive layout.
- `app.js` contains the product list, image paths, and Facebook Marketplace links.

## What to update

1. Put your item photos inside `images/`.
2. In `app.js`, update the product info and Facebook Marketplace listing URLs as needed.
3. If you rename an image, update the matching `image` path in `app.js`.

## Suggested image filenames

- `images/outlaws-of-thunder-junction-deluxe-commander-kit.jpeg`
- `images/iphone-14-128gb-black.webp`
- `images/lego-good-fortune-set.jpg`
- `images/kidkraft-fresh-farm-market-stand.jpg`
- `images/pikachu-squishmallow-20-inch.jpg`
- `images/pikachu-fresh-market-stand-bundle.jpg`

## Open locally

Open `index.html` in a browser to preview the site.

Or run a local server:

```bash
cd /Users/will/Documents/CodexRequests/houston_tcg_site
python3 -m http.server 8001
```

Then open `http://localhost:8001`.

## Publish on GitHub Pages

1. Create a new GitHub repository.
2. Upload everything inside this `houston_tcg_site` folder to the root of that repository.
3. Make sure `index.html` stays in the repository root.
4. Push the repository to GitHub.
5. In GitHub, open `Settings` -> `Pages`.
6. Under `Build and deployment`, choose `Deploy from a branch`.
7. Select your main branch and the `/ (root)` folder.
8. Save, then wait for GitHub Pages to publish.

Your site URL will usually look like:

`https://YOUR-USERNAME.github.io/YOUR-REPOSITORY-NAME/`

## Notes for GitHub Pages

- This project does not need Node, React, or a build command.
- The `.nojekyll` file is included so GitHub Pages serves the site as plain static files.
- Since your links and assets use relative paths, the site should work fine on GitHub Pages as long as all files stay together.
