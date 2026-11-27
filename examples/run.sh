#!/bin/sh
# APIFY_TOKEN=... sh run.sh   — waits for the run and prints the rows as JSON
curl -s -X POST "https://api.apify.com/v2/acts/sumitr_mardy~google-hotels-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d @"$(dirname "$0")/input.json"
