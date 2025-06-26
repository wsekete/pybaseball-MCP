"""
Enhanced plotting and visualization tools for pybaseball MCP server.

These tools provide data visualization capabilities including spray charts,
statistical plots, and other baseball-specific visualizations with improved display.
"""

import logging
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
import io
from typing import Optional, List, Dict, Any, Tuple

from mcp.server.fastmcp import FastMCP, Context
import pybaseball as pyb
from utils.data_processing import DataProcessor
from utils.validation import Validator, ValidationError
from utils.chart_display import ChartProcessor, create_chart_artifact

logger = logging.getLogger(__name__)

# Set up matplotlib for non-interactive use
plt.style.use('default')
plt.rcParams['figure.figsize'] = (6, 4)  # Compact figure size
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10


def register_plotting_tools(mcp: FastMCP):
    """Register all plotting and visualization tools with the MCP server"""
    
    @mcp.tool()
    def create_spray_chart(
        player_name: str,
        season: int,
        game_type: str = "regular",
        chart_type: str = "standard",
        ctx: Context = None
    ) -> str:
        """
        Generate a spray chart for a player's hitting data.
        
        Args:
            player_name: Player's name (e.g., "Albert Pujols")
            season: Season year (e.g., 2012)
            game_type: "regular", "postseason", or "all"
            chart_type: "standard", "heat_map", or "overlay"
            
        Returns:
            Chart artifact with tabular data and visualization
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            clean_name = validator.validate_player_name(player_name)
            season = validator.validate_season(season)
            
            valid_game_types = ["regular", "postseason", "all"]
            if game_type not in valid_game_types:
                raise ValidationError(f"Invalid game_type. Valid options: {', '.join(valid_game_types)}")
            
            valid_chart_types = ["standard", "heat_map", "overlay"]
            if chart_type not in valid_chart_types:
                raise ValidationError(f"Invalid chart_type. Valid options: {', '.join(valid_chart_types)}")
            
            # Look up player ID
            player_df = pyb.playerid_lookup(clean_name, fuzzy=True)
            if player_df.empty:
                return f"❌ Player '{clean_name}' not found"
            
            player_info = player_df.iloc[0]
            player_id = player_info.get('key_mlbam')
            
            if not player_id:
                return f"❌ No MLB AM ID found for {clean_name} (required for Statcast data)"
            
            # Get Statcast data for the player
            start_date = f"{season}-03-01"
            end_date = f"{season}-11-30"
            
            statcast_df = pyb.statcast_batter(
                start_dt=start_date,
                end_dt=end_date,
                player_id=player_id
            )
            
            if statcast_df.empty:
                return f"❌ No Statcast data found for {clean_name} in {season}"
            
            # Filter for hits only (events that result in batted balls in play)
            hit_events = ['single', 'double', 'triple', 'home_run']
            hits_df = statcast_df[statcast_df['events'].isin(hit_events)].copy()
            
            if hits_df.empty:
                return f"❌ No hit data found for {clean_name} in {season}"
            
            # Create spray chart - compact version
            fig, ax = plt.subplots(figsize=(5, 4))
            
            # Draw basic field outline
            _draw_field_outline(ax)
            
            # Plot hits based on chart type
            if chart_type == "standard":
                _plot_standard_spray_chart(ax, hits_df)
            elif chart_type == "heat_map":
                _plot_heatmap_spray_chart(ax, hits_df)
            elif chart_type == "overlay":
                _plot_overlay_spray_chart(ax, hits_df)
            
            # Set up the plot
            ax.set_xlim(-200, 200)
            ax.set_ylim(-30, 350)
            ax.set_aspect('equal')
            ax.set_title(f"{clean_name} - {season} Spray Chart", fontsize=12, fontweight='bold')
            
            # Add legend but make it compact
            if chart_type in ["standard", "overlay"]:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            
            # Convert to base64 - optimized for display
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close()
            
            img_base64 = data_processor.encode_image_to_base64(img_buffer)
            
            # Calculate insights in structured format
            insights = _calculate_spray_insights_structured(hits_df, clean_name, season)
            
            # Process chart data for artifact creation
            chart_processor = ChartProcessor()
            chart_data = {
                'type': 'spray_chart',
                'title': f"{clean_name} - {season} Spray Chart",
                'image_data': img_base64,
                'insights': insights,
                'tabular_data': _create_spray_table_data(hits_df)
            }
            
            # Create artifact
            artifact_data = create_chart_artifact(chart_data, compact=True)
            
            return f"CHART_ARTIFACT:{artifact_data}"
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in create_spray_chart: {e}")
            return f"❌ Error creating spray chart: {e}"

    @mcp.tool()
    def create_stat_comparison_chart(
        players: List[str],
        season: int,
        stat_type: str = "batting",
        metrics: List[str] = None,
        ctx: Context = None
    ) -> str:
        """
        Create a comparison chart for multiple players' statistics.
        
        Args:
            players: List of player names to compare
            season: Season year
            stat_type: "batting" or "pitching"
            metrics: List of specific metrics to compare
            
        Returns:
            Chart artifact with comparison data and visualization
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            if not players or len(players) < 2:
                raise ValidationError("Need at least 2 players for comparison")
            
            if len(players) > 4:  # Reduced for compact display
                raise ValidationError("Maximum 4 players allowed for compact comparison")
            
            season = validator.validate_season(season)
            
            valid_stat_types = ["batting", "pitching"]
            if stat_type not in valid_stat_types:
                raise ValidationError(f"Invalid stat_type. Valid options: {', '.join(valid_stat_types)}")
            
            # Set default metrics if not provided - compact set
            if metrics is None:
                if stat_type == "batting":
                    metrics = ["AVG", "OBP", "SLG", "HR"]
                else:
                    metrics = ["ERA", "WHIP", "K/9", "WAR"]
            
            # Limit metrics for compact display
            metrics = metrics[:4]
            
            # Get stats for all players
            player_stats = []
            
            for player_name in players:
                clean_name = validator.validate_player_name(player_name)
                
                # Get player stats
                if stat_type == "batting":
                    stats_df = pyb.batting_stats(season, season, qual=1)
                else:
                    stats_df = pyb.pitching_stats(season, season, qual=1)
                
                # Find player in stats
                player_row = stats_df[stats_df['Name'].str.contains(clean_name, case=False, na=False)]
                
                if not player_row.empty:
                    player_stats.append({
                        'name': clean_name,
                        'data': player_row.iloc[0]
                    })
            
            if len(player_stats) < 2:
                return f"❌ Could not find sufficient stats for comparison in {season}"
            
            # Create comparison chart - compact version
            fig, axes = plt.subplots(1, len(metrics), figsize=(2.5*len(metrics), 3.5))
            if len(metrics) == 1:
                axes = [axes]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(player_stats)))
            
            for i, metric in enumerate(metrics):
                ax = axes[i]
                
                values = []
                names = []
                
                for player_stat in player_stats:
                    if metric in player_stat['data'].index:
                        values.append(player_stat['data'][metric])
                        # Shorten names for compact display
                        name_parts = player_stat['name'].split()
                        short_name = f"{name_parts[0][0]}. {name_parts[-1]}" if len(name_parts) > 1 else player_stat['name']
                        names.append(short_name)
                
                if values:
                    bars = ax.bar(names, values, color=colors[:len(names)])
                    ax.set_title(f"{metric}", fontweight='bold', fontsize=10)
                    ax.tick_params(axis='x', rotation=45, labelsize=8)
                    ax.tick_params(axis='y', labelsize=8)
                    
                    # Add value labels on bars - smaller font
                    for bar, value in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{value:.2f}' if isinstance(value, float) else str(value),
                               ha='center', va='bottom', fontsize=7)
            
            plt.suptitle(f"{season} {stat_type.title()} Comparison", fontsize=12, fontweight='bold')
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=120, bbox_inches='tight',
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close()
            
            img_base64 = data_processor.encode_image_to_base64(img_buffer)
            
            # Create structured insights
            insights = _create_comparison_insights_structured(player_stats, metrics, stat_type)
            
            # Process chart data for artifact creation
            chart_data = {
                'type': 'comparison_chart',
                'title': f"{season} {stat_type.title()} Comparison",
                'image_data': img_base64,
                'insights': insights,
                'tabular_data': _create_comparison_table_data(player_stats, metrics)
            }
            
            # Create artifact
            artifact_data = create_chart_artifact(chart_data, compact=True)
            
            return f"CHART_ARTIFACT:{artifact_data}"
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in create_stat_comparison_chart: {e}")
            return f"❌ Error creating comparison chart: {e}"

    logger.info("Enhanced plotting tools registered successfully")


