# -*- coding: utf-8 -*-
'''
Importing all the requierd libraries 

'''
import numpy as np
#import time
#import os
import ssl
import smtplib
import pandas as pd
import yfinance as yf
#import matplotlib.pyplot as plt
#import seaborn as sns
from datetime import datetime, timedelta, date
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from Pivot_point import function_call
#%matplotlib inline

''' 
Nifty 400 stocks import 

'''
def get_400nsedata():
    data = pd.read_csv('harish.txt')
    #data = pd.read_csv('Filtered_stocks.txt')
    nse_400data = data['Symbol'].to_list()
    nse_400data = nse_400data[1:]
    return nse_400data

'''
Download data from Yahoo finance based on stock name and date, interval
'''
def get_histdata(ticker, startdate, enddate, interval):
    Buy_stock = []
    sell_stock = []
    output = []
    tickk = ["{}.ns".format(tick) for tick in ticker]
    for line in tickk:
        symbol = line.split(",")[0]
        data = yf.download(symbol, start=startdate, end=enddate, interval=interval)
        data = data[(data[['Volume']] != 0).all(axis=1)]
        data['Date'] = data.index
        data['10_Days_EMA'] = Moving_average(data,9)
        data['21_Days_EMA'] = Moving_average(data,21)
        data = data.dropna()
        data = crossover(data)
        buy,sell = find_signal(data,symbol,Buy_stock,sell_stock)
        get_volume_analysis(data,symbol,output)
        #data.to_csv('C:/Users/admin/Desktop/option chain analysis/datasets/Stock/{}.csv'.format(symbol))
    return buy,sell,data,output

def Moving_average(data,period):
    #to calculate simple moving average 
    return round(data['Close'].rolling(period).mean(),2)

def crossover(data):
    signal_buy_check = 1
    signal_sell_check = 1
    data['signal'] = ''
    len_10_days = len(data['10_Days_EMA'])
    for days in range(0,len_10_days):
        if data['10_Days_EMA'][days] > data['21_Days_EMA'][days]:
            if signal_buy_check == 1:
                #print('this is the time to buy')
                #print('BUY PRICE : ', data['Date'][days],data['Close'][days])
                try:
                    data['signal'].iloc[days] = 'Buy' 
                    signal_buy_check = signal_buy_check + 1
                    signal_sell_check = 1
                except SettingWithCopyWarning:
                    print('warning message')
        elif data['10_Days_EMA'][days] < data['21_Days_EMA'][days]:
            if signal_sell_check == 1:
                #print('this is the time to sell')
                #print('SELL PRICE : ', data['Date'][days],data['Close'][days])
                try:
                    data['signal'].iloc[days] = 'Sell' 
                    signal_sell_check = signal_sell_check + 1
                    signal_buy_check = 1
                except SettingWithCopyWarning:
                    print('warning message')
        else:
            pass
    return data

def find_signal(data,symbol,Buy_stock,sell_stock):
    
    for i in range(-5,0):
        try:
            if data['signal'][i] == 'Buy':
                #print('the stock ready to buy : ', symbol)
                Buy_stock.append(symbol.replace('.ns',''))
            elif data['signal'][i] == 'Sell':
                #print('the stock ready to sell : ', symbol)
                sell_stock.append(symbol.replace('.ns',''))
            else:
                pass
        except IndexError:
            print('index error : ', symbol)
            pass
    return Buy_stock, sell_stock

''' Volume check '''
def get_volume_analysis(data,symbol,output):
    try:
        prev_avg = data['Volume'].iloc[-6:-1].mean()
        last_traded_price = data['Volume'].iloc[-1]
        prev_avg = int(prev_avg)
        last_traded_price = last_traded_price.item()
        if last_traded_price > prev_avg:
            output.append(symbol.replace('.ns',''))
    
    except IndexError:
        print('index error : ', symbol)
        pass
    return output

'''the most accurate may be'''
def final_output(output,buy,accurate):
    out_len = len(buy)
    for len_n in range (out_len):
        if buy[len_n] in output:
            accurate.append(buy[len_n])
    return accurate

'''execute the mailing steps'''
def email_output():
    email_sender = 'kalyankar4133@gmail.com'
    #email_sender = 'balachandru1997@gmail.com'
    email_password ='uporqxospkpuhexg'
    #email_receiver = 'digambark4133@gmail.com'
    email_receiver = ["BalaChandru1997@gmail.com" , "sureshrajss887@gmail.com" , "Baskaravikraman@gmail.com", "gharesh4@live.com"]
    #email_receiver = ["BalaChandru1997@gmail.com"]
    subject = '10 cross 21 moving average and volume analysis '
    body = """
    Please find The stocks in the attached document 
    Buy_10_21_cs -(ready to buy stocks) file contains the stocks where 10 crossover 21 happened in last 5 days.
    Sell_10_21_cs -(ready to sell stocks) file contains the stocks where 10 crossover 21 happened in last 5 days.
    accu - high precission both 10 crossover 21 and high voume passed 
    """
    
    em = MIMEMultipart()
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    
    Pathname = ['Buy_10_21_cs.csv','Sell_10_21_cs.csv','accu.csv']
    for Path in Pathname:
        with open(Path,'rb') as file:
            em.add_attachment(MIMEApplication(file.read(), Name=Path.replace('csv','txt')))
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender , email_password)
        smtp.sendmail(email_sender , email_receiver, em.as_string())

'''execute the main program/function call'''

if __name__ == '__main__':
    
    accurate = []
    Nifty_data = get_400nsedata()
    #date1 = int(input('enter the date : '))
    #month = int(input('enter the Month : '))
    date1 = 1
    month = 6
    startdate = datetime(2021,month,date1)
    enddate = datetime.today()
    #interval = str(input('Enter the Time interval like: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk : '))
    interval = '1d'
    buy,sell,data,output = get_histdata(Nifty_data, startdate, enddate, interval)
    accu = final_output(output,buy,accurate)
    print('the stocks are in buy zone : ', buy)
    print('the stocks are in sell zone : ', sell)
    print('the stocks are in accurate are : ', accu)
    print('the stocks are above the last 5 days volume : {}'.format(output))
    function_call(buy,startdate, enddate, interval)
    np.savetxt("Buy_10_21_cs.csv", buy, delimiter =", ", fmt ='% s')
    np.savetxt("Sell_10_21_cs.csv", sell, delimiter =", ", fmt ='% s')
    np.savetxt("accu.csv", accu, delimiter =", ", fmt ='% s')
    email_output()

