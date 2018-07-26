import configparser
import psycopg2

class ShopDatabase:
	#Оборачивает функцию, работающую с курсором, в try
	def __TryWrapper(self, func):
		def safe_func(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as error:
				print("Exception during execution! Connection will be closed, you will have to reconnect!")
				self.CloseConnection()
				print(error)
		return safe_func

	# Создает функцию, которая делает запрос и возвращает курсор для итерирования (уже безопасную по исключениям).
	def __MakeQueryFunction(self, query_filename):
		with open(query_filename, "r") as file:
			query_str = file.read()

		def query_function():
			self.cursor.execute(query_str)
			return self.cursor	
		return self.__TryWrapper(query_function) 
		
	def __GetOrderGoodPairID(self, order_id, good_id):
		self.cursor.execute("SELECT order_item_id, quantity FROM order_items WHERE order_id = {0} AND good_id = {1};".format( \
							order_id, good_id))
		results = self.cursor.fetchall()
		if len(results) > 1:
			print("WARNING: Pairs order-good are not unique! They will be concated")
			count = results[0][1] #В первой строке
			for i in range(1, len(results)):
				count += results[i][1]
				self.cursor.execute("DELETE FROM order_items WHERE order_item_id = {0};".format(results[i][0]))
			self.cursor.execute("UPDATE order_items SET quantity = {0} WHERE order_item_id = {1};".format(count, results[0][0]))

		if len(results) == 0:
			return -1
		else:
			return results[0][0]
	
	def __AddToOrder(self, order_id, good_id, quantity):
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			self.cursor.execute("INSERT INTO order_items (order_id, good_id, quantity) VALUES ({0}, {1}, {2});".format( \
								order_id, good_id, quantity))
		else:
			print("Good already in order, changing count")
			self.cursor.execute("UPDATE order_items SET quantity = quantity+{0} WHERE order_item_id = {1};".format( \
								quantity, pair_id))
	
	def __RemoveFromOrder(self, order_id, good_id):
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			print("Nothing to remove!")
		else:
			self.cursor.execute("DELETE FROM order_items WHERE order_item_id = {0};".format(pair_id))
	
	def __ChangeCount(self, order_id, good_id, quantity):
		pair_id = self.__GetOrderGoodPairID(order_id, good_id)
		if pair_id == -1:
			self.__AddToOrder(order_id, good_id, quantity)
		else:
			self.cursor.execute("UPDATE order_items SET quantity = {0} WHERE order_item_id = {1};".format( \
								quantity, pair_id))
								
	def __Dump(self, filename):
		with open(filename, "w") as file:
			self.cursor.execute("SELECT goods.name, goods.vendor, customers.first_nm, customers.last_nm " \
								"FROM order_items INNER JOIN goods ON order_items.good_id = goods.good_id " \
												 "INNER JOIN orders ON order_items.order_id = orders.order_id " \
												 "INNER JOIN customers ON customers.id = orders.order_id;")
			results = self.cursor.fetchall()
			file.write("good_name\tgood_vendor\tcustomer_firstname\tcustomet_latname\n")
			for res in results:
				file.write("{0}\t{1}\t{2}\t{3}\n".format(res[0], res[1], res[2], res[3]))
			
	def __InitFunctions(self):
		self.CreateTables = self.__MakeQueryFunction("create.sql")
		self.CreateSampleData = self.__MakeQueryFunction("sample_data.sql")
		
		self.AddToOrder = self.__TryWrapper(self.__AddToOrder)
		self.RemoveFromOrder = self.__TryWrapper(self.__RemoveFromOrder)
		self.ChangeCount = self.__TryWrapper(self.__ChangeCount)
		
		self.Dump = self.__TryWrapper(self.__Dump)

	def __init__(self, config_name='config.ini', autocommit_p=True):
		config = configparser.ConfigParser()
		config.read('config.ini')
		self.connection_params = config['Connection']
		self.autocommit = autocommit_p
		self.Reconnect()
		
		self.__InitFunctions()
	
	def Reconnect(self):
		# psycopg2 перадает пароли как md5 автоматически
		self.connection = psycopg2.connect(**self.connection_params)
		self.connection.set_session(autocommit=self.autocommit) #В нашей маленькой задаче транзацкции не нужны
		self.cursor = self.connection.cursor()
	
	def CloseConnection(self):
		self.cursor.close()
		self.connection.close()
