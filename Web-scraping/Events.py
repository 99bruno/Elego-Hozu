from bs4 import BeautifulSoup
import requests
from openpyexcel import load_workbook
headers = {"Accept": "*/*",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}


def get_bs(url):
    req = requests.get(url, headers)
    src = req.text
    return BeautifulSoup(src, "lxml")


def get_places(link):
    page = get_bs(link)
    places_classes = page.find_all(class_="loc_item")
    places = []
    for place_class in places_classes:
        places.append(f"https://lviv.kontramarka.ua{place_class.get('href')}")
    return places


def get_events_links(link):
    global events
    page = get_bs(link)
    events_link_classes = page.find_all(class_="block-info__title")
    events_links = []
    for events_link_class in events_link_classes:
        if events_link_class.get("href") not in events:
            events_links.append(events_link_class.get("href"))
    return events_links


def save_info(link, wb):
    global i
    page = get_bs(link)
    name = page.find("h1", class_="event-card__title").text.strip()
    price_range = page.find(class_="event-price").text.replace("грн", "").strip()
    place = page.find(class_="event-card__place").text.strip()
    address = page.find(class_="event-card__address").text.strip()
    try:
        duration = page.find(class_="afisha-info__title").find("div").text.strip()
        duration = duration[duration.find("— ") + 1:duration.find("хв")].strip()
    except AttributeError:
        duration = "Не вказано"
    try:
        description_1 = page.find(class_='content_cut').find("p").text.strip()
    except AttributeError:
        description_1 = "Не вказано"
    event_dates = page.find_all(class_="spoiler__head2")
    try:
        hashtags_a = page.find(class_= "event-card__tags").find_all("a")
        hashtags = ""
        for hashtag in hashtags_a:
            hashtags += hashtag.text + " "
    except AttributeError:
        hashtags = "Не вказано"
    for event_date in event_dates:
        try:
            date = event_date.find("span").find("a").text.strip()
        except AttributeError:
            date = event_date.find("span").text.strip()
        body = event_date.find_next_sibling()
        start_time = body.find(class_='time-link').text.strip()
        tickets_link = body.find(class_="btn").get("href")
        if tickets_link is None:
            tickets_link = "Розпродано"
        ws = wb["Events"]
        ws.append([i, name, date, start_time, duration, price_range, place, address, tickets_link, description_1, hashtags])
        i += 1
    return None


wb = load_workbook("Events_database.xlsx")
ws = wb['Events']
ws.append(["ID", "Name", "Date", "Start time", "Duration", "Price range ₴", "Place", "Address", "Tickets link", "Description 1", "Hashtags"])


places = get_places("https://lviv.kontramarka.ua/uk/concert/kinodvorec-im-a-dovzenka-503.html")
events = []
j = 1
for place in places:
    events.extend(get_events_links(place))
    print(f"#{j} is done!")
    j += 1

i = 1
for event in events:
    try:
        save_info(event, wb)
    except Exception as e:
        print(e)
        print(event)
    print(f"#{i} is done!")


wb.save("Events_database.xlsx")
wb.close()

