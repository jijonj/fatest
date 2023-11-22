-- INSERT INTO todos (title, description, priority, complete, owner_id) VALUES
--   ('Dummy Task 4', 'This is a dummy task 1', 3, false, 4),
--   ('Dummy Task 5', 'This is a dummy task 2', 3, false, 2),
--   ('Dummy Task 6', 'This is a dummy task 3', 3, false, 3);
select * from todos;

-- uvicorn main:app --host 0.0.0.0 --port 10000