def _draw_field_outline(ax):
    """Draw simplified baseball field outline for compact display"""
    # Infield diamond - simplified
    diamond = patches.Polygon([(0, 0), (60, 60), (0, 120), (-60, 60)], 
                             fill=False, edgecolor='black', linewidth=1.5)
    ax.add_patch(diamond)
    
    # Pitcher's mound
    mound = patches.Circle((0, 40), 6, fill=False, edgecolor='black', linewidth=1)
    ax.add_patch(mound)
    
    # Foul lines
    ax.plot([-300, 0], [300, 0], 'k-', linewidth=1, alpha=0.7)  # Left foul line
    ax.plot([300, 0], [300, 0], 'k-', linewidth=1, alpha=0.7)   # Right foul line
    
    # Outfield wall (approximate) - simplified
    angles = np.linspace(-np.pi/4, np.pi/4, 50)
    wall_x = 250 * np.sin(angles)
    wall_y = 250 * np.cos(angles)
    ax.plot(wall_x, wall_y, 'k-', linewidth=1.5)


def _plot_standard_spray_chart(ax, hits_df):
    """Plot standard spray chart with different colors for hit types"""
    colors = {
        'single': '#3498db',
        'double': '#2ecc71', 
        'triple': '#f39c12',
        'home_run': '#e74c3c'
    }
    
    for event_type, color in colors.items():
        event_hits = hits_df[hits_df['events'] == event_type]
        if not event_hits.empty:
            ax.scatter(event_hits['hc_x'] - 125.42,  # Adjust for coordinate system
                      event_hits['hc_y'] - 198.27,   # Adjust for coordinate system
                      c=color, alpha=0.7, s=30, label=event_type.title(), edgecolors='white', linewidth=0.5)


