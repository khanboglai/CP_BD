CREATE VIEW analitic_view AS
SELECT worker_login, activity_count 
FROM user_activity_log;

CREATE VIEW user_with_age AS
SELECT *, DATE_PART('year', AGE(current_date, birth_date))::INTEGER AS age
FROM users;

CREATE VIEW auth_view AS
SELECT id, usr_role, hashed_password, login 
FROM users;