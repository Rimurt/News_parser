import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from db import session, News
import time
import random
import re


# Инициализируем генератор User-Agent для создания случайных заголовков
ua = UserAgent()

# Создаём экземпляр cloudscraper, который является оберткой над requests
# и умеет автоматически обходить защиту от ботов Cloudflare.
scraper = cloudscraper.create_scraper()

BASE_URL = "https://www.igromania.ru"



def get_headers():
    """Генерирует HTTP-заголовки, имитирующие реальный браузер,
    чтобы снизить вероятность блокировки со стороны сайта."""
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
            # Проверяем, не вернул ли сервер код ошибки (4xx или 5xx)
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

    # На главной странице есть несколько видов карточек новостей с разными классами. Собираем все.
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

    # Преобразуем список в множество и обратно, чтобы удалить дубликаты ссылок.
    all_links = list(set(all_links))
    print(f"✅ Найдено ссылок: {len(all_links)}")
    # Рекурсивный вызов на случай, если первая попытка не дала результатов.
    # Может быть полезно при нестабильном соединении или временных проблемах сайта.
    if len(all_links) == 0:
        return get_links()
    else:
        return all_links

def extract_id(url: str) -> str | None:
    """
    Извлекает числовой ID из ссылок Игромании:
    /news/<id>/..., /review/<id>/..., /article/<id>/...
    """
    match = re.search(r"/(?:news|review|article)/(\d+)/", url)
    return match.group(1) if match else None

def get_news_content(news_url):

    # Проверяем, существует ли новость с таким ID в базе данных, чтобы избежать дублирования.
    if session.get(News,extract_id(news_url)):
        print("Новость уже есть в базе данных")
        return
    
    """Получаем заголовок новости."""
    response = safe_get(news_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "lxml")
    news = {
        "id": "",
        "title": "",
        "content": "",
        "image": "",
    }
    
    news["id"] = str(extract_id(news_url))
    h1 = soup.find("h1")
    if h1:
        news["title"] = h1.text
    content_grid = soup.find("div",class_="d-grid template-columns-5 gap-20 w-100")
    content_text = content_grid.find_all("p") #type:ignore
    # Объединяем параграфы
    # .get_text(" ", strip=True) извлекает текст из тегов <p>, заменяя <br> и другие теги на пробел.
    raw_text = "\n\n".join(p.get_text(" ", strip=True) for p in content_text)

    # Очищаем текст от мусорных строк, например, от упоминания источника.
    clean_text = re.sub(r"Источник:.*?(?=\n|$)", "", raw_text)
    # Заменяем множественные пробелы на один для чистоты.
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    news["content"] = clean_text

    image = soup.find("img",class_="MaterialCommonImage_picture__Z_3EU")
    if image:
        news["image"] = image.get("src")#type:ignore
    else:
        news["image"] = ""
    
    data = News(
        id=news["id"],
        title=news["title"],
        content=news["content"],
        image=news["image"],
    )
    # Добавляем новый объект News в сессию и сохраняем изменения в БД.
    session.add(data)
    session.commit()
    print(f"✅ Добавлена новость в базу данных c id: {news['id']}")


# Основная логика
def parsing():
    print("📡 Получаем ссылки с главной страницы...")
    news_links = get_links()

    if not news_links:
        return "error"

    for link in news_links:
        print(f"\n📰 Парсим: {link}")
        time.sleep(random.uniform(4, 8))  # пауза между запросами
        get_news_content(link)
    return "ok"
    
