from bs4 import BeautifulSoup
import requests
from openpyxl import load_workbook

headers = {"Accept": "*/*",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}


class Category:
    def __init__(self, link, name):
        self.link = link
        self.name = name


def get_bs(url):
    req = requests.get(url, headers)
    src = req.text
    return BeautifulSoup(src, "lxml")


def get_restaurants_links(page):
    link_classes = page.find_all(class_="collection-item hover-effect full-width--mobile")
    links = []
    for link in link_classes:
        links.append(f"https://glovoapp.com{link.get('href')}")
    return links


def save_restaurant_info(link, work_sheet):
    import googlemaps_creator
    global i

    page = get_bs(link)
    name = page.find(class_="store-info__title").text.strip()
    city = page.find(class_="breadcrumb__item--linkable").text.strip()
    info = googlemaps_creator.data_place(name, city)
    work_sheet.append([i, name, link, info["location_address"], info["location_coordinates"], info["work_hours"]])
    return None


def get_categories(link):
    page = get_bs(link)
    categories = []
    categories_classes = page.find_all(class_="collection__child__button collection__child__button--selected")
    for category_class in categories_classes:
        if "hit-prodazhiv" not in category_class.get("href"):
            categories.append(Category(f"https://glovoapp.com{category_class.get('href')}", category_class.find(class_= "collection__child-label collection__child-label--selected").next.text.strip()))
    return categories


def save_restaurant_menu(link, work_sheet):
    global j
    global i
    restaurant_categories = get_categories(link)
    if restaurant_categories[0].name == "МЕНЮ":
        restaurant_categories = get_bs(restaurant_categories[0].link).find_all(class_="list", type="LIST")
        for category in restaurant_categories:
            dishes_classes = category.find_all(class_="product-row")
            for dish in dishes_classes:
                name = dish.find(class_="product-row__name").next.next.text.strip()
                price = dish.find(class_="product-price__effective product-price__effective--new-card").text.strip()
                try:
                    description = dish.find(class_="product-row__info__description").next.text.strip()
                except AttributeError:
                    description = ""
                work_sheet.append([j, i, name, description, price, category.find(class_="list__title").text.strip(), ""])
                j += 1
    else:
        for category in restaurant_categories:
            category_page = get_bs(category.link)
            dishes_classes = category_page.find_all(class_="product-row")
            for dish in dishes_classes:
                name = dish.find(class_="product-row__name").next.next.text.strip()
                price = dish.find(class_="product-price__effective product-price__effective--new-card").text.strip()
                try:
                    description = dish.find(class_="product-row__info__description").next.text.strip()
                except AttributeError:
                    description = ""
                work_sheet.append([j, i, name, description, price, category.name, ""])
                j += 1
    return None


wb = load_workbook("database_restaurant.xlsx")
ws = wb['food_establishments']
ws1 = wb['food_positions']

restaurant_links = []
for i in range(11):
    page = get_bs(f"https://glovoapp.com/ua/uk/lviv/restorani_1/?page={i+1}")
    restaurant_links.extend(get_restaurants_links(page))
    print(f"#{i+1} done")

i = 1
j = 1
for link in restaurant_links:
    try:
        save_restaurant_info(link, ws)
    except:
        print("Fail")
        continue
    try:
        save_restaurant_menu(link, ws1)
    except:
        print("Fail")
        i += 1
        continue
    print(f"Rest#{i} done!")
    i += 1

wb.save("database_restaurant.xlsx")
wb.close()