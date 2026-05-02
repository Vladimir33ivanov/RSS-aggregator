import csv

def save_to_csv(news, filename="news.csv"):
    if not news:
        return

    with open(filename, "w", newline = "", encoding = "utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link"])
        writer.writeheader()
        writer.writerows(news)