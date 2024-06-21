import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer


def get_new_articles(most_recent_article) -> BeautifulSoup:
    web_address = "https://www.lebensmittelwarnung.de/SiteGlobals/Forms/Suche/Expertensuche/Expertensuche_Formular.html?templateQueryString=&lastChangeAfter=&lastChangeBefore=&resultsPerPage=100&resultsPerPage.GROUP=1"
    requests_website = requests.get(web_address)
    main_page = BeautifulSoup(requests_website.text, "html.parser")
    article_list = []
    most_recent_article_refreshed = False
    helper_most_recent_article = ""
    for link in main_page.find_all("a"):
        href = link.get("href")
        if href and "Meldungen" in href:
            if href == most_recent_article:
                break
            if not most_recent_article_refreshed:
                helper_most_recent_article = href
                most_recent_article_refreshed = True
            article_list.append(href)
    if helper_most_recent_article != "":
        most_recent_article = helper_most_recent_article
    for article in article_list:
        get_article_content("https://www.lebensmittelwarnung.de/" + article)
    return most_recent_article


def get_product_type(article_content):
    if article_content.find("span", class_="lmw-producttype__label"):
        return article_content.find(
            "span", class_="lmw-producttype__label"
        ).text.strip()
    return None


def get_product_name(article_content):
    if article_content.find("dd", class_="lmw-description-list__description"):
        return article_content.find(
            "dd", class_="lmw-description-list__description"
        ).text.strip()
    return None


def get_manufacturer(article_content):
    if article_content.find(
        "dt",
        class_="lmw-description-list__term",
        string="Hersteller / Inverkehrbringer:",
    ):
        manufacturer_unfiltered = (
            article_content.find(
                "dt",
                class_="lmw-description-list__term",
                string="Hersteller / Inverkehrbringer:",
            )
            .find_next()
            .text.strip()
        )
        prefilter_pattern = re.compile(r"^Inverkehrbringer", re.IGNORECASE)
        if prefilter_pattern.search(manufacturer_unfiltered):
            return None
        filter_pattern = re.compile(
            r"^(?:Firma|Hersteller):?\s*(.*?)(,|\n|$)", re.IGNORECASE
        )
        match = filter_pattern.search(manufacturer_unfiltered)
        if match:
            return match.group(1).strip()
        return re.split(r",|\n", manufacturer_unfiltered)[0].strip()
    return None


def get_category(article_content):
    if article_content.find(
        "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
    ):
        return article_content.find(
            "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
        ).text.strip()
    return None


def get_bundeslaender(article_content):
    if article_content.find_all("li", class_="lmw-list__item"):
        bundeslaender = []
        bulae = article_content.find_all("li", class_="lmw-list__item")
        for bula in bulae:
            bundeslaender.append(bula.text.strip())
        bundeslaender = list(set(bundeslaender))
        return ", ".join(bundeslaender)
    return None


def get_description(article_content):
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Weitere Informationen:"
    ):
        return (
            article_content.find(
                "dt",
                class_="lmw-description-list__term",
                string="Weitere Informationen:",
            )
            .find_next()
            .text.strip()
        )
    return None


def get_consequence(article_content):
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Mögliche Folgen:"
    ):
        return (
            article_content.find(
                "dt", class_="lmw-description-list__term", string="Mögliche Folgen:"
            )
            .find_next()
            .text.strip()
        )
    return None


def get_reseller(article_content):
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Vertrieb über:"
    ):
        reseller_unfiltered = (
            article_content.find(
                "dt", class_="lmw-description-list__term", string="Vertrieb über:"
            )
            .find_next()
            .text.strip()
        )
        filter_pattern = r"\b(?:REWE|Aldi|Lidl|Edeka|Netto|Penny|Kaufland|dm|Rossmann|Müller|Real|Globus)\b"
        reseller = re.findall(filter_pattern, reseller_unfiltered, re.IGNORECASE)
        reseller_without_dulicates = list(set(reseller))
        if len(reseller_without_dulicates) > 0:
            return ", ".join(reseller_without_dulicates)
        return "Sonstige"
    return None


def get_date(article_content):
    if article_content.find("time", class_="lmw-datetime lmw-card__datetime"):
        date_unformatted = article_content.find(
            "time", class_="lmw-datetime lmw-card__datetime"
        ).text.strip()
        date_formatted = (
            date_unformatted[6:]
            + "-"
            + date_unformatted[3:5]
            + "-"
            + date_unformatted[0:2]
        )
        return date_formatted
    return None


def get_article_content(article):
    requests_article = requests.get(article)
    article_content = BeautifulSoup(requests_article.text, "html.parser")
    product_type = get_product_type(article_content)
    product_name = get_product_name(article_content)
    manufacturer = get_manufacturer(article_content)
    category = get_category(article_content)
    bundeslaender = get_bundeslaender(article_content)
    description = get_description(article_content)
    consequence = get_consequence(article_content)
    reseller = get_reseller(article_content)
    date = get_date(article_content)
    send_article(
        product_type,
        product_name,
        manufacturer,
        category,
        bundeslaender,
        description,
        consequence,
        reseller,
        date,
        article,
    )


def send_article(
    product_type,
    product_name,
    manufacturer,
    category,
    bundeslaender,
    description,
    consequence,
    reseller,
    date,
    article,
):

    data = {
        "Produkttyp": product_type,
        "Produktname": product_name,
        "Hersteller": manufacturer,
        "Kategorie": category,
        "Bundeslaender": bundeslaender,
        "Beschreibung": description,
        "Folgen": consequence,
        "Vertrieb": reseller,
        "Datum": date,
        "URL": article,
    }
    print(data)
    message = str(data)
    conf = {"bootstrap.servers": "localhost:9092"}
    producer = Producer(conf)
    producer.produce("lebensmittelwarnungen", message)
    producer.flush()


def main() -> None:
    most_recent_article_file = "most_recent_article.txt"
    if not Path(most_recent_article_file).is_file():
        with open(most_recent_article_file, "w") as file:
            file.write("")
    while True:
        with open(most_recent_article_file, "r") as file:
            most_recent_article = str(file.read()).strip()
        new_most_recent_article = get_new_articles(most_recent_article)
        with open(most_recent_article_file, "w") as file:
            file.write(str(new_most_recent_article))

        time.sleep(3600)


if __name__ == "__main__":
    main()
