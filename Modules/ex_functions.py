import os, time

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import helpfunctions as hp
import signature as sig
from decimal import Decimal
import math
import time
from datetime import datetime, timedelta 
import data
import numpy as np
import pandas as pd
import configdb as db
# import talib


# init
BASE_URL = 'https://api.binance.com' # production base url

client = Client(sig.KEY, sig.SECRET)


# initialise
base = 'USDT'
simQuantity = 0
orderPause = 2






def CheckCoinOnBinance(c):
	try:
		ls_pricedata = client.get_all_tickers()
		ls_binance = [x['symbol'].replace('USDT','') for x in ls_pricedata if x['symbol'].count(base) > 0] #get all coins with base pair equals 'base'
		

		if (ls_binance.count(c.upper()) > 0):
			return True
		else:
			return False
	except:
		print('error in ef.CheckCoinOnBinance: unable to access exchange ticker data')




def PriceAction(c, b):
	try:
		coin = c
		base = b
		prices = client.get_all_tickers()

		ticker = coin.upper() + base.upper()

		price_data = [x for x in prices if x['symbol'] == ticker]
		timestamp = hp.TimeStamp()
		epoch = int(time.time())
		price = round(float(price_data[0]['price']),4)
		return price
	except:
		return -1.0



def PriceAction2(symbol):
	try:
		prices = client.get_all_tickers()

		price_data = [x for x in prices if x['symbol'] == symbol]
		timestamp = hp.TimeStamp()
		epoch = int(time.time())
		price = round(float(price_data[0]['price']),4)
		result = (symbol, timestamp, epoch, price)
		return result
	except:
		print('error in ef.PriceAction: unable to fetch price')

# prices = client.get_all_tickers()
# print(prices)

def CheckBalance(c):
	try:
		response = sig.send_signed_request('GET', '/api/v3/account')
		balanceData = [x for x in response['balances'] if x['asset'] == c.upper()]
		freeBalance = float(balanceData[0]['free'])

		return freeBalance
	except:
		print('error in ef.CheckBalance: unable to fetch exchange balance data')




def CheckBalanceTotal(c):
	try:
		response = sig.send_signed_request('GET', '/api/v3/account')
		balanceData = [x for x in response['balances'] if x['asset'] == c.upper()]
		freeBalance = float(balanceData[0]['free'])
		lockedBalance = float(balanceData[0]['locked'])

		return (freeBalance, lockedBalance)
	except:
		print('error in ef.CheckBalance: unable to fetch exchange balance data')


# print(CheckBalanceTotal('btc'))



def CheckBalanceValue(c, n):
	try:
		response = sig.send_signed_request('GET', '/api/v3/account')
		balanceData = [x for x in response['balances'] if x['asset'] == c.upper()]
		freeBalance = float(balanceData[0]['free'])
		price = PriceAction(coin, base)
		# price = priceaction[3]

		freeBalanceValue = freeBalance * price
		if freeBalanceValue > n:
			return True
		else:
			return False

	except:
		print('error in ef.CheckQuantity: unable to fetch quantity balance data')


def AssetList():
	ls = []
	try:
		response = sig.send_signed_request('GET', '/api/v3/account')
		ls_balance = response['balances']
		for i in ls_balance:
			ls.append(i['asset'])
		return ls
	except:
		print('error in ef.CheckBalance: unable to fetch exchange balance data')



def GetMinNotional(c, b): # get min amount of tradable asset
	coin = c.upper()
	base = b.upper()
	symbol = coin + base
	response = client.get_symbol_info(symbol)
	minNotional = response['filters'][3]['minNotional']
	return float(minNotional)

