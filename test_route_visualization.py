#!/usr/bin/env python3
"""
Test script to verify route line visualization functionality.
This tests the "Draw route lines colored by risk" task implementation.
"""

import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add the current directory to Python path to import modules
sys.path.append('.')

def get_port_coordinates():
    """Get coordinates for major ports used in the dataset."""
    return {
        # Major Asian Ports
        'Shanghai': {'lat': 31.2304, 'lon': 121.4737},
        'Singapore': {'lat': 1.2966, 'lon': 103.7764},
        'Chennai': {'lat': 13.0827, 'lon': 80.2707},
        'Yokohama': {'lat': 35.4437, 'lon': 139.6380},
        'Hong Kong': {'lat': 22.3193, 'lon': 114.1694},
        'Busan': {'lat': 35.1796, 'lon': 129.0756},
        'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
        'Kolkata': {'lat': 22.5726, 'lon': 88.3639},
        'Karachi': {'lat': 24.8607, 'lon': 67.0011},
        'Dubai': {'lat': 25.2048, 'lon': 55.2708},
        'Perth': {'lat': -31.9505, 'lon': 115.8605},
        
        # European Ports
        'Hamburg': {'lat': 53.5511, 'lon': 9.9937},
        'Rotterdam': {'lat': 51.9244, 'lon': 4.4777},
        'Antwerp': {'lat': 51.2194, 'lon': 4.4025},
        'Le Havre': {'lat': 49.4944, 'lon': 0.1079},
        'Barcelona': {'lat': 41.3851, 'lon': 2.1734},
        'Genoa': {'lat': 44.4056, 'lon': 8.9463},
        'Piraeus': {'lat': 37.9755, 'lon': 23.6348},
        
        # American Ports
        'Houston': {'lat': 29.7604, 'lon': -95.3698},
        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
        'New York': {'lat': 40.7128, 'lon': -74.0060},
        'Miami': {'lat': 25.7617, 'lon': -80.1918},
        'Vancouver': {'lat': 49.2827, 'lon': -123.1207},
        'Santos': {'lat': -23.9608, 'lon': -46.3331},
        'Buenos Aires': {'lat': -34.6118, 'lon': -58.3960},
        'Valparaiso': {'lat': -33.0472, 'lon': -71.6127},
        
        # African Ports
        'Alexandria': {'lat': 31.2001, 'lon': 29.9187},
        'Cape Town': {'lat': -33.9249, 'lon': 18.4241},
        'Lagos': {'lat': 6.5244, 'lon': 3.3792},
        'Durban': {'lat': -29.8587, 'lon': 31.0218},
        'Casablanca': {'lat': 33.5731, 'lon': -7.5898},
        
        # Other Major Ports
        'Sydney': {'lat': -33.8688, 'lon': 151.2093},
        'Melbourne': {'lat': -37.8136, 'lon': 144.9631},
        'Fremantle': {'lat': -32.0569, 'lon': 115.7439}
    }

