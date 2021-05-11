import numpy as np
import pandas as pd
from enum import Enum
import matplotlib as mt
import matplotlib.pyplot as plt
import tti
from tti.indicators import StochasticMomentumIndex as smi
from tti.indicators import _moving_average_convergence_divergence as macd
from tti.indicators import RelativeStrengthIndex as rsi
import data as dt
import datetime as dat
from scipy.signal import argrelextrema
import statistics as st
import math
from statistics import stdev as de


class ActionColorMapping(Enum):
    SELL = 'red'
    BUY = 'green'


class ActionPricePoint:
    def __init__(self, price, date, action):
        self.price = price
        self.date = date
        self.action = action


def sell():
    return lambda left, right: left < right


def buy():
    return lambda left, right: left >= right


def plot(price, ma_20, ma_100, action_price_points):
    ax = price.plot(figsize=(16, 10))

    ma_20.plot(label='Promedio móvil 20 dias', ax=ax)
    ma_100.plot(label='Promedio móvil 100 dias', ax=ax)

    ax.set_xlabel('Número de día', fontsize=18)
    ax.set_ylabel('Precio de cierre', fontsize=18)
    ax.set_title('Activo', fontsize=20)
    ax.legend(loc='upper left', fontsize=15)

    for position in action_price_points:
        plt.scatter(position.date, position.price, s=600, c=position.action.value)

    plt.show()


def retrieve_closing_price(symbol):
    df = dt.precios.get(symbol)
    return df['Close']


def data_not_available(price):
    return np.isnan(price)


def estrategia_promediosm(symbol):
    closing_price = retrieve_closing_price(symbol)

    rm_20 = closing_price.rolling(window=20).mean()
    rm_100 = closing_price.rolling(window=100).mean()

    action = ActionColorMapping.SELL
    signal_detected = sell()
    signals = []
    buy_signal = []
    sell_signal = []

    for index in range(closing_price.size):
        if data_not_available(rm_20[index]) or data_not_available(rm_100[index]):
            continue

        if signal_detected(rm_20[index], rm_100[index]):
            mean_price = (rm_20[index] + rm_100[index]) / 2
            action = ActionPricePoint(mean_price, index, action)
            signals.append(action)

        if rm_20[index] >= rm_100[index]:
            action = ActionColorMapping.SELL
            signal_detected = sell()
            buy_signal.append(index)
        else:
            action = ActionColorMapping.BUY
            signal_detected = buy()
            sell_signal.append(index)
    return buy_signal, sell_signal, signals, closing_price, rm_20, rm_100


def estrategia_mm(symbol):
    """
    :param symbol: Este es el activo que el usuario decida.
    :return: Senales tanto de venta como de compra, asi como las fechas de ambas posiciones.
    """
    df = dt.precios.get(symbol)

    date = []
    price = []
    value = []
    for position in estrategia_promediosm(symbol)[2]:
        date.append(position.date)
        price.append(position.price)
        value.append(position.action.value)

    venta = []
    venta_fech = []
    compra = []
    compra_fech = []
    for n in range(len(value)):
        if value[n] == 'red':
            venta.append(price[n])
            venta_fech.append(date[n])
        elif value[n] == 'green':
            compra.append(price[n])
            compra_fech.append(date[n])

    lista_buy = []
    lista_sell = []
    for i in compra_fech:
        lista_buy.append(df['Date'][i])

    for i in venta_fech:
        lista_sell.append(df['Date'][i])

    return compra, venta, lista_buy, lista_sell


