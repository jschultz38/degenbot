import json

from selenium import webdriver

with open("../res/teams.json") as teams_file:
    json_data = json.load(teams_file)

teams = json_data["teams"]

for team in teams:
    if team['league'] == "SPC":
        URL = 'https://my.seattlepridehockey.org/leagues/' + team['div'] + '/teams/' + team['id']
        print(URL)

        # use selenium driver because this site happens to be dynamically generated
        options = webdriver.FirefoxOptions()
        # headless is necessary otherwise it will pop up in a browser window
        options.add_argument('--headless')
        # bunch of flags to lighten the load i borrowed from here:
        # https://stackoverflow.com/questions/55072731/selenium-using-too-much-ram-with-firefox
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Firefox(options=options)

        page_html = None
        # try/finally block to make sure the driver always gets closed even after exception or interrupt
        try:
            # todo: we could optimize this by creating one global driver and reusing the same one for each team
            driver.get(URL)
            page_html = driver.page_source
        finally:
            # important: always quit the driver when you're done or else the invisible firefox window will persist
            driver.quit()

        team['cache'] = page_html

        file_name = "saveHTMLSPC" + team['name'].replace(' ', '').replace('\'', '') + ".txt"
        with open(file_name, "w") as f:
            f.write(page_html)
        print('done')
