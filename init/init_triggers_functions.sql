CREATE OR REPLACE FUNCTION log_ticket_changes()
RETURNS TRIGGER AS $func$
BEGIN
    INSERT INTO ticket_logs (ticket_id, old_status, new_status)
    VALUES (OLD.id, OLD.status, NEW.status);
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_ticket_changes
AFTER UPDATE ON trouble_tickets
FOR EACH ROW
EXECUTE FUNCTION log_ticket_changes();

-- тут триггер для ведения анализа успеваемости

CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    worker_login VARCHAR(100),
    activity_count INT DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (worker_login)
);

CREATE OR REPLACE FUNCTION log_user_activity()
RETURNS TRIGGER AS $func$
BEGIN
    -- Проверяем, существует ли запись для данного worker_login
    IF EXISTS (SELECT 1 FROM user_activity_log WHERE worker_login = NEW.worker_login) THEN
        -- Если существует, увеличиваем счетчик
        UPDATE user_activity_log
        SET activity_count = activity_count + 1,
            last_activity = CURRENT_TIMESTAMP
        WHERE worker_login = NEW.worker_login;
    ELSE
        -- Если не существует, создаем новую запись
        INSERT INTO user_activity_log (worker_login, activity_count)
        VALUES (NEW.worker_login, 1);
    END IF;

    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_works
AFTER INSERT ON works
FOR EACH ROW
EXECUTE FUNCTION log_user_activity();
