from datetime import datetime

def print_as_table(news):
    """"Печатает новости в виде таблицы"""
    if not news:
        print("Новостей не найдено")
        return

    print("\n" + "=" * 80)
    print(f"Rss news | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 80)

    for i, item in enumerate(news, start = 1):
        title = item['title'][:55] + "..." if len(item['title']) > 55 else item['title']
        print(f"{i:>2}. {title}")
        print(f"    🔗 {item['link']}")
        print("-" * 80)

    print(f"📊 Всего: {len(news)} новостей\n")
