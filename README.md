PgEvents
========

Dispatching events with Postgres and its NOTIFY/LISTEN.

It will be never better than Redis or other real pubsub project, but it's more integrated.
Less parts, less troubles.

This code targets stable Debian, so use of Postgresql before 9.0.

Triggering events
-----------------

A simple procstoc is used to triggering event.

    trigger_event(channel varchar, payload varchar) RETURNS timestamp

You can trigger events anywhere you can talk to psotgresql.
Serialize payload the way you want : json, msgpack, protobuff… .

Listening events
----------------

Postgresql provides a strange pubsub pattern with its NOTIFY/LISTEN.
Listening is not a blocking action. After listening a channel, your connection
is able to get events, anytime, maybe while executing an other query.
Your driver have to handle it specificaly. The PHP implementation is a joke.
Psycopg (a fancy python drivers) handles it nicely, and the documentation explains
how to implement a subscribe pattern.

Events (the tuple timestamp, channel, payload) are stored because Postgresql
handles payload in 9.0, too young for stable Debian.
Subscriber can crash, or be started later, it will fetch old events before being more realtime.
This pattern is a way to decoupling main application, a website wich can't wait nobody,
and more quiet async workers. It's not a real working queue, this is not yet another Celery.

Licence
-------

Three clauses BSD Licence.
