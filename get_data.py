import asyncio

from foudinge.data import (
    get_all_reviews_sqlite,
    filter_restaurant_urls,
    parse_directory,
    get_page,
    check_urls,
)


base_url = "https://lefooding.com/restaurants"
n_pages = 107
urls = []
for page in range(n_pages):
    urls += list(
        set(
            filter_restaurant_urls(
                parse_directory(get_page(base_url + f"?page={page}"))
            )
        )
    )  ## moche

db_name = "reviews.db"
base_url = "https://lefooding.com/"
missing_urls = check_urls(db_name, urls)
print(len(missing_urls))
print(asyncio.run(get_all_reviews_sqlite(db_name, base_url, missing_urls)))
