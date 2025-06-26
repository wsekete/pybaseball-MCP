"""
Artifact creator for baseball charts.
"""

from typing import Dict, Any, Optional
import uuid


def create_chart_artifact(chart_data: Dict[str, Any], compact: bool = False) -> Dict[str, Any]:
    """
    Create an artifact from chart data.
    
    Args:
        chart_data: Processed chart data from ChartProcessor
        compact: Whether to create a compact version for inline display
        
    Returns:
        Artifact dictionary for Claude
    """
    
    artifact_id = f"baseball_chart_{uuid.uuid4().hex[:8]}"
    
    if compact:
        content = _create_compact_artifact_content(chart_data)
        artifact_type = "text/html"
    else:
        content = _create_full_artifact_content(chart_data)
        artifact_type = "text/html"
    
    artifact = {
        "type": "create",
        "id": artifact_id,
        "title": chart_data.get('title', 'Baseball Chart'),
        "content": content,
        "artifact_type": artifact_type
    }
    
    return artifact


def _create_compact_artifact_content(chart_data: Dict[str, Any]) -> str:
    """Create compact HTML content for inline display."""
    
    # Extract summary metrics
    summary_data = _extract_summary_metrics(chart_data)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_data.get('title', 'Chart')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #ffffff;
            font-size: 14px;
        }}
        .chart-container {{
            max-width: 500px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            overflow: hidden;
            background: white;
            box-shadow: 0 3px 12px rgba(0,0,0,0.15);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 16px;
            font-weight: bold;
            font-size: 16px;
        }}
        .content {{
            padding: 16px;
        }}
        .chart-and-data {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }}
        .chart-image {{
            flex: 1.2;
            max-width: 250px;
        }}
        .chart-image img {{
            width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid #ddd;
        }}
        .summary-data {{
            flex: 1;
            font-size: 12px;
            line-height: 1.4;
        }}
        .metric {{
            margin-bottom: 6px;
            padding: 4px 8px;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }}
        .metric-label {{
            font-weight: bold;
            color: #495057;
        }}
        .metric-value {{
            color: #6c757d;
        }}
        @media (max-width: 400px) {{
            .chart-and-data {{
                flex-direction: column;
            }}
            .chart-image {{
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="header">
            {chart_data.get('title', 'Baseball Chart')}
        </div>
        <div class="content">
            <div class="chart-and-data">
                <div class="chart-image">
                    {"<img src='data:image/png;base64," + chart_data['image_data'] + "' alt='Chart'/>" if chart_data.get('image_data') else "<div style='padding: 20px; text-align: center; color: #6c757d;'>No chart available</div>"}
                </div>
                <div class="summary-data">
                    {_format_summary_metrics(summary_data)}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_content.strip()


def _create_full_artifact_content(chart_data: Dict[str, Any]) -> str:
    """Create full HTML content for detailed display."""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_data.get('title', 'Chart')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}
        .content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            padding: 24px;
        }}
        .chart-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        .chart-section h2 {{
            margin: 0 0 16px 0;
            color: #495057;
            font-size: 18px;
        }}
        .chart-image {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        .data-section {{
            background: #ffffff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }}
        .data-section h2 {{
            margin: 0 0 16px 0;
            color: #495057;
            font-size: 18px;
        }}
        .insights {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .insights li {{
            padding: 8px 12px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            font-size: 14px;
            line-height: 1.4;
        }}
        .insights li.category {{
            background: #e3f2fd;
            border-left-color: #1976d2;
            font-weight: bold;
        }}
        @media (max-width: 768px) {{
            .content {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{chart_data.get('title', 'Baseball Chart')}</h1>
        </div>
        <div class="content">
            <div class="chart-section">
                <h2>📊 Visualization</h2>
                {"<img src='data:image/png;base64," + chart_data['image_data'] + "' class='chart-image' alt='Chart'/>" if chart_data.get('image_data') else "<p>No chart data available</p>"}
            </div>
            <div class="data-section">
                <h2>📈 Analysis</h2>
                <ul class="insights">
                    {_format_insights_list(chart_data.get('insights', []))}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_content.strip()


def _extract_summary_metrics(chart_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract key metrics for compact display."""
    metrics = {}
    
    insights = chart_data.get('insights', [])
    
    for insight in insights:
        insight = insight.strip()
        
        # Extract total hits
        if 'Total Hits' in insight:
            total = insight.split(':')[-1].strip().replace('*', '')
            metrics['Total Hits'] = total
        
        # Extract hit type percentages
        elif insight.startswith('- ') and ':' in insight and '%' in insight:
            parts = insight.replace('- ', '').split(':')
            if len(parts) == 2:
                hit_type = parts[0].strip()
                count_pct = parts[1].strip()
                metrics[hit_type] = count_pct
        
        # Extract field distribution
        elif 'Field:' in insight and '%' in insight:
            parts = insight.replace('- ', '').split(':')
            if len(parts) == 2:
                field = parts[0].strip()
                count_pct = parts[1].strip()
                metrics[field] = count_pct
        
        # Extract exit velocity
        elif 'Average:' in insight and 'mph' in insight:
            avg_velo = insight.split(':')[-1].strip()
            metrics['Avg Exit Velocity'] = avg_velo
    
    return metrics


def _format_summary_metrics(metrics: Dict[str, str]) -> str:
    """Format metrics for compact display."""
    if not metrics:
        return "<div style='color: #6c757d; text-align: center;'>No summary data available</div>"
    
    formatted_metrics = []
    
    for label, value in metrics.items():
        formatted_metrics.append(f"""
            <div class="metric">
                <span class="metric-label">{label}:</span><br>
                <span class="metric-value">{value}</span>
            </div>
        """)
    
    return "".join(formatted_metrics)


def _format_insights_list(insights: list) -> str:
    """Format insights as HTML list items."""
    if not insights:
        return "<li>No insights available</li>"
    
    formatted_insights = []
    
    for insight in insights:
        insight = insight.strip()
        if insight.startswith(('📊', '🎯', '⚡')):
            # Category header
            clean_insight = insight.replace('**', '').replace('*', '')
            formatted_insights.append(f'<li class="category">{clean_insight}</li>')
        elif insight.startswith('- '):
            # Regular insight
            clean_insight = insight.replace('- ', '')
            formatted_insights.append(f'<li>{clean_insight}</li>')
        elif insight:
            formatted_insights.append(f'<li>{insight}</li>')
    
    return "".join(formatted_insights)


def create_chart_response_with_artifact(chart_data: Dict[str, Any], compact: bool = True) -> str:
    """
    Create a response that includes both artifact creation and summary text.
    
    Args:
        chart_data: Processed chart data
        compact: Whether to create compact version
        
    Returns:
        Formatted response string for Claude
    """
    
    # Create artifact
    artifact = create_chart_artifact(chart_data, compact=compact)
    
    # Create summary text
    summary_lines = [
        f"I've created a {'compact' if compact else 'detailed'} chart display for: **{chart_data.get('title', 'Chart')}**",
        "",
        "**Key Highlights:**"
    ]
    
    # Add key metrics to summary
    insights = chart_data.get('insights', [])
    for insight in insights[:3]:  # Show top 3 insights
        if insight.strip() and not insight.startswith(('📊', '🎯', '⚡')):
            clean_insight = insight.replace('- ', '').replace('**', '').replace('*', '')
            summary_lines.append(f"• {clean_insight}")
    
    if len(insights) > 3:
        summary_lines.append("• ... and more details in the chart above")
    
    summary_text = "\n".join(summary_lines)
    
    return {
        'artifact': artifact,
        'summary': summary_text
    }
