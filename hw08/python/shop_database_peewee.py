#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import configparser
import sys

import peewee as pw
import datetime

class ShopDatabase:
	"""
	Класс для работы с базой данных магазина. Требуется, чтобы не хранить
	connection в глобальной переменной. Реализован на основе peewee
	"""
	
	def __TryWrapper(func):
		"""
		Оборачивает функцию, работающую с БД в try блок, при ошибке - обеспечивается
		корректное завершение работы
		"""
		def safe_func(self, *args, **kwargs):
			try:
				return func(self, *args, **kwargs)
			except Exception as error:
				print("Exception during execution! Connection will be closed, "+ \
					  "you will have to reconnect!", file=sys.stderr)
				self.CloseConnection()
				print(error, file=sys.stderr)
		return safe_func
		
	def __GetGoodOrederPair(self, order_object, good_object):
		"""
		Функция получения пары товар-заказ
		
		Args:
			order_object: объект заказа, куда идет добавление
			good_object: добавляемый товар
		Return value:
			OrderItem объект, если пара найдена. Если таких пар >1, то выполнится сведение
			Иначе - None
		"""
		order_items = list(OrderItem.select().where((OrderItem.item == good_object) &
													(OrderItem.order == order_object)))
		if len(order_items) > 1:
			print("Warning! Order-item pairs are not unique!")
			for i in range(1, len(order_items)):
				order_items[0] += order_items[i].quantity
				order_items[i].delete_instance()
			order_items[0].save()
		
		if len(order_items) > 0:
			return order_items[0]
		else:
			return None
	
	@__TryWrapper
	def AddToOrder(self, order_object, good_object, quantity):
		"""
		Функция добавления товара в заказ.
		
		Args:
			order_object: объект заказа, куда идет добавление
			good_object: добавляемый товар
			quantity(int): количество товара
		"""
		order_item = self.__GetGoodOrederPair(order_object, good_object)
		if order_item is None:
			order_item = OrderItem.create(item=good_object, order=order_object,
										  quantity=quantity)
		else:
			print("Good is already in order, quantity will be added")
			order_item.quantity += quantity
			order_item.save()
	
	@__TryWrapper
	def RemoveFromOrder(self, order_object, good_object):
		"""
		Функция удаления товара из заказа. Private, т.к. ее нужно обернуть
		
		Args:
			order_object: объект заказа, откуда удаляется товар
			good_object: удаляемый товар
		"""
		order_item = self.__GetGoodOrederPair(order_object, good_object)
		if order_item is None:
			print("Nothing to remove!")
		else:
			order_items.delete_instance()
	
	@__TryWrapper
	def ChangeCount(self, order_id, good_id, quantity):
		"""
		Функция изменения количества товара в заказе. Private, т.к. ее нужно обернуть
		
		Args:
			order_object: объект заказа, куда идет добавление
			good_object: добавляемый товар
			quantity(int): количество товара
		"""
		order_item = self.__GetGoodOrederPair(order_object, good_object)
		if order_item is None:
			self.__AddToOrder(order_id, good_id, quantity)
		else:
			order_item.quantity = quantity
			order_item.save()

	@__TryWrapper
	def Dump(self, filename):
		"""
		Функция сохранения заказов в файл. Private, т.к. ее нужно обернуть
		
		Args:
			filename(str): имя файла, куда сохранять информацию
		"""
		with open(filename, "w") as file:
			results = OrderItem.select(OrderItem, Good, Order, Customer) \
							   .join(Good).switch(OrderItem).join(Order).join(Customer)
			for res in results:
				file.write("{0}\t{1}\t{2}\t{3}\n".format(res.item.vendor, res.item.name,
														 res.order.customer.first_name,
														 res.order.customer.last_name))
	
	@__TryWrapper
	def CreateTables(self):
		self.db.create_tables([Customer, Order, Good, OrderItem])
	
	@__TryWrapper
	def CreateSampleData(self):
		ivanov = Customer.create(first_name='Ivan', last_name='Ivanov')
		petrov = Customer.create(first_name='Vasily', last_name='Petrov')
		order1 = Order.create(customer=ivanov, status='Accepted')
		order2 = Order.create(customer=petrov, status='Waits confirm')
		phone = Good.create(vendor='Siemens', name='Phone', description='Simple')
		iron = Good.create(vendor='Philips', name='Iron', description='Electronic')
		
		OrderItem.create(item=iron, order=order1, quantity=5)
		OrderItem.create(item=phone, order=order1, quantity=2)
		OrderItem.create(item=phone, order=order2, quantity=10)

	def __init__(self):
		"""
		Создает объект ShopDatabase.
		Args:
			config_name (str): имя конфига с параметрами подключения
		"""
		config = configparser.ConfigParser()
		config.read('config.ini')
		connection_params = config['Connection']
		database_name = connection_params['database']
		del connection_params['database']
		
		self.db = pw.PostgresqlDatabase(database_name, **connection_params)
	
	def Reconnect(self):
		"""
		Подключается к базе данных. Здесь не ловим исключения, т.к. они фатальны
		"""
		self.db.connect()
	
	def CloseConnection(self):
		"""
		Завершает соединение с БД. Здесь не ловим исключения, т.к. они фатальны
		"""
		self.db.close()

#При работе нужно использовать этот экземпляр
ShopDatabaseObject = ShopDatabase()

class Customer(pw.Model):
	first_name = pw.CharField()
	last_name = pw.CharField()
	class Meta:
		database = ShopDatabaseObject.db
		
class Order(pw.Model):
	customer = pw.ForeignKeyField(Customer, backref='orders')
	timestamp = pw.DateTimeField(default=datetime.datetime.now)
	status = pw.CharField()
	class Meta:
		database = ShopDatabaseObject.db
		
class Good(pw.Model):
	vendor = pw.CharField()
	description = pw.CharField()
	name = pw.CharField()
	class Meta:
		database = ShopDatabaseObject.db
		
class OrderItem(pw.Model):
	item = pw.ForeignKeyField(Good, backref='order_items')
	order = pw.ForeignKeyField(Order, backref='order_items')
	quantity = pw.IntegerField()
	class Meta:
		database = ShopDatabaseObject.db

		
if __name__ == "__main__":
	ShopDatabaseObject.Reconnect()

	ShopDatabaseObject.CreateTables()
	ShopDatabaseObject.CreateSampleData()
	
	ShopDatabaseObject.Dump("example_dump.txt")
	
	ShopDatabaseObject.CloseConnection()
