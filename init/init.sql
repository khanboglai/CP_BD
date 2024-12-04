CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    birth_date TIMESTAMP,
    email VARCHAR(100) UNIQUE,
    login VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(100),
    usr_role VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS complexes (
    ИСН SERIAL PRIMARY KEY,
    name VARCHAR(300),
    factory_id INT,
    creation_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS storage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    count INT,
    complex_name VARCHAR(300)
);

CREATE TABLE IF NOT EXISTS trouble_tickets (
    id SERIAL PRIMARY KEY,
    ИСН SERIAL,
    name VARCHAR(300)
    problem VARCHAR(1000),
    date TIMESTAMP,
    status BOOLEAN,
    FOREIGN KEY (ИСН) REFERENCES complexes(ИСН) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    creation_date TIMESTAMP,
    file_path TEXT,
    author_id INT,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);