def _plot_heatmap_spray_chart(ax, hits_df):
    """Plot heatmap style spray chart"""
    x = hits_df['hc_x'] - 125.42
    y = hits_df['hc_y'] - 198.27
    
    # Create heatmap with fewer bins for clarity
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=20)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                   cmap='YlOrRd', alpha=0.8)


def _plot_overlay_spray_chart(ax, hits_df):
    """Plot overlay combining scatter and heatmap"""
    # First draw simplified heatmap
    _plot_heatmap_spray_chart(ax, hits_df)
    
    # Then overlay home runs
    hr_hits = hits_df[hits_df['events'] == 'home_run']
    if not hr_hits.empty:
        ax.scatter(hr_hits['hc_x'] - 125.42,
                  hr_hits['hc_y'] - 198.27,
                  c='red', s=60, alpha=0.9, 
                  marker='*', label='Home Runs', edgecolors='white', linewidth=1)


def _calculate_spray_insights_structured(hits_df, player_name, season):
    """Calculate insights from spray chart data in structured format for artifacts"""
    insights = []
    
    # Basic hit counts
    hit_counts = hits_df['events'].value_counts()
    total_hits = len(hits_df)
    
    insights.append(f"📊 **Total Hits Tracked: {total_hits}**")
    
    for hit_type, count in hit_counts.items():
        percentage = (count / total_hits) * 100
        insights.append(f"- {hit_type.title()}: {count} ({percentage:.1f}%)")
    
    # Field direction analysis
    if 'hc_x' in hits_df.columns:
        center_x = 125.42  # Home plate x-coordinate
        
        # Determine field direction with adjusted thresholds
        left_field = hits_df[hits_df['hc_x'] > center_x + 15]
        center_field = hits_df[abs(hits_df['hc_x'] - center_x) <= 15]
        right_field = hits_df[hits_df['hc_x'] < center_x - 15]
        
        insights.append("🎯 **Field Distribution:**")
        insights.append(f"- Left Field: {len(left_field)} ({len(left_field)/total_hits*100:.1f}%)")
        insights.append(f"- Center Field: {len(center_field)} ({len(center_field)/total_hits*100:.1f}%)")
        insights.append(f"- Right Field: {len(right_field)} ({len(right_field)/total_hits*100:.1f}%)")
    
    # Exit velocity analysis (if available)
    if 'launch_speed' in hits_df.columns and not hits_df['launch_speed'].isna().all():
        avg_exit_velo = hits_df['launch_speed'].mean()
        max_exit_velo = hits_df['launch_speed'].max()
        
        insights.append("⚡ **Exit Velocity:**")
        insights.append(f"- Average: {avg_exit_velo:.1f} mph")
        insights.append(f"- Maximum: {max_exit_velo:.1f} mph")
    
    return insights


