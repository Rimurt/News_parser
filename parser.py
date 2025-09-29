import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


url = "https://www.igromania.ru"
headers = {"User-Agent": UserAgent(os="Windows",platforms='desktop',browsers='chrome').chrome}

print(headers)

response = requests.get(url,headers=headers)
soup = BeautifulSoup(response.text, "lxml")

data = soup.find("div",class_= "app-main")

div_grid = data.find("div",class_="app-container")#type:ignore

big_news = div_grid.find_all("div", class_="style_card__mRsjZ knb-card knb-grid-cell cell--row-2 cell--col-2")#type:ignore

all_news = []
for i in big_news:
    news = []
    title = i.find("h3",class_="knb-card--title").text#type:ignore
    img = i.find("img",class_="knb-card--image").get("src")#type:ignore
    link = "https://www.igromania.ru" + i.find("a",class_="knb-card--image").get("href")#type:ignore
    news.append(title)
    news.append(img)
    news.append(link)
    all_news.append(news)

little_news = div_grid.find_all("div", class_="style_card__ZD6TK knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore

for i in little_news:
    news = []
    title = i.find("h3",class_="knb-card--title").text #type:ignore
    img = i.find("img",class_="knb-card--image").get("src")#type:ignore
    link = "https://www.igromania.ru" + i.find("a",class_="knb-card--image").get("href")#type:ignore
    news.append(title)
    news.append(img)
    news.append(link)
    all_news.append(news)

news_without_img = div_grid.find_all("div", class_="style_card__iYFwf knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore

for i in news_without_img:
    news = []
    title = i.find("h3",class_="knb-card--title").text#type:ignore
    link = "https://www.igromania.ru" + i.find("a",class_="style_body__UFvmv").get("href")#type:ignore
    news.append(title)
    news.append(link)
    all_news.append(news)

for i in all_news:
    print(f"Title {i[0]}")
    if len(i) == 2:
        print(f"Link {i[1]}")
        print("------------------------------")
    else:
        print(f"Img {i[1]}")
    if len(i) == 3:
        print(f"Link {i[2]}")
        print("------------------------------")