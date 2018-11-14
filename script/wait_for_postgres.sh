#!/bin/bash

# wait for Postgres to start
function postgres_ready() {
python << END
import sys
import psycopg2
import os
try:
    conn = psycopg2.connect(dbname=os.environ.get('POSTGRES_DB'),
                            user=os.environ.get('POSTGRES_USER'),
                            password=os.environ.get('POSTGRES_PASSWORD'),
                            host="db")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Start app
>&2 echo "Postgres is up - executing command"

./script/start.sh