def _create_spray_table_data(hits_df):
    """Create structured table data for spray chart"""
    hit_counts = hits_df['events'].value_counts()
    total_hits = len(hits_df)
    
    table_data = []
    table_data.append("| Hit Type | Count | Percentage |")
    table_data.append("| --- | --- | --- |")
    
    for hit_type, count in hit_counts.items():
        percentage = (count / total_hits) * 100
        table_data.append(f"| {hit_type.title()} | {count} | {percentage:.1f}% |")
    
    table_data.append(f"| **Total** | **{total_hits}** | **100.0%** |")
    
    return table_data


def _create_comparison_insights_structured(player_stats, metrics, stat_type):
    """Create structured insights for comparison chart"""
    insights = []
    
    insights.append(f"📊 **{stat_type.title()} Comparison Summary**")
    insights.append(f"- Players compared: {len(player_stats)}")
    insights.append(f"- Metrics analyzed: {', '.join(metrics)}")
    
    # Find leaders for each metric
    insights.append("🏆 **Metric Leaders:**")
    
    for metric in metrics:
        values = []
        names = []
        
        for player_stat in player_stats:
            if metric in player_stat['data'].index:
                values.append(player_stat['data'][metric])
                names.append(player_stat['name'])
        
        if values:
            # Determine if higher is better
            if stat_type == "batting" or metric in ['K/9', 'WAR', 'K%']:
                best_idx = np.argmax(values)
                best_label = "highest"
            else:  # For pitching stats like ERA, WHIP
                best_idx = np.argmin(values)
                best_label = "lowest"
            
            insights.append(f"- {metric} ({best_label}): {names[best_idx]} ({values[best_idx]})")
    
    return insights


def _create_comparison_table_data(player_stats, metrics):
    """Create structured table data for comparison chart"""
    table_data = []
    
    # Create header
    header = ["| Player |"] + [f" {metric} |" for metric in metrics]
    table_data.append("".join(header))
    
    # Create separator
    separator = ["| --- |"] + [" --- |" for _ in metrics]
    table_data.append("".join(separator))
    
    # Create data rows
    for player_stat in player_stats:
        row = [f"| {player_stat['name']} |"]
        
        for metric in metrics:
            if metric in player_stat['data'].index:
                value = player_stat['data'][metric]
                if isinstance(value, float):
                    formatted_value = f" {value:.3f} |"
                else:
                    formatted_value = f" {value} |"
                row.append(formatted_value)
            else:
                row.append(" N/A |")
        
        table_data.append("".join(row))
    
    return table_data


logger.info("Enhanced plotting tools module loaded")
