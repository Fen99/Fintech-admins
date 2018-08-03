CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
	first_nm varchar(100),
	last_nm varchar(100)
);

CREATE TABLE orders (
	order_id SERIAL PRIMARY KEY,
	cust_id integer REFERENCES customers(id),
	order_dttm timestamp DEFAULT current_timestamp,
	status varchar(20)
);

CREATE TABLE goods (
	good_id SERIAL PRIMARY KEY, 
	vendor varchar(100),
	name varchar(100),
	description varchar(300)
);

CREATE TABLE order_items (
	order_item_id SERIAL PRIMARY KEY,
	order_id integer REFERENCES orders(order_id),
	good_id integer REFERENCES goods(good_id),
	quantity integer
);
