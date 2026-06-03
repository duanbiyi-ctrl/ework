# Item Domain LDM Documentation

Documentation for Item Domain Logical Data Model (LDM) in GDS, built with [MkDocs](https://www.mkdocs.org/) and deployed to GitHub Pages.

## 🌐 Live Documentation

Visit the documentation at: **https://pages.github.corp.ebay.com/GDS/gds-item-docs/**

## 📚 What's Inside

This documentation covers:

- **Item LDM Overview** - Core entities and relationships in Item Domain
- **Core Concepts** - LDM fundamentals and modeling patterns (M:N, EAV, SCD2)
- **User Guides** - How to query LDM tables and onboard new tables
- **Reference** - Detailed physical table mappings
- **FAQ** - Frequently asked questions

## 🚀 Local Development

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GDS/gds-item-docs.git
   cd gds-item-docs
   ```

2. Install dependencies:
   ```bash
   pip install mkdocs mkdocs-material pymdown-extensions
   ```

### Preview Locally

Start the development server:

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000/ in your browser. The site will auto-reload when you save changes.


## 📁 Project Structure

```
gds-item-docs/
├── docs/                      # Documentation source files
├── mkdocs.yml                # MkDocs configuration
└── README.md                 # This file
```

## 🔧 Configuration

The site configuration is in `mkdocs.yml`. Key settings:

- **Theme**: Material for MkDocs
- **Plugins**: Search
- **Extensions**: Code highlighting, tabs, admonitions, tables

## 🚢 Deployment

### Deploy to GitHub Pages

When you're ready to publish your documentation updates:

```bash
mkdocs gh-deploy
```

This command will:
1. Build the static site from your markdown files
2. Push the generated HTML to the `gh-pages` branch
3. Make it available at https://yeqli.github.io/gds-item-docs/

**Typical workflow:**

```bash
# 1. Edit documentation
vim docs/index.md

# 2. Preview locally
mkdocs serve

# 3. Commit changes to master
git add .
git commit -m "Update documentation"
git push origin master

# 4. Deploy to GitHub Pages (when ready)
mkdocs gh-deploy
```

**Notes:**
- You don't need to deploy every time you commit
- Deploy only when you want to publish changes to the live site
- The `gh-pages` branch is auto-managed by MkDocs (don't edit it manually)

## 📝 Contributing

### Adding New Pages

1. Create a new markdown file in `docs/` (or appropriate subdirectory)
2. Add the page to `nav` section in `mkdocs.yml`
3. Commit and push

Example:

```yaml
# mkdocs.yml
nav:
  - Home: index.md
  - Guides:
      - Querying: guides/querying-ldm.md
      - Your New Page: guides/your-new-page.md  # Add here
```

### Updating Existing Pages

1. Edit the markdown file in `docs/`
2. Preview with `mkdocs serve`
3. Commit and push to master
4. Deploy with `mkdocs gh-deploy` when ready to publish

### Markdown Features

MkDocs supports:

- Standard Markdown
- GitHub-flavored Markdown
- Code blocks with syntax highlighting
- Tables
- Admonitions (notes, warnings, tips)
- Tabs
- And more via extensions

See [MkDocs Material Reference](https://squidfunk.github.io/mkdocs-material/reference/) for full feature list.

## 🔗 Useful Links

- **Live Site**: https://yeqli.github.io/gds-item-docs/
- **MkDocs**: https://www.mkdocs.org/
- **Material for MkDocs**: https://squidfunk.github.io/mkdocs-material/
- **Item Domain Table Analysis**: [Google Sheets](https://docs.google.com/spreadsheets/d/1Kha6mEY946d8JBRsyrZrHEFCFGZd0-wDgBVU7X3pTuc/edit?gid=210660642#gid=210660642)
- **ER Diagram**: [Lucidchart](https://lucid.app/lucidchart/c4cfa8db-e69d-40ec-aa5c-1a09a9cb69fe/edit?invitationId=inv_4b39ef94-d310-4a06-b777-f2baa2887a66&page=Sx2PbBrGHaKl#)

## 📄 License

Internal documentation for GDS platform.

## 💬 Contact

For questions or feedback, contact the GDS Data Platform team.
