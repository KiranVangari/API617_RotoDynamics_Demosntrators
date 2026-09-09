import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Register this file as a page
dash.register_page(__name__, path='/', name='Separation Margin')


def create_slider_card(label, slider_id, min_v, max_v, step_v, val, marks_dict):
    return html.Div([
        html.Label(label, style={'font-weight': 'bold', 'color': '#34495e', 'font-size': '14px'}),
        html.Div(dcc.Slider(id=slider_id, min=min_v, max=max_v, step=step_v, value=val,
                            marks=marks_dict, tooltip={"placement": "bottom", "always_visible": False}),
                 style={'margin-top': '10px'})
    ], style={'background': '#ffffff', 'padding': '15px 20px', 'border-radius': '8px',
              'margin-bottom': '15px', 'box-shadow': '0px 2px 5px rgba(0,0,0,0.05)', 'border': '1px solid #e2e8f0'})


# Define layout
layout = html.Div([
    html.Div([
        html.H3("Rotor Properties", style={'color': '#2c3e50', 'margin-top': '0', 'margin-bottom': '20px'}),
        create_slider_card("1st Critical Speed (Nc1):", 'nc1', 1000, 6000, 100, 4000,
                           {i: str(i) for i in range(1000, 6001, 1000)}),
        create_slider_card("1st Mode AF:", 'af1', 1.5, 15, 0.5, 6.5, {i: str(i) for i in range(2, 16, 2)}),
        create_slider_card("Min Allowable Speed (Nma):", 'nma', 5000, 10000, 100, 7000,
                           {i: str(i) for i in range(5000, 10001, 1000)}),
        create_slider_card("Max Continuous Speed (Nmc):", 'nmc', 6000, 12000, 100, 9000,
                           {i: str(i) for i in range(6000, 12001, 1000)}),
        create_slider_card("2nd Critical Speed (Nc2):", 'nc2', 10000, 16000, 100, 11500,
                           {i: str(i) for i in range(10000, 16001, 1000)}),
        create_slider_card("2nd Mode AF:", 'af2', 1.5, 15, 0.5, 4.0, {i: str(i) for i in range(2, 16, 2)}),

        # -> RESET BUTTON CODE <-
        html.Button('Reset Defaults', id='reset-button', n_clicks=0,
                    style={'margin-top': '10px', 'padding': '10px 20px',
                           'background-color': '#3498db', 'color': 'white',
                           'border': 'none', 'border-radius': '8px',
                           'font-weight': 'bold', 'cursor': 'pointer',
                           'box-shadow': '0px 2px 5px rgba(0,0,0,0.1)'}),
        html.Hr(style={'margin-top': '25px', 'margin-bottom': '25px', 'border-color': '#bdc3c7'}),
        html.Div(id='calc-output')
    ], style={'width': '35%', 'display': 'inline-block', 'padding': '25px', 'verticalAlign': 'top',
              'backgroundColor': '#f0f4f8', 'height': '100vh', 'overflowY': 'auto', 'box-sizing': 'border-box'}),

    html.Div([
        dcc.Graph(id='rotor-plot', style={'height': '95vh'})
    ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px', 'box-sizing': 'border-box',
              'backgroundColor': '#ffffff'})
], style={'display': 'flex', 'width': '100%'})


