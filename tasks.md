## STEP 1 — Rapid diagnosis

* **Current mode:** Architecture + repo scaffolding
* **Active task:** Convert your landing page into an **Astro static repo** for **GitHub Pages**, with `/` as the primary landing and client demo pages under `/demos/<slug>/`.
* **Strategy:** Build an Astro “static-first” codebase (minimal JS), wire correct base-path handling for GitHub Pages, generate demo pages from `clients.json`, and support **manual per-client markdown overrides** (Option **B**).

---

## STEP 2 — Deep work (Astro repo blueprint + complete key files)

### Assumptions (reasonable defaults)

* You’re deploying to **GitHub Pages Project Site**: `https://<username>.github.io/<repo>/`
* You want **trailing slashes** for stable routing (`/demos/acme/`).
* You prefer **override mechanism B**: optional markdown content per client at `/src/content/demos/<slug>.md`

---

# ✅ Deliverables

## 1) Folder tree (full)

```txt
astro-client-demos/
├─ .github/
│  └─ workflows/
│     └─ deploy.yml
├─ public/
│  ├─ assets/
│  │  ├─ hero.jpg                 (optional example)
│  │  ├─ clients/
│  │  │  └─ acme-bg.jpg           (example bg image)
│  │  └─ og-default.jpg           (default OG image)
│  ├─ themes/
│  │  ├─ modern.css
│  │  ├─ luxury.css
│  │  └─ earthy.css
│  ├─ favicon.svg
│  └─ robots.txt
├─ src/
│  ├─ components/
│  │  ├─ ClientCard.astro
│  │  ├─ Footer.astro
│  │  ├─ Header.astro
│  │  ├─ SeoHead.astro
│  │  └─ Section.astro
│  ├─ content/
│  │  └─ demos/
│  │     └─ acme.md               (optional per-client override content)
│  ├─ data/
│  │  └─ clients.json
│  ├─ layouts/
│  │  └─ BaseLayout.astro
│  ├─ pages/
│  │  ├─ index.astro
│  │  └─ demos/
│  │     ├─ index.astro
│  │     └─ [slug]/
│  │        └─ index.astro
│  ├─ styles/
│  │  └─ base.css
│  └─ utils/
│     ├─ clients.ts
│     ├─ markdown.ts
│     └─ paths.ts
├─ astro.config.mjs
├─ package.json
├─ README.md
└─ tsconfig.json
```

---

## 2) `package.json` (complete)

```json
{
  "name": "astro-client-demos",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check",
    "format": "npx prettier . --write"
  },
  "dependencies": {
    "@astrojs/sitemap": "^3.6.0",
    "astro": "^5.0.0"
  },
  "devDependencies": {
    "prettier": "^3.3.3"
  }
}
```

---

## 3) `astro.config.mjs` (GitHub Pages-ready base + sitemap)

> **IMPORTANT:** set `site` and `base` correctly for your repo name.

```js
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// ✅ For GitHub Pages project site:
// site: https://<username>.github.io
// base: /<repo-name>/
export default defineConfig({
  output: "static",
  trailingSlash: "always",

  site: "https://<username>.github.io",
  base: "/<repo-name>/",

  integrations: [sitemap()]
});
```

If you deploy to a **user/organization root Pages site** (`https://<username>.github.io/`), use:

* `site: "https://<username>.github.io"`
* `base: "/"`

---

## 4) `tsconfig.json`

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "types": ["astro/client"]
  }
}
```

---

## 5) Data model — `src/data/clients.json` (sample)

```json
[
  {
    "slug": "acme",
    "company_name": "Acme Trading Co.",
    "owner_name": "Ravi Kumar",
    "phone": "+91 98765 43210",
    "primary_color": "#39FF14",
    "theme": "modern",
    "bg_image": "/assets/clients/acme-bg.jpg"
  },
  {
    "slug": "lotus",
    "company_name": "Lotus Wholesale",
    "owner_name": "Ayesha Khan",
    "phone": "+91 91234 56789",
    "primary_color": "#00E5FF",
    "theme": "luxury",
    "bg_image": "/assets/clients/acme-bg.jpg"
  }
]
```

---

## 6) Utilities

### `src/utils/paths.ts` (base-safe links for GitHub Pages)

**Rule:** never use `href="/demos/"` on GH Pages project sites. Always prefix with `BASE_URL`.

```ts
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL || "/";
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  return `${base}${cleanPath}`;
}

