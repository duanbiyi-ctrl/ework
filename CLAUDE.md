# Item Domain LDM Documentation

MkDocs documentation for Item Domain Logical Data Model in GDS platform.

## Project Structure

```
gds-item-docs/
├── docs/                           # Documentation source (Markdown)
│   ├── index.md                   # Home - Product landing page
│   ├── ldm-entities.md            # Entity catalog and relationships
│   ├── guides/                    # User guides
│   │   └── query-examples.md      # Scenario-based query examples
│   ├── concepts/                  # Core concepts (advanced)
│   │   └── modeling-patterns.md   # M:N, EAV, SCD2 patterns
│   ├── reference/                 # Reference docs
│   │   └── table-mappings.md      # Physical table mappings
│   ├── faq.md                     # FAQ
│   ├── assets/                    # Images and static files
│   └── stylesheets/
│       └── extra.css              # Custom CSS for wider content
├── mkdocs.yml                     # MkDocs configuration
└── README.md                      # Setup and deployment guide
```

## Tech Stack

- **MkDocs** - Static site generator
- **Material for MkDocs** - Theme
- **GitHub Pages** - Hosting (manual deployment)

## Common Tasks

### Local Development

```bash
# Preview docs locally (auto-reload on changes)
mkdocs serve
# Visit http://127.0.0.1:8000/

# Build static site
mkdocs build
```

### Deployment

```bash
# Deploy to GitHub Pages (manual)
mkdocs gh-deploy
```

**Workflow:**
1. Edit docs in `docs/`
2. Preview with `mkdocs serve`
3. Commit to `master`
4. Deploy with `mkdocs gh-deploy` when ready

## Content Organization

**User-Facing Documentation (prioritized for data consumers):**
- **index.md** - Product landing page: What is Item LDM, LDM catalog, quick start
- **ldm-entities.md** - Entity catalog: All 9 entities, relationships, ER diagram, usage examples
- **guides/query-examples.md** - Scenario-based query examples (by use case)
- **faq.md** - Common questions

**Advanced/Reference (for advanced users):**
- **concepts/modeling-patterns.md** - M:N, EAV, SCD2 pattern theory
- **reference/table-mappings.md** - Physical table mappings and source details

**Content Strategy:**
- Focus on use cases and practical examples
- Minimal duplication between pages
- ldm-entities.md is the single source of truth for entity relationships
- table-mappings.md focuses only on physical implementation details

## Adding New Pages

1. Create `.md` file in appropriate `docs/` subdirectory
2. Add to `nav` section in `mkdocs.yml`
3. Follow existing structure and style

## Styling

- Custom CSS in `docs/stylesheets/extra.css`
- Current customization: Wider content area (1600px vs default 1220px)
- Left/right sidebars reduced to 220px (from 242px)

## Navigation

- Left sidebar: Page navigation
- Right sidebar: Table of contents (current page)
- No top tabs (removed `navigation.tabs`)

## Future Expansion

When adding new domains (e.g., User, Transaction):

```
docs/
├── domains/
│   ├── item/          # Move current content here
│   ├── user/          # New domain
│   └── transaction/   # New domain
```

Update `index.md` to become platform overview and link to domain-specific docs.

## Notes

- Manual deployment (no GitHub Actions)
- Material theme with light/dark mode
- Search enabled
- Code highlighting with copy button
