
"""
Program: Elysim II GridTrader
Current Version: 1.1 Beta
Modifications: 
date: 02-5-2022 | version 1.1 Beta | Initial development, copy from Elysium I 



backlog
-20220507-1: db connection write balance to db
+20220507-2: db connection write orders to db
-20220507-3: calculate balance total per hour
-20220507-4: test 24h with 2 grids
-20220507-5: test solution on 2nd computer
-20220507-6: create elysium2 repo
-20220507-7: new grid create function with ranges
-20220507-8: profit per transaction
-20220507-9: github repo
+20220507-10: check live order status 
-20220507-11: renew order



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




# intitialise global variables
programName = 'Elysium GridTrader'
programVersion = '1.0 Beta'
programDuration = 24 #in hours
ReAdjustInterval = 3 #in hours

NewSellLimitPriceHigh = 0
orderDict = {}
url = 'https://api.binance.com' #binance server
timeout = 5


trade_interval = 90 #in seconds
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
takeProfit = 1
adjustmentValue = 0.2
# priceLevel = 2830
tradeQuantity = 0.2  #in ETH
lowerBound = 1800
upperBound = 2200




# start Main program
timestamp = hp.TimeStamp()
print('%s: Starting Elysium version 1.0 leah was here %s' %(timestamp, programVersion))
orderNum = len(db.SQLSelectOrder())
# create orderlist if order table is empty
if orderNum == 0: #order table is empty
	orderList = ef.SetGrid(coin, base, lowerBound, upperBound, takeProfit)
	for order in orderList:
			if order != {}:
				symbol = order['symbol']
				orderId = order['orderId']
				transactTime = str(hp.EpochmsToDatetime(order['transactTime']))
				price = float(order['price'])
				quantity = order['origQty']
				status = order['status']
				side = order['side']
				db.SQLInsertOrder(symbol, orderId, transactTime, price, quantity,status, side)
			
else: #order table is filled, update live order status
	liveOrderList = ef.GetLiveOrders(coin, base, orderNum)
	orderList = db.SQLSelectOrder()
	for order in orderList:
		orderId = int(order[2])
		for liveOrder in liveOrderList:
			if orderId == liveOrder[0]:
				liveStatus = liveOrder[5]
				db.SQLUpdateOrderStatus(liveStatus, orderId)


while datetime.now() < program_end:
	
	try:
		request = requests.get(url, timeout=timeout) #check internet connection


		
		# update live order status
		orderNum = len(db.SQLSelectOrder())
		liveOrderList = ef.GetLiveOrders(coin, base, orderNum)

		orderList = db.SQLSelectOrder()
		for order in orderList:
			symbol = order[1]
			orderId = int(order[2])
			price = float(order[4])
			quantity = float(order[5])
			side = order[7]

			status = order[6]
			for liveOrder in liveOrderList:
				liveStatus = liveOrder[5]
				if orderId == liveOrder[0] and status != liveStatus:
					timestamp = hp.TimeStamp()
					print('%s update dborder %f from status %s to live status %s' %(timestamp,orderId, status, liveStatus))					

					db.SQLUpdateOrderStatus(liveStatus, orderId)


		ef.RenewBuyOrder(coin, base)
		print('program running...')


					
		# print('\n')

		# # check balance
		# coinBalance = ef.CheckBalanceTotal(coin)
		# baseBalance = ef.CheckBalanceTotal(base)

		# if isinstance(coinBalance, float) and isinstance(baseBalance, float):
		# 	coinBalance = coinBalance[0] + coinBalance[1]
		# 	currentPrice = ef.PriceAction2(symbol)[3]
		# 	coinBalance = coinBalance * currentPrice
		# 	print('coin balance: %f' %coinBalance)

	

		# 	baseBalance = baseBalance[0] + baseBalance[1]
		# 	print('base balance: %f' %baseBalance)

		# 	totalBalance = coinBalance + baseBalance
		# 	print('total balance: %f' %totalBalance)





	except (requests.ConnectionError, requests.Timeout) as exception:
		print("Internet connection lost..")

	time.sleep(trade_interval)