def fechas_precios_orden(symbol, estrategia):
    """
    :param symbol: Este es el activo que el usuario decida.
    :param estrategia:
    :return:
    """
    precios = dt.precios.get(symbol)

    if estrategia == 'promedios':
        p1 = estrategia_mm(symbol)[2]
        p2 = estrategia_mm(symbol)[3]
        fecha_compra = estrategia_mm(symbol)[2]
        fecha_venta = estrategia_mm(symbol)[3]
    elif estrategia == 'smi':
        p1 = estrategia_smi(symbol)[2]
        p2 = estrategia_smi(symbol)[3]
        fecha_compra = estrategia_smi(symbol)[2]
        fecha_venta = estrategia_smi(symbol)[3]
    fechasc = []
    preciosc = []
    counter = 0
    for i in range(len(precios['Date'])):
        if counter <= len(p1) - 1:
            if p1[counter] == precios['Date'][i]:
                fechasc.append(p1[counter])
                preciosc.append(precios['Close'][i])
                counter += 1
            else:
                fechasc.append(np.nan)
                preciosc.append(np.nan)
        else:
            fechasc.append(np.nan)
            preciosc.append(np.nan)

    fechasv = []
    preciosv = []
    counterv = 0
    for i in range(len(precios['Date'])):
        if counterv <= len(p2) - 1:
            if p2[counterv] == precios['Date'][i]:
                fechasv.append(p2[counterv])
                preciosv.append(precios['Close'][i])
                counterv += 1
            else:
                fechasv.append(np.nan)
                preciosv.append(np.nan)
        else:
            fechasv.append(np.nan)
            preciosv.append(np.nan)

    lista_Buy = [preciosc[i] for i in range(len(preciosc)) if math.isnan(preciosc[i]) is False]
    lista_Sell = [preciosv[i] for i in range(len(preciosv)) if math.isnan(preciosv[i]) is False]

    senales = []
    senales.extend(lista_Buy)
    senales.extend(lista_Sell)

    fechas = []
    fechas.extend(fecha_compra)
    fechas.extend(fecha_venta)

    posicion = []
    for i in range(len(senales)):
        if senales[i] in lista_Buy:
            posicion.append('Compra')
        elif senales[i] in lista_Sell:
            posicion.append('Venta')

    datos = pd.DataFrame()
    datos['fechas'] = fechas
    datos['precios'] = senales
    datos['posicion'] = posicion
    return preciosc, preciosv, fecha_compra, fecha_venta, datos


# def rsi_manual(symbol):
#     df = dt.precios.get(symbol)
#     n = 14  # len(df)
#     i = 0
#     upi = [0]
#     doi = [0]
#     while i + 1 <= df.index[-1]:
#         upmove = df['High'][i + 1] - df['High'][i]
#         domove = df['Low'][i] - df['Low'][i + 1]
#         if upmove > domove and upmove > 0:
#             upd = upmove
#         else:
#             upd = 0
#         upi.append(upd)
#         if domove > upmove and domove > 0:
#             dod = domove
#         else:
#             dod = 0
#         doi.append(dod)
#         i = i + 1
#     upi = pd.Series(upi)
#     doi = pd.Series(doi)
#     posdi = pd.Series(pd.Series.ewm(upi, span=n, min_periods=n - 1).mean())
#     negdi = pd.Series(pd.Series.ewm(doi, span=n, min_periods=n - 1).mean())
#     RSI = pd.Series(posdi / (posdi + negdi), name='RSI_' + str(n))
#     df = df.join(RSI)
#     df.set_index('Date', inplace=True)
#     x = range(len(df.index))
#     fig = plt.figure(figsize=(16, 8))
#     gs = mt.gridspec.GridSpec(2, 1, figure=fig, height_ratios=[3, 1])
#     plt.plot(x, df.Close)
#     plt.grid(True)
#     plt.title('RSI_' + str(symbol))
#     plt.plot(x, df.RSI_14, color='r')
#     plt.axhline(y=0.7, color='k', linestyle='--')
#     plt.axhline(y=0.3, color='k', linestyle='--')
#     plt.legend()
#     plt.grid(True)
#     plt.show()
#     return df


def soporteresistencia(symbol):
    """
    :param symbol: Esta variable, al igual que las demas funciones, necesita el nombre del ticker que quiere visualizar.
    :return: Grafica con los soportes/resistencias creados bajo la condiciones mencionadas en el codigo.
    """
    df = dt.precios.get(symbol)
    data = df.set_index('Date')

    pivot = []  # Se inicializa la variable pivot, aqui se iran pegando los puntos pivote que existan en la data.
    dates = []  # Aqui al igual que en pivot, se pegaran las fechas donde fueron los pivotes.
    counter = 0  # Este es un contador que noayudara a saber si el puntos es el maximo

    Range = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # Este rango es para verificar que el punto sea el mas alto.
    dateRange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in data.index:
        currentMax = max(Range, default=0)
        value = round(data['High'][i], 2)

        Range = Range[1:9]
        Range.append(value)
        dateRange = dateRange[1:9]
        dateRange.append(i)

        if currentMax == max(Range, default=0):
            counter += 1
        else:
            counter = 0

        if counter == 5:
            lastPivot = currentMax
            dateloc = Range.index(lastPivot)
            lastDate = dateRange[dateloc]

            pivot.append(lastPivot)
            dates.append(lastDate)

    timeD = dat.timedelta(days=60)

    for index in range(len(pivot)):
        print(str(pivot[index]) + ": " + str(dates[index]))

        plt.plot_date([dates[index], dates[index] + timeD],
                      [pivot[index], pivot[index]], linestyle="-", linewidth=2, marker=",")

    data['High'].plot(label='High')
    plt.show()