def MarketBuy(c, b, p, m):
	global simQuantity
	order = {}
	coin = c
	base = b
	purchase = p #purchase amount in dollar value
	mode = m
	timestamp = hp.TimeStamp()
	symbol = coin.upper() + base.upper()

	print("%s attempting to buy %s coin for %f USD..." %(timestamp, coin, purchase))
	time.sleep(orderPause)

	try:
		minNotional = GetMinNotional(coin, base)
		
		if purchase > float(minNotional):
			price = PriceAction(coin, base)
			# price = priceaction[3]
			quantity = purchase / price

			adjustedQuantity = GetLotsize(coin, quantity)
			simQuantity = adjustedQuantity
			
			if mode == 'LIVE': # live mode 
				try:
					order = client.order_market_buy(symbol=symbol,quantity=adjustedQuantity)

				except BinanceAPIException as error:
					print(error)

				
			
				if order: # if order is not empty 
					if (isinstance(order['orderId'],int) and order['orderId'] > 0 and order['status'] == 'FILLED'):	
						price = float(order['fills'][0]['price'])			
						print ('%s: --- LIVE MODE --- MARKET BUY %s coin succeeded! Order quantity %f. Price %f ' %(timestamp, coin, quantity, price))
		

			if mode == 'SIM': #simulation mode
				print ('%s: --- SIM MODE --- MARKET BUY %s coin succeeded! Order quantity %f. Price %f ' %(timestamp, coin.upper(), simQuantity, price))
				
		else:
			# orderSucceeded = False
			print('purchase value must be greater than MIN_NOTIONAL')


	except:
		# orderSucceeded = False
		print('general error in MarketBuy:')






def MarketSell(c, b, s, m):
	global simQuantity
	order = {}
	coin = c
	base = b
	saleValue = s #sale amount in dollar value
	mode = m
	timestamp = hp.TimeStamp()
	symbol = coin.upper() + base.upper()

	print("%s attempting to sell %s coin for %f USD..." %(timestamp, coin, saleValue))
	time.sleep(orderPause)

	try:
		minNotional = GetMinNotional(coin, base)
		
		
		if saleValue > float(minNotional):
			price = PriceAction(coin, base)
			# price = priceaction[3]
			quantity = saleValue / price

			adjustedQuantity = GetLotsize(coin, quantity)
			simQuantity = adjustedQuantity
			
			if mode == 'LIVE': # live mode 
				try:
					order = client.order_market_sell(symbol=symbol,quantity=adjustedQuantity)
					
				except BinanceAPIException as error:
					print(error)

				
			
				if order: # if order is not empty 
					if (isinstance(order['orderId'],int) and order['orderId'] > 0 and order['status'] == 'FILLED'):	
						price = float(order['fills'][0]['price'])			
						print ('%s: --- LIVE MODE --- MARKET SELL %s coin succeeded! Order quantity %f. Price %f ' %(timestamp, coin, quantity, price))
		

			if mode == 'SIM': #simulation mode
				print ('%s: --- SIM MODE --- MARKET SELL %s coin succeeded! Order quantity %f. Price %f ' %(timestamp, coin.upper(), simQuantity, price))
				
		else:
			print('salevalue must be greater than MIN_NOTIONAL')


	except:
		print('general error in MarketSell:')
	

def AddCoinToPortFolio2(c,ls,m):
	mode = m
	coin = c
	if mode == "LIVE":
		if hp.CoinInPortfolio(coin, ls) == False: #coin is not in portfolio
			quantity = CheckBalance(coin)
			if quantity > 0:
				tup = (coin, quantity)
				ls.append(tup)
				timestamp = hp.TimeStamp()
				print('%s: %s coin added to portfolio' %(timestamp, c.upper()))
				return ls
			else:
				print ('error: %s coin not added, quantity is zero' %c.upper())
		else:
			print('%s coin already in portfolio' %c.upper())

	if mode == "SIM":
		if hp.CoinInPortfolio(coin, ls) == False: #coin is not in portfolio
			tup = (coin, simQuantity)
			if simQuantity > 0:
				ls.append(tup)
				timestamp = hp.TimeStamp()
				print('%s: %s coin added to portfolio' %(timestamp, c.upper()))
				return ls
			else:
				print ('error: %s coin not added, quantity is zero' %c.upper())
		else:
			print('%s coin already in portfolio or quantity is zero' %c.upper())


