import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

ua = UserAgent()

# Создаём cloudscraper (автоматически обходит Cloudflare)
scraper = cloudscraper.create_scraper()

BASE_URL = "https://www.igromania.ru"


def get_headers():
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def safe_get(url, retries=5, delay=5):
    """Безопасный GET-запрос с повторными попытками."""
    for attempt in range(1, retries + 1):
        try:
            response = scraper.get(url, headers=get_headers(), timeout=20)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"[{attempt}/{retries}] Ошибка запроса: {e}")
            if attempt < retries:
                sleep_time = delay + random.uniform(1, 4)
                print(f"Повтор через {sleep_time:.1f} сек...")
                time.sleep(sleep_time)
            else:
                print("❌ Превышено число попыток. Пропуск.")
                return None


def get_links():
    """Получаем список ссылок на новости с главной страницы."""
    response = safe_get(BASE_URL)
    if not response:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    main_div = soup.find("div", class_="app-main")
    if not main_div:
        print("⚠️ Не найден главный контейнер новостей.")
        return []

    container = main_div.find("div", class_="app-container")#type:ignore
    if not container:
        print("⚠️ Не найден контейнер с новостями.")
        return []

    # Ищем все карточки новостей
    news_blocks = container.find_all("a", href=True)#type:ignore
    all_links = []

    for a in news_blocks:
        href = a.get("href")#type:ignore
        if href and href.startswith("/news/"):#type:ignore
            all_links.append(BASE_URL + href) #type:ignore

    all_links = list(set(all_links))
    print(f"✅ Найдено ссылок: {len(all_links)}")
    return all_links


def get_title(news_url):
    """Получаем заголовок новости."""
    response = safe_get(news_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "lxml")
    h1 = soup.find("h1")
    if h1:
        return h1.text.strip()
    return None


# Основная логика
if __name__ == "__main__":
    print("📡 Получаем ссылки с главной страницы...")
    news_links = get_links()

    if not news_links:
        print("❌ Не удалось получить ссылки. Возможно, сайт изменил структуру.")
        exit()

    titles = []
    for link in news_links[:10]:  # ограничим 10 новостями
        print(f"\n📰 Парсим: {link}")
        time.sleep(random.uniform(4, 8))  # пауза между запросами
        title = get_title(link)
        if title:
            titles.append(title)
            print(f"→ {title}")
        else:
            print("⚠️ Не удалось извлечь заголовок")

    print("\n=== Итоговые заголовки ===")
    for t in titles:
        print("•", t)
