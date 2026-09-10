import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Register this file as a page in the multi-page app
dash.register_page(__name__, path='/campbell', name='Torsional Campbell')


def create_slider_card(label, slider_id, min_v, max_v, step_v, val, marks_dict):
    return html.Div([
        html.Label(label, style={'font-weight': 'bold', 'color': '#34495e', 'font-size': '14px'}),
        html.Div(dcc.Slider(id=slider_id, min=min_v, max=max_v, step=step_v, value=val,
                            marks=marks_dict, tooltip={"placement": "bottom", "always_visible": False}),
                 style={'margin-top': '10px'})
    ], style={'background': '#ffffff', 'padding': '12px 15px', 'border-radius': '8px',
              'margin-bottom': '12px', 'box-shadow': '0px 2px 5px rgba(0,0,0,0.05)', 'border': '1px solid #e2e8f0'})


# ==========================================
# PAGE LAYOUT
# ==========================================
layout = html.Div([
    # LEFT PANEL: Controls
    html.Div([
        html.H3("Train Parameters", style={'color': '#2c3e50', 'margin-top': '0', 'margin-bottom': '5px'}),
        # html.P("API 617 Figure D.1 Replication",
        #        style={'color': '#7f8c8d', 'font-size': '13px', 'margin-bottom': '15px'}),

        # Speeds and Gear Ratio
        html.H4("Operating Conditions", style={'color': '#2980b9', 'margin-bottom': '10px', 'margin-top': '0'}),
        create_slider_card("Normal Speed (Motor RPM):", 'ref-speed', 1000, 3000, 1, 1781,
                           {1000: '1000', 2000: '2000', 3000: '3000'}),
        create_slider_card("Compressor Gear Ratio:", 'gear-ratio', 1.0, 8.0, 0.05, 4.25,
                           {1: '1x', 4.25: '4.25x', 8: '8x'}),

        # Torsional Modes (TNFs)
        html.H4("Torsional Natural Frequencies", style={'color': '#2980b9', 'margin-bottom': '10px'}),
        create_slider_card("First Mode (CPM):", 'tnf1', 1000, 3000, 1, 1754, {1000: '1k', 3000: '3k'}),
        create_slider_card("Second Mode (CPM):", 'tnf2', 2000, 5000, 1, 3474, {2000: '2k', 5000: '5k'}),
        create_slider_card("Third Mode (CPM):", 'tnf3', 10000, 14000, 1, 12165, {10000: '10k', 14000: '14k'}),
        create_slider_card("Fourth Mode (CPM):", 'tnf4', 13000, 17000, 1, 15491, {13000: '13k', 17000: '17k'}),
        create_slider_card("Fifth Mode (CPM):", 'tnf5', 14000, 18000, 1, 16039, {14000: '14k', 18000: '18k'}),

        # Reset Button
        html.Button('Reset to API 617 Defaults', id='reset-campbell-button', n_clicks=0,
                    style={'margin-top': '5px', 'padding': '10px 20px',
                           'background-color': '#3498db', 'color': 'white',
                           'border': 'none', 'border-radius': '8px',
                           'font-weight': 'bold', 'cursor': 'pointer',
                           'box-shadow': '0px 2px 5px rgba(0,0,0,0.1)'}),

    ], style={'width': '32%', 'display': 'inline-block', 'padding': '25px', 'verticalAlign': 'top',
              'backgroundColor': '#f0f4f8', 'height': '100vh', 'overflowY': 'auto', 'box-sizing': 'border-box'}),

    # RIGHT PANEL: Plot
    html.Div([
        dcc.Graph(id='torsional-only-plot', style={'height': '95vh'})
    ], style={'width': '68%', 'display': 'inline-block', 'padding': '20px', 'box-sizing': 'border-box',
              'backgroundColor': '#ffffff'})
], style={'display': 'flex', 'width': '100%'})


# ==========================================
# CALLBACKS
# ==========================================

# 1. Reset Button Callback
@dash.callback(
    [Output('ref-speed', 'value'), Output('gear-ratio', 'value'),
     Output('tnf1', 'value'), Output('tnf2', 'value'),
     Output('tnf3', 'value'), Output('tnf4', 'value'), Output('tnf5', 'value')],
    [Input('reset-campbell-button', 'n_clicks')],
    prevent_initial_call=True
)
def reset_campbell(n_clicks):
    # Returns the exact values from API 617 Appendix D, Figure D.1
    return 1781, 4.25, 1754, 3474, 12165, 15491, 16039


