-- Создание роли worker
CREATE ROLE worker WITH LOGIN PASSWORD 'worker';

-- Назначение прав на чтение и запись на все существующие таблицы в схеме public
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO worker;

-- Установка прав на создание новых таблиц в схеме public
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO worker;

-- Создание роли admin
CREATE ROLE admin WITH LOGIN PASSWORD 'admin' SUPERUSER;

-- Создание пользователей
CREATE USER worker1 WITH PASSWORD 'worker';
GRANT worker TO worker1;

CREATE USER admin1 WITH PASSWORD 'admin';
GRANT admin TO admin1;
