"""
MkDocs hook to automatically generate BOM reports and parts table.

This hook runs during the MkDocs build process to:
1. Parse all bom.yaml files
2. Generate a searchable parts table
3. Create BOM reports
4. Inject the parts table into the BOM index page
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def parse_bom_files(docs_dir: Path) -> tuple[List[Dict], Dict]:
    """Parse all BOM YAML files and return components and assemblies."""
    assembly_dir = docs_dir / "assembly"
    components = []
    assemblies = {}

    for bom_file in assembly_dir.glob("**/bom.yaml"):
        try:
            with open(bom_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'components' not in data:
                continue

            assembly_name = data.get('assembly', 'unknown')
            assembly_path = bom_file.relative_to(assembly_dir).parent

            assemblies[assembly_name] = {
                'description': data.get('description', ''),
                'path': str(assembly_path)
            }

            for component in data.get('components', []):
                component['assembly'] = assembly_name
                component['assembly_path'] = str(assembly_path)
                components.append(component)

        except Exception as e:
            print(f"Warning: Could not parse {bom_file}: {e}")

    return components, assemblies


def generate_parts_table_html(components: List[Dict]) -> str:
    """Generate an HTML table with searchable/filterable parts."""

    # Sort components by assembly and criticality
    sorted_components = sorted(
        components,
        key=lambda x: (
            x.get('assembly', ''),
            {'essential': 0, 'important': 1, 'optional': 2}.get(x.get('criticality', 'optional'), 3)
        )
    )

    # Generate unique values for filters
    assemblies = sorted(set(c.get('assembly', 'unknown') for c in components))
    statuses = sorted(set(c.get('status', 'unknown') for c in components))
    categories = sorted(set(c.get('category', 'unknown') for c in components))

    html = [
        '<div class="parts-table-container">',
        '  <div class="parts-filters" style="margin-bottom: 1em; padding: 1em; background: #f5f5f5; border-radius: 4px;">',
        '    <label style="margin-right: 1em;">',
        '      <strong>Search:</strong> ',
        '      <input type="text" id="partsSearch" placeholder="Search parts..." style="padding: 0.3em; width: 300px;">',
        '    </label>',
        '    <label style="margin-right: 1em;">',
        '      <strong>Assembly:</strong> ',
        '      <select id="assemblyFilter" style="padding: 0.3em;">',
        '        <option value="">All</option>'
    ]

    for assembly in assemblies:
        html.append(f'        <option value="{assembly}">{assembly.title()}</option>')

    html.extend([
        '      </select>',
        '    </label>',
        '    <label style="margin-right: 1em;">',
        '      <strong>Status:</strong> ',
        '      <select id="statusFilter" style="padding: 0.3em;">',
        '        <option value="">All</option>'
    ])

    for status in statuses:
        html.append(f'        <option value="{status}">{status.replace("_", " ").title()}</option>')

    html.extend([
        '      </select>',
        '    </label>',
        '    <label>',
        '      <strong>Category:</strong> ',
        '      <select id="categoryFilter" style="padding: 0.3em;">',
        '        <option value="">All</option>'
    ])

    for category in categories:
        html.append(f'        <option value="{category}">{category.replace("_", " ").title()}</option>')

    html.extend([
        '      </select>',
        '    </label>',
        '    <span id="partsCount" style="margin-left: 1em; font-weight: bold;"></span>',
        '  </div>',
        '',
        '  <table id="partsTable" class="parts-table" style="width: 100%; border-collapse: collapse;">',
        '    <thead>',
        '      <tr style="background: #2196F3; color: white;">',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(0)">ID ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(1)">Part # ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(2)">Description ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(3)">Assembly ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(4)">Category ↕</th>',
        '        <th style="padding: 0.75em; text-align: right; cursor: pointer;" onclick="sortTable(5)">Qty ↕</th>',
        '        <th style="padding: 0.75em; text-align: right; cursor: pointer;" onclick="sortTable(6)">Cost ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(7)">Status ↕</th>',
        '        <th style="padding: 0.75em; text-align: left; cursor: pointer;" onclick="sortTable(8)">Critical ↕</th>',
        '      </tr>',
        '    </thead>',
        '    <tbody>'
    ])

    # Add component rows
    for idx, component in enumerate(sorted_components):
        bg_color = '#f9f9f9' if idx % 2 == 0 else 'white'
        status_color = {
            'active': '#4CAF50',
            'pending': '#FF9800',
            'needs_specification': '#F44336'
        }.get(component.get('status', 'unknown'), '#9E9E9E')

        criticality_color = {
            'essential': '#F44336',
            'important': '#FF9800',
            'optional': '#2196F3'
        }.get(component.get('criticality', 'optional'), '#9E9E9E')

        html.append(f'      <tr style="background: {bg_color};" data-assembly="{component.get("assembly", "")}" data-status="{component.get("status", "")}" data-category="{component.get("category", "")}">')
        html.append(f'        <td style="padding: 0.5em; font-family: monospace; font-size: 0.9em;">{component.get("id", "N/A")}</td>')
        html.append(f'        <td style="padding: 0.5em; font-family: monospace; font-size: 0.9em;">{component.get("part_number", "N/A")}</td>')
        html.append(f'        <td style="padding: 0.5em;">{component.get("description", "N/A")}</td>')
        html.append(f'        <td style="padding: 0.5em;">{component.get("assembly", "N/A")}</td>')
        html.append(f'        <td style="padding: 0.5em;">{component.get("category", "N/A").replace("_", " ").title()}</td>')
        html.append(f'        <td style="padding: 0.5em; text-align: right;">{component.get("quantity", 1)}</td>')

        unit_cost = component.get('unit_cost', 0.0)
        currency = component.get('currency', 'EUR')
        html.append(f'        <td style="padding: 0.5em; text-align: right;">{currency} {unit_cost:.2f}</td>')

        status = component.get('status', 'unknown').replace('_', ' ').title()
        html.append(f'        <td style="padding: 0.5em;"><span style="background: {status_color}; color: white; padding: 0.2em 0.5em; border-radius: 3px; font-size: 0.85em;">{status}</span></td>')

        criticality = component.get('criticality', 'optional').title()
        html.append(f'        <td style="padding: 0.5em;"><span style="background: {criticality_color}; color: white; padding: 0.2em 0.5em; border-radius: 3px; font-size: 0.85em;">{criticality}</span></td>')
        html.append('      </tr>')

    html.extend([
        '    </tbody>',
        '  </table>',
        '</div>',
        '',
        '<script>',
        '  // Filter functionality',
        '  function filterTable() {',
        '    const searchTerm = document.getElementById("partsSearch").value.toLowerCase();',
        '    const assemblyFilter = document.getElementById("assemblyFilter").value;',
        '    const statusFilter = document.getElementById("statusFilter").value;',
        '    const categoryFilter = document.getElementById("categoryFilter").value;',
        '    const table = document.getElementById("partsTable");',
        '    const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");',
        '    let visibleCount = 0;',
        '',
        '    for (let row of rows) {',
        '      const text = row.textContent.toLowerCase();',
        '      const assembly = row.getAttribute("data-assembly");',
        '      const status = row.getAttribute("data-status");',
        '      const category = row.getAttribute("data-category");',
        '',
        '      const matchesSearch = text.includes(searchTerm);',
        '      const matchesAssembly = !assemblyFilter || assembly === assemblyFilter;',
        '      const matchesStatus = !statusFilter || status === statusFilter;',
        '      const matchesCategory = !categoryFilter || category === categoryFilter;',
        '',
        '      if (matchesSearch && matchesAssembly && matchesStatus && matchesCategory) {',
        '        row.style.display = "";',
        '        visibleCount++;',
        '      } else {',
        '        row.style.display = "none";',
        '      }',
        '    }',
        '',
        f'    document.getElementById("partsCount").textContent = `Showing ${{visibleCount}} of {len(components)} parts`;',
        '  }',
        '',
        '  // Add event listeners',
        '  document.getElementById("partsSearch").addEventListener("keyup", filterTable);',
        '  document.getElementById("assemblyFilter").addEventListener("change", filterTable);',
        '  document.getElementById("statusFilter").addEventListener("change", filterTable);',
        '  document.getElementById("categoryFilter").addEventListener("change", filterTable);',
        '',
        '  // Initialize count',
        f'  document.getElementById("partsCount").textContent = "Showing {len(components)} of {len(components)} parts";',
        '',
        '  // Simple table sorting',
        '  function sortTable(columnIndex) {',
        '    const table = document.getElementById("partsTable");',
        '    const tbody = table.getElementsByTagName("tbody")[0];',
        '    const rows = Array.from(tbody.getElementsByTagName("tr"));',
        '    const isNumeric = [5, 6].includes(columnIndex);',
        '',
        '    rows.sort((a, b) => {',
        '      const aText = a.getElementsByTagName("td")[columnIndex].textContent.trim();',
        '      const bText = b.getElementsByTagName("td")[columnIndex].textContent.trim();',
        '',
        '      if (isNumeric) {',
        '        return parseFloat(aText.replace(/[^0-9.-]/g, "")) - parseFloat(bText.replace(/[^0-9.-]/g, ""));',
        '      }',
        '      return aText.localeCompare(bText);',
        '    });',
        '',
        '    rows.forEach(row => tbody.appendChild(row));',
        '  }',
        '</script>'
    ])

    return '\n'.join(html)


def generate_cost_summary_section(components: List[Dict], assemblies: Dict) -> str:
    """Generate cost summary markdown section."""
    by_assembly = defaultdict(lambda: {'total': 0.0, 'count': 0})
    total_cost = 0.0

    for component in components:
        cost = component.get('unit_cost', 0.0) * component.get('quantity', 1)
        assembly = component.get('assembly', 'unknown')
        by_assembly[assembly]['total'] += cost
        by_assembly[assembly]['count'] += 1
        total_cost += cost

    lines = [
        '## 💰 Cost Summary\n',
        '| Assembly | Components | Total Cost |',
        '|----------|------------|------------|'
    ]

    for assembly in sorted(by_assembly.keys()):
        data = by_assembly[assembly]
        lines.append(f'| **{assembly.title()}** | {data["count"]} | €{data["total"]:.2f} |')

    lines.extend([
        f'| **TOTAL** | **{len(components)}** | **€{total_cost:.2f}** |',
        ''
    ])

    return '\n'.join(lines)


def on_page_markdown(markdown: str, page, config, files):
    """Hook called when processing markdown pages."""

    # Only process the BOM index page
    if page.file.src_path != 'bom/index.md':
        return markdown

    docs_dir = Path(config['docs_dir'])
    components, assemblies = parse_bom_files(docs_dir)

    if not components:
        return markdown

    # Generate dynamic content
    cost_summary = generate_cost_summary_section(components, assemblies)
    parts_table = generate_parts_table_html(components)

    # Inject into markdown
    # Add the dynamic parts table before the "## Assembly Overview" section
    if '## Assembly Overview' in markdown:
        parts_section = f'\n## 🔍 Searchable Parts Database\n\n{parts_table}\n\n'
        markdown = markdown.replace('## Assembly Overview', f'{parts_section}## Assembly Overview')

    # Add cost summary at the top after the initial description
    if '## BOM Structure' in markdown:
        markdown = markdown.replace('## BOM Structure', f'{cost_summary}## BOM Structure')

    return markdown