def stochastic(symbol):
    """
    :param symbol:
    :return:
    """

    df = dt.precios.get(symbol)
    data = df.set_index('Date')

    # stoch3 = smi(input_data=data, period=5, smoothing_period=3, double_smoothing_period=3)
    # stoch12 = smi(input_data=data, period=5, smoothing_period=5, double_smoothing_period=5)
    stoch3 = smi(input_data=data, period=3, smoothing_period=3)
    stoch12 = smi(input_data=data, period=5, smoothing_period=5)
    stoch3 = stoch3.getTiData()
    stoch12 = stoch12.getTiData()
    stoch3.reset_index(inplace=True)
    stoch12.reset_index(inplace=True)
    return df, stoch3, stoch12


def smiventa(symbol):
    """
    :param symbol: Ticker que es el que el usuario quiere visualizar
    :return: Datos numericos, de las senales de venta.
    """
    df = stochastic(symbol=symbol)[0]
    stoch3 = stochastic(symbol=symbol)[1]

    y = np.array(stoch3['smi'])
    x = np.linspace(1, len(y), y.size)

    peaks_indx = argrelextrema(y, np.greater)[0]
    numeros_max = [p for p in peaks_indx]

    fechas_max = []
    puntaje_smi_max = []
    precio_max = []

    for n in numeros_max:
        fechas_max.append(df['Date'][n])
        puntaje_smi_max.append(stoch3['smi'][n])
        precio_max.append(df['High'][n])

    fechas = []
    puntaje = []
    preciov = []

    for i in range(len(numeros_max) - 1):
        if puntaje_smi_max[i] > 40:
            fechas.append(fechas_max[i])
            puntaje.append(puntaje_smi_max[i])
            preciov.append(precio_max[i])
    return fechas, puntaje, preciov


def smicompra(symbol):
    """
    :param symbol: Ticker que el usuario quiere visualizar.
    :return: Datos numericos para las senales de compra.
    """
    df = stochastic(symbol=symbol)[0]
    stoch3 = stochastic(symbol=symbol)[1]

    y = np.array(stoch3['smi'])

    peaks_indx = argrelextrema(y, np.less)[0]
    numeros_min = [p for p in peaks_indx]

    fechas_min = []
    puntaje_smi_min = []
    precio_min = []

    for n in numeros_min:
        fechas_min.append(df['Date'][n])
        puntaje_smi_min.append(stoch3['smi'][n])
        precio_min.append(df['Low'][n])

    fechasc = []
    puntajec = []
    precioc = []

    for i in range(len(numeros_min) - 1):
        if puntaje_smi_min[i] < -40:
            fechasc.append(fechas_min[i])
            puntajec.append(puntaje_smi_min[i])
            precioc.append(precio_min[i])
    return fechasc, puntajec, precioc


def estrategia_smi(symbol):
    """
    :param symbol:
    :return:
    """
    grsventa = []
    grpventa = []
    grscompra = []
    grpcompra = []
    preciov = []
    precioc = []

    precioventa = smiventa(symbol)[2]
    pivot = smiventa(symbol)[1]
    senalventa = smiventa(symbol)[0]
    preciocompra = smicompra(symbol)[2]
    pivotcompra = smicompra(symbol)[1]
    senalcompra = smicompra(symbol)[0]

    for i in range(len(precioventa) - 1):
        difv1 = precioventa[i] - precioventa[i - 1]
        difv2 = pivot[i] - pivot[i - 1]
        if difv1 > 0 and difv2 < 0 or difv1 < 0 and difv2 > 0:
            grsventa.append(senalventa[i])
            grpventa.append(pivot[i])
            preciov.append(precioventa[i])

        else:
            pass

    for i in range(len(preciocompra) - 1):
        difv1 = preciocompra[i] - preciocompra[i - 1]
        difv2 = pivotcompra[i] - pivotcompra[i - 1]
        if difv1 > 0 and difv2 < 0 or difv1 < 0 and difv2 > 0:
            grscompra.append(senalcompra[i])
            grpcompra.append(pivotcompra[i])
            precioc.append(preciocompra[i])

        else:
            pass

    return precioc, preciov, grscompra, grsventa, grpventa, grpcompra


