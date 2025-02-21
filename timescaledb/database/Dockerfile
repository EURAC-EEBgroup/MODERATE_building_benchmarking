# FROM postgres:11
FROM timescale/timescaledb:latest-pg13

ENV POSTGRES_DB store_data

COPY initdb.sql /docker-entrypoint-initdb.d/