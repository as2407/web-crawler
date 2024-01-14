import json
import re
import csv


def read_files():
    with open('google_result.json', 'r') as file:
        google = json.load(file)

    with open('our_result.json', 'r') as file:
        bing = json.load(file)

    queries = []
    with open('query_set.txt') as qs:
        for query in qs:
            queries.append(query.strip())

    return google, bing, queries


def clean_link(link):
    print(link)
    link = re.sub('https://', '', link)
    link = re.sub('http://', '', link)
    link = re.sub('www.', '', link)
    link = link.rstrip('/')
    return link


def analyze(g_data, b_data, ans, idx):
    for i in range(len(g_data)):
        g_data[i] = clean_link(g_data[i])
    for i, val in enumerate(b_data):
        b_data[i] = clean_link(val)

    ranks = []
    for d in g_data:
        if d in b_data:
            ranks.append((g_data.index(d) + 1, b_data.index(d) + 1))

    overlapping_no = len(ranks)
    percent = overlapping_no * 10
    coeff = spearman_coefficient(ranks)

    ans.append([f'Query {idx}', overlapping_no, percent, coeff])


def spearman_coefficient(ranks):
    n = len(ranks)
    if n == 0:
        return 0
    if n == 1:
        rank = ranks[0]
        if rank[0] == rank[1]:
            return 1
        return 0

    sum_di = 0
    for rank in ranks:
        sq_di = (rank[0] - rank[1]) ** 2
        sum_di += sq_di
    deno = n * (n ** 2 - 1)
    neu = 6 * sum_di

    return 1 - (neu / deno)


if __name__ == '__main__':
    google_data, bing_data, queries = read_files()
    ans = []
    idx = 1
    for q in queries:
        analyze(google_data[q], bing_data[q], ans, idx)
        idx += 1

    avg_overlap = sum([a[1] for a in ans]) / 100
    avg_percent = sum([a[2] for a in ans]) / 100
    avg_coeff = sum([a[3] for a in ans]) / 100

    ans.append(['Averages', avg_overlap, avg_percent, avg_coeff])
    ans.insert(0, ['Queries', 'Number of Overlapping Results', 'Percent Overlap', 'Spearman Coefficient'])

    with open('results_summary.csv', 'w+', newline='') as file:
        csv_writer = csv.writer(file)
        for a in ans:
            csv_writer.writerow(a)
