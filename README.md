# Google Hotels Scraper

> **This repository holds usage examples only.** The scraper itself runs on Apify:
> **[https://apify.com/sumitr_mardy/google-hotels-scraper](https://apify.com/sumitr_mardy/google-hotels-scraper)** (no install, no server, pay per result).
>
> Examples here: [Python](examples/run.py) · [Node.js](examples/run.mjs) · [cURL](examples/run.sh) · [input.json](examples/input.json)

Export public Google Hotels nightly prices, calculated stay totals, hotel stars, guest ratings, review counts and coordinates for city/date searches. Exactly **2 adults** are supported. Not affiliated with Google.

Use relative check-in dates for daily price monitoring. For flight fares, use the sister [Google Flights Scraper](https://apify.com/sumitr_mardy/google-flights-scraper).

<!-- firstscreen:start -->
## Try it in one minute, no code

1. Open the [Google Hotels Scraper on Apify Store](https://apify.com/sumitr_mardy/google-hotels-scraper) and click **Try for free**. Apify's free plan gives you **$5 of credit every month**, no credit card needed.
2. Type a city, such as `Lisbon`, and pick check-in and nights.
3. Click **Start**, then download the results as **Excel, CSV or JSON**, or send them to Google Sheets.

**Price: $2.00 per 1,000 hotels.** The free $5 covers about **2,500 hotels** a month.

Real output from a run of the default input:

| Hotel | Stars | Rating | Reviews | Price/night |
|---|---|---|---|---|
| Brown's / Avenue Hotel | 5 | 4.6 | 290 | $150 |
| Next Level Premium Hotels Lisbon | 3 | 4.6 | 975 | $89 |
| WC by The Beautique Hotels | 4 | 4.4 | 1050 | $88 |
<!-- firstscreen:end -->

## Quick start

```json
{
  "locations": ["Lisbon"],
  "checkInDaysFromToday": 30,
  "nights": 2,
  "adults": 2,
  "maxHotels": 18
}
```

The small default input returns at most 5 hotels from one query. NYC/New York and Da Nang/Đà Nẵng aliases are supported. Location names are resolved against a bundled GeoNames city directory before requesting hotel results; unknown names return a free invalid_input row. Use a city, optionally with a comma-separated country. The directory covers cities over roughly 15,000 population plus administrative capitals, not every village. Ambiguous names prefer the most populous matching city unless a recognized country qualifier is provided.

## Input

| Field | Default | Meaning |
|---|---|---|
| locations | required | Up to 50 city strings. Aliases that resolve to the same city and stay are deduplicated. |
| checkIn / checkOut | absent | YYYY-MM-DD dates; future/tonight, checkout after check-in, at most 30 nights. |
| checkInDaysFromToday | 30 | 0–365 UTC days from original run start, used when checkIn is absent. |
| nights | 2 | 1–30 nights, used when checkOut is absent. |
| adults | 2 | Only 2 is supported. Any other value is failed/invalid_input with zero hotel events. |
| maxHotels | 18 | 1–200 unique rows per location; default prefill uses 5. |
| expandWithVariants | maxHotels > 18 | Adds star-class queries (5, 4, 3, 2) and cheap, then extraAreas. |
| extraAreas | [] | Up to 10 neighbourhood names appended to city queries. Used with expansion enabled. |
| minStars | 0 | Local 0–5 hotel-class filter, not guest rating. Filtered rows are not charged. |
| currency | USD | Requested currency; output currency always reflects the returned page. |
| language / country | en / us | Requested page locale/search context; country is not a geographic filter. |

A location can optionally be an object with location, checkIn, checkOut, checkInDaysFromToday, nights or adults overrides. This is useful for mixed stays; invalid entries produce individual free rows. Relative dates use the original Actor start timestamp so migration across midnight does not change the requested stay.

## Output

One row per unique hotel per location. Every row always contains the same 29 keys, with no null: missing strings are empty, numbers 0, arrays [].

| Field | Type |
|---|---|
| inputIndex | number |
| location | string |
| resolvedLocation | string |
| checkIn | string |
| checkOut | string |
| nights | number |
| adults | number |
| name | string |
| hotelClass | string |
| stars | number |
| rating | number |
| reviewsCount | number |
| price | number |
| pricePerNight | number |
| priceTotal | number |
| priceText | string |
| currency | string |
| dealText | string |
| latitude | number |
| longitude | number |
| amenities | array |
| thumbnail | string |
| queryVariant | string |
| position | number |
| searchUrl | string |
| status | string |
| subStatus | string |
| error | string |
| scrapedAt | string |

price and pricePerNight are the numeric nightly rate from Google's public result data. priceTotal is pricePerNight × nights, rounded to two decimals. It is a calculated total, not a separate vendor offer or guaranteed checkout amount; Google's rounded display total can differ. priceText preserves the displayed nightly label. These are the lowest offers Google shows at run time for those dates, currency and country, not a booking quote. Taxes/fees are not broken out. No per-vendor offers or booking URLs are collected.

resolvedLocation always reports Google's resolved place label when a page was returned; it is empty for errors rejected before fetching. Names are compared without accents, with known aliases expanded. For recognized input cities, a hotel is rejected for location mismatch only when there is **no shared place-name word and it is more than 100 km from the requested city's offline coordinate**. Nearby neighbourhoods can have different labels and remain valid. This is a broad city/metro check, not a city-boundary guarantee; shared generic place words can also make the test permissive.

Returned stay dates and the HTML Adults control must match the requested stay and 2 adults before rows are saved or charged. The stay-array value after the dates is nights, not occupancy.

Amenities and thumbnail are optional; absent fields remain [] / empty. queryVariant identifies which query first found a hotel; position counts saved rows across that location. Zero stars means no class was supplied, not a zero-star hotel.

## Status and charging

| status / subStatus | Meaning | Hotel event charged? |
|---|---|---|
| ok / hotel | Unique hotel saved after checks and filters | Yes |
| no_results / no_results | No hotels remained after search/filtering | No |
| failed / invalid_input | Unsupported occupancy, unknown city or invalid date/input | No |
| failed / dates_not_applied | Returned stay differs | No |
| failed / occupancy_not_applied | HTML does not confirm two adults | No |
| failed / location_not_applied | No shared place-name word and hotels farther than 100 km | No |
| failed / http_NNN, blocked, empty_page, parse_error, network_error | Fetch or extraction failed | No |
| failed / free_work_limit, cost_limit_reached | Work/spending guard stopped remaining work | No |

## Pricing

Per saved hotel: FREE $0.002, BRONZE $0.0015, SILVER $0.0012, GOLD and higher $0.001. Default Actor start is $0.00005 (per GB, minimum one event). Failed, empty, duplicate and filtered rows have no hotel event; the start fee still applies. Platform usage is included; there is no separate dataset-item charge.

## Coverage and reliability

Only the first public server-rendered result list for each query is used, typically 18–20 hotels. Query variants broaden coverage: the measured Lisbon spike found 111 unique hotels across city, star, cheap and area queries before a 100-hotel cap. Expect roughly up to 100 in supported cities, not the full inventory; maxHotels 200 is a cap, not a promise. No pagination through internal RPC. A minStars query starts with the requested star class and filters locally.

The initial spike returned rows for 13/13 real queries, with 235/235 prices and matching stay dates; Apify returned USD. A second owner-approved check confirmed that natural-language requests for 3 adults were ignored, and a nonsense location fell back to Washington DC. Those are now rejected or guarded rather than sold as successful results. No success-rate advantage over a competitor is claimed from these small tests.

Two searches at most run concurrently; each worker pauses at least 500 ms after a response. Empty shells have bounded retries, with default datacenter proxy only as a final fallback. Actual CAPTCHA, sorry or consent pages stop the host for the run. Pages are loaded in a real headless Chrome that identifies itself as HeadlessChrome, because Google Travel turns away non-browser clients. No cookies, login, residential proxy, page-JS tokens or challenge bypass. Hard request deadlines and a free-work budget bound failed searches. Progress and dedupe are checkpointed between query pages; abrupt failure between saving data and its checkpoint can replay in-flight work, so downstream consumers can also dedupe by inputIndex, name, coordinates and dates.

## Public presets and scheduled checks

- [Google Hotels Scraper - Prices for a City and Dates](https://apify.com/sumitr_mardy/google-hotels-scraper/examples/google-hotels-scraper-prices-for-a-city-and-dates)
- [5-Star Hotel Prices by City - Google Hotels Export](https://apify.com/sumitr_mardy/google-hotels-scraper/examples/5-star-hotel-prices-by-city-google-hotels-export)
- [Google Hotels Price Monitor for Scheduled Runs](https://apify.com/sumitr_mardy/google-hotels-scraper/examples/google-hotels-price-monitor-for-scheduled-runs)

To schedule: duplicate a preset into your account, keep checkInDaysFromToday and nights instead of fixed dates, save input, then open Apify Console → Schedules → Create schedule. Choose the saved task, your timezone and daily frequency. Review run statuses and actual currency before comparing snapshots. This Actor does not create schedules automatically.

## API examples

```bash
curl -X POST "https://api.apify.com/v2/acts/sumitr_mardy~google-hotels-scraper/run-sync-get-dataset-items?format=json" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"locations":["Lisbon"],"checkInDaysFromToday":30,"nights":2,"maxHotels":5}'
```

```python
import os
from apify_client import ApifyClient
client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("sumitr_mardy/google-hotels-scraper").call(
    run_input={"locations": ["Da Nang"], "checkInDaysFromToday": 14,
               "nights": 1, "adults": 2, "maxHotels": 36}
)
for row in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(row["name"], row["resolvedLocation"], row["pricePerNight"], row["currency"], row["status"])
```

For multiple cities or variants, use asynchronous runs and fetch the dataset after completion.


<!-- seo:start -->
## What can you do with Google Hotels data?

- Monitor hotel prices in a city for revenue management
- Compare hotel rates, stars and ratings for travel planning
- Export hotels with coordinates for market maps

## How to scrape Google Hotels

1. Open the actor and click **Try for free** (an Apify account is free, no card needed).
2. Fill in **Locations** (cities) and check-in / check-out dates.
3. Click **Start** and wait for the run to finish.
4. Download the results as JSON, CSV, Excel or HTML, or get them through the API, Zapier, Make, n8n or MCP.

## How much does it cost to scrape Google Hotels?

It costs **$2 per 1,000 hotels** on the free plan, less on paid Apify plans, and failed inputs cost nothing. Apify's free plan includes $5 of monthly credit, which covers about **2,500 hotels** every month.

## Is it legal to scrape Google Hotels?

This actor only reads publicly available data and does not log in. Scraping public data is generally lawful, but results can include personal data protected by GDPR, CCPA and similar laws, and each website has its own terms. Use the data for legitimate purposes and ask a lawyer if you are unsure.

## Related scrapers

- [Google Flights Scraper](https://apify.com/sumitr_mardy/google-flights-scraper)
- [Airbnb Scraper](https://apify.com/sumitr_mardy/airbnb-search-scraper)

<!-- seo:end -->

## Use it from AI agents (MCP)

Hosted OAuth:
```json
{"mcpServers":{"hotels":{"url":"https://mcp.apify.com/?tools=sumitr_mardy/google-hotels-scraper"}}}
```

Hosted Bearer alternative:
```json
{"mcpServers":{"hotels":{"url":"https://mcp.apify.com/?tools=sumitr_mardy/google-hotels-scraper","headers":{"Authorization":"Bearer YOUR_APIFY_TOKEN"}}}}
```

Stdio:
```json
{"mcpServers":{"hotels":{"command":"npx","args":["-y","@apify/actors-mcp-server","--tools","sumitr_mardy/google-hotels-scraper"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask for a city, currency and stay strategy. Use exactly two adults, inspect status/subStatus, resolvedLocation and actual currency, and distinguish calculated totals from booking quotes. For flights combine this with the [Google Flights Scraper](https://apify.com/sumitr_mardy/google-flights-scraper).

City anchors and alternate names: [GeoNames](https://www.geonames.org/), derived from its [cities15000 dump](https://download.geonames.org/export/dump/) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).


## Node.js

```js
import { ApifyClient } from "apify-client";

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor("sumitr_mardy/google-hotels-scraper").call({
  "locations": [
    "Lisbon"
  ],
  "maxHotels": 5
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```