# def smivisual(symbol):
#     """
#     :param symbol: El ticker que el ussuario decida.
#     :return: Visualmente, te grafica mediante el indicador las senales.
#     """
#     stoch3 = stochastic(symbol)[1]
#     stoch12 = stochastic(symbol)[2]
#     grsventa = estrategia_smi(symbol)[0]
#     grpventa = estrategia_smi(symbol)[1]
#     grscompra = estrategia_smi(symbol)[3]
#     grpcompra = estrategia_smi(symbol)[4]
#
#     plt.figure(figsize=(16, 12))
#     plt.plot(stoch3['Date'], stoch3['smi'], label='Smooth 3')
#     plt.plot(stoch12['Date'], stoch12['smi'], label='Smooth 5')
#     plt.scatter(grsventa, grpventa, s=120, c='red', label='Puntos de venta')
#     plt.scatter(grscompra, grpcompra, s=120, c='green', label='Puntos de compra')
#     plt.title('STOCHASTIC MOMENTUM INDEX STRATEGY', size=20)
#     plt.axhline(40, 0, 1)
#     plt.axhline(-40, 0, 1)
#     plt.legend()
#     plt.show()


# def smiestrategia(symbol):
#     """
#     :param symbol: Es el ticker del activo que se quiere visualizar
#     :return: Grafica en donde aparecen los precios historicos del activo y sus respectivas senales.
#     """
#     # Fijamos los datos que necesitamos para la grafica.
#     # Estos provienen de otras funciones anteriores, como stochastic() y smiconjunto()
#     df = stochastic(symbol=symbol)[0]
#     grsventa = estrategia_smi(symbol)[0]
#     preciov = estrategia_smi(symbol)[2]
#     grscompra = estrategia_smi(symbol)[3]
#     precioc = estrategia_smi(symbol)[5]
#
#     plt.figure(figsize=(16, 12))
#     plt.plot(df['Date'], df['Close'], label='Close')
#     plt.scatter(grsventa, preciov, s=120, c='red', label='Puntos de venta')
#     plt.scatter(grscompra, precioc, s=120, c='green', label='Puntos de compra')
#     plt.title('STOCHASTIC MOMENTUM INDEX STRATEGY', size=20)
#     plt.legend()
#     plt.show()


def estrategia_macd(symbol):
    """
    :param symbol: El ticker que el usuario decida visualizar y analizar.
    :return: Grafica las senales de venta o compra que analice la estrategia
    """
    df = dt.precios.get(symbol)  # Dataframe de precios descargados de yahoo finance
    # data = df.set_index('Date')  # Pones la columna Date como index, esto se necesita para la libreria de indicadores
    # signal = macd.MovingAverageConvergenceDivergence(input_data=data)  # Este es el indicador de MACD
    # signal = signal.getTiData()  # Guardas variables numericas en signal
    shortema = df.Close.ewm(span=12, adjust=False).mean()
    longema = df.Close.ewm(span=26, adjust=False).mean()
    macd2 = shortema - longema
    signal_s = macd2.ewm(span=9, adjust=False).mean()

    signal = pd.DataFrame()
    signal['macd'] = macd2
    signal['signal_line'] = signal_s

    Buy = []
    buydate = []
    Sell = []
    selldate = []
    flag = -1

    for i in range(0, len(signal)):
        if signal['macd'][i] > signal['signal_line'][i]:
            Sell.append(np.nan)
            if flag != 1:
                Buy.append(df['Close'][i])
                buydate.append(df['Date'][i])
                flag = 1
            else:
                #  pass
                Buy.append(np.nan)
        elif signal['macd'][i] < signal['signal_line'][i]:
            Buy.append(np.nan)
            if flag != 0:
                Sell.append(df['Close'][i])
                selldate.append(df['Date'][i])
                flag = 0
            else:
                #  pass
                Sell.append(np.nan)
        else:
            #  pass
            Buy.append(np.nan)
            Sell.append(np.nan)

    lista_Buy = [Buy[i] for i in range(len(Buy)) if math.isnan(Buy[i]) is False]
    lista_Sell = [Sell[i] for i in range(len(Sell)) if math.isnan(Sell[i]) is False]

    senales = []
    senales.extend(lista_Buy)
    senales.extend(lista_Sell)

    fechas = []
    fechas.extend(buydate)
    fechas.extend(selldate)

    posicion = []
    for i in range(len(senales)):
        if senales[i] in lista_Buy:
            posicion.append('Compra')
        elif senales[i] in lista_Sell:
            posicion.append('Venta')

    datos = pd.DataFrame()
    datos['fechas'] = fechas
    datos['precios'] = senales
    datos['posicion'] = posicion
    return Buy, Sell, buydate, selldate, datos

    # plt.figure(figsize=(12, 8))
    # plt.plot(df['Date'], df['Close'], label='Close Price', alpha=0.35)
    # plt.scatter(df['Date'], Sell, s=120, c='red', label='Puntos de venta', marker='v', alpha=1)
    # plt.scatter(df['Date'], Buy, s=120, c='green', label='Puntos de compra', marker='^', alpha=1)
    # plt.title('MACD STRATEGY', size=20)
    # plt.xlabel('Date')
    # plt.ylabel('Close Price ($)')
    # plt.legend(loc='best')
    # plt.show()


