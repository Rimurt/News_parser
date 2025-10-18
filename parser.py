import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import re

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
    big_news = container.find_all("div", class_="style_card__mRsjZ knb-card knb-grid-cell cell--row-2 cell--col-2")#type:ignore
    little_news = container.find_all("div", class_="style_card__ZD6TK knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore
    news_without_img = container.find_all("div", class_="style_card__iYFwf knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore
    all_links = []

    for a in big_news:
        link = "https://www.igromania.ru" + a.find("a",class_="knb-card--image style_wrap___iepK style_isAbsolute__P_sj_").get("href")#type:ignore
        all_links.append(link) #type:ignore
    
    for a in little_news:
        link = "https://www.igromania.ru" + a.find("a").get("href")#type:ignore
        all_links.append(link) #type:ignore
    
    for a in news_without_img:
        link = "https://www.igromania.ru" + a.find("a").get("href")#type:ignore
        all_links.append(link) #type:ignore

    all_links = list(set(all_links))
    print(f"✅ Найдено ссылок: {len(all_links)}")
    if len(all_links) == 0:
        get_links()
    else:
        return all_links

def extract_id(url: str) -> str | None:
    """
    Извлекает числовой ID из ссылок Игромании:
    /news/<id>/..., /review/<id>/..., /article/<id>/...
    """
    match = re.search(r"/(?:news|review|article)/(\d+)/", url)
    return match.group(1) if match else None

def get_title(news_url):
    """Получаем заголовок новости."""
    response = safe_get(news_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "lxml")
    news = {
        "id": "",
        "title": "",
        "content": ""
    }
    
    news["id"] = str(extract_id(news_url))
    h1 = soup.find("h1")
    if h1:
        news["title"] = h1.text
    content_grid = soup.find("div",class_="d-grid template-columns-5 gap-20 w-100")
    content_text = content_grid.find_all("p") #type:ignore
    # Объединяем параграфы
    raw_text = "\n\n".join(p.get_text(" ", strip=True) for p in content_text)

    clean_text = re.sub(r"Источник:.*?(?=\n|$)", "", raw_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    news["content"] = clean_text
    return news 


# Основная логика
if __name__ == "__main__":
    print("📡 Получаем ссылки с главной страницы...")
    news_links = get_links()

    if not news_links:
        print("❌ Не удалось получить ссылки. Возможно, сайт изменил структуру.")
        exit()

    news_list = []
    
    for link in news_links:  # ограничим 10 новостями
        print(f"\n📰 Парсим: {link}")
        time.sleep(random.uniform(4, 8))  # пауза между запросами
        content = get_title(link)
        if content:
            news_list.append(content)
            print(f"→ {content}")
        else:
            print("⚠️ Не удалось извлечь заголовок")

    print("\n=== Итоговые заголовки ===")
    for t in news_list:
        print("•", t)
