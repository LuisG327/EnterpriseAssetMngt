# EAM Operations Dashboard
# Luis GUtierrez | Data Science Portfolio
# Interactive Asset Health & Maintanance KPI Dashboard

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go 
import plotly.express as px
import pandas as pd
import numpy as np

np.random.seed(42)

#---- EAM Data Simulate   --------
n_assets = 150


asset_id = [f'ASSET-{i:04d}' for i in range (1, n_assets+1)]
category = np.random.choice(['Rotating Equipment', 'Electrical','HVAC','Pipping', 'Instrumental'], n_assets, p=[0.25, 0.20, 0.20, 0.20, 0.15])
health_score = np.random.beta(5, 2, n_assets) * 100
age_years = np.random.randint(1, 25, n_assets)
last_pm_days = np.random.exponential(45, n_assets)
mtbf = np.random.normal(120, 30, n_assets).clip(0, 180)
location = np.random.choice(['Plant A', 'Plant B', 'Plant C', 'Substraction 1', 'Substraction 2'],n_assets)

assets = pd.DataFrame()
assets['asset_id'] = asset_id
assets['category'] = category
assets['health_score'] = health_score
assets['age_years'] = age_years
assets['last_pm_days'] = last_pm_days
assets['mtbf'] = mtbf
assets['location'] = location
assets['risk_level'] = pd.cut(assets['health_score'], bins=[0, 40, 70, 100], labels=['High Risk', 'Medium Risk', 'Low Risk'])

n_wo = 500
work_orders = pd.DataFrame({
    'wo_id' :[f'WO--{i:05d}' for i in range(1, n_wo+1)],
    'type' : np.random.choice(['Corrective', 'Preventice',' Emergency','Inspection'], n_wo, p=[0.35, 0.40,0.10, 0.15]),
    'status' : np.random.choice(['Open', 'In Progress','Completed', 'Deferred'], n_wo, p=[0.25, 0.20, 0.45, 0.10]),
    'Priority' : np.random.choice(['Critical', 'High', 'Medium', 'Low'], n_wo, p=[0.10, 0.25, 0.40, 0.25]),
    'planned_cost' : np.random.lognormal(7.1, 0.9, n_wo),
    'actual_cost' : np.random.lognormal(7.1, 0.9, n_wo) ,
    'days_open' : np.random.exponential(12, n_wo).clip(1, 90),
    'month' :np.random.choice(['Jan', 'Feb', 'Mar', 'APR', 'May', 'Jun', 'Jul'], n_wo)
})
work_orders['cost_variance'] = work_orders['actual_cost'] - work_orders['planned_cost']
work_orders['Over_budget'] = work_orders['cost_variance']>0

print("Data Generated Successfully!")
print(f"Assets: {len(assets)} | Work  Orders: {len(work_orders)}")



# ── Dashboard Layout ──────────────────────────────────────
app = dash.Dash(__name__)

NAVY = '#1B3A6B'
RED = '#E50914'
GRAY = '#F2F4F7'

