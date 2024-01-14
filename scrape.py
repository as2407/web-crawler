from bs4 import BeautifulSoup
import time
import requests
import json

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}


def retryable(max_retries=3, delay=10):
    def decorator_retryable(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    return result

                except Exception as e:
                    print(f"Attempt {attempt}/{max_retries} failed: {e}")
                    if attempt < max_retries:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print("Max retries reached, operation failed.")
                        raise

        return wrapper

    return decorator_retryable


def read_queries():
    queries = []
    with open('query_set.txt') as qs:
        for query in qs:
            queries.append(query.strip())
    return queries


def scrape_search_result(soup):
    raw_results = soup.find_all('li', class_='b_algo')
    results = []
    unique_set = set()
    for result in raw_results:
        if len(results) == 10:
            break
        a_tag = result.find('a')
        if a_tag:
            link = a_tag.get('href')
            if link in unique_set or link is None:
                continue
            results.append(link)
            unique_set.add(link)
    return results


@retryable(max_retries=10, delay=60)
def search(query):
    # time.sleep(1)
    url = 'https://www.bing.com/search'
    params = {'q': query, 'count': 30}
    response = requests.get(url, headers=USER_AGENT, params=params, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")
    #         print(soup.find_all('li'))
    new_results = scrape_search_result(soup)
    while len(new_results) == 0:
        response = requests.get(url, headers=USER_AGENT, params=params, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")
        new_results = scrape_search_result(soup)
    return new_results


def automate_search(query_list):
    dataset = {}
    for query in query_list:
        print(len(dataset) + 1, query)
        dataset[query] = search(query)

    return dataset


if __name__ == '__main__':
    query_list = read_queries()
    data = automate_search(query_list)
    json_string = json.dumps(data, indent=4)
    with open('our_result.json', 'w') as json_file:
        json_file.write(json_string)
