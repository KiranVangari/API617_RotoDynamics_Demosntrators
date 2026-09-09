import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Register this file as a page
dash.register_page(__name__, path='/logdec', name='Log Decrement')

# Define layout (not app.layout)
layout = html.Div([
    html.Div([
        html.H2("API 617 Stability & Log Decrement", style={'color': '#2c3e50', 'margin-top': '0'}),
        # Slider Control
        html.Div([
            html.Label("Adjust Log Decrement (δ):",
                       style={'font-weight': 'bold', 'color': '#34495e', 'font-size': '16px'}),
            dcc.Slider(id='log-dec-slider', min=-0.05, max=0.5, step=0.01, value=0.15,
                       marks={-0.05: '-0.05', 0: '0', 0.1: '0.1', 0.3: '0.3', 0.5: '0.5'},
                       tooltip={"placement": "bottom", "always_visible": True}),

            # -> ADD THIS NEW BUTTON CODE <-
            html.Button('Reset Default', id='reset-logdec-button', n_clicks=0,
                        style={'margin-top': '15px', 'padding': '10px 20px',
                               'background-color': '#3498db', 'color': 'white',
                               'border': 'none', 'border-radius': '8px',
                               'font-weight': 'bold', 'cursor': 'pointer',
                               'box-shadow': '0px 2px 5px rgba(0,0,0,0.1)'}),

        ], style={'background': '#ffffff', 'padding': '20px', 'border-radius': '8px', 'margin-bottom': '20px',
                  'box-shadow': '0px 2px 5px rgba(0,0,0,0.1)'}),
        html.Div(id='status-output', style={'margin-bottom': '20px'}),
        html.Div([
            html.H4("1. Definition", style={'color': '#2980b9', 'margin-bottom': '5px'}),
            html.P("The logarithmic decrement (δ) measures the rate of decay of free vibration. It is mathematically defined as the natural log of the ratio of two successive amplitudes: δ = ln(X_1 / X_2). In complex eigenvalue analysis, it represents the ratio of the real part of the eigenvalue (damping) to the imaginary part (damped natural frequency)."),
            html.H4("2. Acceptance Limits", style={'color': '#2980b9', 'margin-bottom': '5px'}),
            html.P("Per API 617, an acceptable rotor must demonstrate a final log decrement (δ_f) > 0.1 in the Level II analysis. This ensures adequate damping reserves against destabilizing cross-coupled forces."),
            html.H4("3. How OEMs Prove Stability", style={'color': '#2980b9', 'margin-bottom': '5px'}),
            html.P("OEMs evaluate stability using a two-tiered analytical approach calculated at Maximum Continuous Speed (MCS)."),
            html.Ul([
                html.Li(html.B("Level I Analysis (Screening): ")),
                html.Span("A standardized, conservative screening tool. A generic anticipated cross-coupling (Q_A) is calculated based on rated power and gas density, then applied to the rotor model. If the rotor maintains δ_A > 0.1 and Q_0/Q_A ≥ 2.0, it passes. Otherwise, Level II is mandated."),
                html.Br(), html.Br(),
                html.Li(html.B("Level II Analysis (Detailed): ")),
                html.Span("Replaces the generic Q_A with the actual dynamic coefficients of internal components (labyrinth seals, damper seals, aero effects, internal friction). The complete model must yield a final δ_f > 0.1.")
            ]),
            html.H4("4. Consequences of Low Log Dec", style={'color': '#e74c3c', 'margin-bottom': '5px'}),
            html.P("If δ approaches 0 or becomes negative, the effective damping of the system is negative. The rotor becomes susceptible to self-excited subsynchronous instability (fluid-induced whirl/whip). A nominal perturbation allows internal rotational energy to feed into the natural frequency, causing unbounded, exponential amplitude growth, regardless of separation margins.")
        ], style={'font-size': '14px', 'line-height': '1.6', 'color': '#34495e'})
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '25px', 'verticalAlign': 'top', 'backgroundColor': '#f4f6f8', 'height': '100vh', 'overflowY': 'auto', 'box-sizing': 'border-box'}),

    html.Div([
        dcc.Graph(id='logdec-plot', style={'height': '95vh'})
    ], style={'width': '62%', 'display': 'inline-block', 'padding': '20px', 'box-sizing': 'border-box', 'backgroundColor': '#ffffff'})
], style={'display': 'flex', 'width': '100%'})

