-- init.sql
CREATE DATABASE superstore;

\c superstore

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    row_id         INTEGER PRIMARY KEY,
    order_id       VARCHAR(20)    NOT NULL,
    order_date     DATE           NOT NULL,
    ship_date      DATE,
    ship_mode      VARCHAR(30),
    customer_id    VARCHAR(20),
    customer_name  VARCHAR(100),
    segment        VARCHAR(30),
    country        VARCHAR(50),
    city           VARCHAR(100),
    state          VARCHAR(50),
    postal_code    VARCHAR(10),
    region         VARCHAR(20),
    product_id     VARCHAR(30),
    category       VARCHAR(50),
    sub_category   VARCHAR(50),
    product_name   VARCHAR(255),
    sales          NUMERIC(12, 4) NOT NULL,
    quantity       INTEGER,
    discount       NUMERIC(4, 2),
    profit         NUMERIC(12, 4)
);

CREATE INDEX idx_orders_order_id    ON orders (order_id);
CREATE INDEX idx_orders_order_date  ON orders (order_date);
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_product_id  ON orders (product_id);