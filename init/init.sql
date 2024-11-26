CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    birth_date TIMESTAMP,
    age INT CHECK (age >= 0),
    email VARCHAR(100) UNIQUE,
    login VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS storage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    count INT,
    complex_name VARCHAR(200)
);


CREATE TABLE IF NOT EXISTS trouble_tickets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    problem VARCHAR(1000),
    date TIMESTAMP,
    status BOOLEAN
);


CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    creation_date TIMESTAMP,
    author_id INT,
    FOREIGN KEY (author_id) REFERENCES users(id)
);