# Use @dash.callback instead of @app.callback
@dash.callback(
    [Output('logdec-plot', 'figure'), Output('status-output', 'children')],
    [Input('log-dec-slider', 'value')]
)
def update_plot_logdec(delta):
    t = np.linspace(0, 1, 1000)
    omega_n = 2 * np.pi * 50

    zeta = delta / np.sqrt((2 * np.pi) ** 2 + delta ** 2)
    omega_d = omega_n * np.sqrt(1 - zeta ** 2) if zeta < 1 else omega_n

    amplitude = np.exp(-zeta * omega_n * t) * np.cos(omega_d * t)
    envelope = np.exp(-zeta * omega_n * t)

    y_max_plot = 2.0
    if delta < 0:
        y_max_plot = min(10.0, max(amplitude))

    if delta >= 0.1:
        status_color, status_text, desc = '#27ae60', "API 617 LEVEL II COMPLIANT: STABLE", "System demonstrates sufficient aerodynamic damping. Vibration decays rapidly."
    elif delta >= 0.0:
        status_color, status_text, desc = '#f39c12', "NON-COMPLIANT: MARGINALLY STABLE", "Vibration decays, but damping reserves are insufficient per API 617 criteria. High risk of instability under off-design conditions."
    else:
        status_color, status_text, desc = '#e74c3c', "CATASTROPHIC INSTABILITY: NEGATIVE DAMPING", "System is self-exciting. A nominal perturbation causes exponential amplitude growth (fluid-induced whirl/whip)."

    status_html = html.Div([
        html.H3(status_text, style={'color': 'white', 'margin': '0', 'text-align': 'center'}),
        html.P(desc, style={'color': 'white', 'margin': '5px 0 0 0', 'text-align': 'center', 'font-size': '14px'})
    ], style={'background': status_color, 'padding': '15px', 'border-radius': '8px', 'box-shadow': '0px 2px 5px rgba(0,0,0,0.2)'})

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=amplitude, mode='lines', line=dict(color=status_color, width=2.5), name="Transient Response"))
    fig.add_trace(go.Scatter(x=t, y=envelope, mode='lines', line=dict(color='#bdc3c7', width=2, dash='dash'), name="Decay Envelope"))
    fig.add_trace(go.Scatter(x=t, y=-envelope, mode='lines', line=dict(color='#bdc3c7', width=2, dash='dash'), showlegend=False))
    fig.add_hline(y=0, line=dict(color='#95a5a6', width=1))

    fig.add_annotation(x=0.95, y=0.90, xref="paper", yref="paper", text=f"<b>δ = {delta:.2f}</b>", showarrow=False, font=dict(size=22, color=status_color), bgcolor="rgba(255, 255, 255, 0.9)", bordercolor=status_color, borderwidth=2, borderpad=10)

    fig.update_layout(
        title=dict(text=f"<b>Time-Domain Transient Rotor Response</b>", font=dict(size=22, color='#2c3e50'), x=0.5, y=0.95),
        xaxis_title="<b>TIME (Seconds)</b>", yaxis_title="<b>NORMALIZED VIBRATION AMPLITUDE</b>", plot_bgcolor='#ffffff', showlegend=False, margin=dict(t=80, b=50, l=60, r=50),
        xaxis=dict(showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1', zeroline=False, range=[0, 1]),
        yaxis=dict(showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1', zeroline=False, range=[-y_max_plot, y_max_plot])
    )
    return fig, status_html

# -> ADD THIS CALLBACK AT THE VERY BOTTOM <-
@dash.callback(
    Output('log-dec-slider', 'value'),
    Input('reset-logdec-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_logdec_slider(n_clicks):
    # Returns the original default log decrement value
    return 0.15