import requests 
from bs4 import BeautifulSoup 

web_address = "https://www.lebensmittelwarnung.de/bvl-lmw-de/liste/alle/deutschlandweit/10/0"
request_website = requests.get(web_address)

bs_website = (request_website.text, "html.parser")
