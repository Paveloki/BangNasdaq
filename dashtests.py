import functions as ft
import data as dt
import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd

TEXTO = "FB"
activo = TEXTO
TEXTO2 = "promedios"
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

traces_estr_1=[]

app = dash.Dash()

for position in estrategia_promedio_smi['posicion'].unique():
    df_position_1=estrategia_promedio_smi[estrategia_promedio_smi['posicion'] == position]
    traces_estr_1.append(go.Scatter(
        x=estrategia_promedio_smi["fechas"],
        y=estrategia_promedio_smi["precios"],
        text=df_position_1["posicion"],
        mode="markers",
        opacity=0.7,
        marker={'size': 5},
        name=position
    ))

app.layout = html.Div([
    html.Div([
    dcc.Graph(
        id='strategy_plot',
        figure={
            'data': traces_estr_1,
            'layout': go.Layout(
                xaxis={'title': 'Fecha'},
                yaxis={'title': 'Precios'},
                hovermode='closest'
            )
        }
    )], style={'width':'30%', 'float':'left'}),

    html.Div([
    html.Pre(id='hover-data', style={'paddingTop':35}) #Elemento HTML Pre (preformateado) conserva espacios y saltos de línea
    ], style={'width':'25%'}),

    html.Div([
    dcc.Graph(id='estrategia_promedios_plot')], style={'width':'30%', 'float':'right'})
])

# CREACIÓN DE INTERACTIVIDAD
#Callback para devolver en componente Pre hover-data la información en formato json respecto a dónde tengamos el cursor en temp_plot
@app.callback(
    Output('hover-data', 'children'),
    [Input('temp_plot', 'hoverData')]) #poder usar las propiedades hoverData, clickData o selectedD
def callback_json(hoverData):
    return json.dumps(hoverData, indent=2) #Información json con propiedades de hoverData

# CREACIÓN DE INTERACTIVIDAD
#Callback para crear un gráfico dinámico con la temperatura máxima y mínima en función de donde tengamos el cursor en temp_plot
@app.callback(
    Output('estrategia_promedios_plot', 'figure'),
    [Input('strategy_plot', 'hoverData')]) #poder usar las propiedades hoverData, clickData o selectedData
def act_grafico(hoverdata):
    v_index = hoverdata['points'][0]['pointIndex']
    print(v_index)

    trace1=go.Scatter(
        x = [buy_str_1.iloc[v_index]['fechas']], #iloc seleccionar la fila del dataframe en base a un índice: v_index
        y = [buy_str_1.iloc[v_index]['posicion']],
        mode='markers',
        name='Compra')

    trace2=go.Scatter(
        x = [sell_str_1.iloc[v_index]['fechas']],
        y = [sell_str_1.iloc[v_index]['posicion']],
        mode='markers',
        name='Venta')


    fig = {
        'data': [trace1, trace2],
        'layout': go.Layout(
            title = "Compra y venta",
            xaxis=dict(title="Fecha"),
            yaxis={'title':"Precios", 'range':[estrategia_promedio_smi["fechas"].min(),estrategia_promedio_smi["fechas"].max()]}
            )}
    return fig

#Sentencias para abrir el servidor al ejecutar este script
if __name__ == '__main__':
    app.run_server(debug=True, port=8100)
