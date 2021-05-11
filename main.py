import functions as ft
import data as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output
from Sentiments_download import get_tweets
import pandas as pd
from dash_html_components import Br, Div
from dash_table import DataTable


activo = 'FB'


Mensaje = "El análisis de sentimiento o sentiment analysis consiste en evaluar las emociones, actitudes y opiniones. Las organizaciones utilizan este método para obtener información que les permita comprender la forma en la que los clientes reaccionan respecto a un producto o servicio específico. " \
          "La herramienta de análisis de sentimiento utiliza tecnologías avanzadas de inteligencia artificial, como procesamiento del lenguaje natural, análisis de texto y ciencia de datos para identificar, extraer y estudiar información subjetiva. En términos más simples, clasifica un texto como positivo, negativo o neutral." \
          "Por lo que en BangNasdaq decidimos evaluar las opiniones de los ultimos 5 dias en Twitter respecto al S&P500, para conocer la opinion" \
          "de miles de personas acerca de este indicador."

def date_act(symbol):
    date = dt.precios.get(symbol)
    return date['Date']


def open_act(symbol):
    open = dt.precios.get(symbol)
    return open['Open']

def vol_act(symbol):
    vol = dt.precios.get(symbol)
    return vol['Volume']

def close_act(symbol):
    close = dt.precios.get(symbol)
    return close['Close']

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


estrategia_promedio = ft.seleccion_estrategia(activo,'promedios')[4]
señales_1 = estrategia_promedio.groupby(estrategia_promedio.posicion)
buy_str_1 = señales_1.get_group("Compra")
sell_str_1 = señales_1.get_group("Venta")

estrategia_smi = ft.seleccion_estrategia(activo,'smi')[4]
señales_2 = estrategia_smi.groupby(estrategia_smi.posicion)
buy_str_2 = señales_2.get_group("Compra")
sell_str_2 = señales_2.get_group("Venta")

estrategia_rsi = ft.seleccion_estrategia(activo,'rsi')[4]
señales_3 = estrategia_rsi.groupby(estrategia_rsi.posicion)
buy_str_3 = señales_3.get_group("Compra")
sell_str_3 = señales_3.get_group("Venta")

estrategia_macd = ft.seleccion_estrategia(activo,'macd')[4]
señales_4 = estrategia_macd.groupby(estrategia_macd.posicion)
buy_str_4 = señales_4.get_group("Compra")
sell_str_4 = señales_4.get_group("Venta")

#Sentimental
df = get_tweets(stock="SPY",update="upyes")
#upyes
#to update Sentimental analysis due limitations of free Twitter free API
df = pd.read_csv("$SPY_tweets.csv")

hist = px.histogram(df['Polarity'], color=df['Sentiment'],nbins= 9,
                    color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "yellow"},
                    width=830,  # figure width in pixels
                    height=300,
                    title='Histogram Sentiment'
                    )
pos = df[df['result'] == 1][['created_at', 'Polarity']]
pos = pos.sort_values(by='created_at', ascending=True)
pos['MA Polarity'] = pos.Polarity.rolling(50, min_periods=10).mean()
neg = df[df['result'] == -1][['created_at', 'Polarity']]
neg = neg.sort_values(by='created_at', ascending=True)
neg['MA Polarity'] = neg.Polarity.rolling(50, min_periods=10).mean()

area_chart = go.Figure()
area_chart.add_trace(
    go.Scatter(x=pos['created_at'], y=pos['MA Polarity'], fill='tozeroy', fillcolor='rgba(26,150,65,0.5)', mode='lines',
               line_color='green', name='Positive'))  # fill down to xaxis
area_chart.add_trace(
    go.Scatter(x=neg['created_at'], y=-neg['MA Polarity'], fill='tozeroy', fillcolor='rgba(230,131,131,0.5)',
               mode='lines', line_color='red', name='Negative'))  # fill to trace0 y
area_chart.update_xaxes(title_text='Date')
area_chart.update_yaxes(title_text='Sentiment')
area_chart.update_layout(title_text="Sentiments")

