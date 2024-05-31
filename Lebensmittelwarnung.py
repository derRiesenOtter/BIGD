import re
import requests 
from bs4 import BeautifulSoup 
import time
import schedule
import date

def get_html_content():
    web_address = "https://www.lebensmittelwarnung.de/bvl-lmw-de/liste/alle/deutschlandweit/10/0"
    request_website = requests.get(web_address)
    return BeautifulSoup(request_website.text, "html.parser")

def get_recent_content(html_content):
    types = html_content.find_all("span", id=re.compile(r"e4pn"))
    dates = html_content.find_all("span", id=re.compile(r"ecqn"))
    products = html_content.find_all("span", id=re.compile(r"egqn"))
    company = html_content.find_all("span", id=re.compile(r"ejqn"))
    cause = html_content.find_all("span", id=re.compile(r"eyqn"))
    fed_states = html_content.find_all("div", id=re.compile(r"e3qn"))
    recent_content = []
    for i in range (10): 
        recent_content.append([types[i].text, dates[i].text, products[i].text, company[i].text, cause[i].text, fed_states[i].text])
    return recent_content

# This function is supposed to take recent_content as input and check if there are new entries from the last day
# It will return the number of new values
def check_for_new_entries():
    pass

# This function will send the new values to our Stream
def send_new_values():
    pass

# This function will hold all tasks this script has to do every day
def daily_task():
    pass

def main():
    html_content = get_html_content()
    recent_content = get_recent_content(html_content)
    print(recent_content)
    # This scheduler will take care of running the script daily
    # schedule.every().day.at("01:00").do(daily_task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)

if __name__ == "__main__":
    main()
