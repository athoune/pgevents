CREATE TABLE events (
    id serial PRIMARY KEY,
    channel varchar,
    payload varchar,
    ts timestamp);

CREATE OR REPLACE FUNCTION trigger_event(channel varchar, payload varchar) RETURNS timestamp AS $$
DECLARE
    ts timestamp;
BEGIN
    ts = 'now';
    INSERT INTO events (channel, payload, ts) VALUES (channel, payload, ts);
    EXECUTE 'NOTIFY ' || channel;
    -- FIXME cleanup old events
    RETURN ts;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION on_event(chan varchar, lastseen timestamp) RETURNS TABLE(ts timestamp, payload varchar) AS $$
DECLARE
BEGIN
    RETURN QUERY SELECT events.ts, events.payload
        FROM events WHERE events.channel=chan AND lastseen < events.ts
        ORDER BY events.ts;
END;
$$ LANGUAGE plpgsql;
-- FIXME add index on events.channel and events.ts
