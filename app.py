import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from spark import load_data_from_hdfs, transform_data

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample layout
app.layout = html.Div([
    dcc.Dropdown(
        id='year-dropdown',
        options=[
            {'label': '2022', 'value': 2022},
            {'label': '2023', 'value': 2023},
            {'label': '2024', 'value': 2024},
        ],
        value=2022
    ),
    dcc.Dropdown(
        id='driver-dropdown',
        options=[
            {'label': 'Charles Leclerc', 'value': 'leclerc'},
            {'label': 'Oscar Piastri', 'value': 'piastri'},
            {'label': 'Lando Norris', 'value': 'norris'},
            {'label': 'Carlos Sainz', 'value': 'sainz'},
            {'label': 'Lewis Hamilton', 'value': 'hamilton'},
            {'label': 'Max Verstappen', 'value': 'max_verstappen'},
            # Add other drivers as needed
        ],
        value='piastri'
    ),
    dcc.Dropdown(
        id='track-dropdown',
        options=[
            {'label': 'Italian Grand Prix', 'value': 'Italian Grand Prix'},
            {'label': 'Australian Grand Prix', 'value': 'Australian Grand Prix'},
            {'label': 'British Grand Prix', 'value': 'British Grand Prix'},
            # Add other tracks as needed
        ],
        value='Italian Grand Prix'
    ),
    dcc.Dropdown(
        id='session-dropdown',
        options=[
            {'label': 'FP1', 'value': 'FP1'},
            {'label': 'FP2', 'value': 'FP2'},
            {'label': 'FP3', 'value': 'FP3'},
            {'label': 'Qualifying', 'value': 'Qualifying'},
            {'label': 'Race', 'value': 'Race'},
        ],
        value='FP1'
    ),
    html.Div(id='output-container')
])

# Callback to update output based on dropdown selections
@app.callback(
    Output('output-container', 'children'),
    [Input('year-dropdown', 'value'),
     Input('driver-dropdown', 'value'),
     Input('track-dropdown', 'value'),
     Input('session-dropdown', 'value')]
)
def update_output(selected_year, selected_driver, selected_track, selected_session):
    df = load_data_from_hdfs(selected_year, selected_track, selected_session)
    if df is not None:
        transformed_data = transform_data(df, selected_driver)
        if transformed_data is not None and not transformed_data.isEmpty():
            return f'Loaded data for {selected_driver} in {selected_year} during {selected_session}.'
        else:
            return "No data available after transformation."
    else:
        return "No data loaded."

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
