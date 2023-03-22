# CREATING AMAZON WEBSCRAPER
import csv                                      # to save the data in csv file

import requests                                 # to get the html content of the page

from bs4 import BeautifulSoup                   # to parse the html content and traverse the html tree . It is a library that makes it easy to scrape           information from web pages. It sits atop an HTML or XML parser, providing Pythonic idioms for iterating, searching, and modifying the parse tree. This will be the main library we will use to scrape the data from the web pages.

from msedge.selenium_tools import Edge, EdgeOptions # to open the web browser and navigate to the web pages . I have used msedge you can use any other browser like chrome, firefox etc but you will have to install the respective webdriver for that browser.

import re                                       # to extract the asin from the url

def get_url(search_term):
    template = "https://www.amazon.in/s?k={}&ref=nb_sb_noss_2" #this will be the generate url for all the searches and we will add the search term to it
    search_term = search_term.replace(" ", "+")
    # add term query to url
    url = template.format(search_term)
    url += "&page={}"                           # add page query placeholder
    return url

def extract_record(item):  # Extract and return data from a single record
    atag = item.h2.a # find the h2 tag with a tag inside it and extract the text as h2 tag is the title of the product
    name = item.h2.text.strip() # extract the text from the h2 tag and strip the white spaces
    description = atag.text.strip() # extract the text from the a tag and strip the white spaces
    url = "https://www.amazon.in" + atag.get("href") # extract the href attribute from the a tag and add it to the base url to get the complete url of the product
    try:           # price
        
        price_parent = item.find("span", "a-price") # find the span tag with class a-price
        price = price_parent.find("span", "a-offscreen").text # find the span tag with class a-offscreen inside the span tag with class a-price and extract the text
    except AttributeError:     # if there is no price tag
        return  

    try:   # rating 
        rating = item.i.text # find the i tag and extract the text
    except AttributeError:
        rating = ""

    try:   # review count
        no_of_reviews = item.find('span', {'class' : 'a-size-base s-underline-text'}).text # find the span tag with class a-size-base s-underline-text and extract the text
    except AttributeError:
        no_of_reviews = ""

    
    asin_list = re.findall(r"/dp/(\w{10})", url)   # Extract ASIN from URL
    asin = asin_list[0] if asin_list else ""

    # opening the product detail page

    options = EdgeOptions() 
    options.use_chromium = True
    capabilities = options.to_capabilities()
    driver = Edge(executable_path="(write the address where msedgedriver would be unzipped)msedgedriver.exe", capabilities=capabilities)

    driver.get(url) 
    soup2 = BeautifulSoup(driver.page_source, "html.parser") # create a soup object for the product detail page and extract the data from it


    # Extracting the manufacturer details from the product detail page  
    try:
        manufacturer_tags = soup2.find_all("span", class_="a-list-item") # find all the span tags with class a-list-item
        manufacturer = ""
        for tag in manufacturer_tags: 
            if "Manufacturer" in tag.text: # if the text in the span tag contains the word Manufacturer
                manufacturer = tag.find("span", class_="a-text-bold").find_next_sibling("span").text.strip() # find the next sibling of the span tag with class a-text-bold and extract the text
                break
    except AttributeError:
        manufacturer = ""
    
    
    try:
        product_desc = soup2.find("div", {"id": "productDescription"}).text.strip() # find the div tag with id productDescription and extract the text
    except AttributeError:
        product_desc = ""

    result = (url, name, price, rating, no_of_reviews, asin, description,product_desc , manufacturer) # create a tuple with all the data which will be returned in a csv file
    driver.close()
    return result

def main(search_term):
    """Run main program routine"""
    # startup the webdriver
    options = EdgeOptions()  # use the default options to create an instance of EdgeOptions
    options.use_chromium = True # set the use_chromium option
    capabilities = options.to_capabilities() # create a dictionary with all the capabilities
    driver = Edge(executable_path="(write the address where msedgedriver would be unzipped)msedgedriver.exe", capabilities=capabilities) # create an instance of Edge with the capabilities dictionary you just created
    records = []
    url = get_url(search_term)
    for page in range(1, 21):
        driver.get(url.format(page)) # get the url with the page number
        soup = BeautifulSoup(driver.page_source, "html.parser") # create a soup object
        results = soup.find_all("div", {"data-component-type": "s-search-result"}) # find all the div tags with data-component-type as s-search-result
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)
    driver.close()
    # save the data to csv file
    with open("results.csv", "w", newline="", encoding="utf-8") as f: # change the path to the location where you want to save the csv file
        writer = csv.writer(f) # create a csv writer object
        writer.writerow(["URL", "Name", "Price", "Rating", "Number of Reviews", "ASIN", "Description","Product Description", "Manufacturer"]) 
        writer.writerows(records) # write all the records to the csv file

if __name__ == '__main__': 
    main('bags') # change the search term here
