import asyncio
import aiohttp
import bs4
import requests
import sqlite3
from typing import Tuple, List


def get_page_async(url):
    with requests.get(url) as response:
        return response.text


def get_page(url):
    with requests.get(url) as response:
        return response.text


def parse_directory(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    targeturis = [
        link["href"]
        for link in links
        if link.has_attr("href") and link["href"].startswith("/restaurants")
    ]
    return targeturis


def filter_restaurant_urls(url_list):
    """
    Filter out non-restaurant URLs.

    This is very crude.
    """
    return [
        url
        for url in url_list
        if url.startswith("/restaurants")
        and not "?" in url
        and not url == "/restaurants"
    ]


async def get_review(session: aiohttp.ClientSession, url: str) -> Tuple[str, str]:
    async with session.get(url) as response:
        html = await response.text()
        soup = bs4.BeautifulSoup(html, "html.parser")
        review = soup.find("article").text.strip().split("//")[0]
        title1 = soup.find("h1", class_="pageGuide__title")
        title2 = soup.find("div", class_="pageGuide__title")
        if title1:
            title = title1.text.strip()
        elif title2:
            title = title2.text.strip()
        else:
            title = "Missing title"
        return title, review


async def get_all_reviews(base_url: str, urls: List[str]) -> List[Tuple[str, str]]:
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=10)
    ) as session:
        results = await asyncio.gather(
            *[get_review(session, base_url + url) for url in urls]
        )

    return results


async def get_all_reviews_sqlite(db_path: str, base_url: str, urls: List[str]):
    # Set up SQLite database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute("""CREATE TABLE IF NOT EXISTS reviews
                 (url TEXT PRIMARY KEY, title TEXT, review TEXT)""")

    # Process in batches of 20
    batch_size = 200

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i : i + batch_size]

            # Get batch of reviews
            results = await asyncio.gather(
                *[get_review(session, base_url + url) for url in batch_urls],
                return_exceptions=True,
            )

            # Filter out any errors and prepare data for insertion
            valid_results = []
            for url, result in zip(batch_urls, results):
                if isinstance(result, Exception):
                    print(f"Error processing {url}: {str(result)}")
                    continue
                title, review = result
                valid_results.append((url, title, review))

            # Update existing rows or insert new ones
            c.executemany(
                """
                INSERT INTO reviews(url, title, review)
                VALUES(?, ?, ?)
                ON CONFLICT(url)
                DO UPDATE SET
                    title=excluded.title,
                    review=excluded.review
            """,
                valid_results,
            )
            conn.commit()

    conn.close()

    return True


def check_urls(db_name, urls):
    try:
        with sqlite3.connect(db_name) as conn:
            c = conn.cursor()

            # Check if all URLs are present in the database
            c.execute("SELECT url FROM reviews")
            existing_urls = set(row[0] for row in c.fetchall())

            missing_urls = set(urls) - existing_urls

            return list(missing_urls)
    except sqlite3.OperationalError:
        print(f"Databse {db_name} does not exist")
        return urls