def PortfolioScaleUp2(ls,c, m): 
	mode = m
	coin = c
	status = SellExistingCoins(ls, mode)
	result = BuyNewVortexCoin(status, coin, mode)
	return result

def PortfolioScaleDown2(ls,c, m): 
	mode = m
	coin = c
	status = SellVortexCoin(ls, coin, mode)
	result = BuyExistingCoins(status, mode)

	return result


def ClosePortfolio(ls, m):
	mode = m
	coin = ls[0][0]
	quantity = ls[0][1]
	currentPrice = PriceAction(coin, base)
	# currentPrice = action[3]
	sellValue = quantity * currentPrice
	MarketSell(coin, base, sellValue, mode)
	return sellValue
	



def SellVortexCoin(ls,c, m):
	mode = m
	coin = c
	lss = []

	if mode == 'LIVE': #calculate remaining quantity
		quantity = CheckBalance(coin)
		currentPrice = PriceAction(coin, base)
		# currentPrice = action[3]
		sellValue = currentPrice * quantity

		MarketSell(coin, base, sellValue, mode)
				
		lss = [x for x in ls if x[0] != coin]	#remove coin from portfolio

	if mode == 'SIM': #calculate remaining quantity
		simQuantity = [x[1] for x in ls if x[0] == coin][0]
		currentPrice = PriceAction(coin, base)
		# currentPrice = action[3]
		sellValue = currentPrice * simQuantity

		MarketSell(coin, base, sellValue, mode)
				
		lss = [x for x in ls if x[0] != coin]	#remove coin from portfolio

	return (sellValue, lss)

def BuyExistingCoins(status, m):
	mode = m
	buyValue = status[0]
	ls = status[1]
	lss = []


	if mode == 'LIVE':
		if len(ls) > 0:
			fraction = 1 / len(ls)
			freeBaseBalance = CheckBalance(base)
			buyValuePerCoin = freeBaseBalance * fraction
			for i in ls:
				coin = i[0]
				MarketBuy(coin, base, buyValuePerCoin, mode)
				quantity = CheckBalance(coin)
				if CheckBalanceValue(coin,1):  #check if dollarvalue of balance is high enough to designate coin to portfolio
					new = (coin, quantity)
					lss.append(new)

	if mode == 'SIM':
		if len(ls) > 0:
			fraction = 1 / len(ls)
			buyValuePerCoin = buyValue * fraction
			for i in ls:
				coin = i[0]
				quantityBefore = i[1]
				MarketBuy(coin, base, buyValuePerCoin, mode)
				currentPrice = PriceAction(coin, base)
				# currentPrice = action[3]
				quantityAdded = buyValuePerCoin / currentPrice
				new = (coin, quantityBefore + quantityAdded)
				lss.append(new)

	ls = lss
	return ls
			
 

def GetLotsize(c,q):
	symbol = c.upper() + base
	response = client.get_symbol_info(symbol)
	stepSize = float(response['filters'][2]['stepSize'])
	f = q / stepSize
	f_round = hp.round_decimals_down(f,0)

	adjustedQuantity = f_round * stepSize

	stepSize = str(stepSize)
	numOfDecimals = stepSize[::-1].find('.')

	if numOfDecimals < 0:
		numOfDecimals = 0

	adjustedQuantity = round(adjustedQuantity,numOfDecimals)

	return adjustedQuantity
			


