## Docker commands to run the container locally:

1. Pull the desired Docker images

docker pull postgres:latest
docker pull dpage/pgadmin4:latest

2. Create a docker volume for minio to persist data

docker volume create postgres-data

3. Run the image as a container

docker run -p 5432:5432 --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_USER=postgresadmin \
  -e POSTGRES_PASSWORD=super_secure_password_987 \
  -e POSTGRES_DB=hobbora-db \
  -d postgres:16.4

## Example of entering the pod and loggining into Postgres

```
# ENTER THE POSTGRES POD
kubectl -n postgresql exec -it postgres-0 -- bash

# LOGIN TO POSTGRES
psql --username=postgresadmin postgresdb

# CREATE A TABLE
CREATE TABLE IF NOT EXISTS USER_ACCOUNT
                        (USER_ID serial PRIMARY KEY, USER_NAME text, USER_PASS text);

# ADD A TABLE RECORD
INSERT INTO USER_ACCOUNT (USER_NAME, USER_PASS) VALUES ( 'Bob', 'Bobpassword123');

#show the table
\dts

# quit out of postgresql
\q
```
