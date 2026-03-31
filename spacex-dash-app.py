# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create Dash app
app = dash.Dash(__name__)

# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div(children=[

    # Title
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    # Payload slider
    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),

])

# -----------------------------
# Callback 1: Pie Chart
# -----------------------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):

    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df.groupby('Launch Site')['class'].sum().reset_index(),
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig

    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Success vs Failure for {selected_site}'
        )
        return fig


# -----------------------------
# Callback 2: Scatter Plot
# -----------------------------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):

    low, high = payload_range

    # Filter by payload
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs Launch Outcome for All Sites'
        )
        return fig

    else:
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == selected_site
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs Launch Outcome for {selected_site}'
        )
        return fig


# Run app
if __name__ == '__main__':
    app.run(debug=True)