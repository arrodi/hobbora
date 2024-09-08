## Example of entering the pod and logining into Postgres

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
