## Example of entering the pod and logining into Postgres

---

kubectl -n postgresql exec -it postgres-0 -- bash

# login to postgres
psql --username=postgresadmin postgresdb

# see our replication user created
\du

#create a table
CREATE TABLE customers (firstname text, customer_id serial, date_created timestamp);

#show the table
\dt

# quit out of postgresql
\q

---
