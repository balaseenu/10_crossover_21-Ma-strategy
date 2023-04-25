'''
Importing all the requierd libraries 

'''
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, date

''' 
Nifty 50 stocks import 

'''
def get_50nsedata():
    # change the filename if requierd
    data = pd.read_csv('ind_nifty50.csv')
    nse_50data = data['Symbol'].to_list()
    nse_50data = nse_50data[1:]
    return nse_50data

'''
Download data from Yahoo finance based on stock name and date, interval
'''
def get_histdata(ticker, startdate, enddate, interval):
    support_pivot = []
    pivot_r1 = []
    resistance1_up = []
    accu_out1 = []
    accu_out2 = []
    accu_out3 = []
    tickk = ["{}.ns".format(tick) for tick in ticker]
    for line in tickk:
        symbol = line.split(",")[0]
        data = yf.download(symbol, start=startdate, end=enddate, interval=interval)
        data = data[(data[['Volume']] != 0).all(axis=1)]
        data['Date'] = data.index
        data = pivot_cal(data)
        sup1, sup2, sup3, s_and_p, p_and_r, r_and_m = Stock_inrange(data,symbol,support_pivot,pivot_r1,resistance1_up,accu_out1,accu_out2,accu_out3)
    return sup1, sup2, sup3, s_and_p, p_and_r, r_and_m
'''
calculate support resistance and pivot region
'''
def pivot_cal(rate):
    pivot              = round((rate['High']+rate['Low']+rate['Close'])/3 ,2)
    rate['Pivot']      = pivot
    support_1          = round((pivot*2)-rate['High'],2)
    rate['support_1']  = support_1
    resistance_1       = round((pivot*2)-rate['Low'],2)
    rate['resistance_1'] = resistance_1
    support_2          = round(pivot -(rate['High']-rate['Low']),2)
    rate['support_2']  = support_2
    resistance_2       = round(pivot +(rate['High']-rate['Low']),2)
    rate['resistance_2'] = resistance_2
    support_3          = round(rate['Low']-2*(rate['High']-pivot),2)
    rate['support_3']  = support_3
    resistance_3       = round(rate['High']+2*(pivot-rate['Low']),2)
    rate['resistance_3'] = resistance_3
    return rate

def Stock_inrange(data,symbol,support_pivot,pivot_r1,resistance1_up,accu_out1,accu_out2,accu_out3):
    cur_price = float(round(data['Close'].iloc[-1],2))
    sup_zone = float(round(data['support_1'].iloc[-1],2))
    pivot_zone = float(round(data['Pivot'].iloc[-1],2))
    res_zone = float(round(data['resistance_1'].iloc[-1],2))
    if ((cur_price >= sup_zone) and (cur_price <= pivot_zone)):
        support_pivot.append(symbol)
        accu_out = more_accuracy(data,symbol)
        accu_out1.append(accu_out)
    elif ((cur_price >= pivot_zone) and (cur_price <= res_zone)):
        pivot_r1.append(symbol)
        accu_out = more_accuracy(data,symbol)
        accu_out2.append(accu_out)
    elif cur_price > res_zone:
        resistance1_up.append(symbol)
        accu_out = more_accuracy(data,symbol)
        accu_out3.append(accu_out)
    else:
        pass
    return support_pivot,pivot_r1,resistance1_up,accu_out1,accu_out2,accu_out3
    
def more_accuracy(rate,stockname):
    if round(rate['Close'].iloc[-1].item(),2) > round(rate['Open'].iloc[-1].item(),2) and round(rate['Close'].iloc[-2].item(),2) > round(rate['Open'].iloc[-2].item(),2) and round(rate['Close'].iloc[-3].item(),2) > round(rate['Open'].iloc[-3].item(),2):
        return stockname
    else:
        pass
    
def function_call(ticker, startdate, enddate, interval):
    print('inside function call')
    sup1, sup2, sup3, s_and_p, p_and_r, r_and_m = get_histdata(ticker, startdate, enddate, interval)
    s_and_p = list(filter(lambda item: item is not None, s_and_p))
    p_and_r = list(filter(lambda item: item is not None, p_and_r))
    r_and_m = list(filter(lambda item: item is not None, r_and_m))
    print('support to pivot zone : ', sup1)
    print('pivot to resistance zone : ', sup2)
    print('greater than resistance zone : ', sup3)
    print('last 3 green candle, support to pivot zone : ', s_and_p)
    print('last 3 green candle, pivot to resistance zone : ', p_and_r)
    print('last 3 green candle, resistance zone : ', r_and_m)
    print('completed')
    
    

    