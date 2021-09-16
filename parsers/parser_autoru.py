import requests
from bs4 import BeautifulSoup
import base64
import csv
import datetime
# from selenium import webdriver
import time

#CONSTANTS
URL = "https://auto.ru/cars/used/"
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15', 'accept': '*/*'}
FILE = str(datetime.datetime.now()).replace(' ', '_') + '_cars.csv'
SCROLL_PAUSE_TIME = 0.4

# browser = webdriver.Chrome('--path--')
# browser.get(URL)
def get_html(url, params=None):
    #w8 4 page loading
#     time.sleep(SCROLL_PAUSE_TIME)
    r = requests.get(url, headers=HEADERS, params=params)
    r.encoding='utf-8'
    return r

def get_numOfPages(html):
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('a', class_='Button Button_color_whiteHoverBlue Button_size_s Button_type_link Button_width_default ListingPagination__page')#.find_next('span', class_='Button__text').get_text()
    if(pages):
        last = int(pages[-1].find_next('span', class_='Button__text').get_text())
    else:
        last = 1
    return last
    
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    items = soup.find_all('div', class_='ListingItem')
    
    cars = []
    for item in items:
        techsum = item.find_all('div', class_='ListingItemTechSummaryDesktop__cell')[0].get_text().replace(u'\xa0', u'').replace('\u2009', '').split('/')
        
        rub_price = item.find('a', class_='ListingItemPrice__link')
        if(rub_price):
            rub_price = item.find('a', class_='ListingItemPrice__link').get_text().replace(u'\xa0', u' ')
        else:
            rub_price = item.find('div', class_='ListingItemPrice__content')
            if(rub_price):
                rub_price = item.find('div', class_='ListingItemPrice__content').get_text().replace(u'\xa0', u' ')
            else:
                rub_price = item.find('svg', class_='IconSvg IconSvg_price-down IconSvg_size_24')
                if(rub_price):
                    rub_price = item.find('svg', class_='IconSvg IconSvg_price-down IconSvg_size_24').find_next('span').get_text().replace(u'\xa0', u' ')
                else:
                    rub_price = None
                    
#         techsum[2]
#         0 - бензин
#         1 - дизель
#         2 - газ
#         3 - гибрид
#         4 - электро
        
        cars.append({
            'title': title_to_mark_to_num(item.find('a', class_='Link ListingItemTitle__link').get_text()),
            'link': item.find('a', class_='Link ListingItemTitle__link').get('href'),
            'rub_price': float(rub_price.replace('₽', '').replace(' ', '')) if (rub_price != None) else None,
            'year': float(item.find('div', class_='ListingItem__year').get_text()),
            'mileage': float(item.find('div', class_='ListingItem__kmAge').get_text().replace(u'\xa0', u'').replace('км', '')),
            'engine_capacity': float(techsum[0].replace(' л', '')) if (techsum[2] != 'Электро') else 0.0,
            'hp': float(techsum[1].replace('л.с.', '')) if (techsum[2] != 'Электро') else float(techsum[0].replace('л.с.', '')),
            'fuel_type': fuel_to_num(techsum[2]),
            'gearbox': gearbox_to_num(item.find_all('div', class_='ListingItemTechSummaryDesktop__cell')[1].get_text().replace(u'\xa0', u' ')),
            'carbody': carbody_to_num(item.find_all('div', class_='ListingItemTechSummaryDesktop__cell')[2].get_text().replace(u'\xa0', u' ')),
            'city': city_to_num(item.find('span', class_='MetroListPlace__regionName MetroListPlace_nbsp').get_text().replace(u'\xa0', u' ') if (item.find('span', class_='MetroListPlace__regionName MetroListPlace_nbsp')) else 136.0), #problem
            'ad_living_time': item.find('span', class_='MetroListPlace__content MetroListPlace_nbsp').get_text().replace(u'\xa0', u' ') if (item.find('span', class_='MetroListPlace__content MetroListPlace_nbsp')) else 'NODATA', #TODO: add script start-time to CSV
            #ListingItemTechSummaryDesktop__column 
            'transmission': transmission_to_num(item.find_all('div', class_='ListingItemTechSummaryDesktop__cell')[3].get_text()),
            'color': color_to_num(item.find_all('div', class_='ListingItemTechSummaryDesktop__cell')[4].get_text())
#             'image_url': "http:" + item.find('img', class_='LazyImage__image').get('src') if (item.find('img', class_='LazyImage__image')) else "NODATA"
        })
    return cars
#     print(cards)
#     for car in cars:
#         print(car, '\n')
#     print(len(cars)) # output: 38

def fuel_to_num(argument):
    switcher = {
        'Бензин': 0,
        'Дизель': 1,
        'Газ': 2,
        'Гибрид': 3,
        'Электро': 4
    }
    return float(switcher.get(argument, 5))
    
def color_to_num(argument):
    switcher = {
        'бежевый': 0,
        'чёрный': 1,
        'серебристый': 2,
        'красный': 3,
        'пурпурный': 4,
        'коричневый': 5,
        'зелёный': 6,
        'жёлтый': 7,
        'серый': 8,
        'синий': 9,
        'розовый': 10,
        'белый': 11,
        'оранжевый': 12,
        'голубой': 13,
        'фиолетовый': 14,
        'золотистый': 15
    }
    return float(switcher.get(argument, 16))
    
def transmission_to_num(arg):
    switcher = {
        'полный': 0,
        'передний': 1,
        'задний': 2
    }
    return float(switcher.get(arg, 3))

def city_to_num(arg):
    switcher = {
        'Таганрог': 1,
        'Пенза': 2,
        'Курск': 3,
        'Адлер': 4,
        'Санкт-Петербург': 5,
        'Йошкар-Ола': 6,
        'Кропоткин': 7,
        'Бахчисарай': 8,
        'Дубовое': 9,
        'Горячеводский': 10,
        'Тверь': 11,
        'Пойковский': 12,
        'Анапа': 13,
        'Химки': 14,
        'Саратов': 15,
        'Гулькевичи': 16,
        'Нижний Тагил': 17,
         'Ижевск': 18,
         'Новочеркасск': 19,
         'NODATA': 20,
         'Липецк': 21,
         'Альметьевск': 22,
         'Ярославль': 23,
         'Смоленск': 24,
         'Балаково': 25,
         'Магнитогорск': 26,
         'Новосибирск': 27,
         'Супонево': 28,
         'Омск': 29,
         'Чебоксары': 30,
         'Иноземцево': 31,
         'Бобров': 32,
         'Саранск': 33,
         'Псков': 34,
         'Аксай': 35,
         'Афонино': 36,
         'Нижнекамск': 37,
         'Республика Татарстан': 38,
         'Ховрино': 39,
         'Краснодар': 40,
         'Свободный': 41,
         'Волгодонск': 42,
         'Видное': 43,
         'Новочебоксарск': 44,
         'Владикавказ': 45,
         'Пригородный': 46,
         'Тучково': 47,
         'Волгоград': 48,
         'Минеральные Воды': 49,
         'Тахтамукай': 50,
         'Вологда': 51,
         'Московский': 52,
         'Мурманск': 53,
         'Севастополь': 54,
         'Владивосток': 55,
         'Буинск': 56,
         'Кудрово': 57,
         'Керчь': 58,
         'Сочи': 59,
         'Тюмень': 60,
         'Ульяновск': 61,
         'Волжский': 62,
         'Баймак': 63,
         'Новоуральск': 64,
         'Великий Новгород': 65,
         'Красное Село': 66,
         'Реутов': 67,
         'Феодосия': 68,
         'Шевырёвка': 69,
         'Набережные Челны': 70,
         'Архангельск': 71,
         'Самара': 72,
         'Ногинск': 73,
         'Шахты': 74,
         'Одинцово': 75,
         'Хабаровск': 76,
         'Заречье': 77,
         'Киров': 78,
         'Нижний Новгород': 79,
         'Дзержинск': 80,
         'Первое Мая': 81,
         'Берёзовский': 82,
         'Репное': 83,
         'Брянск': 84,
         'Энгельс': 85,
         'Майкоп': 86,
         'Владимир': 87,
         'Челябинск': 88,
         'Оренбург': 89,
         'Минск': 90,
         'Симферополь': 91,
         'Подольск': 92,
         'Темрюк': 93,
         'Старый Оскол': 94,
         'Ставрополь': 95,
         'Обнинск': 96,
         'Калуга': 97,
         'Домодедово': 98,
         'Кострома': 99,
         'Иваново': 100,
         'Балашиха': 101,
         'Быково': 102,
         'Тольятти': 103,
         'Москва': 104,
         'Уфа': 105,
         'Златоуст': 106,
         'Гаспра': 107,
         'Грушевская': 108,
         'Курган': 109,
         'Волосово': 110,
         'Ростов-на-Дону': 111,
         'Лобня': 112,
         'Рязань': 113,
         'Екатеринбург': 114,
         'Барнаул': 115,
         'Воронеж': 116,
         'Богданович': 117,
         'Иркутск': 118,
         'Тамбов': 119,
         'Мытищи': 120,
         'Пятигорск': 121,
         'Пермь': 122,
         'Белгород': 123,
         'Красноярск': 124,
         'Тула': 125,
         'Юца': 126,
         'Мирное': 127,
         'Раздоры': 128,
         'Новокузнецк': 129,
         'Коломна': 130,
         'Пушкино': 131,
         'Казань': 132,
         'Петрозаводск': 133,
        'Орёл': 134
        }
    return float(switcher.get(arg, 135))

def gearbox_to_num(arg):
    switcher = {
        'вариатор': 0,
        'автомат': 1,
        'робот': 2,
        'механика': 3
        }
    return float(switcher.get(arg, 4))

def title_to_mark_to_num(argu):
    arg = argu.split(sep=' ')[0]
    switcher = {
        'Smart': 0,
        'Daewoo': 1,
        'ТагАЗ': 2,
        'GMC': 3,
        'BAIC': 4,
        'Subaru': 5,
        'Honda': 6,
        'Porsche': 7,
        'Land': 8,
        'Mitsubishi': 9,
        'Hummer': 10,
        'Haval': 11,
        'Skoda': 12,
        'Mazda': 13,
        'Chrysler': 14,
        'Kia': 15,
        'Rolls-Royce': 16,
        'MINI': 17,
        'Renault': 18,
        'Jaguar': 19,
        'Opel': 20,
        'Genesis': 21,
        'Lifan': 22,
        'Bentley': 23,
        'ЗАЗ': 24,
        'Cadillac': 25,
        'Toyota': 26,
        'Mercedes-Benz': 27,
        'ГАЗ': 28,
        'Chery': 29,
        'SEAT': 30,
        'Peugeot': 31,
        'Dodge': 32,
        'Lexus': 33,
        'Geely': 34,
        'Ravon': 35,
        'BMW': 36,
        'Volvo': 37,
        'Great': 38,
        'Acura': 39,
        'Citroen': 40,
        'Vortex': 41,
        'DW': 42,
        'Tesla': 43,
        'DongFeng': 44,
        'SsangYong': 45,
        'Zotye': 46,
        'Datsun': 47,
        'LADA': 48,
        'Volkswagen': 49,
        'Chevrolet': 50,
        'Nissan': 51,
        'Suzuki': 52,
        'Hawtai': 53,
        'Audi': 54,
        'Hyundai': 55,
        'Jeep': 56,
        'УАЗ': 57,
        'Infiniti': 58,
        'Fiat': 59,
        'Changan': 60,
        'Ford': 61
        }
    return float(switcher.get(arg, 62))

def carbody_to_num(arg):
    switcher = {
        'хэтчбек 5 дв.': 1,
         'купе': 2,
         'внедорожник 5 дв.': 3,
         'компактвэн': 4,
         'родстер': 5,
         'пикап двойная кабина': 6,
         'лифтбек': 7,
         'пикап полуторная кабина': 8,
         'фургон': 9,
         'внедорожник 3 дв.': 10,
         'хэтчбек 3 дв.': 11,
         'внедорожник открытый': 12,
         'купе-хардтоп': 13,
         'кабриолет': 14,
         'седан': 15,
         'универсал 5 дв.': 16,
         'минивэн': 17
    }
    return float(switcher.get(arg, 18))
                   
def save_fileCSV(items, path):
    with open(path, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['title', 'link', 'rub_price', 'year', 'mileage', 'engine_capacity', 'hp', 'fuel_type', 'gearbox', 'carbody', 'city', 'ad_living_time', 'transmission', 'color'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['rub_price'], item['year'], item['mileage'], item['engine_capacity'], item['hp'], item['fuel_type'], item['gearbox'], item['carbody'], item['city'], item['ad_living_time'], item['transmission'], item['color']])
        print('csv file was created')
    
def parse():
    html = get_html(URL)
    if(html.status_code == 200):
        cars = []
        num = get_numOfPages(html.text)
        for page in range(1, num + 1): #num + 1
            print(f'parsing page {page} of {num}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
#         print(len(cars))
        #4 test:
#         print(cars) 
#         for car in cars:
#             print(car, '\n')
        save_fileCSV(cars, FILE)
    #TODO: CSV creation + add script start-time to CSV
    else:
        print('Something goes wrong -_-')

parse()