export function absoluteUrl(path: string, site?: URL): string {
  if (!site) return path;
  const url = new URL(withBase(path), site);
  return url.toString();
}
```

### `src/utils/clients.ts`

```ts
import clients from "../data/clients.json";

export type ClientTheme = "modern" | "luxury" | "earthy";

export type Client = {
  slug: string;
  company_name: string;
  owner_name: string;
  phone: string;
  primary_color: string;
  theme: ClientTheme;
  bg_image: string;
};

export function getAllClients(): Client[] {
  return (clients as Client[]).slice().sort((a, b) => a.company_name.localeCompare(b.company_name));
}

export function getClientBySlug(slug: string): Client | undefined {
  return getAllClients().find((c) => c.slug === slug);
}
```

### `src/utils/markdown.ts` (Option B: optional content per client)

```ts
type DemoMarkdownModule = {
  url: string;
  frontmatter: Record<string, unknown>;
  Content: any;
};

export async function getDemoMarkdownBySlug(slug: string) {
  const modules = (await Astro.glob<DemoMarkdownModule>("../content/demos/*.md")) as DemoMarkdownModule[];

  for (const mod of modules) {
    // mod.url ends like ".../acme.md"
    const fileSlug = mod.url.split("/").pop()?.replace(".md", "");
    if (fileSlug === slug) return mod;
  }
  return null;
}
```

> Note: `Astro.glob` is available in Astro frontmatter context. We’ll use it directly from the page file for reliability (see below). If you prefer strict separation, we can keep this function inside the page.

---

## 7) Global base styles — `src/styles/base.css`

Minimal, fast, “premium dark” defaults, plus clean focus styles and layout rhythm.

```css
:root {
  --bg: #070a0f;
  --surface: rgba(255, 255, 255, 0.06);
  --surface-2: rgba(255, 255, 255, 0.09);
  --border: rgba(255, 255, 255, 0.10);
  --text: rgba(255, 255, 255, 0.92);
  --muted: rgba(255, 255, 255, 0.72);

  --brand: #39ff14;
  --brand-2: #00e5ff;

  --radius: 16px;
  --radius-sm: 12px;

  --shadow: 0 16px 40px rgba(0, 0, 0, 0.55);

  --container: 1120px;
  --gutter: 20px;

  --h1: clamp(2.2rem, 4vw, 3.4rem);
  --h2: clamp(1.6rem, 2.4vw, 2.2rem);
  --h3: 1.25rem;
  --p: 1rem;
  --lh: 1.65;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html:focus-within {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Apple Color Emoji",
    "Segoe UI Emoji";
  background: radial-gradient(1200px 600px at 20% -10%, rgba(57, 255, 20, 0.10), transparent 60%),
    radial-gradient(900px 500px at 90% 0%, rgba(0, 229, 255, 0.10), transparent 55%),
    var(--bg);
  color: var(--text);
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  height: auto;
}

.container {
  width: min(var(--container), calc(100% - (var(--gutter) * 2)));
  margin: 0 auto;
}

.muted {
  color: var(--muted);
}

.skip-link {
  position: absolute;
  left: 12px;
  top: 12px;
  padding: 10px 12px;
  background: #0c1220;
  border: 1px solid var(--border);
  border-radius: 10px;
  transform: translateY(-140%);
  transition: transform 150ms ease;
  z-index: 9999;
}

.skip-link:focus {
  transform: translateY(0);
  outline: none;
}

:where(a, button, input, summary, [tabindex]):focus-visible {
  outline: 2px solid rgba(57, 255, 20, 0.85);
  outline-offset: 3px;
  border-radius: 10px;
}

button {
  font: inherit;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 999px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.06);
  color: var(--text);
  transition: transform 150ms ease, background 150ms ease, border-color 150ms ease;
  cursor: pointer;
  white-space: nowrap;
}

