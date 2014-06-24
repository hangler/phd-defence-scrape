from uoft_public_health import *
import pprint

suffixes = [
    "phd-final-oral-examination-2011-current",
    "phd-final-oral-examination-2006-2010",
    "phd-final-oral-examination-2000-2005",
]

def test_first_page():

    for suffix in suffixes:
        listing_url = UofTPublicHealthListing.listing_url() + suffix
        page = requests.get(listing_url).text
        soup = BeautifulSoup(page, "html5lib")
        directory = UofTPublicHealthListing(soup)

        pp = pprint.PrettyPrinter(indent = 2)

        for defence in directory.defences(listing_url):
            pp.pprint(defence.visit())
        

def scrape():
    t = TabWriter("output/uoft_public_health.tab")
    t.write_headers()

    for suffix in suffixes:
        listing_url = UofTPublicHealthListing.listing_url() + suffix
        page = requests.get(listing_url).text
        soup = BeautifulSoup(page, "html5lib")
        directory = UofTPublicHealthListing(soup)

        pp = pprint.PrettyPrinter(indent = 2)

        for defence in directory.defences(listing_url):
            t.write_row(defence)


#test_first_page()
scrape()