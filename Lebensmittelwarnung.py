import time

import mysql.connector
import requests
from bs4 import BeautifulSoup


def get_new_articles(most_recent_article) -> BeautifulSoup:
    web_address = "https://www.lebensmittelwarnung.de/DE/Home/home_node.html"
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
        get_article_content(article)
    return most_recent_article


def get_product_type(article_content):
    if article_content.find("span", class_="lmw-producttype__label"):
        return article_content.find(
            "span", class_="lmw-producttype__label"
        ).text.strip()
    return "NA"


def get_product_name(article_content):
    if article_content.find("dd", class_="lmw-description-list__description"):
        return article_content.find(
            "dd", class_="lmw-description-list__description"
        ).text.strip()
    return "NA"


def get_manufacturer(article_content):
    if article_content.find(
        "dt",
        class_="lmw-description-list__term",
        string="Hersteller / Inverkehrbringer:",
    ):
        return (
            article_content.find(
                "dt",
                class_="lmw-description-list__term",
                string="Hersteller / Inverkehrbringer:",
            )
            .find_next()
            .text.strip()
        )
    return "NA"


def get_category(article_content):
    if article_content.find(
        "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
    ):
        return article_content.find(
            "span", class_="lmw-badge lmw-badge--dark lmw-badge--large"
        ).text.strip()
    return "NA"


def get_bundeslaender(article_content):
    if article_content.find_all("li", class_="lmw-list__item"):
        bundeslaender = []
        bulae = article_content.find_all("li", class_="lmw-list__item")
        for bula in bulae:
            bundeslaender.append(bula.text.strip())
        return ", ".join(bundeslaender)
    return "NA"


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
    return "NA"


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
    return "NA"


def get_reseller(article_content):
    if article_content.find(
        "dt", class_="lmw-description-list__term", string="Vertrieb über:"
    ):
        return (
            article_content.find(
                "dt", class_="lmw-description-list__term", string="Vertrieb über:"
            )
            .find_next()
            .text.strip()
        )
    return "NA"


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
    send_article(
        product_type,
        product_name,
        manufacturer,
        category,
        bundeslaender,
        description,
        consequence,
        reseller,
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
    article,
):
    print(
        "\nProdukttyp:\n",
        product_type,
        "\nProduktname:\n",
        product_name,
        "\nHersteller:\n",
        manufacturer,
        "\nKategorie:\n",
        category,
        "\nBundeslaender:\n",
        bundeslaender,
        "\nBeschreibung:\n",
        description,
        "\nFolgen:\n",
        consequence,
        "\nVertrieb:\n",
        reseller,
        "\nURL:",
        article,
        sep="\n",
    )
    mydb = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="debezium",
        database="Lebensmittelwarnungen",
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO WARNUNGEN (product_type, product_name, manufacturer, category, bundeslaender, description, consequence, reseller, article) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        product_type,
        product_name,
        manufacturer,
        category,
        bundeslaender,
        description,
        consequence,
        reseller,
        article,
    )
    mycursor.execute(sql, val)

    mydb.commit()


def main() -> None:
    most_recent_article = ""
    while True:
        most_recent_article = get_new_articles(most_recent_article)
        time.sleep(3600)


if __name__ == "__main__":
    main()


# def get_recent_content(html_content: BeautifulSoup) -> list[list[str]]:
#     """
#     This function takes the BeautifulSoup Object created by
#     get_html_content and searches for all required information.
#     It returns a list of lists containing the information of each
#     warning.
#     """
#     types = html_content.find_all("span", id=re.compile(r"e4pn"))
#     dates = html_content.find_all("span", id=re.compile(r"ecqn"))
#     products = html_content.find_all("span", id=re.compile(r"egqn"))
#     company = html_content.find_all("span", id=re.compile(r"ejqn"))
#     cause = html_content.find_all("span", id=re.compile(r"eyqn"))
#     fed_states = html_content.find_all("div", id=re.compile(r"e3qn"))
#
#     regex_microorganism = re.compile(
#         "(.Listeri.*)|(Salmonell.*)|(Patulin.*)|(.*(T|t)oxin.*)|"
#         "(Pseudomon.*)|(Schimmel.*)|(Escherichia.*)|((M|m)ikro.*)|(Ba(c|z)ill.*)|(Hefe.*)"
#     )
#     regex_allergen = re.compile(
#         "(.*(A|a)llerg.*)|(.*nuss)|(Senf.*)|(Milch.*)|(Sesam.*)"
#     )
#     regex_foreign_body = re.compile(
#         "(.*(F|f)remd.*)|(Glas.*)|(Metall.*)|(Kunststoff.*)|(Stein.*)"
#     )
#     regex_limit = re.compile(
#         "(.*(W|w)ert.*)|(.*(G|g)ehalt.*)|((R|r)ückst.*)|(.*(M|m)enge.*)|(Arznei.*)|(Nachweis.*)|((G|g)esund.*)|((G|g)esetz.*)|(krebs.*)|(Befund.*)|((G|g)ef(a|ä)hr.*)|(zugelassen.*)"
#     )
#
#     cause_category = []
#     for i in cause:
#         if bool(regex_microorganism.search(i.text)):
#             cause_category.append("Mikroorganismen und Toxine")
#         elif bool(regex_allergen.search(i.text)):
#             cause_category.append("Allergene")
#         elif bool(regex_foreign_body.search(i.text)):
#             cause_category.append("Fremdkörper/-stoffe")
#         elif bool(regex_limit.search(i.text)):
#             cause_category.append("Grenzwertüberschreitung und Gesundheitsgefährdung")
#         else:
#             cause_category.append("Sonstiges")
#
#     recent_content = []
#     for i in range(10):
#         recent_content.append(
#             [
#                 types[i].text,
#                 dates[i].text,
#                 products[i]
#                 .text.replace("\n", " ")
#                 .replace("\r", " ")
#                 .replace("  ", " "),
#                 company[i]
#                 .text.replace("Hersteller:\n", "")
#                 .split("\n")[0]
#                 .replace("Hersteller:", "")
#                 .split(",")[0]
#                 .strip(),
#                 cause[i].text.replace("\n", " ").replace("\r", " ").replace("  ", " "),
#                 cause_category[i],
#                 fed_states[i].text.replace(
#                     "\nbetroffene Länder (alphabetisch):\n\n", ""
#                 ),
#             ]
#         )
#     return recent_content