pie_chart = px.pie(
    data_frame=df,
    values=df['result'].value_counts(),
    names=df['Sentiment'].value_counts().index,
    color=df['Sentiment'].value_counts().index,  # differentiate markers (discrete) by color
    # color_discrete_sequence=["red","green","blue"],     #set marker colors
    color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "yellow"},
    hover_name=df['Sentiment'].value_counts().index,  # values appear in bold in the hover tooltip
    # hover_data=['positive'],          #values appear as extra data in the hover tooltip
    # custom_data=['total'],            #values are extra data to be used in Dash callbacks
    title='Tweets Sentiment',  # figure title
    template='presentation',  # 'ggplot2', 'seaborn', 'simple_white', 'plotly',
    width=830,  # figure width in pixels
    height=300,  # figure height in pixels
    hole=0.5,   # represents the hole in middle of pie
)
pie_chart.update_traces(hoverinfo='label+percent', textinfo='percent+label', textfont_size=10,
                        marker=dict(line=dict(color='#000000', width=2)))

#Recomendacion:

def recomendation(df):
    pos = df['result'].value_counts(normalize=True)
    if pos[1] >= .6:
        signal = html.H3('⬆️️Compra fuerte⬆️',style = {'color': 'green' ,'text-align': 'center'})
    elif pos[1] > .2 and pos[1] < .6 and pos[-1] < pos[1]:
        signal = html.H3('⬆️Compra⬆️',style = {'color': 'green' , 'text-align': 'center'})
    elif pos[0] > pos[1] or pos[0] > pos[-1] or pos[1] == pos[-1]:
        signal = html.H3('Neutral',style = {'color': 'yellow', 'text-align': 'center'})
    elif pos[-1] >= .6:
        signal = html.H3('⬇️Venta⬇️',style = {'color': 'red','text-align': 'center'})
    elif pos[-1] > .2 and pos[-1] < .6 and pos[1] < pos[-1]:
        signal = html.H3('⬇️Venta fuerte⬇️',style = {'color': 'red','text-align': 'center'})
    return signal


#%%
app = dash.Dash()

