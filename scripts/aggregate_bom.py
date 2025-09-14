#!/usr/bin/env python3
"""
BOM Aggregation Script for Kart Documentation

This script traverses the assembly folder structure, reads all BOM YAML files,
and generates comprehensive reports including cost summaries, supplier lists,
and component status reports.

Usage:
    python scripts/aggregate_bom.py [--output-dir reports] [--format json|csv|html]
"""

import os
import yaml
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

class BOMProcessor:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.assemblies_dir = self.docs_dir / "assembly"
        self.components = []
        self.assemblies = {}

    def load_bom_files(self) -> None:
        """Load all BOM YAML files from the assemblies directory."""
        print(f"Loading BOM files from: {self.assemblies_dir}")

        for bom_file in self.assemblies_dir.rglob("bom.yaml"):
            try:
                with open(bom_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                assembly_path = bom_file.relative_to(self.docs_dir / "assembly").parent
                assembly_name = data.get('assembly', str(assembly_path))

                print(f"  - Loaded: {assembly_name} ({bom_file.relative_to(self.docs_dir)})")

                self.assemblies[assembly_name] = {
                    'data': data,
                    'path': assembly_path,
                    'file': bom_file
                }

                # Process components
                for component in data.get('components', []):
                    component['assembly'] = assembly_name
                    component['assembly_path'] = str(assembly_path)
                    self.components.append(component)

            except Exception as e:
                print(f"  ✗ Error loading {bom_file}: {e}")

    def generate_cost_summary(self) -> Dict[str, Any]:
        """Generate cost summary by assembly and overall."""
        summary = {
            'by_assembly': defaultdict(lambda: {'total': 0.0, 'count': 0, 'components': []}),
            'by_status': defaultdict(lambda: {'total': 0.0, 'count': 0}),
            'by_criticality': defaultdict(lambda: {'total': 0.0, 'count': 0}),
            'total_project_cost': 0.0,
            'total_components': len(self.components),
            'currency': 'EUR'
        }

        for component in self.components:
            assembly = component['assembly']
            cost = float(component.get('unit_cost', 0.0))
            quantity = int(component.get('quantity', 1))
            total_cost = cost * quantity
            status = component.get('status', 'unknown')
            criticality = component.get('criticality', 'unknown')

            # By assembly
            summary['by_assembly'][assembly]['total'] += total_cost
            summary['by_assembly'][assembly]['count'] += quantity
            summary['by_assembly'][assembly]['components'].append({
                'id': component.get('id', 'unknown'),
                'description': component.get('description', 'No description'),
                'unit_cost': cost,
                'quantity': quantity,
                'total_cost': total_cost
            })

            # By status
            summary['by_status'][status]['total'] += total_cost
            summary['by_status'][status]['count'] += quantity

            # By criticality
            summary['by_criticality'][criticality]['total'] += total_cost
            summary['by_criticality'][criticality]['count'] += quantity

            # Overall total
            summary['total_project_cost'] += total_cost

        return summary

    def generate_supplier_list(self) -> Dict[str, List[Dict]]:
        """Generate comprehensive supplier information."""
        suppliers = defaultdict(lambda: {'components': [], 'verified_count': 0, 'total_components': 0})

        for component in self.components:
            for supplier in component.get('suppliers', []):
                supplier_name = supplier.get('name', 'Unknown Supplier')
                suppliers[supplier_name]['total_components'] += 1

                if supplier.get('verified', False):
                    suppliers[supplier_name]['verified_count'] += 1

                suppliers[supplier_name]['components'].append({
                    'component_id': component.get('id'),
                    'part_number': component.get('part_number'),
                    'description': component.get('description'),
                    'assembly': component.get('assembly'),
                    'url': supplier.get('url'),
                    'verified': supplier.get('verified', False),
                    'notes': supplier.get('notes')
                })

        return dict(suppliers)

    def generate_status_report(self) -> Dict[str, List[Dict]]:
        """Generate component status report."""
        status_groups = defaultdict(list)

        for component in self.components:
            status = component.get('status', 'unknown')
            status_groups[status].append({
                'id': component.get('id'),
                'part_number': component.get('part_number'),
                'description': component.get('description'),
                'assembly': component.get('assembly'),
                'unit_cost': component.get('unit_cost'),
                'quantity': component.get('quantity'),
                'criticality': component.get('criticality'),
                'notes': component.get('notes')
            })

        return dict(status_groups)

    def export_json(self, output_dir: Path) -> None:
        """Export all reports as JSON files."""
        reports = {
            'cost_summary': self.generate_cost_summary(),
            'supplier_list': self.generate_supplier_list(),
            'status_report': self.generate_status_report(),
            'all_components': self.components,
            'assemblies': self.assemblies,
            'generated_at': datetime.now().isoformat()
        }

        output_file = output_dir / 'bom_complete_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, default=str)

        print(f"✓ JSON report saved: {output_file}")

    def export_csv_summary(self, output_dir: Path) -> None:
        """Export cost summary as CSV."""
        cost_summary = self.generate_cost_summary()

        # Assembly summary CSV
        assembly_file = output_dir / 'bom_assembly_costs.csv'
        with open(assembly_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Assembly', 'Total Cost (EUR)', 'Component Count', 'Average Cost'])

            for assembly, data in cost_summary['by_assembly'].items():
                avg_cost = data['total'] / data['count'] if data['count'] > 0 else 0
                writer.writerow([assembly, f"{data['total']:.2f}", data['count'], f"{avg_cost:.2f}"])

        # All components CSV
        components_file = output_dir / 'bom_all_components.csv'
        with open(components_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'part_number', 'description', 'assembly', 'quantity',
                'unit_cost', 'currency', 'status', 'criticality'
            ])
            writer.writeheader()

            for component in self.components:
                writer.writerow({
                    'id': component.get('id', ''),
                    'part_number': component.get('part_number', ''),
                    'description': component.get('description', ''),
                    'assembly': component.get('assembly', ''),
                    'quantity': component.get('quantity', ''),
                    'unit_cost': component.get('unit_cost', ''),
                    'currency': component.get('currency', 'EUR'),
                    'status': component.get('status', ''),
                    'criticality': component.get('criticality', '')
                })

        print(f"✓ CSV reports saved: {assembly_file}, {components_file}")

    def print_summary(self) -> None:
        """Print a summary to console."""
        cost_summary = self.generate_cost_summary()
        suppliers = self.generate_supplier_list()

        print("\n" + "="*50)
        print("KART BOM SUMMARY")
        print("="*50)

        print(f"Total Components: {cost_summary['total_components']}")
        print(f"Total Project Cost: €{cost_summary['total_project_cost']:.2f}")
        print(f"Assemblies: {len(self.assemblies)}")
        print(f"Suppliers: {len(suppliers)}")

        print(f"\nCost by Assembly:")
        for assembly, data in sorted(cost_summary['by_assembly'].items()):
            print(f"  {assembly:20} €{data['total']:8.2f} ({data['count']:2d} components)")

        print(f"\nComponents by Status:")
        for status, data in cost_summary['by_status'].items():
            print(f"  {status:15} €{data['total']:8.2f} ({data['count']:2d} components)")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Aggregate BOM data from YAML files')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--format', choices=['json', 'csv', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--docs-dir', default='docs', help='Documentation directory')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Process BOM data
    processor = BOMProcessor(args.docs_dir)
    processor.load_bom_files()

    if not processor.components:
        print("No components found. Check that BOM YAML files exist in docs/assembly/")
        return

    # Generate reports
    if args.format in ['json', 'both']:
        processor.export_json(output_dir)

    if args.format in ['csv', 'both']:
        processor.export_csv_summary(output_dir)

    # Print summary
    processor.print_summary()

if __name__ == '__main__':
    main()