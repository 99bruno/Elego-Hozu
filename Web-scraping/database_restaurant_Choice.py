from openpyxl import load_workbook
from bs4 import BeautifulSoup
import requests

urls = ["https://demandjaro.choiceqr.com/menu/section:menyu/to-start",
        "https://salalat.choiceqr.com", "https://chicken.cukor.lviv.ua/section:food"]

wb = load_workbook("database_restaurant.xlsx")
ws = wb['food_establishments']
ws1 = wb['food_positions']
for row in ws.values:
    index_rest = row[0]

for row in ws1.values:
    index_food = row[0]


def save_rest_info(url):
    global index_rest

    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    info_ = []
    for data_ in soup.find(class_="styles_mainInfo__Ivw42").find_all(class_="styles_value__plyFY"):
        info_.append("".join(data_.text.split()))
    name = soup.find("div", class_="styles_placeName___Lwcq").text
    ws.append([index_rest, name, url, info_[1], "", info_[0]])


def save_menu_info(url):
    global index_food
    global index_rest
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    tabs = soup.find_all("div",
                         class_="category-observer-js styles_menu-category__R1fOI styles_menuCategoryDesktop__R8Evo")
    for tab in tabs:
        positions = tab.find_all("div", class_="styles_menu-item__K3Y0r styles_menu-item-desktop__3gkQ1")
        for position in positions:
            name = position.find("div", class_="styles_menu-item-title__92eAl").text
            description = position.find("div", class_="styles_menu-item-description__jSMJ6")
            if description is not None:
                description = position.find("div", class_="styles_menu-item-description__jSMJ6").text
            price = position.find("div", class_="styles_menu-item-price__H0JSQ").text
            category = tab.find("div", class_="styles_menu-category-title__GU2xx").text
            ws1.append([index_food, index_rest, name, description, price, category])
            index_food += 1


for link in urls:
    save_rest_info(link)
    save_menu_info(link)
    index_rest += 1

wb.save("database_restaurant.xlsx")