def SellExistingCoins(ls,m): 

	lss = []
	mode = m
	totalSellValue = 0


	# only applies to coins that are not already in portfolio

	numberOfCoins = len(ls)
	if numberOfCoins > 0:
		sellFraction = 1 / (numberOfCoins + 1)

	
	print('Splitting portfolio')
	lss = []
	for i in ls:
		
		coin = i[0]
		quantity = i[1]

		currentPrice = PriceAction(coin, base)
		# currentPrice = action[3]
		

		
		sellValue = currentPrice * quantity * sellFraction
		totalSellValue += sellValue
		MarketSell(coin, base, sellValue, mode)


		
		if mode == 'LIVE': #lookup remaining quantity on exchange
			remainingQuantity = CheckBalance(coin)
			tup = (coin,  remainingQuantity)
			lss.append(tup)
		if mode == 'SIM': #calculate remaining quantity
			simQuantity = quantity * sellFraction
			remainingQuantity = quantity - simQuantity
			tup = (coin,  remainingQuantity)
			lss.append(tup)

	ls = lss
	return (totalSellValue, ls)



def BuyNewVortexCoin(status, c, m):
	coin = c
	mode = m
	buyValue = status[0]
	portfolio_list = status[1]
	MarketBuy(coin, base, buyValue, mode)

	if mode == 'LIVE': #lookup quantity on exchange
		quantity = CheckBalance(coin)
		if CheckBalanceValue(coin,1):  #check if dollarvalue of balance is high enough to designate coin to portfolio
			new = (coin, quantity)
	

	if mode == 'SIM': #calculate rquantity
		currentPrice = PriceAction(coin, base)
		# currentPrice = action[3]
		quantity = buyValue / currentPrice
		new = (coin, quantity)
	

	portfolio_list.append(new)
	return portfolio_list



def SellAll(ls,m):
	mode = m
	if m == 'LIVE':
		for i in ls:
			coin = i[0]
			quantity = CheckBalance(coin)
			currentPrice = PriceAction(coin, base)
			# currentPrice = action[3]
			saleValue = quantity * currentPrice
			MarketSell(coin, base, saleValue, mode)
	if m == 'SIM':
		for i in ls:
			coin = i[0]
			quantity = i[1]
			currentPrice = PriceAction(coin, base)
			# currentPrice = action[3]
			saleValue = quantity * currentPrice
			MarketSell(coin, base, saleValue, mode)




def SellAsset(asset):
	coin = asset.coin
	base = asset.base
	symbol = coin.upper() + base.upper()
	quantity = CheckBalance(coin)
	adjustedQuantity = GetLotsize(coin, quantity)
	timestamp = hp.TimeStamp()
	try:
		order = client.order_market_sell(symbol=symbol,quantity=adjustedQuantity)
		print ('%s: --- LIVE MODE --- MARKET SELL %s coin succeeded! Order quantity %f.' %(timestamp, coin, adjustedQuantity))
		asset.inPortfolio = False
		asset.inPreselect = True
					
	except BinanceAPIException as error:
		print(error)


def InPortfolio(base):
	prices = client.get_all_tickers()

	portfolioList = []
	response = sig.send_signed_request('GET', '/api/v3/account')
	balanceData = [x for x in response['balances']]
	assetBalanceList = [(asset['asset'], asset['free']) for asset in balanceData if float(asset['free']) > 0 and asset['asset'] not in data.ls_blacklist]
	for asset in assetBalanceList:
		coin = asset[0]
		freeBalance = float(asset[1])
		currentPrice = PriceAction(coin, base) 
		dollarValue = freeBalance * currentPrice
		if dollarValue > 1:
			portfolioList.append((coin, dollarValue))
		elif coin == base:
			portfolioList.append((coin, freeBalance))

	return portfolioList





	portfolioList = []
	response = sig.send_signed_request('GET', '/api/v3/account')
	balanceData = [x for x in response['balances']]
	assetBalanceList = [(asset['asset'], asset['free']) for asset in balanceData if float(asset['free']) > 0 and asset['asset'] not in data.ls_blacklist]
	for asset in assetBalanceList:
		coin = asset[0]
		freeBalance = float(asset[1])
		currentPrice = PriceAction(coin, base) 
		dollarValue = freeBalance * currentPrice
		if dollarValue > 1:
			portfolioList.append((coin, dollarValue))
		elif coin == base:
			portfolioList.append((coin, freeBalance))

	return portfolioList




