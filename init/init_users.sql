-- Создание роли worker
CREATE ROLE worker WITH LOGIN PASSWORD 'worker';

-- Назначение прав на чтение и запись на все существующие таблицы в схеме public
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO worker;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO worker;

-- Установка прав на создание новых таблиц и последовательностей в схеме public
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO worker;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO worker;

-- Создание роли admin
CREATE ROLE admin WITH LOGIN PASSWORD 'admin' SUPERUSER;

-- Выдача прав для роли admin
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Установка прав по умочанию для новых таблиц и последовательностей в схеме public
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO admin;

-- Создание пользователей
CREATE USER worker1 WITH PASSWORD 'worker';
GRANT worker TO worker1;

CREATE USER admin1 WITH PASSWORD 'admin';
GRANT admin TO admin1;
