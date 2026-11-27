# pip install apify-client ; export APIFY_TOKEN=...  (Apify Console > Settings > API & Integrations)
import json, os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run_input = json.load(open(os.path.join(os.path.dirname(__file__), "input.json")))
run = client.actor("sumitr_mardy/google-hotels-scraper").call(run_input=run_input)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(json.dumps(item, ensure_ascii=False))
