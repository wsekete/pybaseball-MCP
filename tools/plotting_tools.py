"""
Plotting and visualization tools for pybaseball MCP server.

These tools provide data visualization capabilities including spray charts,
statistical plots, and other baseball-specific visualizations.
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

logger = logging.getLogger(__name__)

# Set up matplotlib for non-interactive use
plt.style.use('default')
plt.rcParams['figure.figsize'] = (8, 6)  # Smaller figure size
plt.rcParams['font.size'] = 8  # Smaller font to fit better


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
            Base64-encoded spray chart image with additional insights
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
            
            # Create spray chart
            fig, ax = plt.subplots(figsize=(8, 6))  # Smaller, more compact chart
            
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
            ax.set_xlim(-250, 250)
            ax.set_ylim(-50, 450)
            ax.set_aspect('equal')
            ax.set_title(f"{clean_name} - {season} Spray Chart ({chart_type.title()})", 
                        fontsize=16, fontweight='bold')
            ax.set_xlabel('Distance from Home Plate (feet)')
            ax.set_ylabel('Distance from Home Plate (feet)')
            
            # Add legend
            _add_spray_chart_legend(ax, chart_type)
            
            # Convert to base64 - optimized for smaller file size
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close()
            
            img_base64 = data_processor.encode_image_to_base64(img_buffer)
            
            # Calculate additional insights
            insights = _calculate_spray_insights(hits_df, clean_name, season)
            
            # Format response
            response = f"""# {clean_name} - {season} Spray Chart

![Spray Chart]({img_base64})

{insights}
"""
            
            return response
            
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
            Base64-encoded comparison chart with analysis
        """
        try:
            # Get app context
            validator = ctx.request_context.lifespan_context.validator
            data_processor = ctx.request_context.lifespan_context.data_processor
            
            # Validate inputs
            if not players or len(players) < 2:
                raise ValidationError("Need at least 2 players for comparison")
            
            if len(players) > 6:
                raise ValidationError("Maximum 6 players allowed for comparison")
            
            season = validator.validate_season(season)
            
            valid_stat_types = ["batting", "pitching"]
            if stat_type not in valid_stat_types:
                raise ValidationError(f"Invalid stat_type. Valid options: {', '.join(valid_stat_types)}")
            
            # Set default metrics if not provided
            if metrics is None:
                if stat_type == "batting":
                    metrics = ["AVG", "OBP", "SLG", "HR", "RBI"]
                else:
                    metrics = ["ERA", "WHIP", "K/9", "BB/9", "WAR"]
            
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
            
            # Create comparison chart - smaller size
            fig, axes = plt.subplots(1, len(metrics), figsize=(3*len(metrics), 4))
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
                        names.append(player_stat['name'])
                
                if values:
                    bars = ax.bar(names, values, color=colors[:len(names)])
                    ax.set_title(f"{metric}", fontweight='bold')
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{value:.3f}' if isinstance(value, float) else str(value),
                               ha='center', va='bottom')
            
            plt.suptitle(f"{season} {stat_type.title()} Comparison", fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Convert to base64 - optimized for smaller file size
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight',
                       facecolor='white', edgecolor='none', pad_inches=0.1)
            plt.close()
            
            img_base64 = data_processor.encode_image_to_base64(img_buffer)
            
            # Create comparison summary
            summary = _create_comparison_summary(player_stats, metrics, stat_type)
            
            response = f"""# {season} {stat_type.title()} Comparison

![Comparison Chart]({img_base64})

{summary}
"""
            
            return response
            
        except ValidationError as e:
            return f"❌ Validation Error: {e}"
        except Exception as e:
            logger.error(f"Error in create_stat_comparison_chart: {e}")
            return f"❌ Error creating comparison chart: {e}"

    logger.info("Plotting tools registered successfully")


