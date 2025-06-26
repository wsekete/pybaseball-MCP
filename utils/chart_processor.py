"""
Chart response processor for converting pybaseball charts to Claude artifacts.
"""

import json
import re
from typing import Dict, Any, Optional


def detect_and_process_chart(response: str) -> Optional[Dict[str, Any]]:
    """
    Detect if a response contains chart data and process it for Claude.
    
    Args:
        response: The tool response string
        
    Returns:
        Dictionary with processed chart data or None if no chart detected
    """
    
    # Look for chart artifact markers
    if "CHART_ARTIFACT:" in response:
        try:
            # Extract the artifact data
            artifact_start = response.find("CHART_ARTIFACT:") + len("CHART_ARTIFACT:")
            artifact_data_str = response[artifact_start:].strip()
            
            # Parse the artifact data (safely, since we control the format)
            artifact_data = eval(artifact_data_str)
            
            return {
                "has_chart": True,
                "artifact": artifact_data,
                "chart_type": artifact_data.get("title", "Baseball Chart")
            }
            
        except Exception as e:
            print(f"Error processing chart artifact: {e}")
            return None
    
    # Look for traditional chart patterns (fallback)
    chart_patterns = [
        r'# (.+) - (\d+) Spray Chart',
        r'# (\d+) (Batting|Pitching) Comparison',
        r'!\[.*?\]\(data:image/png;base64,([^)]+)\)'
    ]
    
    for pattern in chart_patterns:
        if re.search(pattern, response):
            return {
                "has_chart": True,
                "needs_processing": True,
                "raw_response": response
            }
    
    return None


def create_inline_chart_display(chart_info: Dict[str, Any]) -> str:
    """
    Create an inline chart display that Claude can render.
    
    Args:
        chart_info: Processed chart information
        
    Returns:
        Formatted response for Claude
    """
    
    if chart_info.get("artifact"):
        artifact = chart_info["artifact"]
        
        # Create a response that tells Claude to create an artifact
        response = f"""I've created a baseball chart: **{artifact.get('title', 'Chart')}**

This chart includes both visual and tabular data for comprehensive analysis. The chart displays:

"""
        
        # Add any summary information if available
        if "content" in artifact and "summary-data" in artifact["content"]:
            response += "Key metrics are shown alongside the visualization for easy reference.\n\n"
        
        response += f"[Chart Type: {chart_info['chart_type']}]"
        
        return response
    
    return chart_info.get("raw_response", "Chart data processed")


def should_use_compact_display(response: str) -> bool:
    """
    Determine if we should use compact display for this chart.
    
    Args:
        response: Tool response string
        
    Returns:
        True if compact display should be used
    """
    
    # Use compact display for most cases to ensure inline visibility
    compact_keywords = [
        "spray chart",
        "comparison",
        "inline",
        "compact"
    ]
    
    response_lower = response.lower()
    return any(keyword in response_lower for keyword in compact_keywords)


def extract_chart_summary(response: str) -> Dict[str, Any]:
    """
    Extract summary information from chart response.
    
    Args:
        response: Tool response string
        
    Returns:
        Dictionary with summary information
    """
    
    summary = {
        "title": "",
        "key_metrics": [],
        "insights": []
    }
    
    # Extract title
    title_match = re.search(r'# (.+)', response)
    if title_match:
        summary["title"] = title_match.group(1)
    
    # Extract key metrics
    metric_pattern = r'- (.+): (.+)'
    metrics = re.findall(metric_pattern, response)
    summary["key_metrics"] = [f"{metric}: {value}" for metric, value in metrics[:5]]
    
    # Extract insights sections
    insight_sections = re.findall(r'(📊|🎯|⚡) \*\*(.+?)\*\*', response)
    summary["insights"] = [section[1] for section in insight_sections]
    
    return summary
