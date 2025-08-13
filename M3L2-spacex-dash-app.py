# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique sites
launch_sites = sorted(spacex_df['Launch Site'].unique())

# Create a dash application
app = dash.Dash(__name__)

app.title = "SpaceX Launch Records Dashboard"

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # Dropdown
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                            [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True,
                                    style={'width': '60%', 'margin': '0 auto'}
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                # Pie chart
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'textAlign': 'center', 'fontWeight': 'bold'}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                    value=[min_payload, max_payload],
                                    tooltip={'placement': 'bottom', 'always_visible': True}
                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                # Scatter plot
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        df_success = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df_success, names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = site_df['class'].value_counts().rename({1: 'Success', 0: 'Failure'}).reset_index()
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Launch Outcomes for {selected_site}')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('payload-slider', 'value'),
     Input('site-dropdown', 'value')]
)
def update_scatter(payload_range, selected_site):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Flight Number', 'Launch Site', 'Booster Version'],
        title=f"{'All Sites' if selected_site=='ALL' else selected_site}: Payload vs. Launch Outcome"
    )
    fig.update_yaxes(title='Launch Outcome (0 = Fail, 1 = Success)', tickvals=[0, 1])
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
