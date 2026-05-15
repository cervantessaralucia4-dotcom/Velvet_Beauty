CREATE DATABASE velvet_beauty;

CREATE TABLE categories(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255)
);

INSERT INTO categories(name)
VALUES
('Skincare'),
('Makeup'),
('Lipstick'),
('Foundation'),
('Perfume');


CREATE TABLE products(

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(255),

    brand VARCHAR(255),

    description TEXT,

    price DECIMAL(10,2),

    stock INT,

    category_id INT,

    main_image VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(category_id)
    REFERENCES categories(id)

);

CREATE TABLE product_images(

    id INT AUTO_INCREMENT PRIMARY KEY,

    product_id INT,

    image_url VARCHAR(255),

    FOREIGN KEY(product_id)
    REFERENCES products(id)

);