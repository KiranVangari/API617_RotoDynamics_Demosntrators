import dash
from dash import html, dcc

# Initialize app with use_pages=True for multi-module architecture
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server

# ==========================================
# STYLES
# ==========================================
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "16vw",
    "padding": "20px 10px", "background-color": "#2c3e50", "color": "white",
    "font-family": "Arial, sans-serif", "box-shadow": "2px 0 5px rgba(0,0,0,0.1)",
    "z-index": "100"
}
CONTENT_STYLE = {
    "margin-left": "16vw", "padding": "0px", "font-family": "Arial, sans-serif",
    "background-color": "#f4f6f8", "min-height": "100vh"
}
NAVLINK_STYLE = {
    "display": "block", "color": "#ecf0f1", "text-decoration": "none",
    "padding": "15px", "margin-bottom": "10px", "border-radius": "5px",
    "background-color": "#34495e", "font-weight": "bold", "text-align": "center"
}

# ==========================================
# MAIN LAYOUT
# ==========================================
app.layout = html.Div([
    # Sidebar
    html.Div([
        html.H2("API 617", style={'text-align': 'center', 'margin-top': '10px'}),
        html.H3("Rotordynamics", style={'text-align': 'center', 'margin-top': '-15px', 'color': '#3498db'}),
        html.Hr(style={'border-color': '#7f8c8d', 'margin-bottom': '30px'}),

        # Dynamically generate navigation links from the pages/ folder
        html.Div([
            dcc.Link(f"{page['name']}", href=page["relative_path"], style=NAVLINK_STYLE)
            for page in dash.page_registry.values()
        ])
    ], style=SIDEBAR_STYLE),

    # Main Content Area (Modules are injected here)
    html.Div([
        dash.page_container
    ], style=CONTENT_STYLE)
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)