import json
import shutil
import pathlib
import sys

# Paths
BASE_DIR = pathlib.Path(__file__).parent
DATA_PATH = BASE_DIR / 'clients.json'
TALLYGO_DIR = BASE_DIR / 'tallygo'
DIST_DIR = BASE_DIR / 'dist'
TEMPLATES_DIR = BASE_DIR / 'templates'

def clean_dist():
    """Removes and recreates the dist directory."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    print(f"[INFO] Cleaned {DIST_DIR}")

def copy_assets():
    """Copies assets from tallygo and generic assets."""
    # Copy Tallygo generic assets (if any)
    # The Tallygo index.html uses inline SVG/Styles mostly or external links.
    # But usually there might be images. For now we copy what we can.
    
    # We also have our 'public/assets' from before (or data/assets)
    src_assets = BASE_DIR / 'public/assets' 
    dist_assets = DIST_DIR / 'assets'
    
    if src_assets.exists():
        shutil.copytree(src_assets, dist_assets)
        print(f"[INFO] Copied assets to {dist_assets}")

def load_clients():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_index(clients):
    """Builds the main landing page using tallygo/index.html"""
    src_html = (TALLYGO_DIR / 'index.html').read_text(encoding='utf-8')
    
    # Custom CSS for the injected section to ensure 100x look and responsiveness
    custom_styles = """
    <style>
      #demos {
        position: relative;
        z-index: 10;
        padding: 100px 0;
        background: linear-gradient(180deg, #0A0E11 0%, #0F1419 100%);
      }
      .demo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
        gap: 32px;
        margin-top: 48px;
        padding: 0 24px;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
      }
      .demo-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(10px);
        min-height: 400px;
      }
      .demo-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      }
      .demo-card__img {
        height: 240px;
        width: 100%;
        position: relative;
        overflow: hidden;
      }
      .demo-card__img img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s ease;
      }
      .demo-card:hover .demo-card__img img {
        transform: scale(1.1);
      }
      .demo-card__overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to top, #0F1419 0%, transparent 100%);
      }
      .demo-card__body {
        padding: 24px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
      .demo-chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
      }
      .demo-title {
        font-size: 1.5rem;
        margin: 0 0 8px 0;
        font-family: 'Outfit', sans-serif;
        color: #fff;
      }
      .demo-meta {
        font-size: 0.9rem;
        color: #8899A6;
        margin-bottom: 20px;
      }
      .demo-btn {
        display: block;
        width: 100%;
        padding: 14px;
        text-align: center;
        background: linear-gradient(135deg, #D4AF37, #B8860B);
        color: #000;
        font-weight: 700;
        text-decoration: none;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        transition: opacity 0.3s;
      }
      .demo-btn:hover {
        opacity: 0.9;
      }
    </style>
    """
    
    # Inject styles into head
    src_html = src_html.replace('</head>', f'{custom_styles}</head>')

    builder_cards = ""
    for client in clients:
        # Use first project cover as card image if no specific bg_image, else fallback
        img_src = client.get('bg_image', 'assets/hero-1.jpg')
        
        # Theme color for chip
        p_color = client.get('primary_color', '#D4AF37')
        
        builder_cards += f"""
        <div class="demo-card">
            <div class="demo-card__img">
                <img src="{img_src}" alt="{client['company_name']}" loading="lazy">
                <div class="demo-card__overlay"></div>
            </div>
            <div class="demo-card__body">
                <div>
                    <span class="demo-chip" style="color:{p_color}; border-color:{p_color}44; background:{p_color}11;">
                        {client.get('theme', 'Modern')}
                    </span>
                    <h3 class="demo-title">{client['company_name']}</h3>
                    <p class="demo-meta">by {client.get('owner_name', 'Builder')} • {client.get('established', '2020')}</p>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px;">
                        {' '.join([f'<span style="font-size:0.75rem; color:#666;">#{t.get("typology","project")}</span>' for t in client.get('projects',[])[:2]])}
                    </div>
                </div>
                <a href="demos/{client['slug']}/index.html" class="demo-btn">
                    Launch Demo
                </a>
            </div>
        </div>
        """
        
    section_html = f"""
    <section id="demos" aria-label="Builder Demos">
        <div class="container" style="text-align:center; max-width:800px; margin:0 auto;">
          <h2 class="section__title" style="font-size:3rem; margin-bottom:16px;">Live Builder Demos</h2>
          <p class="section__sub" style="font-size:1.2rem; color:#8899A6;">
            Explore premium generated sites powered by Apex Engine. <br>
            Each demo is a fully functional, high-performance static site.
          </p>
        </div>
        <div class="demo-grid">
            {builder_cards}
        </div>
    </section>
    """
    
    # HACK: We will inject this RIGHT AFTER the Hero Section closing tag </section>
    parts = src_html.split('<!-- Problem Section -->')
    if len(parts) > 1:
        new_html = parts[0] + section_html + "<!-- Problem Section -->" + parts[1]
    else:
        new_html = src_html.replace('</main>', f'{section_html}</main>')

    # Update Branding
    new_html = new_html.replace('<title>Tallygo — The Ultimate B2B SaaS for Messaging Based Business</title>', 
                                '<title>Apex Builder — The Ultimate Real Estate Cloud</title>')
    # Branding text replacement if exists in template
    new_html = new_html.replace('Tallygo', 'Apex Builder')
    
    (DIST_DIR / 'index.html').write_text(new_html, encoding='utf-8')
    print("[INFO] Built index.html with premium styling")

def build_demos(clients):
    """Generates individual builder pages."""
    demo_template = (TEMPLATES_DIR / 'demo.html').read_text(encoding='utf-8')
    
    for client in clients:
        client_dir = DIST_DIR / 'demos' / client['slug']
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Stats HTML
        stats_html = ""
        for stat in client.get('stats', []):
            stats_html += f"""
            <div class="stat-item">
                <h4>{stat['value']}</h4>
                <span>{stat['label']}</span>
            </div>
            """
            
        # 2. Projects HTML
        projects_html = ""
        for p in client.get('projects', []):
            projects_html += f"""
            <div class="project-card scroll-trigger">
                <div class="project-img">
                    <img src="../../{p.get('cover_image','')}" alt="{p.get('name')}" loading="lazy">
                </div>
                <div class="project-info">
                    <div class="project-meta">
                        <span class="chip" style="color:var(--primary); border:1px solid var(--primary);">{p.get('status')}</span>
                        <span class="chip">{p.get('typology')}</span>
                    </div>
                    <h3>{p.get('name')}</h3>
                    <p style="margin-bottom:0; font-size:0.95rem;">{p.get('location')}</p>
                </div>
            </div>
            """

        # 3. Inject Basics
        page_html = demo_template.replace('{{company_name}}', client.get('company_name', 'Builder'))
        page_html = page_html.replace('{{owner_name}}', client.get('owner_name', ''))
        page_html = page_html.replace('{{tagline}}', client.get('tagline', 'Excellence in Construction'))
        page_html = page_html.replace('{{established_year}}', client.get('established', '2000'))
        page_html = page_html.replace('{{location_base}}', 'Premium Location') # Placeholder or add to data
        page_html = page_html.replace('{{phone}}', client.get('phone', ''))
        page_html = page_html.replace('{{theme}}', client.get('theme', 'Custom'))
        page_html = page_html.replace('{{company_initial}}', client.get('company_name', 'A')[0])
        page_html = page_html.replace('{{bg_image}}', client.get('bg_image', ''))
        
        # 4. Inject Rich Content
        page_html = page_html.replace('{{stats_html}}', stats_html)
        page_html = page_html.replace('{{projects_html}}', projects_html)
        
        (client_dir / 'index.html').write_text(page_html, encoding='utf-8')
        print(f"[INFO] Built demo for {client['slug']}")

def main():
    clean_dist()
    copy_assets()
    
    clients = load_clients()
    
    # Verify templates exist
    if not (TALLYGO_DIR / 'index.html').exists():
        print("[ERROR] Tallygo index.html not found!")
        return

    # Create templates dir if not exists (we need to write the demo template first)
    TEMPLATES_DIR.mkdir(exist_ok=True)
    
    build_index(clients)
    build_demos(clients)
    print("[SUCCESS] Build complete.")

if __name__ == "__main__":
    main()
