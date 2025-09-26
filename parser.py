import requests
from bs4 import BeautifulSoup

url = "https://www.igromania.ru"

response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

data = soup.find("div",class_= "app-main")

div_grid = data.find("div",class_="app-container")#type:ignore

big_news = div_grid.find_all("div", class_="style_card__mRsjZ knb-card knb-grid-cell cell--row-2 cell--col-2")#type:ignore

all_news = []
for i in big_news:
    news = []
    title = i.find("h3",class_="knb-card--title").text#type:ignore
    img = i.find("img",class_="knb-card--image").get("src")#type:ignore
    news.append(title)
    news.append(img)
    all_news.append(news)

little_news = div_grid.find_all("div", class_="style_card__ZD6TK knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore

for i in little_news:
    news = []
    title = i.find("h3",class_="knb-card--title").text #type:ignore
    img = i.find("img",class_="knb-card--image").get("src")#type:ignore
    news.append(title)
    news.append(img)
    all_news.append(news)

news_without_img = div_grid.find_all("div", class_="style_card__iYFwf knb-card knb-grid-cell withShadow cell--row-2 cell--col-1")#type:ignore

for i in news_without_img:
    news = []
    title = i.find("h3",class_="knb-card--title").text#type:ignore
    news.append(title)
    all_news.append(news)

print(all_news)