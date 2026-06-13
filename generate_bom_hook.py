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


# Status / criticality value → badge colour class (see docs/stylesheets/bom.css)
STATUS_BADGE = {
    'active': 'green',
    'planned': 'blue',
    'pending': 'amber',
    'legacy': 'grey',
    'needs_specification': 'red',
    'needs_replacement': 'red',
}
CRITICALITY_BADGE = {
    'essential': 'red',
    'important': 'amber',
    'optional': 'blue',
}


def generate_parts_table_html(components: List[Dict]) -> str:
    """Generate a themed, searchable/filterable HTML parts table.

    Styling lives in docs/stylesheets/bom.css so the table inherits the
    Material theme (and works in dark mode). This function emits class-based
    markup only — no inline styles.
    """

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

    def options(values: List[str]) -> str:
        return '\n'.join(
            f'        <option value="{v}">{v.replace("_", " ").title()}</option>'
            for v in values
        )

    html = [
        '<div class="parts-table-container">',
        '  <div class="parts-filters">',
        '    <label><strong>Search</strong>',
        '      <input type="text" id="partsSearch" placeholder="part number, name…">',
        '    </label>',
        '    <label><strong>Assembly</strong>',
        '      <select id="assemblyFilter"><option value="">All</option>',
        options(assemblies),
        '      </select></label>',
        '    <label><strong>Status</strong>',
        '      <select id="statusFilter"><option value="">All</option>',
        options(statuses),
        '      </select></label>',
        '    <label><strong>Category</strong>',
        '      <select id="categoryFilter"><option value="">All</option>',
        options(categories),
        '      </select></label>',
        '    <span id="partsCount"></span>',
        '  </div>',
        '',
        '  <table id="partsTable" class="parts-table">',
        '    <thead>',
        '      <tr>',
        '        <th onclick="sortTable(0)">ID ↕</th>',
        '        <th onclick="sortTable(1)">Part # ↕</th>',
        '        <th onclick="sortTable(2)">Description ↕</th>',
        '        <th onclick="sortTable(3)">Assembly ↕</th>',
        '        <th onclick="sortTable(4)">Category ↕</th>',
        '        <th class="num" onclick="sortTable(5)">Qty ↕</th>',
        '        <th class="num" onclick="sortTable(6)">Cost ↕</th>',
        '        <th onclick="sortTable(7)">Status ↕</th>',
        '        <th onclick="sortTable(8)">Critical ↕</th>',
        '      </tr>',
        '    </thead>',
        '    <tbody>',
    ]

    # Add component rows
    for component in sorted_components:
        status = component.get('status', 'unknown')
        criticality = component.get('criticality', 'optional')
        status_class = STATUS_BADGE.get(status, 'grey')
        crit_class = CRITICALITY_BADGE.get(criticality, 'grey')
        unit_cost = component.get('unit_cost', 0.0)
        currency = component.get('currency', 'EUR')

        html.extend([
            f'      <tr data-assembly="{component.get("assembly", "")}" data-status="{status}" data-category="{component.get("category", "")}">',
            f'        <td class="mono">{component.get("id", "—")}</td>',
            f'        <td class="mono">{component.get("part_number", "—")}</td>',
            f'        <td>{component.get("description", "—")}</td>',
            f'        <td>{component.get("assembly", "—")}</td>',
            f'        <td>{component.get("category", "—").replace("_", " ").title()}</td>',
            f'        <td class="num">{component.get("quantity", 1)}</td>',
            f'        <td class="num">{currency} {unit_cost:.2f}</td>',
            f'        <td><span class="bom-badge bom-badge--{status_class}">{status.replace("_", " ").title()}</span></td>',
            f'        <td><span class="bom-badge bom-badge--{crit_class}">{criticality.title()}</span></td>',
            '      </tr>',
        ])

    total = len(components)
    html.extend([
        '    </tbody>',
        '  </table>',
        '</div>',
        '',
        '<script>',
        '(function () {',
        '  const search = document.getElementById("partsSearch");',
        '  if (!search) return;',
        '  const table = document.getElementById("partsTable");',
        '  const rows = Array.from(table.tBodies[0].rows);',
        '  const count = document.getElementById("partsCount");',
        '  const filters = {',
        '    assembly: document.getElementById("assemblyFilter"),',
        '    status: document.getElementById("statusFilter"),',
        '    category: document.getElementById("categoryFilter"),',
        '  };',
        '',
        '  function apply() {',
        '    const term = search.value.toLowerCase();',
        '    let visible = 0;',
        '    for (const row of rows) {',
        '      const okText = row.textContent.toLowerCase().includes(term);',
        '      const okA = !filters.assembly.value || row.dataset.assembly === filters.assembly.value;',
        '      const okS = !filters.status.value || row.dataset.status === filters.status.value;',
        '      const okC = !filters.category.value || row.dataset.category === filters.category.value;',
        '      const show = okText && okA && okS && okC;',
        '      row.hidden = !show;',
        '      if (show) visible++;',
        '    }',
        f'    count.textContent = visible === {total} ? "{total} parts" : visible + " of {total} parts";',
        '  }',
        '',
        '  search.addEventListener("keyup", apply);',
        '  Object.values(filters).forEach(sel => sel.addEventListener("change", apply));',
        '',
        '  let sortCol = -1, sortAsc = true;',
        '  window.sortTable = function (col) {',
        '    const numeric = col === 5 || col === 6;',
        '    sortAsc = sortCol === col ? !sortAsc : true;',
        '    sortCol = col;',
        '    rows.sort((a, b) => {',
        '      let x = a.cells[col].textContent.trim();',
        '      let y = b.cells[col].textContent.trim();',
        '      if (numeric) {',
        '        x = parseFloat(x.replace(/[^0-9.-]/g, "")) || 0;',
        '        y = parseFloat(y.replace(/[^0-9.-]/g, "")) || 0;',
        '        return sortAsc ? x - y : y - x;',
        '      }',
        '      return sortAsc ? x.localeCompare(y) : y.localeCompare(x);',
        '    });',
        '    const body = table.tBodies[0];',
        '    rows.forEach(r => body.appendChild(r));',
        '  };',
        '',
        '  apply();',
        '})();',
        '</script>',
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