# DEFINICIÓN LAYOUT
app.layout = html.Div([
                dcc.Tabs([
                    dcc.Tab(label='Estrategias', children=[
                        html.Div(className='row',children=[
                            html.Div(className='four columns div-user-controls',children=[
                                html.Label('Precios de: '),
                                dcc.Dropdown(id='selector',
                                options=[
                                {'label': 'Apertura', 'value': 'Open'},
                                {'label': 'Cierre', 'value': 'Close'}
                                ],
                                value='Close'
                                ),
                            html.Div([
                            html.Label('Rango de fechas'),
                            dcc.DatePickerRange(id='selector_fecha',start_date=df_act["Date"].min(),end_date=df_act["Date"].max()),
                        ]),
                            html.Div([
                            html.Label('Stock: '),
                            dcc.Dropdown(id='Stock',
                                             options=[
                                                {'label': 'AAPL','value': 'AAPL'},
                                                {'label': 'MSFT','value': 'MSFT'},
                                                {'label': 'AMZN','value': 'AMZN'},
                                                {'label': 'TSLA','value': 'TSLA'},
                                                {'label': 'GOOG','value': 'GOOG'},
                                                {'label': 'FB','value': 'FB'},
                                                {'label': 'GOOGL','value': 'GOOGL'},
                                                {'label': 'NVDA','value': 'NVDA'},
                                                {'label': 'PYPL','value': 'PYPL'},
                                                {'label': 'NFLX','value': 'NFLX'},
                                                {'label': 'INTC','value': 'INTC'},
                                                {'label': 'ADBE','value': 'ADBE'},
                                                {'label': 'CMCSA','value': 'CMCSA'},
                                                {'label': 'CSCO','value': 'CSCO'},
                                                {'label': 'PEP','value': 'PEP'},
                                                {'label': 'AVGO','value': 'AVGO'},
                                                {'label': 'QCOM','value': 'QCOM'},
                                                {'label': 'COST','value': 'COST'},
                                                {'label': 'TXN','value': 'TXN'},
                                                {'label': 'TMUS','value': 'TMUS'},
                                                {'label': 'AMGN','value': 'AMGN'},
                                                {'label': 'SBUX','value': 'SBUX'},
                                                {'label': 'CHTR','value': 'CHTR'},
                                                {'label': 'AMD','value': 'AMD'},
                                                {'label': 'INTU','value': 'INTU'},
                                                {'label': 'MELI','value': 'MELI'},
                                                {'label': 'AMAT','value': 'AMAT'},
                                                {'label': 'MU','value': 'MU'},
                                                {'label': 'ISRG','value': 'ISRG'},
                                                {'label': 'BKNG','value': 'BKNG'},
                                                {'label': 'GILD','value': 'GILD'},
                                                {'label': 'JD','value': 'JD'},
                                                {'label': 'ZM','value': 'ZM'},
                                                {'label': 'MDLZ','value': 'MDLZ'},
                                                {'label': 'ATVI','value': 'ATVI'},
                                                {'label': 'FISV','value': 'FISV'},
                                                {'label': 'BIDU','value': 'BIDU'},
                                                {'label': 'LRCX','value': 'LRCX'},
                                                {'label': 'ADP','value': 'ADP'},
                                                {'label': 'MRNA','value': 'MRNA'},
                                                {'label': 'CSX','value': 'CSX'},
                                                {'label': 'ADSK','value': 'ADSK'},
                                                {'label': 'ILMN','value': 'ILMN'},
                                                {'label': 'PDD','value': 'PDD'},
                                                {'label': 'VRTX','value': 'VRTX'},
                                                {'label': 'ADI','value': 'ADI'},
                                                {'label': 'REGN','value': 'REGN'},
                                                {'label': 'NXPI','value': 'NXPI'},
                                                {'label': 'ALGN','value': 'ALGN'},
                                                {'label': 'MNST','value': 'MNST'},
                                                {'label': 'WDAY','value': 'WDAY'},
                                                {'label': 'DOCU','value': 'DOCU'},
                                                {'label': 'KDP','value': 'KDP'},
                                                {'label': 'KLAC','value': 'KLAC'},
                                                {'label': 'WBA','value': 'WBA'},
                                                {'label': 'EBAY','value': 'EBAY'},
                                                {'label': 'IDXX','value': 'IDXX'},
                                                {'label': 'EXC','value': 'EXC'},
                                                {'label': 'ROST','value': 'ROST'},
                                                {'label': 'MAR','value': 'MAR'},
                                                {'label': 'ASML','value': 'ASML'},
                                                {'label': 'LULU','value': 'LULU'},
                                                {'label': 'MTCH','value': 'MTCH'},
                                                {'label': 'SNPS','value': 'SNPS'},
                                                {'label': 'KHC','value': 'KHC'},
                                                {'label': 'EA','value': 'EA'},
                                                {'label': 'BIIB','value': 'BIIB'},
                                                {'label': 'AEP','value': 'AEP'},
                                                {'label': 'NTES','value': 'NTES'},
                                                {'label': 'CTSH','value': 'CTSH'},
                                                {'label': 'DXCM','value': 'DXCM'},
                                                {'label': 'PTON','value': 'PTON'},
                                                {'label': 'CDNS','value': 'CDNS'},
                                                {'label': 'MCHP','value': 'MCHP'},
                                                {'label': 'CTAS','value': 'CTAS'},
                                                {'label': 'SGEN','value': 'SGEN'},
                                                {'label': 'OKTA','value': 'OKTA'},
                                                {'label': 'ALXN','value': 'ALXN'},
                                                {'label': 'MRVL','value': 'MRVL'},
                                                {'label': 'PCAR','value': 'PCAR'},
                                                {'label': 'XLNX','value': 'XLNX'},
                                                {'label': 'XEL','value': 'XEL'},
                                                {'label': 'PAYX','value': 'PAYX'},
                                                {'label': 'ANSS','value': 'ANSS'},
                                                {'label': 'ORLY','value': 'ORLY'},
                                                {'label': 'TEAM','value': 'TEAM'},
                                                {'label': 'VRSK','value': 'VRSK'},
                                                {'label': 'SWKS','value': 'SWKS'},
                                                {'label': 'CPRT','value': 'CPRT'},
                                                {'label': 'SPLK','value': 'SPLK'},
                                                {'label': 'FAST','value': 'FAST'},
                                                {'label': 'SIRI','value': 'SIRI'},
                                                {'label': 'DLTR','value': 'DLTR'},
                                                {'label': 'CERN','value': 'CERN'},
                                                {'label': 'MXIM','value': 'MXIM'},
                                                {'label': 'VRSN','value': 'VRSN'},
                                                {'label': 'CDW','value': 'CDW'},
                                                {'label': 'INCY','value': 'INCY'},
                                                {'label': 'TCOM','value': 'TCOM'},
                                                {'label': 'CHKP','value': 'CHKP'},
                                                {'label': 'FOXA','value': 'FOXA'}
                                             ],
                                             value='FB'
                                             ),
                                    ]),
                            ]),
                        html.Div(className='eight columns div-for-charts bg-grey', children=[
                            html.H6('💣 BangNasdaq 💣 ',style={'textAlign': 'center'}),
                            html.H5('',style={'textAlign': 'center'}),
                            dcc.Graph(id='lineplot'),
                            dcc.Graph(id='barplot'),
                            dcc.Graph(id='Candlestick'),
                            dcc.Graph(id='estrategia1'),
                            html.Div(id='dt_estrategia1', style={'width': '40%', 'font-size':'15px',
                                                                 'align': 'center','font-family': 'verdana',
                                                                 'margin-left': 'auto', 'margin-right': 'auto'}),
                            dcc.Graph(id='estrategia2'),
                            html.Div(id='dt_estrategia2', style={'width': '40%', 'font-size': '15px',
                                                                 'align': 'center', 'font-family': 'verdana',
                                                                 'margin-left': 'auto', 'margin-right': 'auto'}),
                            dcc.Graph(id='estrategia3'),
                            html.Div(id='dt_estrategia3', style={'width': '40%', 'font-size': '15px',
                                                                 'align': 'center', 'font-family': 'verdana',
                                                                 'margin-left': 'auto', 'margin-right': 'auto'}),
                            dcc.Graph(id='estrategia4'),
                            html.Div(id='dt_estrategia4', style={'width': '40%', 'font-size': '15px',
                                                                 'align': 'center', 'font-family': 'verdana',
                                                                 'margin-left': 'auto', 'margin-right': 'auto'}),

                              ])
                            ])]),
                    dcc.Tab(label='Analisis Sentimental $SPY', children=[
                    html.Div(children=[
                        html.Div(className='row',  # Define the row element
                            children=[
                                html.Div(className='four columns div-user-controls',
                                    children=[
                                       html.H2('Analisis sentimental $SPY'),
                                       html.P(Mensaje),
                                       html.H3('Bang recommendation 😎:'),
                                       recomendation(df)
                                           ]),  # Define the left element
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                           children=[
                                                   html.H6('💣 BangNasdaq 💣',style={'textAlign': 'center'}),
                                                   dcc.Graph(id = 'pie_chart',figure = pie_chart),
                                                   dcc.Graph(id = 'hist',figure = hist),
                                                   dcc.Graph(id = 'area_char',figure = area_chart)

                                           ])  # Define the right element
                                  ])
                                ])
                    ])
    ])
])




