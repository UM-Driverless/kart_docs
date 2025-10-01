#!/bin/bash
# Generate BOM Reports
#
# This script runs the BOM aggregation script to generate cost summaries,
# supplier lists, and component status reports.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Generating BOM Reports..."
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv not found. Please install uv first."
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Run the aggregation script
uv run python scripts/aggregate_bom.py --output-dir reports/bom --format both

echo ""
echo "✅ Reports generated successfully!"
echo ""
echo "📊 Output files:"
echo "   - reports/bom/bom_complete_report.json (complete data)"
echo "   - reports/bom/bom_assembly_costs.csv (cost breakdown)"
echo "   - reports/bom/bom_all_components.csv (parts list)"
echo ""
echo "💡 Tip: Import CSV files into spreadsheet software for analysis"
