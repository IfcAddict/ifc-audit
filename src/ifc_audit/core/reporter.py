import json
import os
from datetime import datetime

class HTMLReporter:
    def __init__(self, results: dict):
        self.results = results
        self.summary = results.get("summary", {})
        self.inventory = results.get("inventory", {})
        self.issues = results.get("issues", {})
        self.metadata = results.get("metadata", {})

    def _get_issue_count(self, key):
        if key in ("heavy_brep", "missing_properties", "orphans"):
            return sum(len(g.get("elements", [])) for g in self.issues.get(key, []))
        return len(self.issues.get(key, []))

    def generate(self, output_path: str):
        """Generates the HTML report."""
        html_content = self._build_html()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return output_path

    def _build_html(self):
        # Premium CSS embedded
        css = """
        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-dim: #64748b;
            --border: #e2e8f0;
            --error: #ef4444;
            --warning: #f59e0b;
            --success: #10b981;
        }
        body { font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text-main); margin: 0; padding: 2rem; }
        .container { max-width: 1000px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 2px solid var(--border); padding-bottom: 1rem; }
        h1 { margin: 0; color: var(--primary); font-size: 2rem; }
        .timestamp { color: var(--text-dim); font-size: 0.9rem; }
        
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: var(--card-bg); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
        .card h3 { margin: 0 0 0.5rem 0; color: var(--text-dim); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .card .value { font-size: 2rem; font-weight: 700; color: var(--primary); }
        .card.error .value { color: var(--error); }
        
        .section { background: var(--card-bg); padding: 2rem; border-radius: 0.75rem; border: 1px solid var(--border); margin-bottom: 2rem; }
        .section h2 { margin-top: 0; border-left: 4px solid var(--primary); padding-left: 1rem; color: var(--text-main); font-size: 1.5rem; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th { text-align: left; background: #f1f5f9; padding: 0.75rem; color: var(--text-dim); font-size: 0.85rem; border-bottom: 2px solid var(--border); }
        td { padding: 0.75rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        tr:hover { background: #f8fafc; }
        
        .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
        .badge.error { background: #fee2e2; color: #b91c1c; }
        .badge.warning { background: #fef3c7; color: #92400e; }
        .badge.very-high { background: #fee2e2; color: #dc2626; border: 1px solid #dc2626; }
        .badge.high { background: #fff7ed; color: #d97706; border: 1px solid #d97706; }
        .badge.medium { background: #f8fafc; color: #000000; border: 1px solid #000000; }
        .badge.low { background: #f0fdf4; color: #15803d; border: 1px solid #15803d; }
        
        .category-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .category-tag { background: #e0f2fe; color: #0369a1; padding: 0.3rem 0.6rem; border-radius: 0.4rem; font-size: 0.8rem; }
        """

        summary_html = f"""
        <div class="dashboard">
            <div class="card"><h3>Entities</h3><div class="value">{self.summary.get('total_entities', 0)}</div></div>
            <div class="card error">
                <h3>Issues Found</h3>
                <div class="value">{self.summary.get('total_issues', 0)}</div>
                <div style="font-size: 0.85rem; margin-top: 1rem; color: var(--text-main); line-height: 1.5;">
                    <div><strong>{self._get_issue_count('orphans')}</strong> Orphans</div>
                    <div><strong>{self._get_issue_count('empty_psets')}</strong> Empty PSets</div>
                    <div><strong>{self._get_issue_count('unused_types')}</strong> Unused Types</div>
                    <div><strong>{self._get_issue_count('duplicate_guids')}</strong> Duplicate GUIDs</div>
                    <div><strong>{self._get_issue_count('missing_properties')}</strong> Missing Props</div>
                    <div><strong>{self._get_issue_count('heavy_brep')}</strong> Heavy BRep</div>
                </div>
            </div>
            <div class="card"><h3>File Size</h3><div class="value">{self.summary.get('file_size_mb', 'N/A')} MB</div></div>
            <div class="card"><h3>Schema</h3><div class="value">{self.summary.get('schema', 'Unknown')}</div></div>
        </div>
        """

        inventory_rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in list(self.inventory.items())[:20]])
        inventory_html = f"""
        <div class="section">
            <h2>Model Inventory (Top 20)</h2>
            <table><thead><tr><th>Entity Type</th><th>Count</th></tr></thead>
            <tbody>{inventory_rows}</tbody></table>
        </div>
        """

        issues_html = ""
        # Orphans
        if self.issues.get("orphans"):
            rows = ""
            for group in self.issues["orphans"]:
                # Group header row
                rows += f"<tr style='background: #f1f5f9; font-weight: bold;'><td colspan='4'>Type: {group['type']} ({len(group['elements'])})</td></tr>"
                for o in group["elements"][:20]: # Limit elements per type to avoid massive reports
                    rows += f"<tr><td>{o['id']}</td><td>{o['name']}</td><td>{o['type']}</td><td><span class='badge {o['severity']}'>{o['severity'].upper()}</span></td></tr>"
            
            issues_html += f"<div class='section'><h2>Orphans ({self._get_issue_count('orphans')})</h2><table><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Severity</th></tr></thead><tbody>{rows}</tbody></table></div>"

        # Duplicate GUIDs
        if self.issues.get("duplicate_guids"):
            rows = "".join([f"<tr><td>{d['guid']}</td><td>{d['count']}</td><td>{', '.join(map(str, d['ids']))}</td></tr>" for d in self.issues["duplicate_guids"]])
            issues_html += f"<div class='section'><h2>Duplicate GUIDs ({len(self.issues['duplicate_guids'])})</h2><table><thead><tr><th>GUID</th><th>Count</th><th>Elements (IDs)</th></tr></thead><tbody>{rows}</tbody></table></div>"

        # Empty PSets
        if self.issues.get("empty_psets"):
            rows = "".join([f"<tr><td>{p['id']}</td><td>{p['name']}</td><td>{p['type']}</td></tr>" for p in self.issues["empty_psets"][:50]])
            issues_html += f"<div class='section'><h2>Empty PSets ({self._get_issue_count('empty_psets')})</h2><table><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead><tbody>{rows}</tbody></table></div>"

        # Unused Types
        if self.issues.get("unused_types"):
            rows = "".join([f"<tr><td>{t['id']}</td><td>{t['name']}</td><td>{t['type']}</td></tr>" for t in self.issues["unused_types"][:50]])
            issues_html += f"<div class='section'><h2>Unused Types ({self._get_issue_count('unused_types')})</h2><table><thead><tr><th>ID</th><th>Name</th><th>Type</th></tr></thead><tbody>{rows}</tbody></table></div>"

        # Missing Properties
        if self.issues.get("missing_properties"):
            rows = ""
            for group in self.issues["missing_properties"]:
                rows += f"<tr style='background: #f1f5f9; font-weight: bold;'><td colspan='4'>Required: {group['property']}</td></tr>"
                for o in group["elements"][:20]:
                    rows += f"<tr><td>{o['id']}</td><td>{o['name']}</td><td>{o['type']}</td><td><span class='badge error'>Missing</span></td></tr>"
            issues_html += f"<div class='section'><h2>Missing Properties ({self._get_issue_count('missing_properties')})</h2><table><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>"

        # Heavy BRep
        if self.issues.get("heavy_brep"):
            rows = ""
            for g in self.issues["heavy_brep"]:
                level_class = "low"
                if "Very High" in g['group']: level_class = "very-high"
                elif "High" in g['group']: level_class = "high"
                elif "Medium" in g['group']: level_class = "medium"
                
                for e in g.get("elements", [])[:10]:
                    rows += f"<tr><td>{e['id']}</td><td>{e['name']}</td><td>{e['faces']}</td><td><span class='badge {level_class}'>{g['group']}</span></td></tr>"
            
            issues_html += f"<div class='section'><h2>Heavy BRep ({self._get_issue_count('heavy_brep')})</h2><table><thead><tr><th>ID</th><th>Name</th><th>Faces</th><th>Complexity</th></tr></thead><tbody>{rows}</tbody></table></div>"

        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IFC Audit Report - {self.summary.get('file', 'Model')}</title>
            <style>{css}</style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div>
                        <h1>IFC Audit Report</h1>
                        <div class="timestamp">File: {self.summary.get('file', 'Model')} | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div>
                        <span class="badge" style="background: var(--primary); color: white;">v0.2.1</span>
                    </div>
                </header>

                {summary_html}
                {inventory_html}
                {issues_html}

                <footer style="margin-top: 4rem; text-align: center; color: var(--text-dim); font-size: 0.8rem; border-top: 1px solid var(--border); padding-top: 2rem;">
                    Generated by <strong>IFC Audit</strong> for Blender + Bonsai.
                    <br>Logic based on AGR Digital Building.
                </footer>
            </div>
        </body>
        </html>
        """
        return full_html
