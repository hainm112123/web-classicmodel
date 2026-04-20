The MySQL container uses the root-level `mysqlsampledatabase.sql` file as its initialization script.

Docker Compose mounts it into `/docker-entrypoint-initdb.d/01-classicmodels.sql` so the sample schema and data load automatically on first startup.