def estrategia_rsi(symbol):
    """
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :return: Grafica con senales de compra o venta, segun lo indique el indicador.
    """

    df = dt.precios.get(symbol)  # Dataframe de precios descargados de yahoo finance
    data = df.set_index('Date')  # Pones la columna Date como index, esto se necesita para la libreria de indicadores

    r14 = rsi(input_data=data, period=14)
    r14 = r14.getTiData()

    r7 = rsi(input_data=data, period=7)
    r7 = r7.getTiData()

    senalventa = []
    puntoventa = []
    precioventa = [np.nan]
    senalcompra = []
    puntocompra = []
    preciocompra = [np.nan]

    for i in range(1, len(df['Date'])):

        if r7['rsi'][i] > 65 and r14['rsi'][i] > 65:
            preciocompra.append(np.nan)
            dif1 = float(r7['rsi'][i - 1] - r14['rsi'][i - 1])
            dif2 = float(r7['rsi'][i] - r14['rsi'][i])

            if dif1 > 0 and dif2 < 0 or dif1 < 0 and dif2 > 0:
                senalventa.append(df['Date'][i])
                puntoventa.append(r7['rsi'][i])
                precioventa.append(df['Close'][i])
            else:
                precioventa.append(np.nan)

        elif r7['rsi'][i] < 35 and r14['rsi'][i] < 35:
            precioventa.append(np.nan)
            dif1 = float(r7['rsi'][i - 1] - r14['rsi'][i - 1])
            dif2 = float(r7['rsi'][i] - r14['rsi'][i])

            if dif1 > 0 and dif2 < 0 or dif1 < 0 and dif2 > 0:
                senalcompra.append(df['Date'][i])
                puntocompra.append(r7['rsi'][i])
                preciocompra.append(df['Close'][i])
            else:
                preciocompra.append(np.nan)

        else:
            preciocompra.append(np.nan)
            precioventa.append(np.nan)

    lista_Buy = [preciocompra[i] for i in range(len(preciocompra)) if math.isnan(preciocompra[i]) is False]
    lista_Sell = [precioventa[i] for i in range(len(precioventa)) if math.isnan(precioventa[i]) is False]

    senales = []
    senales.extend(lista_Buy)
    senales.extend(lista_Sell)

    fechas = []
    fechas.extend(senalcompra)
    fechas.extend(senalventa)

    posicion = []
    for i in range(len(senales)):
        if senales[i] in lista_Buy:
            posicion.append('Compra')
        elif senales[i] in lista_Sell:
            posicion.append('Venta')

    datos = pd.DataFrame()
    datos['fechas'] = fechas
    datos['precios'] = senales
    datos['posicion'] = posicion
    return preciocompra, precioventa, senalcompra, senalventa, datos


def mediana(lista):
    """
    :param lista: Se entrega una lista en donde se contegan los valores a los cuales se le quiera sacar la mediana.
    :return: Mediana de la lista.
    """
    med = st.median(lista)  # Libreria de statistics para el calculo de la mediana
    #  Se deja la mediana en numero entero.
    return med


