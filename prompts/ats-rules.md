# ATS rules

Generated resumes should survive automated parsing AND read well to a human. Both matter.

## Parser-safe formatting
- One column, top-to-bottom flow. No multi-column layouts that confuse the parser.
- No text in headers/footers, no text in images, no text inside SVGs.
- No tables for layout. Tables for tabular data only, and even then prefer plain lines.
- Standard section headings: `Experience`, `Skills`, `Education`, `Projects`. Avoid cute names.
- Standard fonts (Inter, Helvetica, Arial, Calibri, system-ui). No decorative fonts.
- Black text on white. Accent color is fine for headings only.

## Keywords
- Pull the JD's hard requirements and surface them verbatim in Skills and at least one bullet.
- Include both spelled-out forms and acronyms when both appear in the wild: "Continuous Integration (CI)", "Kubernetes (K8s)".
- Do NOT keyword-stuff. Each keyword needs a real bullet or a real skill behind it.

## Contact block
- Plain text email, phone, city/country.
- Linkedin and GitHub as full URLs (the parser handles them; the human clicks them).
- No icons-only contact rows. Always pair an icon with text.

## Dates and locations
- Use unambiguous date formats: `05/2024`, not `May '24`.
- Include city + country for each role. Helps both parsers and recruiters scanning for location fit.

## Files and naming
- PDF output. Filename: `FirstLast_Role_Company.pdf`.
- Embed fonts. Selectable text (no rasterized resume images).
- Keep file size under ~1MB.

## Anti-patterns to avoid
- Emojis in body text.
- Star ratings or progress bars for skill levels — parsers can't read them, recruiters distrust them.
- Photos for non-EU markets. (In Germany/EU, optional. Match the JD's region.)
- Hyperlinks hiding important text (e.g., role title as a link with no plain-text role).
