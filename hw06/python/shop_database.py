#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import configparser
import psycopg2
import sys

class ShopDatabase:
	"""
	Класс для работы с базой данных магазина. Требуется, чтобы не хранить
	connection и cursor в глобальных переменных
	"""
	
	def __TryWrapper(self, func):
		"""
		Оборачивает функцию, работающую с SQL в try блок, при ошибке - обеспечивается
		корректное завершение работы
		"""
		def safe_func(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as error:
				print("Exception during execution! Connection will be closed, "+ \
					  "you will have to reconnect!", file=sys.stderr)
				self.CloseConnection()
				print(error, file=sys.stderr)
		return safe_func

	def __MakeQueryFunction(self, query_filename):
		"""
		Создает функцию, выполняющую запрос, записанный в файле query_filename
		Создаваемая функция уже обернута в try
		
		Args:
			query_filename (str): Имя файла с SQL-запросом.
		"""
		with open(query_filename, "r") as file:
			query_str = file.read()

		def query_function():
			self.cursor.execute(query_str)
			return self.cursor	
		return self.__TryWrapper(query_function) 
		
	def __GetOrderGoodPairID(self, order_id, good_id):
		"""
		Получает пару заказ-товар из таблицы order_item_id. Если пара не уникальна,
		то выполняется объединение строк
		
		Args:
			order_id(int): id заказа
			good_id(int): id товара
			
		Returns:
			int: -1, если пара не нейдена, иначе - id пары
		"""
		self.cursor.execute("SELECT order_item_id, quantity FROM order_items "+ \
							"WHERE order_id = %s AND good_id = %s;", (order_id, good_id))
		results = self.cursor.fetchall()
		
		# Если много пар заказ-товар => выполняем сведение (в первую строку)
		if len(results) > 1:
			print("WARNING: Pairs order-good are not unique! They will be concated",
				  file=sys.stderr)
			count = results[0][1] #Количество товара в первой строке
			for i in range(1, len(results)):
				count += results[i][1]
				self.cursor.execute("DELETE FROM order_items WHERE order_item_id = %s;",
									(results[i][0], ))
			self.cursor.execute("UPDATE order_items SET quantity = %s "+ \
								"WHERE order_item_id = %s;", (count, results[0][0]))

		if len(results) == 0:
			return -1
		else:
			return results[0][0]
	
	def __AddToOrder(self, order_id, good_id, quantity):
		"""
		Функция добавления товара в заказ. Private, т.к. ее нужно обернуть
		
		Args:
			order_id(int): id заказа
			good_id(int): id товара
			quantity(int): количество товара
		"""
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			self.cursor.execute("INSERT INTO order_items (order_id, good_id, "+ \
								"quantity) VALUES (%s, %s, %s);",
								(order_id, good_id, quantity))
		else:
			print("Good already in order, changing count")
			self.cursor.execute("UPDATE order_items SET quantity = quantity+%s "+ \
								"WHERE order_item_id = %s;", (quantity, pair_id))
	
	def __RemoveFromOrder(self, order_id, good_id):
		"""
		Функция удаления товара из заказа. Private, т.к. ее нужно обернуть
		
		Args:
			order_id(int): id заказа
			good_id(int): id товара
		"""
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			print("Nothing to remove!")
		else:
			self.cursor.execute("DELETE FROM order_items WHERE order_item_id = %s;",
							    (pair_id, ))
	
	def __ChangeCount(self, order_id, good_id, quantity):
		"""
		Функция изменения количества товара в заказе. Private, т.к. ее нужно обернуть
		
		Args:
			order_id(int): id заказа
			good_id(int): id товара
			quantity(int): количество товара
		"""
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			self.__AddToOrder(order_id, good_id, quantity)
		else:
			self.cursor.execute("UPDATE order_items SET quantity = %s "+ \
								"WHERE order_item_id = %s;", (quantity, pair_id))
								
	def __Dump(self, filename):
		"""
		Функция сохранения заказов в файл. Private, т.к. ее нужно обернуть
		
		Args:
			filename(str): имя файла, куда сохранять информацию
		"""
		with open(filename, "w") as file:
			self.cursor.execute("SELECT goods.name, goods.vendor, customers.first_nm, customers.last_nm "+ \
								"FROM order_items INNER JOIN goods ON order_items.good_id = goods.good_id " \
												 "INNER JOIN orders ON order_items.order_id = orders.order_id " \
												 "INNER JOIN customers ON customers.id = orders.order_id;")
			results = self.cursor.fetchall()
			file.write("good_name\tgood_vendor\tcustomer_firstname\tcustomet_latname\n")
			for res in results:
				file.write("{0}\t{1}\t{2}\t{3}\n".format(res[0], res[1], res[2], res[3]))
			
	def __InitFunctions(self):
		"""
		Служебная функция - создает методы класса (из файлов и оборачивая в 
		try-блоки)
		"""
		self.CreateTables = self.__MakeQueryFunction("create.sql")
		self.CreateSampleData = self.__MakeQueryFunction("sample_data.sql")
		
		self.AddToOrder = self.__TryWrapper(self.__AddToOrder)
		self.RemoveFromOrder = self.__TryWrapper(self.__RemoveFromOrder)
		self.ChangeCount = self.__TryWrapper(self.__ChangeCount)
		
		self.Dump = self.__TryWrapper(self.__Dump)

	def __init__(self, config_name='config.ini', autocommit_p=True):
		"""
		Создает объект ShopDatabase.
		Args:
			config_name (str): имя конфига с параметрами подключения
			autocommit_p (bool): Нужно ли автоматически выполнять транзакции. В нашей задаче - оптимально True
		"""
		config = configparser.ConfigParser()
		config.read('config.ini')
		self.connection_params = config['Connection']
		self.autocommit = autocommit_p
		self.Reconnect()
		
		self.__InitFunctions()
	
	def Reconnect(self):
		"""
		Подключается к базе данных. Здесь не ловим исключения, т.к. они фатальны
		"""
		# psycopg2 перадает пароли как md5 автоматически
		self.connection = psycopg2.connect(**self.connection_params)
		self.connection.set_session(autocommit=self.autocommit)
		self.cursor = self.connection.cursor()
	
	def CloseConnection(self):
		"""
		Завершает соединение с БД. Здесь не ловим исключения, т.к. они фатальны
		"""
		self.cursor.close()
		self.connection.close()
		
if __name__ == "__main__":
	shop_db = ShopDatabase()
	shop_db.CreateTables()
	shop_db.CreateSampleData()
	
	shop_db.Dump("example_dump.txt")
	
	shop_db.CloseConnection()