app.layout = html.Div(style={'backgroundColor': '#F8F9FA', 'fontFamily': 'Arial'}, children=[

    # Header
    html.Div(style={'backgroundColor': NAVY, 'padding': '20px', 'marginBottom': '20px'}, children=[
        html.H1('EAM Operations Dashboard', style={'color': 'white', 'margin': 0, 'fontSize': '28px'}),
        html.P('Asset Health | Work Orders | Maintenance KPIs | Cost Analysis', 
               style={'color': '#AAB8C2', 'margin': '5px 0 0 0'})
    ]),

    # KPI Cards Row
    html.Div(style={'display': 'flex', 'gap': '20px', 'padding': '0 20px 20px'}, children=[
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 
                        'flex': 1, 'borderLeft': f'4px solid {NAVY}'}, children=[
            html.H3(f"{len(assets)}", style={'color': NAVY, 'margin': 0, 'fontSize': '36px'}),
            html.P('Total Assets', style={'color': '#666', 'margin': '5px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'flex': 1, 'borderLeft': '4px solid #E74C3C'}, children=[
            html.H3(f"{(assets['risk_level'] == 'High Risk').sum()}", 
                    style={'color': '#E74C3C', 'margin': 0, 'fontSize': '36px'}),
            html.P('High Risk Assets', style={'color': '#666', 'margin': '5px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'flex': 1, 'borderLeft': '4px solid #F39C12'}, children=[
            html.H3(f"{(work_orders['status'] == 'Open').sum()}", 
                    style={'color': '#F39C12', 'margin': 0, 'fontSize': '36px'}),
            html.P('Open Work Orders', style={'color': '#666', 'margin': '5px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'flex': 1, 'borderLeft': '4px solid #27AE60'}, children=[
            html.H3(f"{assets['health_score'].mean():.1f}%", 
                    style={'color': '#27AE60', 'margin': 0, 'fontSize': '36px'}),
            html.P('Avg Asset Health Score', style={'color': '#666', 'margin': '5px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px',
                        'flex': 1, 'borderLeft': f'4px solid {NAVY}'}, children=[
            html.H3(f"{(work_orders['type'] == 'Preventive').sum() / len(work_orders) * 100:.1f}%",
                    style={'color': NAVY, 'margin': 0, 'fontSize': '36px'}),
            html.P('PM Compliance Rate', style={'color': '#666', 'margin': '5px 0 0 0'})
        ]),
    ]),

    # Charts Row 1
    html.Div(style={'display': 'flex', 'gap': '20px', 'padding': '0 20px 20px'}, children=[
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'flex': 1}, children=[
            dcc.Graph(id='health-by-category')
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'flex': 1}, children=[
            dcc.Graph(id='wo-status')
        ]),
    ]),

    # Charts Row 2
    html.Div(style={'display': 'flex', 'gap': '20px', 'padding': '0 20px 20px'}, children=[
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'flex': 1}, children=[
            dcc.Graph(id='risk-distribution')
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'flex': 1}, children=[
            dcc.Graph(id='cost-analysis')
        ]),
    ]),
])

# ── Callbacks ─────────────────────────────────────────────
@app.callback(Output('health-by-category', 'figure'), Input('health-by-category', 'id'))
def health_chart(_):
    avg_health = assets.groupby('category')['health_score'].mean().reset_index()
    fig = px.bar(avg_health, x='health_score', y='category', orientation='h',
                 title='Average Asset Health Score by Category',
                 color='health_score', color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'])
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
    return fig

@app.callback(Output('wo-status', 'figure'), Input('wo-status', 'id'))
def wo_chart(_):
    wo_counts = work_orders.groupby(['status', 'type']).size().reset_index(name='count')
    fig = px.bar(wo_counts, x='status', y='count', color='type',
                 title='Work Orders by Status and Priority',
                 color_discrete_map={'Critical': '#E74C3C', 'High': '#F39C12', 
                                     'Medium': '#3498DB', 'Low': '#95A5A6'})
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    return fig

@app.callback(Output('risk-distribution', 'figure'), Input('risk-distribution', 'id'))
def risk_chart(_):
    risk_counts = assets['risk_level'].value_counts().reset_index()
    risk_counts.columns = ['risk_level', 'count']
    fig = px.pie(risk_counts, values='count', names='risk_level',
                 title='Asset Risk Distribution',
                 color_discrete_map={'High Risk': '#E74C3C', 
                                     'Medium Risk': '#F39C12', 
                                     'Low Risk': '#27AE60'})
    fig.update_layout(paper_bgcolor='white')
    return fig

@app.callback(Output('cost-analysis', 'figure'), Input('cost-analysis', 'id'))
def cost_chart(_):
    monthly = work_orders.groupby('month').agg(
        planned=('planned_cost', 'sum'),
        actual=('actual_cost', 'sum')
    ).reset_index()
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly['month'] = pd.Categorical(monthly['month'], categories=month_order, ordered=True)
    monthly = monthly.sort_values('month')
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Planned Cost', x=monthly['month'], 
                         y=monthly['planned'], marker_color='#1B3A6B'))
    fig.add_trace(go.Bar(name='Actual Cost', x=monthly['month'], 
                         y=monthly['actual'], marker_color='#E74C3C'))
    fig.update_layout(title='Planned vs Actual Maintenance Cost by Month',
                      plot_bgcolor='white', paper_bgcolor='white', barmode='group')
    return fig

if __name__ == '__main__':
    app.run(debug=True)



