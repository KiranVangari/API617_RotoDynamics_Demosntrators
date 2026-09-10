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
    "z-index": "100",
    "display": "flex",
    "flex-direction": "column"  # This allows us to push the footer to the bottom
}
CONTENT_STYLE = {
    "margin-left": "16vw", "padding": "0px", "font-family": "Arial, sans-serif",
    "background-color": "#f4f6f8", "min-height": "100vh"
}
NAVLINK_STYLE = {
    "display": "block", "color": "#ecf0f1", "text-decoration": "none",
    "padding": "8px 15px", "margin-bottom": "5px", "font-size": "15px"
}

# ==========================================
# MAIN LAYOUT
# ==========================================
app.layout = html.Div([
    # Sidebar
    html.Div([

        # TOP SECTION (Title and Links)
        html.Div([
            html.H2("API 617", style={'text-align': 'center', 'margin-top': '10px'}),
            html.H3("Rotordynamics", style={'text-align': 'center', 'margin-top': '-15px', 'color': '#3498db'}),
            html.Hr(style={'border-color': '#7f8c8d', 'margin-bottom': '20px'}),

            # Contents Header
            html.H4("Contents", style={'color': '#bdc3c7', 'padding-left': '15px', 'margin-bottom': '15px',
                                       'text-transform': 'uppercase', 'letter-spacing': '1px'}),

            # Dynamically generate numbered navigation links
            html.Div([
                dcc.Link(f"{i}. {page['name']}", href=page["relative_path"], style=NAVLINK_STYLE)
                for i, page in enumerate(dash.page_registry.values(), start=1)
            ])
        ], style={'flex-grow': '1'}),  # This forces the section to take up available vertical space

        # BOTTOM SECTION (LinkedIn Footer)
        html.Div([
            html.Hr(style={'border-color': '#7f8c8d', 'margin-bottom': '15px'}),
            html.Span("Website created by:", style={'font-size': '13px', 'color': '#bdc3c7'}),
            html.Br(),
            html.A("Kiran Vangari", href="https://www.linkedin.com/in/kiranvangari/", target="_blank",
                   style={'color': '#3498db', 'text-decoration': 'none', 'font-weight': 'bold', 'font-size': '15px'})
        ], style={'text-align': 'center', 'padding-bottom': '10px'})

    ], style=SIDEBAR_STYLE),

    # Main Content Area (Modules are injected here)
    html.Div([
        dash.page_container
    ], style=CONTENT_STYLE)
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)