@dash.callback(
    [Output('rotor-plot', 'figure'), Output('calc-output', 'children')],
    [Input('nc1', 'value'), Input('af1', 'value'), Input('nma', 'value'),
     Input('nmc', 'value'), Input('nc2', 'value'), Input('af2', 'value')]
)
def update_plot_margin(nc1, af1, nma, nmc, nc2, af2):
    if nma <= nc1: nma = nc1 + 100
    if nmc <= nma: nmc = nma + 100
    if nc2 <= nmc: nc2 = nmc + 100

    N = np.linspace(0, max(nmc * 1.3, nc2 * 1.2), 8000)
    zeta1 = 1 / (2 * af1)
    zeta2 = 1 / (2 * af2)

    def pure_api_response(n, nc, af, scale):
        r = n / (nc + 1e-9)
        amp = 1.0 / np.sqrt(1 + 4 * (af ** 2) * (r - 1) ** 2)
        envelope = 1.0 - np.exp(-10 * (n / nc) ** 2)
        return scale * amp * envelope

    amp1 = pure_api_response(N, nc1, af1, 1.0)
    amp2 = pure_api_response(N, nc2, af2, 0.6)

    p = 8
    amplitude = (amp1 ** p + amp2 ** p) ** (1 / p)

    N1, N2 = nc1 * (1 - 1 / (2 * af1)), nc1 * (1 + 1 / (2 * af1))
    N3, N4 = nc2 * (1 - 1 / (2 * af2)), nc2 * (1 + 1 / (2 * af2))

    Ac1, Ac2 = 1.0, 0.6
    half_power_amp1, half_power_amp2 = 0.707 * Ac1, 0.707 * Ac2

    # Calculate Compliance
    SMr1 = 17 * (1 - (1 / (af1 - 1.5))) if af1 >= 2.5 else 0.0
    SMa1 = 100 * (nma - nc1) / nma
    is_compliant1 = SMa1 >= SMr1

    SMr2 = 10 + 17 * (1 - (1 / (af2 - 1.5))) if af2 >= 2.5 else 0.0
    SMa2 = 100 * (nc2 - nmc) / nmc
    is_compliant2 = SMa2 >= SMr2

    # Dynamic Color Logic for the Plot
    overall_compliant = is_compliant1 and is_compliant2
    op_range_fill_color = "#2ecc71" if overall_compliant else "#e74c3c"  # Green if both pass, Red if either fails
    op_range_text_color = "#27ae60" if overall_compliant else "#c0392b"  # Darker shade for text/lines

    fig = go.Figure()

    # Apply dynamic colors to the Operating Speed Range rectangle and text
    fig.add_vrect(x0=nma, x1=nmc, fillcolor=op_range_fill_color, opacity=0.15, line_width=0)
    fig.add_annotation(x=(nma + nmc) / 2, y=max(amplitude) * 1.2, text="<b>Operating Speed Range</b>", showarrow=False,
                       font=dict(size=15, color=op_range_text_color))

    fig.add_trace(go.Scatter(x=N, y=amplitude, mode='lines', fill='tozeroy', fillcolor='rgba(149, 165, 166, 0.15)',
                             line=dict(color='#7f8c8d', width=3, shape='spline'), hoverinfo='skip'))

    color_mode1, color_mode2 = "#005b96", "#8e44ad"

    def add_vline(x_val, label, y_max, color="#7f8c8d"):
        fig.add_shape(type="line", x0=x_val, y0=0, x1=x_val, y1=y_max, line=dict(color=color, width=2, dash="dash"))
        fig.add_annotation(x=x_val, y=-0.05 * max(amplitude), text=label, showarrow=False,
                           font=dict(size=15, color=color))

    add_vline(nc1, "<b>N<sub>c1</sub></b>", Ac1, color=color_mode1)
    add_vline(N1, "<b>N<sub>1</sub></b>", half_power_amp1, color=color_mode1)
    add_vline(N2, "<b>N<sub>2</sub></b>", half_power_amp1, color=color_mode1)

    # Apply dynamic colors to the Nma and Nmc vertical lines
    add_vline(nma, "<b>N<sub>ma</sub></b>", max(amplitude) * 1.15, color=op_range_text_color)
    add_vline(nmc, "<b>N<sub>mc</sub></b>", max(amplitude) * 1.15, color=op_range_text_color)

    add_vline(nc2, "<b>N<sub>c2</sub></b>", Ac2, color=color_mode2)
    add_vline(N3, "<b>N<sub>3</sub></b>", half_power_amp2, color=color_mode2)
    add_vline(N4, "<b>N<sub>4</sub></b>", half_power_amp2, color=color_mode2)

    fig.add_shape(type="line", x0=0, y0=half_power_amp1, x1=N2, y1=half_power_amp1,
                  line=dict(color=color_mode1, width=2, dash="dot"))
    fig.add_annotation(x=nc1 * 0.1, y=half_power_amp1 * 1.05, text="<b>.707 × A<sub>c1</sub></b>", showarrow=False,
                       font=dict(size=14, color=color_mode1))
    fig.add_shape(type="line", x0=0, y0=half_power_amp2, x1=N4, y1=half_power_amp2,
                  line=dict(color=color_mode2, width=2, dash="dot"))
    fig.add_annotation(x=nc1 * 0.1, y=half_power_amp2 * 1.05, text="<b>.707 × A<sub>c2</sub></b>", showarrow=False,
                       font=dict(size=14, color=color_mode2))
    fig.add_shape(type="line", x0=0, y0=Ac1, x1=nc1, y1=Ac1, line=dict(color=color_mode1, width=2, dash="dot"))
    fig.add_annotation(x=nc1 * 0.1, y=Ac1 * 1.05, text="<b>A<sub>c1</sub></b>", showarrow=False,
                       font=dict(size=14, color=color_mode1))
    fig.add_shape(type="line", x0=0, y0=Ac2, x1=nc2, y1=Ac2, line=dict(color=color_mode2, width=2, dash="dot"))
    fig.add_annotation(x=nc1 * 0.1, y=Ac2 * 1.05, text="<b>A<sub>c2</sub></b>", showarrow=False,
                       font=dict(size=14, color=color_mode2))

    y_arrow = max(amplitude) * 1.25
    fig.add_annotation(x=nma, y=y_arrow, ax=nc1, ay=y_arrow, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                       arrowhead=2, arrowcolor="#2c3e50")
    fig.add_annotation(x=nc1, y=y_arrow, ax=nma, ay=y_arrow, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                       arrowhead=2, arrowcolor="#2c3e50")
    fig.add_annotation(x=(nc1 + nma) / 2, y=y_arrow * 1.03, text="<b>S<sub>a1</sub></b>", showarrow=False,
                       font=dict(size=16, color="#2c3e50"))
    fig.add_annotation(x=nc2, y=y_arrow, ax=nmc, ay=y_arrow, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                       arrowhead=2, arrowcolor="#2c3e50")
    fig.add_annotation(x=nmc, y=y_arrow, ax=nc2, ay=y_arrow, xref="x", yref="y", axref="x", ayref="y", showarrow=True,
                       arrowhead=2, arrowcolor="#2c3e50")
    fig.add_annotation(x=(nmc + nc2) / 2, y=y_arrow * 1.03, text="<b>S<sub>a2</sub></b>", showarrow=False,
                       font=dict(size=16, color="#2c3e50"))
    fig.add_annotation(x=nc1, y=Ac1, text=f"<b>ζ₁ = {zeta1:.3f}</b>", showarrow=True, ax=-40, ay=-40, arrowhead=2,
                       arrowcolor=color_mode1, font=dict(size=14, color=color_mode1))
    fig.add_annotation(x=nc2, y=Ac2, text=f"<b>ζ₂ = {zeta2:.3f}</b>", showarrow=True, ax=40, ay=-40, arrowhead=2,
                       arrowcolor=color_mode2, font=dict(size=14, color=color_mode2))

    fig.update_layout(
        title=dict(text="<b>Rotor Response Plot and Separation Margin Calculation</b>",
                   font=dict(size=22, color='#2c3e50'), x=0.5, y=0.97),
        xaxis_title="<b>ROTOR SPEED (rpm)</b>", yaxis_title="<b>VIBRATION AMPLITUDE</b>", plot_bgcolor='#ffffff',
        margin=dict(t=70, b=50, l=50, r=50),
        xaxis=dict(showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1', zeroline=False,
                   range=[0, N[-1]], tickformat="d", tickfont=dict(size=15, color='#2c3e50')),
        yaxis=dict(showline=True, linewidth=2, linecolor='#34495e', showgrid=False, zeroline=False, tickvals=[0],
                   ticktext=['0'], tickfont=dict(size=15, color='#2c3e50'), range=[0, max(amplitude) * 1.35])
    )

    calc_html = html.Div([
        html.H4("API 617 CALCULATIONS",
                style={'color': '#2c3e50', 'margin-top': '0', 'border-bottom': '2px solid #bdc3c7',
                       'padding-bottom': '10px'}),
        html.Div([
            html.H4("1st Critical Mode (Below Nma)",
                    style={'color': color_mode1, 'margin-bottom': '8px', 'margin-top': '0'}),
            html.P([f"Nc1: {nc1:.0f} rpm", html.Br(), f"N1: {N1:.0f} rpm | N2: {N2:.0f} rpm", html.Br(),
                    html.Span(f"Calculated AF1: {af1:.2f}", style={'font-weight': 'bold'}), html.Br(),
                    html.Span(f"Damping Ratio (ζ₁): {zeta1:.4f}", style={'font-style': 'italic', 'color': '#7f8c8d'}),
                    html.Br(), html.Br(), f"Actual SMa1: {SMa1:.1f} %", html.Br(), f"Required SMr1: {SMr1:.1f} %"],
                   style={'margin-top': '0', 'line-height': '1.6', 'color': '#34495e'}),
            html.Div("COMPLIANT" if is_compliant1 else "NON-COMPLIANT",
                     style={'color': 'white', 'background': '#27ae60' if is_compliant1 else '#e74c3c', 'padding': '8px',
                            'text-align': 'center', 'font-weight': 'bold', 'border-radius': '4px',
                            'margin-top': '10px'})
        ], style={'background': '#ffffff', 'padding': '15px', 'border': '1px solid #e2e8f0', 'border-radius': '8px',
                  'margin-bottom': '20px', 'box-shadow': '0px 2px 5px rgba(0,0,0,0.05)'}),
        html.Div([
            html.H4("2nd Critical Mode (Above Nmc)",
                    style={'color': color_mode2, 'margin-bottom': '8px', 'margin-top': '0'}),
            html.P([f"Nc2: {nc2:.0f} rpm", html.Br(), f"N3: {N3:.0f} rpm | N4: {N4:.0f} rpm", html.Br(),
                    html.Span(f"Calculated AF2: {af2:.2f}", style={'font-weight': 'bold'}), html.Br(),
                    html.Span(f"Damping Ratio (ζ₂): {zeta2:.4f}", style={'font-style': 'italic', 'color': '#7f8c8d'}),
                    html.Br(), html.Br(), f"Actual SMa2: {SMa2:.1f} %", html.Br(), f"Required SMr2: {SMr2:.1f} %"],
                   style={'margin-top': '0', 'line-height': '1.6', 'color': '#34495e'}),
            html.Div("COMPLIANT" if is_compliant2 else "NON-COMPLIANT",
                     style={'color': 'white', 'background': '#27ae60' if is_compliant2 else '#e74c3c', 'padding': '8px',
                            'text-align': 'center', 'font-weight': 'bold', 'border-radius': '4px',
                            'margin-top': '10px'})
        ], style={'background': '#ffffff', 'padding': '15px', 'border': '1px solid #e2e8f0', 'border-radius': '8px',
                  'box-shadow': '0px 2px 5px rgba(0,0,0,0.05)'})
    ])
    return fig, calc_html

# -> ADD THIS CALLBACK AT THE VERY BOTTOM <-
@dash.callback(
    [Output('nc1', 'value'), Output('af1', 'value'), Output('nma', 'value'),
     Output('nmc', 'value'), Output('nc2', 'value'), Output('af2', 'value')],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def reset_sliders(n_clicks):
    # Returns the original default values: nc1, af1, nma, nmc, nc2, af2
    return 4000, 6.5, 7000, 9000, 11500, 4.0