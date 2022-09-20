#! /bin/bash

docker compose down
docker compose up -d
while ! curl -sSL "http://localhost:4444/wd/hub/status" 2>&1 \
        | jq -r '.value.ready' 2>&1 | grep "true" >/dev/null; do
    echo 'Waiting for the Grid'
    sleep 1
done

source /home/emerson/git/tcc/googlemaps-scraper/.venv/bin/activate
python scraper.py &
