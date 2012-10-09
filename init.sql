CREATE TABLE events (
    id serial PRIMARY KEY,
    channel varchar,
    payload varchar,
    ts timestamp);

CREATE TYPE event AS (
    payload varchar,
    ts timestamp
);

CREATE TYPE my_events AS (
    events event[],
    last timestamp
);

CREATE OR REPLACE FUNCTION trigger_event(channel varchar, payload varchar) RETURNS timestamp AS $$
DECLARE
    ts timestamp;
BEGIN
    INSERT INTO events (channel, payload, ts) VALUES (channel, payload, ts);
    NOTIFY channel;
    RETURN ts;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION on_event(channel varchar, lastseen timestamp) RETURNS my_events AS $$
DECLARE
    max timestamp;
    tas event[];
    my my_events;
    e event;
BEGIN
    LISTEN channel;
    FOR e IN SELECT payload, ts FROM events WHERE lastseen > ts ORDER BY ts LOOP
        tas := tas || ARRAY[e];
        max := ts;
    END LOOP;
    my := (tas, max);
    RETURN my;
END;
$$ LANGUAGE plpgsql;
