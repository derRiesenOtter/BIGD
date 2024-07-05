import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer


def get_new_articles(most_recent_article):
    """
    Fetches new articles from the website and updates the most recent article reference.

    Args:
        most_recent_article (str): URL of the most recent article processed.

    Returns:
        str: URL of the new most recent article.
    """
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
    """
    Extracts the product type from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Product type if found, otherwise 'NA'.
    """
    if article_content.find("span", class_="lmw-producttype__label"):
        return article_content.find(
            "span", class_="lmw-producttype__label"
        ).text.strip()
    return "NA"


def get_product_name(article_content):
    """
    Extracts the product name from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Product name if found, otherwise 'NA'.
    """
    if article_content.find("dd", class_="lmw-description-list__description"):
        return (
            article_content.find("dd", class_="lmw-description-list__description")
            .text.strip()
            .replace('"', "")
            .replace("'", "")
        )
    return "NA"


def get_manufacturer(article_content):
    """
    Extracts the manufacturer from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Manufacturer if found, otherwise 'NA'.
    """
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
            .replace('"', "")
            .replace("'", "")
        )
        prefilter_pattern = re.compile(r"^Inverkehrbringer", re.IGNORECASE)
        if prefilter_pattern.search(manufacturer_unfiltered):
            return "NA"
        filter_pattern = re.compile(
            r"^(?:Firma|Hersteller):?\s*(.*?)(,|\n|$)", re.IGNORECASE
        )
        match = filter_pattern.search(manufacturer_unfiltered)
        if match:
            return match.group(1).strip()
        return re.split(r",|\n", manufacturer_unfiltered)[0].strip()
    return "NA"


def get_category(article_content):
    """
    Extracts the category from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Category if found, otherwise 'NA'.
    """
    if article_content.find(
        "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
    ):
        return article_content.find(
            "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
        ).text.strip()
    return "NA"


def get_bundeslaender(article_content):
    """
    Extracts the Bundesländer (states) from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        list: List of Bundesländer if found, otherwise 'NA'.
    """
    if article_content.find_all("li", class_="lmw-list__item"):
        bundeslaender = []
        bulae = article_content.find_all("li", class_="lmw-list__item")
        for bula in bulae:
            bundeslaender.append(bula.text.strip())
        bundeslaender = list(set(bundeslaender))
        return bundeslaender
    return "NA"


def get_description(article_content):
    """
    Extracts the description from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Description if found, otherwise 'NA'.
    """
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
            .replace('"', "")
            .replace("'", "")
        )
    return "NA"


def get_consequence(article_content):
    """
    Extracts the possible consequences from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Consequences if found, otherwise 'NA'.
    """
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Mögliche Folgen:"
    ):
        return (
            article_content.find(
                "dt", class_="lmw-description-list__term", string="Mögliche Folgen:"
            )
            .find_next()
            .text.strip()
            .replace('"', "")
            .replace("'", "")
        )
    return "NA"


def get_reseller(article_content):
    """
    Extracts the resellers from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        list: List of resellers if found, otherwise 'Sonstige' or 'NA'.
    """
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Vertrieb über:"
    ):
        reseller_unfiltered = (
            article_content.find(
                "dt", class_="lmw-description-list__term", string="Vertrieb über:"
            )
            .find_next()
            .text.strip()
            .replace('"', "")
            .replace("'", "")
        )
        filter_pattern = r"\b(?:REWE|Aldi|Lidl|Edeka|Netto|Penny|Kaufland|dm|Rossmann|Müller|Real|Globus)\b"
        reseller = re.findall(filter_pattern, reseller_unfiltered, re.IGNORECASE)
        reseller_without_dulicates = list(set(reseller))
        if len(reseller_without_dulicates) > 0:
            return reseller_without_dulicates
        return "Sonstige"
    return "NA"


def get_date(article_content):
    """
    Extracts the date from the article content.

    Args:
        article_content (BeautifulSoup): Parsed HTML content of the article.

    Returns:
        str: Date in YYYY-MM-DD format if found, otherwise 'NA'.
    """
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
    return "NA"


def get_article_content(article):
    """
    Processes an article to extract various details and send them for further processing.

    Args:
        article (str): URL of the article to be processed.
    """
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
    """
    Sends the article details to a Kafka topic.

    Args:
        product_type (str): Type of the product.
        product_name (str): Name of the product.
        manufacturer (str): Manufacturer of the product.
        category (str): Category of the product.
        bundeslaender (list): List of Bundesländer (states).
        description (str): Description of the product.
        consequence (str): Possible consequences.
        reseller (list): List of resellers.
        date (str): Date of the article.
        article (str): URL of the article.
    """

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
    message = json.dumps(data, ensure_ascii=False)
    print(message)
    conf = {"bootstrap.servers": "localhost:9092"}
    producer = Producer(conf)
    producer.produce("lebensmittelwarnungen", message)
    producer.flush()


def main():
    """
    Main function to execute the script. It fetches new articles periodically
    and processes them.
    """
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
