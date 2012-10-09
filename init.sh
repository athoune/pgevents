#!/bin/sh

dropdb pubsub
createdb pubsub
psql pubsub -f init.sql
