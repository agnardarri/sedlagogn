import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from pathlib import Path

def load_data(csv_path="backend/parsed_data/banking_flat_data.csv"):
    """Load data from CSV file"""
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Return the DataFrame
    return df

def plot_top_level_trends(df, output_dir="backend/parsed_data"):
    """Plot trends of top-level assets and liabilities"""
    # Filter to hierarchy level 1 (top level)
    top_level = df[df['hierarchy_level'] == 1].copy()
    
    # Group by date and type, summing the values
    grouped = top_level.groupby(['date', 'type'])['value'].sum().reset_index()
    
    # Pivot to have types as columns
    pivoted = grouped.pivot(index='date', columns='type', values='value')
    
    # Create plot
    plt.figure(figsize=(12, 6))
    ax = pivoted.plot(figsize=(12, 6), linewidth=2.5)
    
    # Format plot
    plt.title('Total Assets vs. Liabilities Over Time', fontsize=16)
    plt.ylabel('Value (ISK millions)', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))  # Every 2 years
    plt.xticks(rotation=45)
    
    # Add legend
    plt.legend(['Assets', 'Liabilities'], fontsize=12)
    
    # Save plot
    output_path = Path(output_dir) / "assets_vs_liabilities.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved plot to {output_path}")
    plt.close()

def plot_category_comparison(df, output_dir="backend/parsed_data"):
    """Plot comparison of main categories within assets and liabilities"""
    # Filter to hierarchy level 2 (main categories)
    categories = df[df['hierarchy_level'] == 2].copy()
    
    # Get top 5 categories by average value for each type
    top_assets = categories[categories['type'] == 'asset'].groupby('name_is')['value'].mean().nlargest(5).index
    top_liabilities = categories[categories['type'] == 'liability'].groupby('name_is')['value'].mean().nlargest(5).index
    
    # Filter to include only top categories
    asset_categories = categories[(categories['type'] == 'asset') & (categories['name_is'].isin(top_assets))]
    liability_categories = categories[(categories['type'] == 'liability') & (categories['name_is'].isin(top_liabilities))]
    
    # Create plots for assets and liabilities
    fig, axes = plt.subplots(2, 1, figsize=(14, 12), sharex=True)
    
    # Plot assets
    for name in top_assets:
        data = asset_categories[asset_categories['name_is'] == name]
        data.set_index('date')['value'].plot(ax=axes[0], linewidth=2, label=name)
    
    axes[0].set_title('Top Asset Categories Over Time', fontsize=16)
    axes[0].set_ylabel('Value (ISK millions)', fontsize=14)
    axes[0].legend(fontsize=10, loc='upper left')
    axes[0].grid(True, alpha=0.3)
    
    # Plot liabilities
    for name in top_liabilities:
        data = liability_categories[liability_categories['name_is'] == name]
        data.set_index('date')['value'].plot(ax=axes[1], linewidth=2, label=name)
    
    axes[1].set_title('Top Liability Categories Over Time', fontsize=16)
    axes[1].set_ylabel('Value (ISK millions)', fontsize=14)
    axes[1].set_xlabel('Date', fontsize=14)
    axes[1].legend(fontsize=10, loc='upper left')
    axes[1].grid(True, alpha=0.3)
    
    # Format x-axis dates
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axes[1].xaxis.set_major_locator(mdates.YearLocator(2))  # Every 2 years
    plt.xticks(rotation=45)
    
    # Save plot
    output_path = Path(output_dir) / "category_comparison.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved plot to {output_path}")
    plt.close()

def plot_stacked_areas(df, output_dir="backend/parsed_data"):
    """Create stacked area plots for assets and liabilities"""
    # Filter to hierarchy level 2 (main categories)
    categories = df[df['hierarchy_level'] == 2].copy()
    
    # Get the latest 10 years of data
    latest_date = df['date'].max()
    ten_years_ago = latest_date - pd.DateOffset(years=10)
    recent_data = categories[categories['date'] >= ten_years_ago]
    
    # Prepare data for plotting
    assets_data = recent_data[recent_data['type'] == 'asset'].pivot_table(
        index='date', columns='name_is', values='value', aggfunc='sum'
    )
    
    liabilities_data = recent_data[recent_data['type'] == 'liability'].pivot_table(
        index='date', columns='name_is', values='value', aggfunc='sum'
    )
    
    # Fill any missing values
    assets_data = assets_data.fillna(0)
    liabilities_data = liabilities_data.fillna(0)
    
    # Create stacked area plots
    fig, axes = plt.subplots(2, 1, figsize=(14, 12), sharex=True)
    
    # Assets stacked area
    assets_data.plot.area(ax=axes[0], stacked=True, alpha=0.7, linewidth=0.5)
    axes[0].set_title('Asset Composition Over the Last 10 Years', fontsize=16)
    axes[0].set_ylabel('Value (ISK millions)', fontsize=14)
    axes[0].legend(fontsize=9, loc='upper left', bbox_to_anchor=(1, 1))
    
    # Liabilities stacked area
    liabilities_data.plot.area(ax=axes[1], stacked=True, alpha=0.7, linewidth=0.5)
    axes[1].set_title('Liability Composition Over the Last 10 Years', fontsize=16)
    axes[1].set_ylabel('Value (ISK millions)', fontsize=14)
    axes[1].set_xlabel('Date', fontsize=14)
    axes[1].legend(fontsize=9, loc='upper left', bbox_to_anchor=(1, 1))
    
    # Format axes
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator())
    
    # Save plot
    output_path = Path(output_dir) / "stacked_areas.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output_path}")
    plt.close()

def plot_hierarchy_levels(df, output_dir="backend/parsed_data"):
    """Plot values aggregated by hierarchy level"""
    # Choose a recent date for the snapshot
    recent_dates = df.sort_values('date')['date'].unique()[-12:]  # Last 12 months
    snapshot_data = df[df['date'].isin(recent_dates)].copy()
    
    # Group by hierarchy level, type, and calculate mean over the period
    grouped = snapshot_data.groupby(['hierarchy_level', 'type'])['value'].mean().reset_index()
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    # Plot bar chart
    sns.barplot(x='hierarchy_level', y='value', hue='type', data=grouped, palette="Set2")
    
    # Format plot
    plt.title('Average Value by Hierarchy Level (Recent Year)', fontsize=16)
    plt.ylabel('Value (ISK millions)', fontsize=14)
    plt.xlabel('Hierarchy Level', fontsize=14)
    plt.xticks(ticks=range(5), labels=['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'])
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend(title='Type')
    
    # Save plot
    output_path = Path(output_dir) / "hierarchy_levels.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved plot to {output_path}")
    plt.close()

def main():
    # Set plot style
    sns.set_style("whitegrid")
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'axes.labelcolor': '#333333',
        'axes.titlecolor': '#333333',
        'text.color': '#333333',
        'figure.facecolor': 'white'
    })
    
    # Load data
    df = load_data()
    print(f"Loaded data with {len(df)} rows")
    
    # Create output directory if it doesn't exist
    output_dir = "backend/parsed_data"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate plots
    print("Generating plots...")
    plot_top_level_trends(df, output_dir)
    plot_category_comparison(df, output_dir)
    plot_stacked_areas(df, output_dir)
    plot_hierarchy_levels(df, output_dir)
    
    print("All plots generated successfully!")

if __name__ == "__main__":
    main() 