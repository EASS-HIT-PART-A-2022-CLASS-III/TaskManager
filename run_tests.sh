docker exec -it taskmanager-db-1 bash -c "
psql -U postgres -c \"DROP DATABASE IF EXISTS test_db;\"
psql -U postgres -c \"CREATE DATABASE test_db;\""

docker exec -it taskmanager-backend-1 pytest