def contador(symbol, pruebas):
    """
    :param pruebas: Estas son las variables que se entregan en cada una de las estrategias (punto de venta o compra)
    :param symbol: Este es el activo que el usuario quiere visualizar.
    :return: Regresa dos lista en donde cuenta la duración de cada una de las estrategias.
    """

    precios = dt.precios.get(symbol)  # Dataframe de precios descargados de yahoo finance

    # lista_buy = np.where(precios['Close'] == pruebas[0])
    # lista_sell = np.where(precios['Close'] == pruebas[1])

    lista_buy = []
    for i in range(len(pruebas[2])):
        for n in range(len(precios['Date'])):
            if precios['Date'][n] == pruebas[2][i]:
                lista_buy.append(n)

    lista_sell = []
    for i in range(len(pruebas[3])):
        for n in range(len(precios['Date'])):
            if precios['Date'][n] == pruebas[3][i]:
                lista_sell.append(n)

    lista_counter_buy = []
    for i in range(len(lista_buy)):
        numero = lista_buy[i]
        counter = 0
        for n in range(1, 100):
            dif = precios['Close'][numero] - precios['Open'][numero]
            if dif > 0:
                counter += 1
                numero += 1
            else:
                lista_counter_buy.append(counter)
                break

    lista_counter_sell = []
    for i in range(len(lista_sell)):
        numero = lista_sell[i]
        counter = 0
        for n in range(1, 100):
            dif = precios['Open'][numero] - precios['Close'][numero]
            if dif > 0:
                counter += 1
                numero += 1
            else:
                lista_counter_sell.append(counter)
                break
    return lista_counter_buy, lista_counter_sell


def seleccion_estrategia(symbol, estrategia: str):
    """
    :param symbol:
    :param estrategia: Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :return:
    """

    if estrategia == 'macd':
        pruebas = estrategia_macd(symbol)
    elif estrategia == 'rsi':
        pruebas = estrategia_rsi(symbol)
    elif estrategia == 'promedios':
        pruebas = fechas_precios_orden(symbol, estrategia)
    elif estrategia == 'smi':
        pruebas = fechas_precios_orden(symbol, estrategia)
    else:
        pass
    return pruebas


def medida_duracion(symbol, estrategia: str):
    """
    :param estrategia:Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :return: Te devuelve la mediana de las duraciones que ocurrieron en las senales propuestas.
    """

    pruebas = seleccion_estrategia(symbol, estrategia)
    lista = contador(symbol, pruebas)
    if len(lista[0]) == 0:
        med_buy = '-'
    else:
        med_buy = mediana(lista[0])

    if len(lista[1]) == 0:
        med_sell = '-'
    else:
        med_sell = mediana(lista[1])

    return med_buy, med_sell


def medida_efectividad(symbol, estrategia: str):
    """
    :param estrategia: Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :return: Porcentaje tanto para compra como venta, de las señales que ha propuesto el sistema, que tan efectivas.
    """

    precios = dt.precios.get(symbol)
    pruebas = seleccion_estrategia(symbol, estrategia)
    p1 = pruebas[0]
    p2 = pruebas[1]

    fechas1 = np.where(p1 == precios['Close'])
    fechas2 = np.where(p2 == precios['Close'])
    longitud = len(precios['Close'])

    dias_check = 5
    contadorc = 0
    contadorv = 0

    rends = [precios['Close'][i + dias_check] - precios['Close'][i] for i in fechas1[0]
             if (i + dias_check) <= longitud]

    for i in range(len(rends)):
        if rends[i] > 0:
            contadorc += 1

    rends2 = [precios['Close'][i] - precios['Close'][i + dias_check] for i in fechas2[0]
              if (i + dias_check) <= longitud]
    for i in range(len(rends2)):
        if rends2[i] > 0:
            contadorv += 1

    if len(rends) == 0:
        contac = '-'
    else:
        contac = str(round((contadorc / len(rends)) * 100, 2)) + ' %'

    if len(rends2) == 0:
        contav = '-'
    else:
        contav = str(round((contadorv / len(rends2)) * 100, 2)) + ' %'

    return contac, contav

