import requests
import pandas as pd
from datetime import datetime
import time

# =============================================================================
# ACTIVE CODE - Used to obtain review datasets
# =============================================================================

def fetch_steam_reviews(app_id,
                        filter_by='all',
                        language='all',
                        day_range=30,
                        review_type='all',
                        purchase_type='all',
                        num_per_page=100):
    """
    Fetches all Steam reviews for a given app_id, paging through cursors.
    Returns a list of raw review dicts and also times how long it takes 
    """
    start = time.time()
    reviews = []
    cursor = '*'

    base_url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        'json': 1,
        'filter': filter_by,
        'language': language,
        'day_range': day_range,
        'review_type': review_type,
        'purchase_type': purchase_type,
        'num_per_page': num_per_page,
        'cursor': cursor,
    }

    while True:
        params['cursor'] = cursor
        resp = requests.get(base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

        batch = data.get('reviews', [])
        if not batch:
            break

        reviews.extend(batch)
        cursor = data.get('cursor')
        # When Steam returns the same cursor twice or no cursor, we stop
        if not cursor or cursor == params['cursor']:
            break
        
    end = time.time()
    print("Time taken to fetch:", end - start)
    return reviews


def reviews_to_dataframe(raw_reviews):
    """
    Maps the raw review JSON into a pandas DataFrame with selected fields.
    """
    records = []
    for r in raw_reviews:
        created = datetime.fromtimestamp(r['timestamp_created'])
        records.append({
            'review_id':              r.get('recommendationid'),
            'steam_id':               r.get('author', {}).get('steamid'),
            'num_games_owned':        r.get('author', {}).get('num_games_owned'),
            'num_reviews_by_user':    r.get('author', {}).get('num_reviews'),
            'playtime_at_review_m':   r.get('author', {}).get('playtime_at_review'),
            'language':               r.get('language'),
            'date_of_review':         created,
            'recommended':            r.get('voted_up'),
            'votes_helpful':          r.get('votes_up'),
            'votes_funny':            r.get('votes_funny'),
            'comment_count':          r.get('comment_count'),
            'steam_purchase':         r.get('steam_purchase'),
            'received_for_free':      r.get('received_for_free'),
            'weighted_vote_score':    r.get('weighted_vote_score'),
            'review_text':            r.get('review'),
        })
    df = pd.DataFrame.from_records(records)
    return df


if __name__ == '__main__':
    print("In main")

    # 1) Set your target App ID (e.g., 730 for CS:GO, 440 for Team Fortress 2)
    app_id = 315210

    # 2) Fetch reviews
    print("Before fetch function")
    raw = fetch_steam_reviews(
        app_id=app_id,
        filter_by='recent',     # recent, updated, or all
        language='english',     # two-letter codes like 'en', or 'all'
        day_range=180,          # up to 365 if filter='all'
        review_type='all',      # all, positive, negative
        purchase_type='all',    # all, steam, non_steam_purchase
        num_per_page=100        # max 100
    )

    # 3) Build DataFrame
    print("Before pandas to storage function")
    df = reviews_to_dataframe(raw)

    # 4) Output to Excel
    print("Before store to excel")
    output_file = f'steam_reviews_{app_id}.xlsx'

    # Using the xlsxwriter engine and set a safe datetime format
    with pd.ExcelWriter(
        output_file,
        engine='xlsxwriter',
        engine_kwargs={'options': {'strings_to_formulas': False}},
        datetime_format='yyyy-mm-dd hh:mm:ss'
    ) as writer:
        df.to_excel(writer, index=False)

    print(f"\nExported {len(df)} reviews to {output_file}")

    print("End of main")