#!/bin/sh

psql -U goldmine -W -h localhost -d goldmine -f schema.sql 