def _draw_field_outline(ax):
    """Draw basic baseball field outline"""
    # Infield diamond
    diamond = patches.Polygon([(0, 0), (90, 90), (0, 180), (-90, 90)], 
                             fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(diamond)
    
    # Pitcher's mound
    mound = patches.Circle((0, 60.5), 9, fill=False, edgecolor='black')
    ax.add_patch(mound)
    
    # Foul lines
    ax.plot([-400, 0], [400, 0], 'k-', linewidth=1)  # Left foul line
    ax.plot([400, 0], [400, 0], 'k-', linewidth=1)   # Right foul line
    
    # Outfield wall (approximate)
    angles = np.linspace(-np.pi/4, np.pi/4, 100)
    wall_x = 330 * np.sin(angles)
    wall_y = 330 * np.cos(angles)
    ax.plot(wall_x, wall_y, 'k-', linewidth=2)


def _plot_standard_spray_chart(ax, hits_df):
    """Plot standard spray chart with different colors for hit types"""
    colors = {
        'single': 'blue',
        'double': 'green', 
        'triple': 'orange',
        'home_run': 'red'
    }
    
    for event_type, color in colors.items():
        event_hits = hits_df[hits_df['events'] == event_type]
        if not event_hits.empty:
            ax.scatter(event_hits['hc_x'] - 125.42,  # Adjust for coordinate system
                      event_hits['hc_y'] - 198.27,   # Adjust for coordinate system
                      c=color, alpha=0.6, s=50, label=event_type.title())


def _plot_heatmap_spray_chart(ax, hits_df):
    """Plot heatmap style spray chart"""
    x = hits_df['hc_x'] - 125.42
    y = hits_df['hc_y'] - 198.27
    
    # Create heatmap
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=30)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                   cmap='YlOrRd', alpha=0.7)
    plt.colorbar(im, ax=ax, label='Hit Frequency')


def _plot_overlay_spray_chart(ax, hits_df):
    """Plot overlay combining scatter and heatmap"""
    # First draw heatmap
    _plot_heatmap_spray_chart(ax, hits_df)
    
    # Then overlay home runs
    hr_hits = hits_df[hits_df['events'] == 'home_run']
    if not hr_hits.empty:
        ax.scatter(hr_hits['hc_x'] - 125.42,
                  hr_hits['hc_y'] - 198.27,
                  c='red', s=100, alpha=0.8, 
                  marker='*', label='Home Runs', edgecolors='black')


def _add_spray_chart_legend(ax, chart_type):
    """Add appropriate legend for spray chart"""
    if chart_type == "standard":
        ax.legend(loc='upper right')
    elif chart_type == "overlay":
        ax.legend(loc='upper right')


def _calculate_spray_insights(hits_df, player_name, season):
    """Calculate insights from spray chart data"""
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
        
        # Determine field direction
        left_field = hits_df[hits_df['hc_x'] > center_x + 20]
        center_field = hits_df[abs(hits_df['hc_x'] - center_x) <= 20]
        right_field = hits_df[hits_df['hc_x'] < center_x - 20]
        
        insights.append("\n🎯 **Field Distribution:**")
        insights.append(f"- Left Field: {len(left_field)} ({len(left_field)/total_hits*100:.1f}%)")
        insights.append(f"- Center Field: {len(center_field)} ({len(center_field)/total_hits*100:.1f}%)")
        insights.append(f"- Right Field: {len(right_field)} ({len(right_field)/total_hits*100:.1f}%)")
    
    # Exit velocity analysis (if available)
    if 'launch_speed' in hits_df.columns:
        avg_exit_velo = hits_df['launch_speed'].mean()
        max_exit_velo = hits_df['launch_speed'].max()
        
        insights.append("\n⚡ **Exit Velocity:**")
        insights.append(f"- Average: {avg_exit_velo:.1f} mph")
        insights.append(f"- Maximum: {max_exit_velo:.1f} mph")
    
    return "\n".join(insights)


def _create_comparison_summary(player_stats, metrics, stat_type):
    """Create summary for player comparison"""
    summary = ["## Comparison Summary\n"]
    
    for metric in metrics:
        values = []
        names = []
        
        for player_stat in player_stats:
            if metric in player_stat['data'].index:
                values.append(player_stat['data'][metric])
                names.append(player_stat['name'])
        
        if values:
            best_idx = np.argmax(values) if stat_type == "batting" or metric in ['K/9', 'WAR'] else np.argmin(values)
            summary.append(f"**{metric} Leader**: {names[best_idx]} ({values[best_idx]})")
    
    return "\n".join(summary)