@app.callback(Output('lineplot', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('selector', 'value'), Input('Stock','value')])

def actualizar_graph_line(fecha_min, fecha_max, seleccion, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price

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
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('Stock','value')])

def actualizar_graph_bar(fecha_min, fecha_max, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price
    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    return{
        'data': [go.Bar(x=filtered_df["Date"],
                        y=filtered_df["Volume"])],

        'layout': go.Layout(title="Activo Volumen negociado",
                        xaxis=dict(title="Fecha"),
                        yaxis=dict(title="Volumen"))
            }


@app.callback(Output('Candlestick', 'figure'),
              [Input('selector_fecha', 'start_date'), Input('selector_fecha','end_date'),Input('Stock','value')])

def actualizar_candle_line(fecha_min, fecha_max, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price
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
                           yaxis=dict(title="Precio" ))
    }


@app.callback(Output('estrategia1', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('Stock','value')])

def actualizar_estrategia1(fecha_min, fecha_max, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price

    estrategia_promedio = ft.seleccion_estrategia(Stock, 'promedios')[4]
    señales_1 = estrategia_promedio.groupby(estrategia_promedio.posicion)
    buy_str_1 = señales_1.get_group("Compra")
    sell_str_1 = señales_1.get_group("Venta")

    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    sell1_df = sell_str_1[(sell_str_1["fechas"] >= fecha_min) & (sell_str_1['fechas']<= fecha_max)]
    buy1_df = buy_str_1[(buy_str_1["fechas"] >= fecha_min) & (buy_str_1['fechas'] <= fecha_max)]
    return{

        'data': [go.Scatter(x = filtered_df["Date"], y = filtered_df["Close"],mode = 'lines', name = 'Activo'),
                 go.Scatter(x = sell1_df["fechas"],
                             y=sell1_df["precios"], mode='markers',marker_color = 'red',marker_size=10,name = 'Venta',opacity=0.8,marker_symbol = 'triangle-down'),
                 go.Scatter(x=buy1_df["fechas"],
                            y=buy1_df["precios"], mode='markers', marker_color='green',marker_size=10,name = 'Compra',opacity=0.8,marker_symbol = 'triangle-up')
                 ],

        'layout': go.Layout(title="Estrategia promedios",
                            xaxis=dict(title="Fecha"),
                            yaxis=dict(title="Precio"))
    }


@app.callback(Output('dt_estrategia1', 'children'),
              Input('Stock', 'value'))
def actualizar_table_estrategia1(Stock):
    radio_sharpe = ft.CFA_sharperatio(Stock, 'promedios')
    radio_sharpe_buy = radio_sharpe[0]
    radio_sharpe_buy = radio_sharpe_buy.rename(columns={"Sharpe":"Sharpe promedios compra"})
    radio_sharpe_sell = radio_sharpe[1]
    radio_sharpe_sell = radio_sharpe_sell.rename(columns={"Sharpe":"Sharpe promedios venta"})
    duration = ft.medida_duracion(Stock, 'promedios')
    duration_data_frame = pd.DataFrame(columns = ["Duracion Señal Compra","Duracion Señal Venta"], index=range(1,2))
    duration_data_frame["Duracion Señal Compra"] = duration[0]
    duration_data_frame["Duracion Señal Venta"] = duration[1]
    effect = ft.medida_efectividad(Stock,'promedios')
    effect_data_frame = pd.DataFrame(columns = ["Efectividad Señal Compra","Efectividad Señal Venta"], index=range(1,2))
    effect_data_frame["Efectividad Señal Compra"] = effect[0]
    effect_data_frame["Efectividad Señal Venta"] = effect[1]
    trackingerror = ft.CFA_trackingerror(Stock, 'promedios')
    trackingerror_data_frame = pd.DataFrame(columns = ["Señal Compra","Señal Venta"], index=range(1,2))
    trackingerror_data_frame["Señal Compra"] = trackingerror[0]
    trackingerror_data_frame["Señal Venta"] = trackingerror[1]


    columns1 = [{"name": i, "id": i } for i in radio_sharpe_buy.columns]
    columns2 = [{"name": i, "id": i} for i in radio_sharpe_sell.columns]
    columns3 = [{"name": i, "id": i} for i in duration_data_frame.columns]
    columns4 = [{"name": i, "id": i} for i in effect_data_frame.columns]
    columns5 = [{"name": i, "id": i} for i in trackingerror_data_frame.columns]

    data1 = radio_sharpe_buy.to_dict('records')
    data2 = radio_sharpe_sell.to_dict('records')
    data3 = duration_data_frame.to_dict('records')
    data4 = effect_data_frame.to_dict('records')
    data5 = trackingerror_data_frame.to_dict('records')

    return Div([
        DataTable(columns=columns1, data=data1, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white',
    },),
        Br(),
        DataTable(columns=columns2, data=data2, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns3, data=data3, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns4, data=data4, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns5, data=data5, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
                ])


@app.callback(Output('estrategia2', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('Stock','value')])

def actualizar_estrategia2(fecha_min, fecha_max, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price

    estrategia_smi = ft.seleccion_estrategia(Stock, 'smi')[4]
    señales_2 = estrategia_smi.groupby(estrategia_smi.posicion)
    buy_str_2 = señales_2.get_group("Compra")
    sell_str_2 = señales_2.get_group("Venta")

    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    sell2_df = sell_str_2[(sell_str_2["fechas"] >= fecha_min) & (sell_str_2['fechas']<= fecha_max)]
    buy2_df = buy_str_2[(buy_str_2["fechas"] >= fecha_min) & (buy_str_2['fechas'] <= fecha_max)]
    return{

        'data': [go.Scatter(x = filtered_df["Date"], y = filtered_df["Close"],mode = 'lines', name = 'Activo'),
                 go.Scatter(x = sell2_df["fechas"],
                             y=sell2_df["precios"], mode='markers',marker_color = 'red',marker_size=10,name = 'Venta',opacity=0.8,marker_symbol = 'triangle-down'),
                 go.Scatter(x=buy2_df["fechas"],
                            y=buy2_df["precios"], mode='markers', marker_color='green',marker_size=10,name = 'Compra',opacity=0.8,marker_symbol = 'triangle-up')
                 ],

        'layout': go.Layout(title="Estrategia SMI",
                            xaxis=dict(title="Fecha"),
                            yaxis=dict(title="Precio"))
    }


@app.callback(Output('dt_estrategia2', 'children'),
              Input('Stock', 'value'))
def actualizar_table_estrategia2(Stock):
    radio_sharpe = ft.CFA_sharperatio(Stock, 'smi')
    radio_sharpe_buy = radio_sharpe[0]
    radio_sharpe_buy = radio_sharpe_buy.rename(columns={"Sharpe":"Sharpe smi compra"})
    radio_sharpe_sell = radio_sharpe[1]
    radio_sharpe_sell = radio_sharpe_sell.rename(columns={"Sharpe":"Sharpe smi venta"})
    duration = ft.medida_duracion(Stock, 'smi')
    duration_data_frame = pd.DataFrame(columns = ["Duracion Señal Compra","Duracion Señal Venta"], index=range(1,2))
    duration_data_frame["Duracion Señal Compra"] = duration[0]
    duration_data_frame["Duracion Señal Venta"] = duration[1]
    effect = ft.medida_efectividad(Stock,'smi')
    effect_data_frame = pd.DataFrame(columns = ["Efectividad Señal Compra","Efectividad Señal Venta"], index=range(1,2))
    effect_data_frame["Efectividad Señal Compra"] = effect[0]
    effect_data_frame["Efectividad Señal Venta"] = effect[1]
    trackingerror = ft.CFA_trackingerror(Stock, 'smi')
    trackingerror_data_frame = pd.DataFrame(columns = ["Señal Compra","Señal Venta"], index=range(1,2))
    trackingerror_data_frame["Señal Compra"] = trackingerror[0]
    trackingerror_data_frame["Señal Venta"] = trackingerror[1]

    columns1 = [{"name": i, "id": i } for i in radio_sharpe_buy.columns]
    columns2 = [{"name": i, "id": i} for i in radio_sharpe_sell.columns]
    columns3 = [{"name": i, "id": i} for i in duration_data_frame.columns]
    columns4 = [{"name": i, "id": i} for i in effect_data_frame.columns]
    columns5 = [{"name": i, "id": i} for i in trackingerror_data_frame.columns]

    data1 = radio_sharpe_buy.to_dict('records')
    data2 = radio_sharpe_sell.to_dict('records')
    data3 = duration_data_frame.to_dict('records')
    data4 = effect_data_frame.to_dict('records')
    data5 = trackingerror_data_frame.to_dict('records')

    return Div([
        DataTable(columns=columns1, data=data1, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white',
    },),
        Br(),
        DataTable(columns=columns2, data=data2, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns3, data=data3, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns4, data=data4, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns5, data=data5, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
                ])


@app.callback(Output('estrategia3', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('Stock','value')])

def actualizar_estrategia3(fecha_min, fecha_max, Stock):

    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price

    estrategia_rsi = ft.seleccion_estrategia(Stock, 'rsi')[4]
    señales_3 = estrategia_rsi.groupby(estrategia_rsi.posicion)
    buy_str_3 = señales_3.get_group("Compra")
    sell_str_3 = señales_3.get_group("Venta")

    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    sell3_df = sell_str_3[(sell_str_3["fechas"] >= fecha_min) & (sell_str_3['fechas']<= fecha_max)]
    buy3_df = buy_str_3[(buy_str_3["fechas"] >= fecha_min) & (buy_str_3['fechas'] <= fecha_max)]
    return{

        'data': [go.Scatter(x = filtered_df["Date"], y = filtered_df["Close"],mode = 'lines', name = 'Activo'),
                 go.Scatter(x = sell3_df["fechas"],
                             y=sell3_df["precios"], mode='markers',marker_color = 'red',marker_size=10,name = 'Venta',opacity=0.8,marker_symbol = 'triangle-down'),
                 go.Scatter(x=buy3_df["fechas"],
                            y=buy3_df["precios"], mode='markers', marker_color='green',marker_size=10,name = 'Compra',opacity=0.8,marker_symbol = 'triangle-up')
                 ],

        'layout': go.Layout(title="Estrategia RSI",
                            xaxis=dict(title="Fecha"),
                            yaxis=dict(title="Precio"))
    }


@app.callback(Output('dt_estrategia3', 'children'),
              Input('Stock', 'value'))
def actualizar_table_estrategia3(Stock):
    radio_sharpe = ft.CFA_sharperatio(Stock, 'rsi')
    radio_sharpe_buy = radio_sharpe[0]
    radio_sharpe_buy = radio_sharpe_buy.rename(columns={"Sharpe":"Sharpe rsi compra"})
    radio_sharpe_sell = radio_sharpe[1]
    radio_sharpe_sell = radio_sharpe_sell.rename(columns={"Sharpe":"Sharpe rsi venta"})
    duration = ft.medida_duracion(Stock, 'rsi')
    duration_data_frame = pd.DataFrame(columns = ["Duracion Señal Compra","Duracion Señal Venta"], index=range(1,2))
    duration_data_frame["Duracion Señal Compra"] = duration[0]
    duration_data_frame["Duracion Señal Venta"] = duration[1]
    effect = ft.medida_efectividad(Stock,'rsi')
    effect_data_frame = pd.DataFrame(columns = ["Efectividad Señal Compra","Efectividad Señal Venta"], index=range(1,2))
    effect_data_frame["Efectividad Señal Compra"] = effect[0]
    effect_data_frame["Efectividad Señal Venta"] = effect[1]
    trackingerror = ft.CFA_trackingerror(Stock, 'rsi')
    trackingerror_data_frame = pd.DataFrame(columns = ["Señal Compra","Señal Venta"], index=range(1,2))
    trackingerror_data_frame["Señal Compra"] = trackingerror[0]
    trackingerror_data_frame["Señal Venta"] = trackingerror[1]

    columns1 = [{"name": i, "id": i } for i in radio_sharpe_buy.columns]
    columns2 = [{"name": i, "id": i} for i in radio_sharpe_sell.columns]
    columns3 = [{"name": i, "id": i} for i in duration_data_frame.columns]
    columns4 = [{"name": i, "id": i} for i in effect_data_frame.columns]
    columns5 = [{"name": i, "id": i} for i in trackingerror_data_frame.columns]

    data1 = radio_sharpe_buy.to_dict('records')
    data2 = radio_sharpe_sell.to_dict('records')
    data3 = duration_data_frame.to_dict('records')
    data4 = effect_data_frame.to_dict('records')
    data5 = trackingerror_data_frame.to_dict('records')

    return Div([
        DataTable(columns=columns1, data=data1, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white',
    },),
        Br(),
        DataTable(columns=columns2, data=data2, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns3, data=data3, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns4, data=data4, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns5, data=data5, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
                ])


@app.callback(Output('estrategia4', 'figure'),
              [Input('selector_fecha', 'start_date'),Input('selector_fecha', 'end_date'),Input('Stock','value')])

def actualizar_estrategia4(fecha_min, fecha_max, Stock):
    date = pd.Series.to_frame(date_act(Stock))
    price_open = pd.Series.to_frame(open_act(Stock))
    price_close = pd.Series.to_frame(close_act(Stock))
    v_act = pd.Series.to_frame(vol_act(Stock))
    low_price = pd.Series.to_frame(low_act(Stock))
    high_price = pd.Series.to_frame(high_act(Stock))

    df_act = pd.DataFrame(date)
    df_act['Open'] = price_open
    df_act['Close'] = price_close
    df_act['Volume'] = v_act
    df_act['Low Price'] = low_price
    df_act['High Price'] = high_price

    estrategia_macd = ft.seleccion_estrategia(Stock, 'macd')[4]
    señales_4 = estrategia_macd.groupby(estrategia_macd.posicion)
    buy_str_4 = señales_4.get_group("Compra")
    sell_str_4 = señales_4.get_group("Venta")

    filtered_df = df_act[(df_act["Date"]>=fecha_min) & (df_act["Date"]<=fecha_max)]
    sell4_df = sell_str_4[(sell_str_4["fechas"] >= fecha_min) & (sell_str_4['fechas']<= fecha_max)]
    buy4_df = buy_str_4[(buy_str_4["fechas"] >= fecha_min) & (buy_str_4['fechas'] <= fecha_max)]
    return{

        'data': [go.Scatter(x = filtered_df["Date"], y = filtered_df["Close"],mode = 'lines', name = 'Activo'),
                 go.Scatter(x = sell4_df["fechas"],
                             y=sell4_df["precios"], mode='markers',marker_color = 'red',marker_size=10,name = 'Venta',opacity=0.8,marker_symbol = 'triangle-down'),
                 go.Scatter(x=buy4_df["fechas"],
                            y=buy4_df["precios"], mode='markers', marker_color='green',marker_size=10,name = 'Compra',opacity=0.8,marker_symbol = 'triangle-up')
                 ],

        'layout': go.Layout(title="Estrategia MACD",
                            xaxis=dict(title="Fecha"),
                            yaxis=dict(title="Precio"))
    }


@app.callback(Output('dt_estrategia4', 'children'),
              Input('Stock', 'value'))
def actualizar_table_estrategia4(Stock):
    radio_sharpe = ft.CFA_sharperatio(Stock, 'macd')
    radio_sharpe_buy = radio_sharpe[0]
    radio_sharpe_buy = radio_sharpe_buy.rename(columns={"Sharpe":"Sharpe macd compra"})
    radio_sharpe_sell = radio_sharpe[1]
    radio_sharpe_sell = radio_sharpe_sell.rename(columns={"Sharpe":"Sharpe macd venta"})
    duration = ft.medida_duracion(Stock, 'macd')
    duration_data_frame = pd.DataFrame(columns = ["Duracion Señal Compra","Duracion Señal Venta"], index=range(1,2))
    duration_data_frame["Duracion Señal Compra"] = duration[0]
    duration_data_frame["Duracion Señal Venta"] = duration[1]
    effect = ft.medida_efectividad(Stock,'macd')
    effect_data_frame = pd.DataFrame(columns = ["Efectividad Señal Compra","Efectividad Señal Venta"], index=range(1,2))
    effect_data_frame["Efectividad Señal Compra"] = effect[0]
    effect_data_frame["Efectividad Señal Venta"] = effect[1]
    trackingerror = ft.CFA_trackingerror(Stock, 'macd')
    trackingerror_data_frame = pd.DataFrame(columns = ["Señal Compra","Señal Venta"], index=range(1,2))
    trackingerror_data_frame["Señal Compra"] = trackingerror[0]
    trackingerror_data_frame["Señal Venta"] = trackingerror[1]


    columns1 = [{"name": i, "id": i } for i in radio_sharpe_buy.columns]
    columns2 = [{"name": i, "id": i} for i in radio_sharpe_sell.columns]
    columns3 = [{"name": i, "id": i} for i in duration_data_frame.columns]
    columns4 = [{"name": i, "id": i} for i in effect_data_frame.columns]
    columns5 = [{"name": i, "id": i} for i in trackingerror_data_frame.columns]

    data1 = radio_sharpe_buy.to_dict('records')
    data2 = radio_sharpe_sell.to_dict('records')
    data3 = duration_data_frame.to_dict('records')
    data4 = effect_data_frame.to_dict('records')
    data5 = trackingerror_data_frame.to_dict('records')

    return Div([
        DataTable(columns=columns1, data=data1, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white',
    },),
        Br(),
        DataTable(columns=columns2, data=data2, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(25,25,112)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns3, data=data3, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns4, data=data4, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
        Br(),
        DataTable(columns=columns5, data=data5, style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
        'backgroundColor': 'rgb(47,79,79)',
        'color': 'white'
    },),
                ])

# Sentencias para abrir el servidor al ejecutar este script
if __name__ == '__main__':
    app.run_server()