def InvestmentPool(base, maxNumberOfAssets): #purchase per asset
	portfolioList = InPortfolio(base)
	currentNoAssets = len([x for x in  portfolioList if x[0] != base])
	freeSpending = [x[1] for x in  portfolioList if x[0] == base][0]
	
	if maxNumberOfAssets == currentNoAssets:
		return 0.0
	elif maxNumberOfAssets > currentNoAssets:
		return hp.round_decimals_down(freeSpending / (maxNumberOfAssets - currentNoAssets))


def UpdateAssetList(assetList):
	portfolioList = InPortfolio(base)
	coinsInPortfolioList = [x[0] for x in  portfolioList]
	for asset in assetList:
		if coinsInPortfolioList.count(asset.coin) == 1: #if asset coin is in portfolio
			asset.inPortfolio = True
			asset.inPreselect = False
		elif coinsInPortfolioList.count(asset.coin) == 0: #if asset coin is not in portfolio
			asset.inPortfolio = False
			




def LastOrderStatus(coin, base, limit):
	symbol = coin.upper() + base.upper()
	orders = client.get_all_orders(symbol=symbol, limit = limit)
	if orders == []:
		return False
	else:
		orderId = orders[0]['orderId']
		side = orders[0]['side']
		time = orders[0]['updateTime']
		state = orders[0]['status']
		price = orders[0]['price']
		quantity = orders[0]['executedQty']
		return (orderId, coin, base, side, time, state, price, quantity)





def SimpleBuy(coin, base, quantity):
	symbol = coin.upper() + base.upper()
	time = hp.TimeStamp()
	try:
		order = client.order_market_buy(symbol=symbol,quantity=quantity)
		print ('%s: MARKET BUY %s succeeded! Order quantity %f.' %(time, symbol, quantity))
		return True

	except BinanceAPIException as error:
		print(error)
		return False

# SimpleBuy(coin, base, quantity)	

def SimpleSell(coin, base, quantity):
	symbol = coin.upper() + base.upper()
	time = hp.TimeStamp()
	try:
		order = client.order_market_sell(symbol=symbol,quantity=quantity)
		print ('%s: MARKET SELL %s succeeded! Order quantity %f.' %(time, symbol, quantity))
		return True


	except BinanceAPIException as error:
		print(error)
		return False



def SimpleLimitSell(symbol, quantity, price):

	try:
		sellLimitOrder = client.order_limit_sell(symbol=symbol, quantity=quantity, price=price)
		print ('LIMIT SELL %s succeeded at %f! Order quantity %f.' %(symbol, price, quantity))
		return sellLimitOrder

	except BinanceAPIException as error:
		print ('Error limit sell order %s coin at level %f: %s' %(symbol.upper(), price, error))



def SimpleLimitBuy(symbol, quantity, price):

	try:
		buyLimitOrder = client.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
		print ('LIMIT BUY %s succeeded at %f! Order quantity %f.' %(symbol, price, quantity))
		return buyLimitOrder
		

	except BinanceAPIException as error:
		print ('Error limit buy order %s coin at level %f: %s' %(symbol.upper(), price, error))



def MaxPriceFromPurchase(coin, base, buyEpoch):
	symbol = coin.upper() + base.upper()
	candles = client.get_klines(symbol = symbol, interval = Client.KLINE_INTERVAL_1MINUTE)
	df = pd.DataFrame(candles)
	df_high = df.rename(columns={0: 'time', 2:'high'})[['time', 'high']]
	# list of highs from purchase time
	ls_highs = df_high[df_high.time > buyEpoch].high.values.tolist()
	return float(max(ls_highs))



def BaseToQuantity(coin, base, baseValue): # returns quantity of coin equal to the base value
	currentPrice = PriceAction(coin, base)
	if currentPrice > 0:
		quantity = baseValue / currentPrice
		quantity = GetLotsize(coin,quantity)
		return quantity
	else: 
		return 0 
		print('not able to retrieve price')

