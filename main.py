import functions as ft
import data as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd


TEXTO = input("Introduce el ticker del activo que quieras visualizar. ")
activo = TEXTO
TEXTO2 = input("Introduce la estrategia que quieras visualizar. ")
estrategia = TEXTO2

def date_act(symbol):
    date = dt.precios.get(symbol)
    return date['Date']


def open_act(symbol):
    open = dt.precios.get(symbol)
    return open['Open']


def close_act(symbol):
    close = dt.precios.get(symbol)
    return close['Close']


def vol_act(symbol):
    vol = dt.precios.get(symbol)
    return vol['Volume']

def low_act(symbol):
    low = dt.precios.get(symbol)
    return low['Low']

def high_act(symbol):
    high = dt.precios.get(symbol)
    return high['High']


date = pd.Series.to_frame(date_act(activo))
price_open = pd.Series.to_frame(open_act(activo))
price_close = pd.Series.to_frame(close_act(activo))
v_act = pd.Series.to_frame(vol_act(activo))
low_price = pd.Series.to_frame(low_act(activo))
high_price = pd.Series.to_frame(high_act(activo))

df_act = pd.DataFrame(date)
df_act['Open'] = price_open
df_act['Close'] = price_close
df_act['Volume'] = v_act
df_act['Low Price'] = low_price
df_act['High Price'] = high_price

estrategia_promedio_smi = ft.fechas_precios_orden(activo, estrategia)[4]
señales_1 = estrategia_promedio_smi.groupby(estrategia_promedio_smi.posicion)
buy_str_1 = señales_1.get_group("Compra")
sell_str_1 = señales_1.get_group("Venta")

estategia_rsi = ft.estrategia_rsi(activo)[4]
estrategia_macd = ft.estrategia_macd(activo)[4]

app = dash.Dash()

# DEFINICIÓN LAYOUT
app.layout = html.Div([
                    html.Div([
                    html.Label('Selección'),
                    dcc.Dropdown(id='selector',
                        options=[
                            {'label': 'Apertura', 'value': 'Open'},
                            {'label': 'Cierre', 'value': 'Close'},
                        ],
                        value='Close'
                    )], style={'width': '48%', 'display': 'inline-block'}),

                    html.Div([
                    html.Label('Rango fechas'),
                    dcc.DatePickerRange(id='selector_fecha',start_date=df_act["Date"].min(),end_date=df_act["Date"].max()),
                    ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

                    dcc.Graph(id='lineplot'),

                    dcc.Graph(id='barplot'),

                    dcc.Graph(id='Candlestick'),

                    dcc.Graph(id='estrategia1')
                              ])


@app.callback(Output('lineplot', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('selector', 'value')])
def actualizar_graph_line(fecha_min, fecha_max, seleccion):
    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]

    if seleccion == "Open":
        return{
            'data': [go.Scatter(x=filtered_df["Date"],
                                y=filtered_df["Open"],
                                mode='lines'
                                )],
            'layout': go.Layout(
                title="Activo Cotizacion",
                xaxis={'title': "Fecha"},
                yaxis={'title': "Valor cotización a apertura"},
                hovermode='closest'
            )}

    else:
        return{
            'data': [go.Scatter(x=filtered_df["Date"],
                                y=filtered_df["Close"],
                                mode="lines")],
            'layout': go.Layout(
                title="Activo Cotización",
                xaxis={'title': "Fecha"},
                yaxis={'title': "Valor cotización a cierre"},
                hovermode='closest'
                )
    }


@app.callback(Output('barplot', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date')])
def actualizar_graph_bar(fecha_min, fecha_max):
    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    return{
        'data': [go.Bar(x=filtered_df["Date"],
                        y=filtered_df["Volume"])],

        'layout': go.Layout(title="Activo Volumen negociado",
                        xaxis=dict(title="Fecha"),
                        yaxis=dict(title="Volumen"))
            }


@app.callback(Output('Candlestick', 'figure'),
              [Input('selector_fecha', 'start_date'), Input('selector_fecha','end_date')])
def actualizar_candle_line(fecha_min,fecha_max):
    filtered_df = df_act[(df_act["Date"] >= fecha_min) & (df_act["Date"] <= fecha_max)]
    return{
        'data': [go.Candlestick(x = filtered_df["Date"],
                                 low = filtered_df["Low Price"],
                                 high = filtered_df["High Price"],
                                 close = filtered_df["Close"],
                                 open = filtered_df["Open"],
                                 increasing_line_color='green',
                                 decreasing_line_color='red')],

        'layout': go.Layout(title="Activo velas",
                           xaxis=dict(title="Fecha"),
                           yaxis=dict(title="Price" ))
    }


@app.callback(Output('estrategia1', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date')])
def actualizar_estrategia1(fecha_min, fecha_max):
    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    fig = go.Figure
    return{

        'data': [fig.add_trace([go.Scatter(x=filtered_df["Date"],
                                            y=filtered_df["Close"],
                                            mode="lines")]),

                fig.add_candlestick(x=estrategia_promedio_smi["Date"],
                                    low=sell_str_1["precios"],
                                    high=buy_str_1["precios"],
                                    close=filtered_df["Close"],
                                    open=filtered_df["Open"],
                                    increasing_line_color='green',
                                    decreasign_line_color='red')],

        'layout': go.Layout(title="Estrategia_promedios",
                            xaxis=dict(title="fecha"),
                            yaxis=dict(title="Price"))
    }



# Sentencias para abrir el servidor al ejecutar este script
if __name__ == '__main__':
    app.run_server()
