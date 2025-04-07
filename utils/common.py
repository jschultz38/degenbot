import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def translateMonth(month_text):
    month_ret = None
    match month_text:
        case 'January' | 'Jan':
            month_ret = 1
        case 'February' | 'Feb':
            month_ret = 2
        case 'March' | 'Mar':
            month_ret = 3
        case 'April' | 'Apr':
            month_ret = 4
        case 'May':
            month_ret = 5
        case 'June' | 'Jun':
            month_ret = 6
        case 'July' | 'Jul':
            month_ret = 7
        case 'August' | 'Aug':
            month_ret = 8
        case 'September' | 'Sep':
            month_ret = 9
        case 'October' | 'Oct':
            month_ret = 10
        case 'November' | 'Nov':
            month_ret = 11
        case 'December' | 'Dec':
            month_ret = 12
        case _:
            print("ERROR: Could not decode: " + month_text)
            month_ret = 1

    return month_ret


def findAllKHLSeasons():
    seasons = []
    URL = 'https://krakenhockeyleague.com/suspensions'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.css.select('a[href*="/suspensions/?season="]')
    for result in results:
        season = result['href'].split("=")[-1]
        if season not in seasons:
            seasons.append(season)

    return seasons

def realToMilitaryTime(time_int, meridiem):
    if time_int == 12 and meridiem == "AM":
        return 0;

    if time_int == 12 and meridiem == "PM":
        return 12;

    return time_int if meridiem == "AM" else time_int + 12

def selenium_retrieve_website_data(url):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        driver.implicitly_wait(2)
        page_content = driver.page_source
        driver.quit()
        return page_content
    except Exception as e:
        print (f"Error getting site data using selenium: {e}")
        return