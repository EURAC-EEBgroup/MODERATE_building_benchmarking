\connect store_data

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';

CREATE TABLE public.measurement (
    time   TIMESTAMPTZ   NOT NULL,
    sensor_id uuid NOT NULL,
    value DOUBLE PRECISION  NOT NULL,
    PRIMARY KEY (time, sensor_id)
);

SELECT create_hypertable('public.measurement', 'time', if_not_exists => TRUE, create_default_indexes => TRUE);
