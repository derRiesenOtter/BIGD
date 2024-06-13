import datetime
import re
import time

import pykafka
import requests
import schedule
from bs4 import BeautifulSoup


def get_html_content() -> BeautifulSoup:
    """
    This function requests the html content of our website and returns
    it as a BeautifulSoup object.
    """
    web_address = (
        "https://www.lebensmittelwarnung.de/bvl-lmw-de/liste/alle/deutschlandweit/10/0"
    )
    requests_website = requests.get(web_address)
    return BeautifulSoup(requests_website.text, "html.parser")


def get_recent_content(html_content: BeautifulSoup) -> list[list[str]]:
    """
    This function takes the BeautifulSoup Object created by
    get_html_content and searches for all required information.
    It returns a list of lists containing the information of each
    warning.
    """
    types = html_content.find_all("span", id=re.compile(r"e4pn"))
    dates = html_content.find_all("span", id=re.compile(r"ecqn"))
    products = html_content.find_all("span", id=re.compile(r"egqn"))
    company = html_content.find_all("span", id=re.compile(r"ejqn"))
    cause = html_content.find_all("span", id=re.compile(r"eyqn"))
    fed_states = html_content.find_all("div", id=re.compile(r"e3qn"))

    regex_microorganism = re.compile("(.Listeri.*)|(Salmonell.*)|(Patulin.*)|(.*(T|t)oxin.*)|(Pseudomon.*)|(Schimmel.*)|(Escherichia.*)|((M|m)ikro.*)|(Ba(c|z)ill.*)|(Hefe.*)")
    regex_allergen = re.compile("(.*(A|a)llerg.*)|(.*nuss)|(Senf.*)|(Milch.*)")
    regex_foreign_body = re.compile("(.*(F|f)remd.*)|(Glas.*)|(Metall.*)|(Kunststoff.*)|(Stein.*)")
    regex_limit = re.compile("(.*(W|w)ert.*)|(.*(G|g)ehalt.*)|((R|r)ückst.*)|(.*(M|m)enge.*)|(Arznei.*)|(Nachweis.*)|((G|g)esund.*)|((G|g)esetz.*)|(krebs.*)|(Befund.*)|((G|g)ef(a|ä)hr.*)|(zugelassen.*)")
    
    cause_category = []
    for i in cause:
        if bool(regex_microorganism.search(i.text)):
            cause_category.append('Mikroorganismen und Toxine')
        elif bool(regex_allergen.search(i.text)):
            cause_category.append('Allergene')
        elif bool(regex_foreign_body.search(i.text)):
            cause_category.append('Fremdkörper/-stoffe')
        elif bool(regex_limit.search(i.text)):
            cause_category.append('Grenzwertüberschreitung und Gesundheitsgefährdung')
        else:
            cause_category.append('Sonstiges')

    recent_content = []
    for i in range(10):
        recent_content.append(
            [
                types[i].text,
                dates[i].text,
                products[i].text.replace("\n"," ").replace("\r"," ").replace("  ", " "),
                company[i].text.replace("Hersteller:\n", "").split("\n")[0].replace("Hersteller:", "").split(",")[0].strip(),
                cause[i].text.replace("\n"," ").replace("\r"," ").replace("  ", " "),
                cause_category[i],
                fed_states[i].text.replace("\nbetroffene Länder (alphabetisch):\n\n", "")
            ]
        )
    return recent_content


def check_for_new_entries(recent_content: list[list[str]]) -> int:
    """
    This function takes the recent_content list and checks if there there are
    new entries created on the day before.
    It returns the number of new entries.
    """
    yesterday = datetime.date.today() - datetime.timedelta(1)
    n_new_entries = 0
    for i in range(10):
        if recent_content[i][1] == yesterday.strftime("%d.%m.%Y"):
            n_new_entries += 1
    return n_new_entries


# This function will send the new values to our Stream
def send_new_values(n_new_entries: int, recent_content: list[list[str]]) -> None:
    if n_new_entries == 0:
        return
    # json formatted data
    i = 0
    data = f"{'type': {recent_content[i][0]},'date': {recent_content[i][1]},'product': {recent_content[i][2]},'company': {recent_content[i][3]},'cause': {recent_content[i][4]},'fed_state': {recent_content[i][5]}}"


# This function will hold all tasks this script has to do every day
def daily_task() -> None:
    pass


def main() -> None:
    html_content = get_html_content()
    recent_content = get_recent_content(html_content)
    n_new_entries = check_for_new_entries(recent_content)
    send_new_values(n_new_entries, recent_content)

    # This scheduler will take care of running the script daily
    # schedule.every().day.at("01:00").do(daily_task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)


if __name__ == "__main__":
    main()
