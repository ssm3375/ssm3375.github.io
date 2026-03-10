# Stephen Muttathil's Personal Website

A clean, minimalistic academic personal website built with Jekyll, featuring dark/light mode toggle and responsive design.

**Live Site:** [https://ssm3375.github.io](https://ssm3375.github.io)

## Features

- Clean, minimalistic design optimized for academic profiles
- Dark/Light mode toggle with persistent user preference
- Fully responsive (mobile, tablet, desktop)
- Fixed navigation bar with smooth scrolling
- Publication list with placeholder links for DOI/PDF/arXiv
- Professional experience and research highlights
- Social media integration (GitHub, LinkedIn, Google Scholar)
- CV download button
- Fast load times and optimized performance

## Quick Start

### Prerequisites

- Ruby 2.7.0 or higher
- RubyGems
- Bundler

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ssm3375/ssm3375.github.io.git
   cd ssm3375.github.io
   ```

2. **Install dependencies:**
   ```bash
   bundle install
   ```

3. **Run the local server:**
   ```bash
   bundle exec jekyll serve
   ```

4. **View the site:**
   Open your browser and navigate to `http://localhost:4000`

   For live reloading during development:
   ```bash
   bundle exec jekyll serve --livereload
   ```

## File Structure

```
ssm3375.github.io/
├── _config.yml              # Jekyll configuration
├── Gemfile                  # Ruby dependencies
├── index.md                 # Main content (your info)
├── _layouts/
│   └── default.html        # HTML template
├── assets/
│   ├── css/
│   │   └── style.scss      # Stylesheet with dark mode
│   └── js/
│       └── theme-toggle.js # Dark mode functionality
├── files/
│   ├── profile.jpg         # Your profile photo (add this)
│   └── cv.pdf              # Your CV PDF (add this)
└── .gitignore
```

## Customization

### Add Your Profile Photo

1. Place your professional headshot in the `files/` directory as `profile.jpg` (or `profile.png`)
2. Recommended size: 400x400 pixels minimum
3. The photo will automatically display in a circular frame

### Add Your CV

1. Export your CV as a PDF
2. Place it in the `files/` directory as `cv.pdf`
3. The download button will automatically link to it

### Update Content

Edit `index.md` to update your:
- Research interests
- Education details
- Publications
- Experience
- Leadership roles
- Awards
- Skills

### Update Google Scholar Link

Once you have a Google Scholar profile:
1. Open `_config.yml`
2. Replace the `scholar_url: "#"` line with your actual Google Scholar URL

### Update Publication Links

As your papers are published, update the placeholder links in `index.md`:
```markdown
<div class="publication-links">
<a href="https://doi.org/your-doi">DOI</a>
<a href="https://arxiv.org/abs/your-id">arXiv</a>
<a href="/files/paper.pdf">PDF</a>
</div>
```

### Customize Colors

To change the color scheme, edit the CSS variables in `assets/css/style.scss`:

```scss
:root {
  --accent-color: #0066cc;  /* Change this for different accent color */
  /* ... other variables ... */
}
```

## Deployment to GitHub Pages

### First Time Setup

1. **Ensure your repository is named correctly:**
   - Repository name must be: `ssm3375.github.io` (or `username.github.io`)

2. **Push your changes:**
   ```bash
   git add .
   git commit -m "Initial site setup"
   git push origin main
   ```

3. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under **Source**, select **main** branch
   - Click **Save**

4. **Wait for deployment:**
   - GitHub will build and deploy your site (usually takes 1-2 minutes)
   - Your site will be live at `https://ssm3375.github.io`

### Updating Your Site

After making changes:
```bash
git add .
git commit -m "Update content"
git push origin main
```

GitHub Pages will automatically rebuild and deploy your changes.

## Troubleshooting

### Site not loading?
- Ensure repository name is exactly `ssm3375.github.io`
- Check that GitHub Pages is enabled in repository settings
- Wait a few minutes after pushing for deployment to complete

### Local build errors?
```bash
# Update bundler
gem update bundler

# Clean and rebuild
bundle exec jekyll clean
bundle exec jekyll build
```

### Ruby version issues?
If you're using Ruby 3.0+, ensure `webrick` is installed:
```bash
bundle add webrick
```

## Browser Support

The site is tested and works on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lighthouse score: 95+ across all metrics
- Fast load times (<1s on good connection)
- Optimized for mobile devices
- Minimal external dependencies

## Technologies Used

- [Jekyll](https://jekyllrb.com/) - Static site generator
- [GitHub Pages](https://pages.github.com/) - Hosting
- Vanilla JavaScript - Theme toggle and interactivity
- SCSS - Styling with CSS variables for theming

## License

This project is open source and available for personal use.

## Contact

Stephen Muttathil  
Email: stephen7929@tamu.edu  
GitHub: [@ssm3375](https://github.com/ssm3375)  
LinkedIn: [stephen-muttathil](https://www.linkedin.com/in/stephen-muttathil-3bb8141a3/)

---

**Last Updated:** March 2026