def medida_claridad(symbol, estrategia: str):
    """
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :param estrategia: Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :return:
    """
    precios = dt.precios.get(symbol)
    pruebas = seleccion_estrategia(symbol, estrategia)
    p1 = pruebas[0]
    p2 = pruebas[1]

    pr = dt.NASDAQ
    fechas1 = np.where(p1 == precios['Close'])
    fechas2 = np.where(p2 == precios['Close'])

    p_rend = [(precios['Close'][i] / precios['Close'][i - 1]) - 1 for i in range(1, len(precios['Close']))]
    b_rend = [(pr['Close'][i] / pr['Close'][i - 1]) - 1 for i in range(1, len(pr['Close']))]

    vol_c = []
    vol_c_b = []
    for i in fechas1[0]:
        lista = []
        lista_b = []
        for j in range(0, i):
            lista.append(p_rend[j])
            lista_b.append(b_rend[j])
            if j == i - 1:
                lista_14 = lista[-14:-1]
                lista_14.append(lista[-1])
                lista_b_14 = lista_b[-14:-1]
                lista_b_14.append(lista_b[-1])
                vol_c.append(st.stdev(lista_14))
                vol_c_b.append(st.stdev(lista_b_14))

    vol_v = []
    vol_v_b = []
    for i in fechas2[0]:
        lista = []
        lista_b = []
        for j in range(0, i):
            lista.append(p_rend[j])
            lista_b.append(b_rend[j])
            if j == i - 1:
                lista_14 = lista[-14:-1]
                lista_14.append(lista[-1])
                lista_b_14 = lista_b[-14:-1]
                lista_b_14.append(lista_b[-1])
                vol_v.append(st.stdev(lista_14))
                vol_v_b.append(st.stdev(lista_b_14))

    tabla = pd.DataFrame()
    tabla['Activo'] = vol_c
    tabla['NASDAQ'] = vol_c_b
    tabla['Diferencia'] = [vol_c[i] - vol_c_b[i] for i in range(len(tabla['Activo']))]
    tabla['Medida'] = ['Claridad' if tabla['Diferencia'][i] > 0 else 'Sin claridad'
                       for i in range(len(tabla['Diferencia']))]

    tabla2 = pd.DataFrame()
    tabla2['Activo'] = vol_v
    tabla2['NASDAQ'] = vol_v_b
    tabla2['Diferencia'] = [vol_v[i] - vol_v_b[i] for i in range(len(tabla2['Activo']))]
    tabla2['Medida'] = ['Claridad' if tabla2['Diferencia'][i] > 0 else 'Sin claridad'
                        for i in range(len(tabla2['Diferencia']))]

    return tabla, tabla2


def CFA_sharperatio(symbol, estrategia: str):
    """
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :param estrategia: Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :return: Dataframe con el sharpe ratio de cada una de las senales generadas.
    """
    precios = dt.precios.get(symbol)  # Pedir datos/precios del simbolo a analizar.
    pruebas = seleccion_estrategia(symbol, estrategia)  # Se selecciona la estrategia para obtener resultados de esta.
    p1 = pruebas[0]  # Compra
    p2 = pruebas[1]  # Venta

    fechas1 = np.where(p1 == precios['Close'])  # Fechas en donde hubo senal de compra
    fechas2 = np.where(p2 == precios['Close'])  # Fechas en donde hubo senal de venta
    longitud = len(precios['Close'])  # Cuantos precios hay en las tablas.

    dias_check = 5  # Se selecciono 5 dias porque al comparar con otros dias, este fue el de mejor resultados.
    contadorc = 0  # Se inicia contador de compra
    contadorv = 0  # Se inicia contador de venta

    rends = [(precios['Close'][i + dias_check] / precios['Close'][i]) - 1 for i in fechas1[0]
             if (i + dias_check) <= longitud]  # Rendimientos de compra
    for i in range(len(rends)):
        if rends[i] > 0:  # Si los rendimientos en los periodos fueron mayores a 0 se cuenta un numero mas en la cuenta
            contadorc += 1  # Se agrega 1 al contador de compra

    rends2 = [(precios['Close'][i] / precios['Close'][i + dias_check]) - 1 for i in fechas2[0]
              if (i + dias_check) <= longitud]
    for i in range(len(rends2)):
        if rends2[i] > 0:  # Si los rendimientos en los periodos fueron mayores a 0 se cuenta un numero mas en la cuenta
            contadorv += 1  # Se agrega 1 al contador de venta

    scompra = [round((rends[i] - (dt.rf / 360 * 5)) / de(rends), 2) for i in range(len(rends))]  # Sharpe ratio formula
    sventa = [round((rends2[i] - (dt.rf / 360 * 5)) / de(rends2), 2) for i in range(len(rends2))]

    sharpesc = pd.DataFrame()  # Se crea un dataframe
    sharpesc['Fechas'] = [precios['Date'][fechas1[0][i]] for i in range(len(fechas1[0]))]  # Se agregan las fechas
    sharpesc['Sharpe'] = scompra  # Se coloca la lista recien creada con la formula de Sharpe ratio. (COMPRA)

    sharpev = pd.DataFrame()
    sharpev['Fechas'] = [precios['Date'][fechas2[0][i]] for i in range(len(fechas2[0]))]
    sharpev['Sharpe'] = sventa  # Se coloca la lista recien creada con la formula de Sharpe ratio. (VENTA)
    return sharpesc, sharpev


