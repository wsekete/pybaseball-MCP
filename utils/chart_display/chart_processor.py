"""
Chart processor for converting baseball chart outputs to displayable artifacts.
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
import pandas as pd


class ChartProcessor:
    """Processes baseball chart outputs and converts them to artifact-ready format."""
    
    def __init__(self):
        self.chart_patterns = {
            'spray_chart': r'# (.+) - (\d+) Spray Chart',
            'comparison_chart': r'# (\d+) (Batting|Pitching) Comparison'
        }
    
    def detect_chart_type(self, output: str) -> Optional[str]:
        """Detect if output contains a chart and what type."""
        for chart_type, pattern in self.chart_patterns.items():
            if re.search(pattern, output):
                return chart_type
        return None
    
    def extract_chart_data(self, output: str, chart_type: str) -> Dict[str, Any]:
        """Extract chart data and metadata from tool output."""
        data = {
            'type': chart_type,
            'title': '',
            'image_data': '',
            'tabular_data': [],
            'insights': [],
            'raw_output': output
        }
        
        # Extract title
        title_match = re.search(r'# (.+)', output)
        if title_match:
            data['title'] = title_match.group(1)
        
        # Extract base64 image if present
        img_match = re.search(r'!\[.*?\]\(data:image/png;base64,([^)]+)\)', output)
        if img_match:
            data['image_data'] = img_match.group(1)
        
        # Extract insights/text content
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('📊') or line.startswith('🎯') or line.startswith('⚡'):
                current_section = line
                data['insights'].append(line)
            elif line.startswith('-') and current_section:
                data['insights'].append(line)
            elif '|' in line and not line.startswith('#'):
                # Potential table data
                data['tabular_data'].append(line)
        
        return data
    
    def create_tabular_summary(self, chart_data: Dict[str, Any]) -> str:
        """Create tabular summary from chart insights."""
        if not chart_data['insights']:
            return ""
        
        # Convert insights to a simple table format
        table_rows = []
        current_category = ""
        
        for insight in chart_data['insights']:
            if insight.startswith(('📊', '🎯', '⚡')):
                current_category = insight.replace('**', '').replace('*', '')
                table_rows.append(f"| **{current_category}** | |")
                table_rows.append("| --- | --- |")
            elif insight.startswith('-'):
                # Parse the insight line
                clean_insight = insight.replace('-', '').strip()
                if ':' in clean_insight:
                    key, value = clean_insight.split(':', 1)
                    table_rows.append(f"| {key.strip()} | {value.strip()} |")
                else:
                    table_rows.append(f"| {clean_insight} | |")
        
        if table_rows:
            return "\n".join(table_rows)
        
        return ""
    
    def format_for_artifact(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format chart data for artifact creation."""
        
        # Create tabular summary
        table_summary = self.create_tabular_summary(chart_data)
        
        artifact_data = {
            'title': chart_data['title'],
            'type': 'text/html',
            'content': self._create_html_content(chart_data, table_summary)
        }
        
        return artifact_data
    
    def _create_html_content(self, chart_data: Dict[str, Any], table_summary: str) -> str:
        """Create HTML content combining chart and table."""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_data['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px;
        }}
        .chart-section {{
            flex: 2;
            min-width: 300px;
        }}
        .data-section {{
            flex: 1;
            min-width: 250px;
        }}
        .chart-image {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        @media (max-width: 768px) {{
            .content {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{chart_data['title']}</h1>
        </div>
        <div class="content">
            <div class="chart-section">
                <div class="section-title">📊 Visualization</div>
                {"<img src='data:image/png;base64," + chart_data['image_data'] + "' class='chart-image' alt='Chart'/>" if chart_data['image_data'] else "<p>No chart data available</p>"}
            </div>
            <div class="data-section">
                <div class="section-title">📈 Summary Data</div>
                {"<table>" + table_summary + "</table>" if table_summary else "<p>No summary data available</p>"}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content.strip()


def create_compact_chart_display(chart_data: Dict[str, Any]) -> str:
    """Create a compact display format for smaller charts."""
    
    # For spray charts and comparisons, create a simplified view
    if chart_data['type'] == 'spray_chart':
        return _create_compact_spray_display(chart_data)
    elif chart_data['type'] == 'comparison_chart':
        return _create_compact_comparison_display(chart_data)
    
    return chart_data['raw_output']


def _create_compact_spray_display(chart_data: Dict[str, Any]) -> str:
    """Create compact spray chart display."""
    
    # Extract key metrics for compact display
    metrics = []
    for insight in chart_data['insights']:
        if 'Total Hits' in insight:
            metrics.append(insight.replace('📊 **', '').replace('**', ''))
        elif 'Field Distribution' in insight:
            continue  # Skip header
        elif insight.startswith('- ') and ('Field:' in insight or '%' in insight):
            metrics.append(insight.replace('- ', ''))
    
    compact_html = f"""
<div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; max-width: 400px;">
    <h3 style="margin: 0 0 10px 0; color: #333;">{chart_data['title']}</h3>
    <div style="display: flex; gap: 10px;">
        <div style="flex: 1;">
            {"<img src='data:image/png;base64," + chart_data['image_data'] + "' style='width: 100%; height: auto; border-radius: 4px;'/>" if chart_data['image_data'] else ""}
        </div>
        <div style="flex: 1; font-size: 12px;">
            {"<br>".join(metrics)}
        </div>
    </div>
</div>
"""
    return compact_html


def _create_compact_comparison_display(chart_data: Dict[str, Any]) -> str:
    """Create compact comparison chart display."""
    
    compact_html = f"""
<div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; max-width: 600px;">
    <h3 style="margin: 0 0 10px 0; color: #333;">{chart_data['title']}</h3>
    {"<img src='data:image/png;base64," + chart_data['image_data'] + "' style='width: 100%; height: auto; border-radius: 4px;'/>" if chart_data['image_data'] else ""}
</div>
"""
    return compact_html
