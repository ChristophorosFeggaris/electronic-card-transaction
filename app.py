import dash
from dash import dcc, html, State
from dash.dependencies import Input, Output
import pandas as pd
from dash.exceptions import PreventUpdate
from urllib.parse import quote




# Read the CSV data
df = pd.read_csv('electronic-card-transactions-october-2023-csv-tables.csv')  

# Initialize the Dash app
app = dash.Dash(__name__)
app.title="Electronic card transaction"

# Define the layout of the app
app.layout = html.Div(
    children=[
        
        html.Link(href='/assets/internet.ico', rel='icon'),
       
        html.H1("Electronic Card Transactions Dashboard", className='header'),
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='dropdown-container',
                    children=[
                        html.Label('Select Series'),
                        dcc.Dropdown(
                            id='series-dropdown',
                            options=[
                                {'label': series, 'value': series}
                                for series in df['Series_reference'].unique()
                            ],
                            value=df['Series_reference'].iloc[0],
                            multi=True,
                            placeholder="Select series",
                        ),
                    ]
                ),
                dcc.RangeSlider(
                    id='time-slider',
                    marks={i: str(i) for i in range(int(df['Period'].min()), int(df['Period'].max()) + 1)},
                    min=df['Period'].min(),
                    max=df['Period'].max(),
                    step=1,
                    value=[df['Period'].min(), df['Period'].max()],
                    className='range-slider'
                ),
                html.Button('Graph Type', id='open-modal-button'),
                html.Button('Download Data', id='download-data-button'),
                dcc.Download(id="download-data"),
            ]
        ),
        dcc.Graph(id='line-plot', className='graph-container'),
        
        html.Div(
            id='modal',
            style={'display': 'none'},
            children=[
                html.Div(
                    className='modal-content',
                    children=[
                        html.H3('Select Graph Type'),
                        dcc.Dropdown(
                            id='graph-type-dropdown',
                            options=[
                                {'label': 'Line Chart', 'value': 'line'},
                                {'label': 'Bar Chart', 'value': 'bar'},
                                {'label': 'Column Chart', 'value':'column'},
                                {'label': 'Pie Chart', 'value': 'pie'},
                                {'label': 'Area Chart', 'value': 'area'},
                                {'label': 'Scatter Chart', 'value': 'scatter'},
                            ],
                            value='line',
                            clearable=False,
                        ),
                        html.Button('Apply', id='close-modal-button'),
                    ]
                ),
            ]
        ),
    ]
)

@app.callback(
    Output('download-data', 'data'),
    [Input('download-data-button', 'n_clicks')],
    [State('series-dropdown', 'value'),
     State('time-slider', 'value'),
     State('graph-type-dropdown', 'value')],
)
def download_data(n_clicks, selected_series, selected_time, graph_type):
    if n_clicks is None:
        raise PreventUpdate

    filtered_df = df[
        (df['Series_reference'].isin(selected_series)) &
        (df['Period'] >= selected_time[0]) &
        (df['Period'] <= selected_time[1])
    ]

    if graph_type != 'pie':
        csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
    else:
        csv_string = pd.DataFrame({'Labels': labels, 'Values': values}).to_csv(index=False, encoding='utf-8')

    return dcc.send_data_frame(filtered_df.to_csv, filename="downloaded_data.csv", index=False)
@app.callback(
    Output('modal', 'style'),
    [Input('open-modal-button', 'n_clicks'),
     Input('close-modal-button', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, close_clicks):
    if open_clicks is None:
        raise PreventUpdate

    ctx = dash.callback_context
    if ctx.triggered_id == 'open-modal-button':
        return {'display': 'block'}
    elif ctx.triggered_id == 'close-modal-button':
        return {'display': 'none'}

@app.callback(
    Output('line-plot', 'figure'),
    [Input('series-dropdown', 'value'),
     Input('time-slider', 'value'),
     Input('graph-type-dropdown', 'value')],
)
def update_graph(selected_series, selected_time, graph_type):
    filtered_df = df[
        (df['Series_reference'].isin(selected_series)) &
        (df['Period'] >= selected_time[0]) &
        (df['Period'] <= selected_time[1])
    ]

    if graph_type == 'line':
        trace_type = 'line'
    elif graph_type == 'bar':
        trace_type = 'bar'
    elif graph_type == 'column':
        trace_type = 'bar'
    elif graph_type == 'area':
        trace_type = 'scatter'
        mode = 'lines'
        fill = 'tozeroy'
    elif graph_type == 'scatter':
        trace_type = 'scatter'
        mode = 'markers'
    elif graph_type == 'pie':
        trace_type = 'pie'
        labels = filtered_df['Series_reference']
        values = filtered_df['Data_value']
    else:
        raise PreventUpdate

    if graph_type != 'pie':
        fig = {
            'data': [
                {
                    'x': filtered_df[filtered_df['Series_reference'] == series]['Period'],
                    'y': filtered_df[filtered_df['Series_reference'] == series]['Data_value'],
                    'type': trace_type,
                    'name': series,
                    'mode': mode if 'mode' in locals() else None,
                    'fill': fill if 'fill' in locals() else None,
                }
                for series in selected_series
            ],
            'layout': {
                'title': 'Electronic Card Transactions Over Time',
                'xaxis': {'title': 'Period'},
                'yaxis': {'title': 'Data Value'},
            }
        }
    else:
        fig = {
            'data': [{
                'labels': labels,
                'values': values,
                'type': 'pie',
            }],
            'layout': {
                'title': 'Pie Chart of Electronic Card Transactions',
            }
        }

    return fig


# @app.callback(
#     Output('download-data-button', 'href'),
#     [Input('series-dropdown', 'value'),
#      Input('time-slider', 'value'),
#      Input('graph-type-dropdown', 'value')],
# )
# def download_data(selected_series, selected_time, graph_type):
#     filtered_df = df[
#         (df['Series_reference'].isin(selected_series)) &
#         (df['Period'] >= selected_time[0]) &
#         (df['Period'] <= selected_time[1])
#     ]

#     if graph_type != 'pie':
#         csv_string = filtered_df.to_csv(index=False, encoding='utf-8')
#     else:
#         csv_string = pd.DataFrame({'Labels': labels, 'Values': values}).to_csv(index=False, encoding='utf-8')

#     href = "data:text/csv;charset=utf-8," + quote(csv_string)
#     return href



    

if __name__ == '__main__':
    app.run_server(debug=True)