def CFA_trackingerror(symbol, estrategia: str):
    """
    :param symbol: Simbolo o ticker que el usuario decidira visualizar.
    :param estrategia: Estrategia que se quiere visualizar, de deberan usar las siguientes palabras: 'macd', 'rsi',
    'promedios', 'smi'
    :return: Dos numeros que son las desviaciones estandar con base en las senales de compra y de venta.
    """
    precios = dt.precios.get(symbol)
    pruebas = seleccion_estrategia(symbol, estrategia)
    p1 = pruebas[0]
    p2 = pruebas[1]

    fechas1 = np.where(p1 == precios['Close'])
    fechas2 = np.where(p2 == precios['Close'])
    longitud = len(precios['Close'])

    fechaschidas = []
    indexamiento = []
    rends = []
    bench = []
    for i in fechas1[0]:
        for j in range(1, 6):
            if (i + j) <= longitud:
                rends.append((precios['Close'][i + j] / precios['Close'][i + (j - 1)]) - 1)
                bench.append((dt.NASDAQ['Close'][i + j] / dt.NASDAQ['Close'][i + (j - 1)]) - 1)
                fechaschidas.append(precios['Date'][i + j])
                indexamiento.append(i)

    hoal = pd.DataFrame()
    hoal['index'] = indexamiento
    hoal['fechas'] = fechaschidas
    hoal['rends'] = rends
    hoal['Benchmark'] = bench
    hoal['Diferencia'] = [rends[i] - bench[i] for i in range(len(rends))]

    trade = 0
    trades = []
    for j in fechas1[0]:
        if j == fechas1[0][0]:
            pass
        else:
            trades.append(trade)
            trade = 0
        for i in range(len(indexamiento)):
            if hoal['index'][i] == j:
                trade += hoal['Diferencia'][i]

    trades.append(trade)

    if len(trades) <= 1:
        desviacion_trade = '-'
    else:
        estra = [trades[i] / 5 for i in range(len(trades))]
        desviacion_trade = de(estra)

    fechaschidas2 = []
    indexamiento2 = []
    rends2 = []
    bench2 = []
    for i in fechas2[0]:
        for j in range(1, 6):
            if (i + j) <= longitud:
                rends2.append((precios['Close'][i + j] / precios['Close'][i + (j - 1)]) - 1)
                bench2.append((dt.NASDAQ['Close'][i + j] / dt.NASDAQ['Close'][i + (j - 1)]) - 1)
                fechaschidas2.append(precios['Date'][i + j])
                indexamiento2.append(i)

    hoal2 = pd.DataFrame()
    hoal2['index'] = indexamiento2
    hoal2['fechas'] = fechaschidas2
    hoal2['rends'] = rends2
    hoal2['Benchmark'] = bench2
    hoal2['Diferencia'] = [rends2[i] - bench2[i] for i in range(len(rends2))]

    trade2 = 0
    trades2 = []
    for j in fechas2[0]:
        if j == fechas2[0][0]:
            pass
        else:
            trades2.append(trade2)
            trade2 = 0
        for i in range(len(indexamiento2)):
            if hoal2['index'][i] == j:
                trade2 += hoal2['Diferencia'][i]

    trades2.append(trade2)

    if len(trades2) <= 1:
        desviacion_trade2 = '-'
    else:
        estra2 = [trades2[i] / 5 for i in range(len(trades2))]
        desviacion_trade2 = de(estra2)

    return desviacion_trade, desviacion_trade2
