
"""
Program: Elysim II GridTrader
Current Version: 1.1 Beta
Modifications: 
date: 02-5-2022 | version 1.1 Beta | Initial development, copy from Elysium I 



backlog
+20220507-1: db connection write balance to db
+20220507-2: db connection write orders to db
+20220507-3: calculate balance total per hour
+20220507-4: test 24h with 2 grids
+20220507-5: test solution on 2nd computer
+20220507-6: create elysium2 repo
+20220507-7: new grid create function with ranges
+20220507-8: profit per transaction
+20220507-9: github repo
+20220507-10: check live order status 
+20220507-11: renew order test run
+20220518: renew order revised with list comprehension and 4 scenario's
+20220521: update order table function
-20220523: 48H prod run





"""

# general modules
import time
from datetime import datetime, timedelta 


# general modules
import requests
import sys, os
import sqlite3



# switch working dir
# path = os.getcwd()
# print(path)
# parentdir = os.path.abspath(os.path.join(path, os.pardir))
# os.chdir(parentdir)

os.chdir('Modules')
path = os.getcwd()
print(path)


# importing specific modules
sys.path.insert(0, path)
import ex_functions as ef
import helpfunctions as hp
import configdb as db
import pytz

# timezone
amsterdam_time = pytz.timezone("Europe/Amsterdam")

# intitialise global variables
programName = 'Elysium GridTrader'
programVersion = '1.0 Beta'
programDuration = 48 #in hours
ReAdjustInterval = 3 #in hours

NewSellLimitPriceHigh = 0
orderDict = {}
url = 'https://api.binance.com' #binance server
timeout = 5


trade_interval = 20 #in seconds
coin = 'ETH'
base = 'USDC'
init = True
# ROI = 0
pool = 0
symbol = coin + base



# initialise program sys.path.append(os.path.join(sys.path[0], 'Modules'))
# takeProfit = 0.2
buyLimitPriceOffset = 0.1
present_time = datetime.now()
program_end = datetime.now() + timedelta(hours = programDuration)
readjustCheckTime = datetime.now() + timedelta(hours = ReAdjustInterval)
ls_order = []
buyLimitPrice =0
countFilled = 0
gridNumber = 1
takeProfit = 1.0
adjustmentValue = 0.2
strategy = 'GridLong 1% TakeProfit'
tradeQuantity = 0.2  #in ETH
lowerBound = 1850
upperBound = 2150




# start Main program
timestamp = hp.TimeStamp()
startEpoch = hp.TimeStampEpochMS()
print('%s: Starting Elysium version leah was here %s' %(timestamp, programVersion))
orderNum = len(db.SQLSelectOrder())

# create orderlist if order table is empty
if orderNum == 0: #order table is empty
	orderList = ef.SetGrid(coin, base, lowerBound, upperBound, takeProfit)
	for order in orderList:
			if order != {}:
				symbol = order['symbol']
				orderId = order['orderId']
				transactTime = hp.EpochmsToString(order['transactTime'])
				price = float(order['price'])
				quantity = order['origQty']
				status = order['status']
				side = order['side']
				db.SQLInsertOrder(symbol, orderId, transactTime, price, quantity,status, side)

# enter while loop
while datetime.now() < program_end:
	
	try:
		request = requests.get(url, timeout=timeout) #check internet connection
		# amsterdam_time = pytz.timezone("Europe/Amsterdam")
		
		# update order table
		liveOrderList = ef.GetLiveOrders(coin, base, 30)
		if len(liveOrderList) > 0:
			db.SQLTruncateOrderTable()
			for liveOrder in liveOrderList:
				orderId = liveOrder[0]
				transactTime = hp.EpochmsToString(liveOrder[4])
				price = float(liveOrder[6])
				quantity = float(liveOrder[7])
				status = liveOrder[5]
				side = liveOrder[3]
				db.SQLInsertOrder(symbol, orderId, transactTime, price, quantity, status, side)


		# # renew orders
		print(ef.RenewOrder(coin, base))

		print('Elysium %s running..' %programVersion)
					
		print('\n')


		lastTime = db.SQLLastBalance()
		if lastTime == None:
			coinBalance = ef.CheckBalanceTotal(coin)
			baseBalance = ef.CheckBalanceTotal(base)
			totalCoinBalance = coinBalance[0] + coinBalance[1]
			currentPrice = ef.PriceAction2(symbol)[3]
			totalBalance = baseBalance[0] + baseBalance[1] + (totalCoinBalance * currentPrice)
			totalBalance = hp.round_decimals_down(totalBalance, 2)
			epoch = hp.TimeStampEpochMS()
			balanceTime = hp.EpochmsToString(epoch)
			db.SQLInsertBalance(strategy, symbol, balanceTime, totalBalance)

		else:
			lastTime = db.SQLLastBalance()
			if datetime.now() > hp.StringToDatetime(lastTime) + timedelta(hours = 4):
				coinBalance = ef.CheckBalanceTotal(coin)
				baseBalance = ef.CheckBalanceTotal(base)
				totalCoinBalance = coinBalance[0] + coinBalance[1]
				currentPrice = ef.PriceAction2(symbol)[3]
				totalBalance = baseBalance[0] + baseBalance[1] + (totalCoinBalance * currentPrice)
				totalBalance = hp.round_decimals_down(totalBalance, 2)
				epoch = hp.TimeStampEpochMS()
				balanceTime = hp.EpochmsToString(epoch)
				db.SQLInsertBalance(strategy, symbol, balanceTime, totalBalance)
		


	except (requests.ConnectionError, requests.Timeout) as exception:
		print("Internet connection lost..")

	time.sleep(trade_interval)