# 2. Main Plot Update Callback
@dash.callback(
    Output('torsional-only-plot', 'figure'),
    [Input('ref-speed', 'value'), Input('gear-ratio', 'value'),
     Input('tnf1', 'value'), Input('tnf2', 'value'),
     Input('tnf3', 'value'), Input('tnf4', 'value'), Input('tnf5', 'value')]
)
def update_torsional_campbell(ref_speed, gear_ratio, tnf1, tnf2, tnf3, tnf4, tnf5):
    max_x = 2600
    max_y = 21000
    N = np.linspace(0, max_x, 500)

    exc_motor = 1.0 * N
    exc_comp = gear_ratio * N

    fig = go.Figure()

    # Determine Intersections inside the 90%-110% Operating Margin
    intersections = []
    min_op = 0.9 * ref_speed
    max_op = 1.1 * ref_speed

    tnf_list = [tnf1, tnf2, tnf3, tnf4, tnf5]
    for tnf in tnf_list:
        # Motor intersection
        x_int_m = tnf / 1.0
        if min_op <= x_int_m <= max_op:
            intersections.append((x_int_m, tnf, "1x motor speed"))

        # Compressor intersection
        x_int_c = tnf / gear_ratio
        if min_op <= x_int_c <= max_op:
            intersections.append((x_int_c, tnf, "1x compressor speed"))

    # Shade Operating Speed Range (Green if safe, Red if interference detected)
    op_color = "#2ecc71" if len(intersections) == 0 else "#e74c3c"
    fig.add_vrect(x0=min_op, x1=max_op, fillcolor=op_color, opacity=0.15, line_width=0)

    # Vertical Speed Lines & Rotated Text
    def add_vline(x_val, label, dash_style):
        fig.add_shape(type="line", x0=x_val, y0=0, x1=x_val, y1=max_y,
                      line=dict(color="#2c3e50", width=2, dash=dash_style))
        fig.add_annotation(x=x_val, y=max_y * 0.95, text=label, showarrow=False, textangle=-90, xanchor="right",
                           yanchor="top", font=dict(size=14, color="#2c3e50"))

    add_vline(min_op, f"<b>90% speed = {int(min_op)} RPM</b>", "dash")
    add_vline(ref_speed, f"<b>Normal speed = {int(ref_speed)} RPM</b>", "solid")
    add_vline(max_op, f"<b>110% speed = {int(max_op)} RPM</b>", "dash")

    # Horizontal TNF Lines & Text
    mode_names = ["First", "Second", "Third", "Fourth", "Fifth"]
    for i, tnf in enumerate(tnf_list):
        fig.add_trace(
            go.Scatter(x=[0, max_x], y=[tnf, tnf], mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))
        fig.add_annotation(x=max_x * 0.02, y=tnf + 250, text=f"{mode_names[i]} mode = {tnf} CPM", showarrow=False,
                           xanchor="left", font=dict(size=13, color="black"))

    # Slanted Excitation Lines
    fig.add_trace(
        go.Scatter(x=N, y=exc_motor, mode='lines', line=dict(color='black', width=1.5, dash='dash'), hoverinfo='skip'))
    fig.add_trace(
        go.Scatter(x=N, y=exc_comp, mode='lines', line=dict(color='black', width=1.5, dash='dot'), hoverinfo='skip'))

    # Line Annotations (1x Motor and 1x Compressor)
    fig.add_annotation(x=max_x * 0.5, y=max_x * 0.5 * 1.0 + 300, text="1 x motor speed", showarrow=False, textangle=-15,
                       font=dict(size=13))
    fig.add_annotation(x=max_x * 0.3, y=max_x * 0.3 * gear_ratio + 500, text="1 x compressor speed", showarrow=False,
                       textangle=-45, font=dict(size=13))

    # Add dynamic interference warning arrows (API 617 Note)
    for x_int, y_int, source in intersections:
        fig.add_annotation(
            x=x_int, y=y_int,
            text=f"<b>Note: Torsional and natural frequency<br>interference with {source}</b>",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#c0392b",
            ax=120, ay=-80,
            font=dict(size=13, color="white"),
            bgcolor="#e74c3c", bordercolor="#c0392b", borderwidth=2, borderpad=6
        )

    # General Layout Formatting
    fig.update_layout(
        title=dict(text="<b>Typical Campbell Diagram</b>", font=dict(size=22, color='#2c3e50'),
                   x=0.5, y=0.95),
        xaxis_title="<b>Reference speed (RPM)</b>",
        yaxis_title="<b>Torsional Natural Frequency (CPM)</b>",
        plot_bgcolor='#ffffff', margin=dict(t=80, b=50, l=70, r=30),
        xaxis=dict(showline=True, linewidth=2, linecolor='black', showgrid=False, range=[0, max_x], tickformat="d",
                   tickfont=dict(size=14)),
        yaxis=dict(showline=True, linewidth=2, linecolor='black', showgrid=False, range=[0, max_y], tickformat="d",
                   tickfont=dict(size=14)),
        showlegend=False
    )

    return fig