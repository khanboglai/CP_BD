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
    name VARCHAR(300) UNIQUE,
    factory_id SERIAL,
    creation_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS storage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    count INT CHECK (count > 0),
    complex_name VARCHAR(300),
    CONSTRAINT fk_complex_name FOREIGN KEY (complex_name) REFERENCES complexes(name) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS trouble_tickets (
    id SERIAL PRIMARY KEY,
    ИСН SERIAL,
    name VARCHAR(300),
    problem VARCHAR(1000),
    date TIMESTAMP,
    status BOOLEAN,
    FOREIGN KEY (ИСН) REFERENCES complexes(ИСН) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(300),
    creation_date TIMESTAMP,
    file_path TEXT,
    author_login VARCHAR(100),
    FOREIGN KEY (author_login) REFERENCES users(login) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS works (
    id SERIAL PRIMARY KEY,
    worker_login VARCHAR(100),
    ИСН SERIAL,
    finisd_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    tt_id SERIAL,
    CONSTRAINT fk_worker_id FOREIGN KEY (worker_login) REFERENCES users(login) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_ISN FOREIGN KEY (ИСН) REFERENCES complexes(ИСН) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_tt_id FOREIGN KEY (tt_id) REFERENCES trouble_tickets(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE ticket_logs (
    id SERIAL PRIMARY KEY,
    ticket_id SERIAL,
    old_status BOOLEAN,
    new_status BOOLEAN,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE used_details (
    id SERIAL PRIMARY KEY,
    work_id SERIAL,
    detail_id SERIAL,
    CONSTRAINT fk_work_id FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_detail_id FOREIGN KEY (detail_id) REFERENCES storage(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    worker_login VARCHAR(100),
    activity_count INT DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (worker_login)
);