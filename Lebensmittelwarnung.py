import re
import requests 
from bs4 import BeautifulSoup 

web_address = "https://www.lebensmittelwarnung.de/bvl-lmw-de/liste/alle/deutschlandweit/10/0"
request_website = requests.get(web_address)

bs_website = BeautifulSoup(request_website.text, "html.parser")

types = bs_website.find_all("span", id=re.compile(r"e4pn"))
dates = bs_website.find_all("span", id=re.compile(r"ecqn"))
products = bs_website.find_all("span", id=re.compile(r"egqn"))
company = bs_website.find_all("span", id=re.compile(r"ejqn"))
cause = bs_website.find_all("span", id=re.compile(r"eyqn"))
fed_states = bs_website.find_all("div", id=re.compile(r"e3qn"))

