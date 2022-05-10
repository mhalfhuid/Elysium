# setup config tables in monitor.db
import os, sys
import sqlite3
import helpfunctions as hp
import pandas as pd
from datetime import datetime, timedelta




# define connection and database
# connection = sqlite3.connect('../Database/monitor.db') # holds vortex trade tables
connection = sqlite3.connect('/Users/malcolmhalfhuid/Python/Ava2/Database/monitor.db')
cursor = connection.cursor()

#----------------------------BEGIN CONFIG TABLE------------------------------------
# creating config table
sql_config = """CREATE TABLE IF NOT EXISTS
ORDERS(id INTEGER PRIMARY KEY, symbol TEXT, orderId INT, transactTime TEXT, price REAL, quantity REAL, status TEXT, side TEXT)"""
cursor.execute(sql_config)

sql_insert_order = """INSERT INTO ORDERS (symbol, orderId, transactTime, price, quantity, status, side) VALUES (?,?,?,?,?,?,?)"""

def SQLInsertOrder(symbol, orderId, transactTime, price, quantity, status, side):
	# time_ind = hp.TimeStamp()
	cursor.execute(sql_insert_order, (symbol, orderId, transactTime, price, quantity, status, side))
	connection.commit()



# check if orders exist
sql_select_order = """SELECT * FROM ORDERS"""
def SQLSelectOrder():
	cursor.execute(sql_select_order)
	ls = cursor.fetchall()
	return ls



# update order status
sql_update_order_status =  """UPDATE ORDERS SET status = ? WHERE orderId = ? """
def SQLUpdateOrderStatus(status, orderId):
	cursor.execute(sql_update_order_status, (status, orderId))
	connection.commit()


# delete order
sql_delete_order = """DELETE FROM ORDERS WHERE orderId = ?"""
def SQLDeleteOrder(orderId):
	cursor.execute(sql_delete_order, (orderId,))
	connection.commit()
	

# SQLUpdateOrderStatus(658346989, 'NEW')	
# 658346989.000000


	
