## Example of entering the pod and logining into Postgres

```
# ENTER THE POSTGRES POD
kubectl -n postgresql exec -it postgres-0 -- bash

# LOGIN TO POSTGRES
psql --username=postgresadmin postgresdb

# CREATE A TABLE
CREATE TABLE # login to postgres (username text, password text, customer_id serial, date_created timestamp);

# ADD A TABLE RECORD
INSERT INTO customers (firstname, lastname) VALUES ( 'Bob', 'Smith');

#show the table
\dts

# quit out of postgresql
\q
```
