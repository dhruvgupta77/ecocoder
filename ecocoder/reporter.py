import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()

class ReportGenerator:
    def generate_text_report(self, emissions_report, detail_level="basic"):
        """Generate a text-based report for CLI output"""
        report = []
        
        # Summary panel
        summary_table = Table(title="Carbon Emissions Summary", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Estimated Emissions", f"{emissions_report['total_emissions_kgco2e']:.6f} kgCO₂e")
        summary_table.add_row("Lines of Code", str(emissions_report['lines_of_code']))
        summary_table.add_row("Files Analyzed", str(emissions_report['analysis_result']['files_analyzed']))
        
        report.append(summary_table)
        
        # Issues found
        if detail_level in ["detailed", "comprehensive"]:
            issues = emissions_report['analysis_result']['issues_found']
            if issues:
                issues_table = Table(title="Sustainability Issues Found", box=box.ROUNDED)
                issues_table.add_column("File", style="cyan")
                issues_table.add_column("Line", style="yellow")
                issues_table.add_column("Issue", style="red")
                issues_table.add_column("Suggestion", style="green")
                
                for issue in issues[:10]:  # Show first 10 issues
                    issues_table.add_row(
                        issue['file'].split('/')[-1],  # Show only filename
                        str(issue.get('line', 'N/A')),
                        issue['issue'],
                        issue.get('suggestion', '')
                    )
                
                if len(issues) > 10:
                    issues_table.add_row("...", "...", f"{len(issues) - 10} more issues", "Use comprehensive mode to see all")
                
                report.append(issues_table)
            else:
                report.append(Panel("No significant sustainability issues found!", style="green"))
        
        # Emissions breakdown
        if detail_level == "comprehensive":
            breakdown_table = Table(title="Emissions Breakdown", box=box.ROUNDED)
            breakdown_table.add_column("Category", style="cyan")
            breakdown_table.add_column("Estimated Emissions (kgCO₂e)", style="green")
            
            for category, value in emissions_report['breakdown'].items():
                breakdown_table.add_row(category.replace('_', ' ').title(), f"{value:.6f}")
            
            report.append(breakdown_table)
        
        # Add comparison context
        context_panel = Panel(
            f"Estimated carbon emissions equivalent to:\n"
            f"• Charging {emissions_report['total_emissions_kgco2e'] * 1000:.1f} smartphones\n"
            f"• Driving {emissions_report['total_emissions_kgco2e'] * 5:.2f} km in a gasoline car",
            title="Emissions Context"
        )
        report.append(context_panel)
        
        # Add recommendations
        rec_panel = Panel(
            "Recommendations to reduce your code's carbon footprint:\n"
            "• Optimize algorithms and data structures\n"
            "• Reduce unnecessary computations\n"
            "• Implement caching for expensive operations\n"
            "• Use more efficient libraries and frameworks\n"
            "• Consider the environmental impact of third-party dependencies",
            title="Sustainability Recommendations"
        )
        report.append(rec_panel)
        
        # Render all elements
        for element in report:
            console.print(element)
        
        return ""
    
    def generate_json_report(self, emissions_report, detail_level="basic"):
        """Generate a JSON report"""
        # Filter data based on detail level
        report_data = {
            "total_emissions_kgco2e": emissions_report["total_emissions_kgco2e"],
            "lines_of_code": emissions_report["lines_of_code"],
            "files_analyzed": emissions_report["analysis_result"]["files_analyzed"],
        }
        
        if detail_level in ["detailed", "comprehensive"]:
            report_data["issues_found"] = emissions_report["analysis_result"]["issues_found"]
        
        if detail_level == "comprehensive":
            report_data["breakdown"] = emissions_report["breakdown"]
            report_data["language_breakdown"] = emissions_report["analysis_result"]["language_breakdown"]
        
        return json.dumps(report_data, indent=2)
    
    def generate_html_report(self, emissions_report, detail_level="basic"):
        """Generate an HTML report"""
        # Simplified HTML report for prototype
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EcoCoder Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2ecc71; }}
                .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 10px 0; }}
                .issue {{ background-color: #f8d7da; padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .metric {{ color: #27ae60; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>EcoCoder Sustainability Report</h1>
            
            <div class="card">
                <h2>Summary</h2>
                <p>Total Estimated Emissions: <span class="metric">{emissions_report['total_emissions_kgco2e']:.6f} kgCO₂e</span></p>
                <p>Lines of Code: <span class="metric">{emissions_report['lines_of_code']}</span></p>
                <p>Files Analyzed: <span class="metric">{emissions_report['analysis_result']['files_analyzed']}</span></p>
            </div>
        """
        
        if detail_level in ["detailed", "comprehensive"] and emissions_report['analysis_result']['issues_found']:
            html += """
            <div class="card">
                <h2>Issues Found</h2>
            """
            
            for issue in emissions_report['analysis_result']['issues_found']:
                html += f"""
                <div class="issue">
                    <p><strong>{issue['file']}:{issue.get('line', 'N/A')}</strong> - {issue['issue']}</p>
                    <p>{issue.get('suggestion', '')}</p>
                </div>
                """
            
            html += "</div>"
        
        html += """
            <div class="card">
                <h2>Recommendations</h2>
                <ul>
                    <li>Optimize algorithms and data structures</li>
                    <li>Reduce unnecessary computations</li>
                    <li>Implement caching for expensive operations</li>
                    <li>Use more efficient libraries and frameworks</li>
                    <li>Consider the environmental impact of third-party dependencies</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html