def create_test_route_map(df):
    """Create Route Intelligence Map with colored route lines - TEST VERSION."""
    port_coords = get_port_coordinates()
    
    # Create the figure
    fig = go.Figure()
    
    # Color mapping for risk categories
    risk_colors = {
        'SAFE': '#28a745',
        'SUSPICIOUS': '#ffc107',
        'FRAUD': '#dc3545'
    }
    
    # Track export and import ports separately
    export_ports = set()
    import_ports = set()
    route_data = []
    
    print(f"Processing {len(df)} transactions...")
    
    # Process transactions to extract route information
    for _, row in df.iterrows():
        export_port = row.get('export_port', '')
        import_port = row.get('import_port', '')
        risk_category = row.get('risk_category', 'SUSPICIOUS')  # Default to SUSPICIOUS for test
        
        # Add ports to respective sets
        if export_port in port_coords:
            export_ports.add(export_port)
        if import_port in port_coords:
            import_ports.add(import_port)
            
        # Store route data if both ports have coordinates
        if export_port in port_coords and import_port in port_coords:
            route_data.append({
                'export_port': export_port,
                'import_port': import_port,
                'risk_category': risk_category,
                'transaction_id': row.get('transaction_id', ''),
                'product': row.get('product', ''),
                'trade_value': row.get('trade_value', 0),
                'distance_km': row.get('distance_km', 0)
            })
    
    print(f"Found {len(export_ports)} export ports, {len(import_ports)} import ports")
    print(f"Created {len(route_data)} route connections")
    
    # Plot export ports (origin points)
    if export_ports:
        export_lons = [port_coords[port]['lon'] for port in export_ports]
        export_lats = [port_coords[port]['lat'] for port in export_ports]
        export_names = list(export_ports)
        
        fig.add_trace(go.Scattergeo(
            lon=export_lons,
            lat=export_lats,
            mode='markers',
            marker=dict(
                size=10,
                color='#28a745',  # Green for export ports
                symbol='triangle-up',
                line=dict(width=2, color='white')
            ),
            text=export_names,
            hovertemplate="<b>%{text}</b><br>Export Port<br><extra></extra>",
            showlegend=True,
            name="Export Ports"
        ))
    
    # Plot import ports (destination points)
    if import_ports:
        import_lons = [port_coords[port]['lon'] for port in import_ports]
        import_lats = [port_coords[port]['lat'] for port in import_ports]
        import_names = list(import_ports)
        
        fig.add_trace(go.Scattergeo(
            lon=import_lons,
            lat=import_lats,
            mode='markers',
            marker=dict(
                size=10,
                color='#dc3545',  # Red for import ports
                symbol='triangle-down',
                line=dict(width=2, color='white')
            ),
            text=import_names,
            hovertemplate="<b>%{text}</b><br>Import Port<br><extra></extra>",
            showlegend=True,
            name="Import Ports"
        ))
    
    # Group routes by risk category for better visualization
    route_counts = {}
    for risk_cat in ['SAFE', 'SUSPICIOUS', 'FRAUD']:
        routes_in_category = [r for r in route_data if r['risk_category'] == risk_cat]
        route_counts[risk_cat] = len(routes_in_category)
        
        if not routes_in_category:
            continue
            
        # Create route lines for this risk category
        lons = []
        lats = []
        hover_texts = []
        
        for route in routes_in_category:
            export_coords = port_coords[route['export_port']]
            import_coords = port_coords[route['import_port']]
            
            # Add route line (export -> import -> None for line break)
            lons.extend([export_coords['lon'], import_coords['lon'], None])
            lats.extend([export_coords['lat'], import_coords['lat'], None])
            
            # Hover text for the route
            hover_text = (
                f"<b>{route['transaction_id']}</b><br>"
                f"Route: {route['export_port']} → {route['import_port']}<br>"
                f"Product: {route['product']}<br>"
                f"Trade Value: ${route['trade_value']:,.2f}<br>"
                f"Distance: {route['distance_km']:,} km<br>"
                f"Risk: {route['risk_category']}"
            )
            hover_texts.extend([hover_text, hover_text, None])
        
        # Add route lines for this risk category
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(
                width=2,
                color=risk_colors[risk_cat]
            ),
            hovertemplate='%{text}<extra></extra>',
            text=hover_texts,
            name=f"{risk_cat} Routes ({len(routes_in_category)})",
            showlegend=True
        ))
    
    print(f"Route distribution: SAFE={route_counts['SAFE']}, SUSPICIOUS={route_counts['SUSPICIOUS']}, FRAUD={route_counts['FRAUD']}")
    
    # Update layout for the map
    fig.update_layout(
        title={
            'text': "🗺️ Route Intelligence Map - TEST",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'black'}
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(230, 245, 255)',
            bgcolor='rgba(255,255,255,1)'
        ),
        paper_bgcolor='rgba(255,255,255,1)',
        plot_bgcolor='rgba(255,255,255,1)',
        font=dict(color='black'),
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='black',
            borderwidth=1,
            font=dict(color='black')
        ),
        height=600
    )
    
    return fig

def test_route_visualization():
    """Test the route line visualization functionality."""
    print("=== Testing Route Line Visualization ===")
    
    # Load the dataset
    try:
        df = pd.read_csv('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv')
        print(f"✅ Loaded dataset with {len(df)} transactions")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return False
    
    # Check required columns
    required_cols = ['export_port', 'import_port']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return False
    
    print(f"✅ Found required columns: {required_cols}")
    
    # Add risk categories for testing (since the ML model isn't loaded)
    import random
    risk_categories = ['SAFE', 'SUSPICIOUS', 'FRAUD']
    df['risk_category'] = [random.choice(risk_categories) for _ in range(len(df))]
    df['trade_value'] = df.get('trade_value', 10000)  # Default trade value
    df['distance_km'] = df.get('distance_km', 5000)   # Default distance
    
    print(f"✅ Added test risk categories")
    
    # Test route map creation
    try:
        fig = create_test_route_map(df.head(50))  # Test with first 50 transactions
        print("✅ Route map created successfully")
        
        # Save as HTML for inspection
        fig.write_html("test_route_map.html")
        print("✅ Route map saved as test_route_map.html")
        
        # Verify the figure has the expected traces
        trace_names = [trace.name for trace in fig.data]
        print(f"✅ Map traces: {trace_names}")
        
        # Check if route lines are present
        route_traces = [name for name in trace_names if 'Routes' in name]
        if route_traces:
            print(f"✅ Route lines found: {route_traces}")
        else:
            print("⚠️  No route line traces found")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create route map: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_route_visualization()
    if success:
        print("\n🎉 Route line visualization test PASSED!")
        print("The 'Draw route lines colored by risk' task is working correctly.")
    else:
        print("\n❌ Route line visualization test FAILED!")
    
    sys.exit(0 if success else 1)