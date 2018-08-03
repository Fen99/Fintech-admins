INSERT INTO customers (first_nm, last_nm) VALUES
    ('Ivan', 'Ivanov'),
    ('Vladimir', 'Petrov');
	
INSERT INTO orders (cust_id, status) VALUES
    (1, 'Accepted'),
    (2, 'Waits confirm');
	
INSERT INTO goods (vendor, name, description) VALUES
	('Siemens', 'Phone', 'Simple phone'),
	('Bosh', 'Iron', 'Electric iron');
	
INSERT INTO order_items (order_id, good_id, quantity) VALUES
	(1, 1, 5),
	(1, 2, 2),
	(2, 2, 4);