.btn:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.18);
}

.btn--primary {
  background: linear-gradient(90deg, rgba(57, 255, 20, 0.20), rgba(0, 229, 255, 0.16));
  border-color: rgba(57, 255, 20, 0.28);
}

.card {
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.grid {
  display: grid;
  gap: 18px;
}

@media (prefers-reduced-motion: reduce) {
  html:focus-within {
    scroll-behavior: auto;
  }
  * {
    transition-duration: 1ms !important;
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
  }
}
```

---

## 8) Theme packs (CSS files, selected via `client.theme`)

These are served from `/public/themes/*` for simplicity and easy manual editing.

### `public/themes/modern.css`

```css
:root {
  --surface: rgba(255, 255, 255, 0.06);
  --surface-2: rgba(255, 255, 255, 0.09);
  --border: rgba(255, 255, 255, 0.12);
}
```

### `public/themes/luxury.css`

```css
:root {
  --surface: rgba(255, 255, 255, 0.05);
  --surface-2: rgba(255, 255, 255, 0.08);
  --border: rgba(255, 255, 255, 0.10);
}
body {
  background: radial-gradient(1200px 700px at 30% -10%, rgba(255, 215, 0, 0.10), transparent 60%),
    radial-gradient(900px 600px at 90% 0%, rgba(0, 229, 255, 0.08), transparent 55%),
    #07080c;
}
```

### `public/themes/earthy.css`

```css
:root {
  --surface: rgba(255, 255, 255, 0.055);
  --surface-2: rgba(255, 255, 255, 0.085);
  --border: rgba(255, 255, 255, 0.11);
}
body {
  background: radial-gradient(1200px 700px at 20% -10%, rgba(124, 252, 0, 0.08), transparent 60%),
    radial-gradient(900px 600px at 90% 0%, rgba(160, 82, 45, 0.10), transparent 55%),
    #070a0f;
}
```

---

## 9) Components & layout

### `src/components/SeoHead.astro`

```astro
---
import { absoluteUrl } from "../utils/paths";

type Props = {
  title: string;
  description: string;
  canonicalPath: string;
  ogImagePath?: string;
};

const { title, description, canonicalPath, ogImagePath = "assets/og-default.jpg" } = Astro.props;

const site = Astro.site;
const canonical = site ? absoluteUrl(canonicalPath, site) : canonicalPath;
const ogImage = site ? absoluteUrl(ogImagePath, site) : ogImagePath;
---

<title>{title}</title>
<meta name="description" content={description} />

<link rel="canonical" href={canonical} />

<meta property="og:type" content="website" />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={ogImage} />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content={title} />
<meta name="twitter:description" content={description} />
<meta name="twitter:image" content={ogImage} />
```

### `src/components/Header.astro`

```astro
---
import { withBase } from "../utils/paths";
const base = import.meta.env.BASE_URL || "/";
---

<header style="position: sticky; top: 0; z-index: 50; backdrop-filter: blur(12px);">
  <a class="skip-link" href="#main">Skip to content</a>

  <div class="container" style="display:flex; align-items:center; justify-content:space-between; padding:14px 0;">
    <a href={base} style="display:flex; align-items:center; gap:10px;">
      <span style="display:inline-flex; width:12px; height:12px; border-radius:999px; background: var(--brand); box-shadow: 0 0 24px rgba(57,255,20,0.35);"></span>
      <strong style="letter-spacing:0.2px;">Tallygo</strong>
    </a>

    <nav aria-label="Primary" style="display:flex; align-items:center; gap:14px;">
      <a class="btn" href={withBase("demos/")}>View demos</a>
      <a class="btn btn--primary" href="https://tallygo.app/start" rel="noopener">Start</a>
    </nav>
  </div>

  <div style="height:1px; background: rgba(255,255,255,0.08);"></div>
</header>
```

### `src/components/Footer.astro`

```astro
---
import { withBase } from "../utils/paths";
const year = new Date().getFullYear();
---

<footer style="padding: 40px 0 60px;">
  <div class="container">
    <div class="card" style="padding: 18px;">
      <div style="display:flex; flex-wrap:wrap; gap:14px; align-items:center; justify-content:space-between;">
        <div>
          <strong>Tallygo</strong>
          <div class="muted" style="font-size: 0.95rem; margin-top: 6px;">
            Static demos built with Astro • {year}
          </div>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <a class="btn" href={withBase("demos/")}>Demos</a>
          <a class="btn" href={withBase("")}>Home</a>
        </div>
      </div>
    </div>
  </div>
</footer>
```

### `src/components/Section.astro`

```astro
---
type Props = { title: string; subtitle?: string; id?: string };
const { title, subtitle, id } = Astro.props;
---

<section id={id} style="padding: 64px 0;">
  <div class="container">
    <div style="max-width: 70ch; margin-bottom: 18px;">
      <h2 style="margin:0; font-size: var(--h2);">{title}</h2>
      {subtitle && <p class="muted" style="margin: 10px 0 0; line-height: var(--lh);">{subtitle}</p>}
    </div>
    <slot />
  </div>
</section>
```

### `src/components/ClientCard.astro`

```astro
---
import type { Client } from "../utils/clients";
import { withBase } from "../utils/paths";

type Props = { client: Client };
const { client } = Astro.props;

const demoHref = withBase(`demos/${client.slug}/`);
const bgUrl = client.bg_image ? withBase(client.bg_image) : "";
---

<a class="card" href={demoHref} style="
  display:block;
  padding: 16px;
  border-radius: var(--radius);
  position: relative;
  overflow:hidden;
  min-height: 160px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
">
  {bgUrl && (
    <div style={`position:absolute; inset:0; background-image:url('${bgUrl}'); background-size:cover; background-position:center; opacity:0.14;`}></div>
  )}
  <div style="position:relative;">
    <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
      <strong style="font-size: 1.05rem;">{client.company_name}</strong>
      <span class="muted" style="font-size: 0.9rem;">/{client.slug}</span>
    </div>
    <div class="muted" style="margin-top: 10px; line-height: 1.5;">
      Owner: {client.owner_name}<br />
      Theme: {client.theme}
    </div>
    <div style="margin-top: 14px;">
      <span class="btn btn--primary" style={`--brand: ${client.primary_color}; border-color: color-mix(in srgb, ${client.primary_color} 30%, rgba(255,255,255,0.10));`}>
        Open demo →
      </span>
    </div>
  </div>
</a>
```

---

## 10) Layout — `src/layouts/BaseLayout.astro`

```astro
---
import "../styles/base.css";
import Header from "../components/Header.astro";
import Footer from "../components/Footer.astro";
import SeoHead from "../components/SeoHead.astro";
import { withBase } from "../utils/paths";

type Props = {
  title: string;
  description: string;
  canonicalPath: string;
  themeCssHref?: string;
  brandColor?: string;
};

const {
  title,
  description,
  canonicalPath,
  themeCssHref,
  brandColor
} = Astro.props;

const faviconHref = withBase("favicon.svg");
const themeHref = themeCssHref ? withBase(themeCssHref) : null;
const brandStyle = brandColor ? `--brand: ${brandColor};` : "";
---

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    <link rel="icon" href={faviconHref} />
    {themeHref && <link rel="stylesheet" href={themeHref} />}

    <SeoHead
      title={title}
      description={description}
      canonicalPath={canonicalPath}
    />

    <style is:global>
      body { ${brandStyle} }
      main { min-height: 60vh; }
      .hero-grid {
        display:grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 18px;
        align-items: stretch;
      }
      @media (max-width: 960px) {
        .hero-grid { grid-template-columns: 1fr; }
      }
    </style>
  </head>

  <body>
    <Header />
    <main id="main">
      <slot />
    </main>
    <Footer />
  </body>
</html>
```

---

# Pages

## 11) Landing — `src/pages/index.astro`

Landing at `/` with hero + sections + CTA + **View demos** listing.

```astro
---
import BaseLayout from "../layouts/BaseLayout.astro";
import Section from "../components/Section.astro";
import ClientCard from "../components/ClientCard.astro";
import { getAllClients } from "../utils/clients";
import { withBase } from "../utils/paths";

const clients = getAllClients();
const demosHref = withBase("demos/");
---

<BaseLayout
  title="Tallygo — Client Demos"
  description="Fast, SEO-first Astro landing page with generated client demo pages under /demos/<slug>/."
  canonicalPath=""
>
  <section style="padding: 64px 0 28px;">
    <div class="container hero-grid">
      <div class="card" style="padding: 22px;">
        <div style="max-width: 70ch;">
          <h1 style="margin:0; font-size: var(--h1); letter-spacing: -0.02em;">
            Your primary landing page — built for speed, SEO, and demos.
          </h1>
          <p class="muted" style="margin: 14px 0 0; font-size: 1.05rem; line-height: var(--lh);">
            Astro static output for GitHub Pages. Client-specific demo pages generated from JSON,
            with optional markdown overrides when you need custom content.
          </p>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top: 18px;">
          <a class="btn btn--primary" href="https://tallygo.app/start" rel="noopener">Start →</a>
          <a class="btn" href={demosHref}>View demos</a>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top: 18px;">
          <span class="card" style="padding:10px 12px; border-radius: 999px; display:inline-flex; gap:8px; align-items:center;">
            <span style="width:10px; height:10px; border-radius:999px; background:rgba(57,255,20,0.8);"></span>
            <span class="muted">Minimal JS</span>
          </span>
          <span class="card" style="padding:10px 12px; border-radius: 999px; display:inline-flex; gap:8px; align-items:center;">
            <span style="width:10px; height:10px; border-radius:999px; background:rgba(0,229,255,0.75);"></span>
            <span class="muted">SEO-first</span>
          </span>
          <span class="card" style="padding:10px 12px; border-radius: 999px; display:inline-flex; gap:8px; align-items:center;">
            <span style="width:10px; height:10px; border-radius:999px; background:rgba(255,255,255,0.35);"></span>
            <span class="muted">GitHub Pages ready</span>
          </span>
        </div>
      </div>

      <div class="card" style="padding: 22px; position:relative; overflow:hidden;">
        <div style="position:absolute; inset:0; opacity:0.18;
          background: radial-gradient(500px 260px at 20% 15%, rgba(57,255,20,0.24), transparent 60%),
          radial-gradient(520px 260px at 90% 20%, rgba(0,229,255,0.20), transparent 58%);
        "></div>

        <div style="position:relative;">
          <strong style="display:block; font-size: 1rem;">Project structure</strong>
          <pre class="card" style="margin-top: 12px; padding: 14px; overflow:auto; border-radius: 14px; background: rgba(0,0,0,0.35); box-shadow:none;">
/ (landing)
└─ /demos/
   ├─ (directory listing)
   └─ /demos/&lt;slug&gt;/ (generated)
          </pre>
          <p class="muted" style="margin: 12px 0 0; line-height: var(--lh);">
            Add clients in <code>/src/data/clients.json</code>. Drop a markdown file in
            <code>/src/content/demos/&lt;slug&gt;.md</code> to override content.
          </p>
        </div>
      </div>
    </div>
  </section>

  <Section
    title="Projects (Client demos)"
    subtitle="Each demo is generated from clients.json and theme-selected per client."
    id="projects"
  >
    <div class="grid" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
      {clients.slice(0, 6).map((client) => <ClientCard client={client} />)}
    </div>

    <div style="margin-top: 16px;">
      <a class="btn" href={demosHref}>Browse all demos →</a>
    </div>

    <style is:global>
      @media (max-width: 960px) {
        #projects .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }
      @media (max-width: 640px) {
        #projects .grid { grid-template-columns: 1fr; }
      }
    </style>
  </Section>

  <Section
    title="How it works"
    subtitle="Static-first pipeline with sane defaults for SEO, base paths, and customization."
  >
    <div class="grid" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
      <div class="card" style="padding: 16px;">
        <strong>1) Add clients</strong>
        <p class="muted" style="margin: 10px 0 0; line-height: var(--lh);">
          Edit <code>/src/data/clients.json</code> with slug, theme, brand color, and bg image.
        </p>
      </div>
      <div class="card" style="padding: 16px;">
        <strong>2) Generate pages</strong>
        <p class="muted" style="margin: 10px 0 0; line-height: var(--lh);">
          Astro generates <code>/demos/&lt;slug&gt;/</code> at build time with zero runtime server.
        </p>
      </div>
      <div class="card" style="padding: 16px;">
        <strong>3) Override when needed</strong>
        <p class="muted" style="margin: 10px 0 0; line-height: var(--lh);">
          Add <code>/src/content/demos/&lt;slug&gt;.md</code> to inject per-client content.
        </p>
      </div>
    </div>

    <style is:global>
      @media (max-width: 960px) {
        .grid { grid-template-columns: 1fr !important; }
      }
    </style>
  </Section>
</BaseLayout>
```

---

## 12) Demos directory listing — `src/pages/demos/index.astro`

```astro
---
import BaseLayout from "../../layouts/BaseLayout.astro";
import ClientCard from "../../components/ClientCard.astro";
import { getAllClients } from "../../utils/clients";

const clients = getAllClients();
---

<BaseLayout
  title="Demos — Tallygo"
  description="Browse all generated client demo pages."
  canonicalPath="demos/"
>
  <section style="padding: 48px 0;">
    <div class="container">
      <h1 style="margin:0; font-size: var(--h1); letter-spacing:-0.02em;">Demos</h1>
      <p class="muted" style="margin: 12px 0 0; max-width: 70ch; line-height: var(--lh);">
        Generated pages under <code>/demos/&lt;slug&gt;/</code>. Each client can choose a theme and brand color.
      </p>

      <div class="grid" style="margin-top: 18px; grid-template-columns: repeat(3, minmax(0, 1fr));">
        {clients.map((client) => <ClientCard client={client} />)}
      </div>

      <style is:global>
        @media (max-width: 960px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; } }
        @media (max-width: 640px) { .grid { grid-template-columns: 1fr !important; } }
      </style>
    </div>
  </section>
</BaseLayout>
```

---

## 13) Individual demo page — `src/pages/demos/[slug]/index.astro`

* Generates routes from `clients.json`
* Sets theme per client (`/public/themes/<theme>.css`)
* Sets CSS variable `--brand` from `primary_color`
* Injects **optional markdown content** if `src/content/demos/<slug>.md` exists

```astro
---
import BaseLayout from "../../../layouts/BaseLayout.astro";
import { getAllClients, getClientBySlug } from "../../../utils/clients";
import { withBase } from "../../../utils/paths";

export async function getStaticPaths() {
  const clients = getAllClients();
  return clients.map((client) => ({
    params: { slug: client.slug }
  }));
}

const { slug } = Astro.params;
const client = slug ? getClientBySlug(slug) : null;

if (!client) {
  // Astro will render a 404-like page if not found; keep minimal.
  throw new Error(`Client not found for slug: ${slug}`);
}

type DemoMarkdownModule = {
  url: string;
  frontmatter: Record<string, unknown>;
  Content: any;
};

const markdownModules = (await Astro.glob<DemoMarkdownModule>("../../../content/demos/*.md")) as DemoMarkdownModule[];

let markdownForClient: DemoMarkdownModule | null = null;
for (const mod of markdownModules) {
  const fileSlug = mod.url.split("/").pop()?.replace(".md", "");
  if (fileSlug === client.slug) {
    markdownForClient = mod;
    break;
  }
}

const themeCssHref = `themes/${client.theme}.css`;
const bgUrl = client.bg_image ? withBase(client.bg_image) : "";
---

<BaseLayout
  title={`${client.company_name} Demo — Tallygo`}
  description={`Demo page for ${client.company_name}. Theme: ${client.theme}.`}
  canonicalPath={`demos/${client.slug}/`}
  themeCssHref={themeCssHref}
  brandColor={client.primary_color}
>
  <section style="padding: 56px 0;">
    <div class="container">
      <div class="card" style="padding: 18px; overflow:hidden; position:relative;">
        {bgUrl && (
          <div style={`position:absolute; inset:0; background-image:url('${bgUrl}'); background-size:cover; background-position:center; opacity:0.14;`}></div>
        )}

        <div style="position:relative; display:flex; flex-wrap:wrap; gap:16px; align-items:flex-start; justify-content:space-between;">
          <div style="max-width: 70ch;">
            <h1 style="margin:0; font-size: var(--h1); letter-spacing:-0.02em;">
              {client.company_name}
            </h1>
            <p class="muted" style="margin: 12px 0 0; line-height: var(--lh);">
              Owner: <strong>{client.owner_name}</strong> • Phone: <strong>{client.phone}</strong><br />
              Theme: <strong>{client.theme}</strong> • Slug: <code>{client.slug}</code>
            </p>

            <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top: 16px;">
              <a class="btn btn--primary" href="https://tallygo.app/start" rel="noopener">Start →</a>
              <a class="btn" href={withBase("demos/")}>Back to demos</a>
            </div>
          </div>

          <div class="card" style="padding: 14px; border-radius: 14px; box-shadow:none; background: rgba(0,0,0,0.28); min-width: 260px;">
            <div class="muted" style="font-size: 0.92rem; margin-bottom: 10px;">Brand preview</div>
            <div style="display:flex; align-items:center; gap:12px;">
              <span style="width: 16px; height: 16px; border-radius: 999px; background: var(--brand); box-shadow: 0 0 24px color-mix(in srgb, var(--brand) 35%, transparent);"></span>
              <code>{client.primary_color}</code>
            </div>
            <div class="muted" style="margin-top: 10px; font-size: 0.92rem; line-height: 1.5;">
              This page uses CSS variables derived from <code>primary_color</code> and loads a theme pack.
            </div>
          </div>
        </div>
      </div>

      <div style="margin-top: 18px;" class="grid">
        <div class="card" style="padding: 18px;">
          <h2 style="margin:0; font-size: var(--h2);">Demo content</h2>
          <p class="muted" style="margin: 10px 0 0; line-height: var(--lh);">
            This section is generated. If <code>/src/content/demos/{client.slug}.md</code> exists, it will render below.
          </p>

          {markdownForClient ? (
            <article style="margin-top: 14px; line-height: var(--lh);">
              <markdownForClient.Content />
            </article>
          ) : (
            <div class="card" style="margin-top: 14px; padding: 14px; box-shadow:none; background: rgba(255,255,255,0.04);">
              <div class="muted" style="line-height: var(--lh);">
                No markdown override found for <code>{client.slug}</code>.
                Add one at <code>/src/content/demos/{client.slug}.md</code>.
              </div>
            </div>
          )}
        </div>

        <div class="card" style="padding: 18px;">
          <h2 style="margin:0; font-size: var(--h2);">Quick actions</h2>
          <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top: 12px;">
            <a class="btn" href={withBase("")}>Home</a>
            <a class="btn" href={withBase("demos/")}>All demos</a>
            <a class="btn btn--primary" href="https://tallygo.app/start" rel="noopener">Primary CTA</a>
          </div>

          <p class="muted" style="margin: 12px 0 0; line-height: var(--lh);">
            Ensure all internal links use base-safe paths via <code>withBase()</code> for GitHub Pages.
          </p>
        </div>
      </div>
    </div>
  </section>
</BaseLayout>
```

---

## 14) Markdown override example — `src/content/demos/acme.md`

```md
---
title: "Acme Demo Notes"
---

### What this demo showcases
- Theme selection (`modern`)
- Per-client background image
- Brand color mapped to CSS variable `--brand`

### Custom section
You can add **any** markdown content here (FAQs, proposal text, screenshots, links).
```

---

# SEO support files

## 15) `public/robots.txt`

```txt
User-agent: *
Allow: /

Sitemap: https://<username>.github.io/<repo-name>/sitemap-index.xml
```

> The sitemap file name may vary depending on plugin version; once deployed, open `/sitemap-index.xml` or `/sitemap.xml` and update this line to match the generated output.

---

# GitHub Actions deployment

## 16) `.github/workflows/deploy.yml`

```yml
name: Deploy Astro to GitHub Pages

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install deps
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

---

# README (exact instructions)

## 17) `README.md`

````md
# Astro Client Demos (GitHub Pages)

## Local dev
```bash
npm install
npm run dev
````

## Build

```bash
npm run build
npm run preview
```

## Data-driven demos

Edit:

* `src/data/clients.json`

Each client generates:

* `/demos/<slug>/`

Optional per-client content override:

* `src/content/demos/<slug>.md`

## GitHub Pages deployment (Project site)

1. Create a GitHub repo named: `<repo-name>`

2. In `astro.config.mjs`, set:

   * `site: "https://<username>.github.io"`
   * `base: "/<repo-name>/"`

3. Commit and push to `main`.

4. In GitHub repo settings:

   * Settings → Pages → Build and deployment → Source: **GitHub Actions**

5. After the workflow runs, your site will be:

   * `https://<username>.github.io/<repo-name>/`

## If deploying as a root site (`<username>.github.io`)

Use:

* `site: "https://<username>.github.io"`
* `base: "/"`

## Important note about links

For project sites, do not use root-absolute links like `/demos/`.
Use `withBase("demos/")` so links work under the repo subpath.

````

---

# Why this design meets your goals

### Fast production performance
- **Static output** only (`output: "static"`), no server runtime.
- **Minimal JS** by default (pure Astro components + CSS).
- Theme packs are **CSS-only** and cache-friendly.

### SEO-first
- Per-page meta title/description
- OG tags + canonical URL
- `@astrojs/sitemap` generates sitemap automatically
- `robots.txt` included (update URL placeholders after you set `site/base`)

### Transferable for GitHub Pages
- `/dist` is deployable as plain static files.
- Base-path safe internal routing via `withBase()`.

### Easy manual customization
- **Option B implemented**: drop markdown at `src/content/demos/<slug>.md` to add custom content without changing code.

---

## STEP 3 — Quality control (self-check)
- ✅ Routes: `/`, `/demos/`, `/demos/<slug>/` generated from JSON.
- ✅ GitHub Pages base path handled via `withBase()` (prevents broken links).
- ✅ Theme packs in CSS files (modern/luxury/earthy) and selected per client.
- ✅ CSS variables set from `primary_color`.
- ✅ Sitemap + robots present (robots needs placeholder replacement).
- ✅ GitHub Actions workflow deploys `dist`.

Potential follow-up improvement (not required, but high ROI):
- Add a tiny `404.astro` page under `src/pages/404.astro` for nicer GH Pages 404 behavior.
- Add image optimization pipeline later (Astro assets) if you start adding large images.

---

## STEP 4 — Updated `tasks.md`
```md
# Astro GitHub Pages Repo — Landing + Client Demos
Progress: ▓▓▓▓▓▓░░░░ 60%

## 0) Repo Scaffolding
[x] Define folder tree and required routes (/ , /demos/ , /demos/<slug>/)
[x] Add clients.json schema and sample data
[x] Implement base-safe routing helper (withBase)
[x] Create BaseLayout, SEO Head component, and shared styles
[x] Implement theme packs (modern, luxury, earthy) as CSS files

## 1) Pages
[x] Landing page at / with hero + “Projects / View demos” section listing clients
[x] /demos/ directory listing page (cards)
[x] /demos/<slug>/ generated demo page from clients.json
[x] Manual overrides implemented (Option B: optional markdown per client)

## 2) SEO + Crawl
[/] Sitemap integration via @astrojs/sitemap
[ ] Confirm final sitemap filename in dist and update robots.txt accordingly
[ ] Add structured data (Organization + WebSite) for richer SEO

## 3) GitHub Pages Deployment
[x] astro.config placeholders for site/base for GitHub Pages
[x] GitHub Actions workflow to build and deploy /dist
[ ] Add README instructions for repo name + base/site setup verification (already included; verify placeholders replaced)

## 4) Polish
[ ] Add 404 page for GitHub Pages
[ ] Add lightweight “theme preview” toggles on landing (optional)
[ ] Add per-client CTA override fields (optional extension to clients.json)

## Done
[x] Provide complete key files: astro.config, package.json, routes, components, styles, clients.json, workflow, README
````