def AccountBalance(minValue): # returns assets including their dollar value balance if balance exceeds minimum value in dollar
	ls = []
	accountInfo = client.get_account()
	n = len(accountInfo['balances'])

	# all assets with a balance greater than zero
	for i in range(n):
		asset = accountInfo['balances'][i]['asset']
		balance = float(accountInfo['balances'][i]['free'])
		if balance > 0:
			currentPrice = PriceAction(asset, 'USDT')
			if (currentPrice * balance) > minValue:
				ls.append((asset, currentPrice, balance))

	return ls



def PlaceLimitBuyOrder(order):
	buyOrderId = order.buyOrderId
	sellFilled = order.sellFilled
	sellLimitActive = order.sellLimitActive
	symbol = order.symbol
	quantity = order.quantity
	buyLimitPrice = order.buyLimitPrice


	if buyOrderId == -1: # first buy order
		try:
			buyLimitOrder = client.order_limit_buy(symbol=symbol, quantity=quantity, price=buyLimitPrice)
			timestamp = hp.TimeStamp()
			print ('%s: --- LIVE MODE --- LIMIT BUY %s succeeded! Order quantity %f.' %(timestamp, symbol, quantity))

		# 	# update order instance
			order.sellFilled = False
			order.buyOrderId = buyLimitOrder['orderId']
			order.buyLimitActive = True


		except BinanceAPIException as error:
				print ('Error buying %s coin: %s' %(symbol.upper(), error))


	elif (buyOrderId > 0 and sellFilled == True and sellLimitActive == False): # recurring buy order when sell order has been filled

		# dynamic buyLimitPrice and quantity adjustment
		# action = PriceAction2(symbol)
		# currentPrice = action[3]
		# buyLimitPrice = round(currentPrice * ((order.buyLimitPriceOffset / 100) +1),0)
	


		try:
			buyLimitOrder = client.order_limit_buy(symbol=symbol, quantity=quantity, price=buyLimitPrice)
			timestamp = hp.TimeStamp()
			print ('%s: --- LIVE MODE --- LIMIT BUY %s succeeded! Order quantity %f.' %(timestamp, symbol, quantity))

		# 	# update order instance
			order.sellFilled = False
			order.buyOrderId = buyLimitOrder['orderId']
			order.buyLimitActive = True
			order.buyLimitPrice = buyLimitPrice


		except BinanceAPIException as error:
				print ('Error buying %s coin: %s' %(symbol.upper(), error))

def CreateGrid(symbol, gridNumber, gridProfit, priceLevel, tradeQuantity):
	base = 'USDC'
	coin = 'ETH'

	result = []

	for i in range(gridNumber):
		if i == 0:
			gridBuyPrice = hp.round_decimals_down(priceLevel - (priceLevel * (gridProfit/100)), 0)
			buyLimitOrder = client.order_limit_buy(symbol=symbol, quantity=tradeQuantity, price=gridBuyPrice)
			previousGridBuyPrice = gridBuyPrice

			lastOrder = LastOrderStatus(coin, base, 1)
			result.append(lastOrder)


			
		else:
			gridBuyPrice = hp.round_decimals_down(previousGridBuyPrice - (previousGridBuyPrice * (gridProfit/100)), 0)
			buyLimitOrder = client.order_limit_buy(symbol=symbol, quantity=tradeQuantity, price=gridBuyPrice)
			previousGridBuyPrice = gridBuyPrice

			lastOrder = LastOrderStatus(coin, base, 1)
			result.append(lastOrder)


	return result





def SetPricelevels(lowerBound, upperBound, takeProfit):
	priceLevelList = []
	priceLevel = lowerBound
	priceLevelList.append(priceLevel) 
	while priceLevel < upperBound:
		priceLevel = priceLevel + (priceLevel * (takeProfit/100))
		priceLevel = hp.round_decimals_down(priceLevel,0)
		priceLevelList.append(priceLevel)

	return priceLevelList

