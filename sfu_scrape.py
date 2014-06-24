from sfu import *
import pprint


def test_first_page():

    listing_url = SFUListing.listing_url().replace("X_FROM_X", "2014-01-01").replace("X_TO_X", "2014-12-31")
    print listing_url
    json = requests.get(listing_url).json()
    directory = SFUListing(json)

    pp = pprint.PrettyPrinter(indent = 2)

    for defence in directory.defences(listing_url):
        pp.pprint(defence.visit())
        

def scrape():
    t = TabWriter("output/sfu.txt")
    t.write_headers()

    for i in range(2010, 2015):
        start_date = "%d-01-01" % i
        end_date = "%d-12-31" % i
        
        listing_url = SFUListing.listing_url().replace("X_FROM_X", start_date).replace("X_TO_X", end_date)
        print listing_url
        try:
            json = requests.get(listing_url).json()
            directory = SFUListing(json)

            for defence in directory.defences(listing_url):
                t.write_row(defence)
        except ValueError:
            # Probably due to JSON not being well-formed
            print "Encountered ValueError, but continuing..."
            continue


#test_first_page()
scrape()