coin = 'ETH'
base = 'USDC'

def CreateGridOrders(coin, base, lowerBound, upperBound, takeProfit):
	orders = []
	priceLevels = SetPricelevels(lowerBound, upperBound, takeProfit)
	symbol = coin + base
	currentPrice = PriceAction2(symbol)[3]
	freeCoinBalance = CheckBalance(coin)

	freeBaseBalance = CheckBalance(base) / currentPrice

	print('freeCoinBalance: %f' %freeCoinBalance)
	print('freeBaseBalance: %f' %freeBaseBalance)

	for i in priceLevels:
		if i >= currentPrice:
			side = 'SELL'
		else:
			side = 'BUY'

		orderPrice = i			
		orders.append((symbol, side, orderPrice, 0))

	

	buyOrders = [o for o in orders if o[1] == 'BUY']
	sellOrders = [o for o in orders if o[1] == 'SELL']	

	buyBucketQuantity = hp.round_decimals_down(freeBaseBalance / len(buyOrders),4) 
	sellBucketQuantity = hp.round_decimals_down(freeCoinBalance / len(sellOrders), 4) 

	print('buyBucketQuantity: %f' %buyBucketQuantity)
	print('sellBucketQuantity: %f' %sellBucketQuantity)

	if buyBucketQuantity * currentPrice > 15 and sellBucketQuantity * currentPrice > 15:
		orderList = []
		for o in orders:
			if o[1] == 'BUY':
				o = list(o)
				o[3] = buyBucketQuantity
				orderList.append(o)

			elif o[1] == 'SELL':
				o = list(o)
				o[3] = sellBucketQuantity
				orderList.append(o)

		return orderList
	else:
		print('bucket too low, increase take profit or budget or decrease range in order to lower number of grids')


def SetGrid(coin, base, lowerBound, upperBound, takeProfit):
	symbol = coin + base
	orders = CreateGridOrders(coin, base, lowerBound, upperBound, takeProfit)
	orderList = []
	

	for o in orders:
		time.sleep(2)
		if o[1] == 'BUY':
			price = o[2]
			quantity = o[3]
			
			newOrder = SimpleLimitBuy(symbol, quantity, price)
			orderList.append(newOrder)


			
			
		elif o[1] == 'SELL':
			price = o[2]
			quantity = o[3]
			
			newOrder = SimpleLimitSell(symbol, quantity, price)
			orderList.append(newOrder) 


	return orderList	


def GetLiveOrders(coin, base, orderNum):
	liveOrderList = []
	for i in range(orderNum):
		i+=1
		order = LastOrderStatus(coin, base, i)
		liveOrderList.append(order)
	return liveOrderList


		
# CreateSellOrder creates sell order at buy order price plus takeProfit, only when the buy order is filled 
# and when currentPrice is below sell order price
def RenewOrder(coin, base, takeProfit, orderId, price, status):
	symbol = coin + base

	# for order in orderList:
	# 	orderId = int(order[2])
	# 	buyPrice = float(order[4])
	# 	quantity = float(order[5])
	# 	status = order[6]
	# 	side = order[7]
	currentPrice = PriceAction2(symbol)[3]
	sellPrice = price + (price * (takeProfit/100))

	if side == 'BUY' and status == 'FILLED' and currentPrice < sellPrice:
		print('buy order %f is filled, creating sell order at %f' %(orderId, sellPrice))

	# 		# SimpleLimitSell(symbol, quantity, sellPrice)
	# 		# db.SQLDeleteOrder(orderId) # delete old filled buy order from db
	# 	else:
	# 		print('buy order %f not filled' %orderId)




# raw_server_time = client.get_server_time()
# server_time = datetime.fromtimestamp(raw_server_time['serverTime']/1000.0)
# print(server_time)