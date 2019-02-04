import requests
import re
from bs4 import BeautifulSoup

import datetime
import time
import sys
import os

```Scrape data from Kijiji and store it in a text file```

def ParseAd(html):  # Parses ad html trees and sorts relevant data into a dictionary
    ad_info = {}

    try:
        ad_info["Title"] = html.find('h1', {'class': re.compile("^title-")}).text.rstrip()
    except:
        print('[Error] Unable to parse Title data.')
        return None

    try:
        ad_info["Visits"] = html.find('div', {'class': re.compile("^visitCounter-")}).text
    except:
        print('[Error] Unable to parse Visits data.')
        return None

    try:
        details = html.find(itemprop="description").get_text()
        lines = details.splitlines()
        description = ''.join(lines)
        ad_info["Details"] = description
    except:
        print('[Error] Unable to parse Description data.')
        return None

    try:
        ad_info["Date"] = html.find(itemprop="datePosted", content=True)['content']
    except:
        print('[Error] Unable to parse Date data.')
        return None

    try:
        ad_info["Location"] = html.find(itemprop="address").get_text()
    except:
        print('[Error] Unable to parse Location data.')
        return None

    try:
        ad_info["Price"] = html.find(itemprop="price").get_text()
    except:
        print('[Error] Unable to parse Price data.')
        return None

    return ad_info


def WriteAds(ad_dict, filename):  # Writes ads from given dictionary to given file
    # try:
    file = open(filename, 'ab')
    file.write("AdId|Title|Visits|Details|Date|Location|Price|Url\n".encode('utf-8'))
    for ad_id in ad_dict:
        #file.write(ad_id.encode('utf-8'))
        #file.write((str(ad_dict[ad_id]) + "\n").encode('utf-8'))
        file.write((ad_id + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Title"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Visits"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Details"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Date"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Location"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Price"] + '|').encode('utf-8'))
        file.write((ad_dict[ad_id]["Url"] + "\n").encode('utf-8'))
    file.close()


def ReadAds(filename):  # Reads given file and creates a dict of ads in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    ad_dict = {}
    with open(filename, 'rb') as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{'.encode('utf-8'))
                ad_id = line[:index].decode('utf-8')
                dictionary = line[index:].decode('utf-8')
                dictionary = ast.literal_eval(dictionary)
                ad_dict[ad_id] = dictionary
    return ad_dict


def scrape_specific_ad(url):
    ad_url = "https://www.kijiji.ca" + url

    try:
        page = requests.get(ad_url)  # Get the html data from the URL
    except:
        print("[Error] Unable to load " + url)
        sys.exit(1)

    soup = BeautifulSoup(page.content, "html.parser")

    ad_dict = ParseAd(soup)

    if ad_dict is not None:
        ad_dict["Url"] = ad_url
        return ad_dict
    else:
        return None


def scrape(url, old_ad_dict, exclude_list, filename):  # Pulls page data from a given kijiji url and finds all ads on each page
    # Initialize variables for loop
    ad_dict = {}
    third_party_ad_ids = []

    while url:

        try:
            page = requests.get(url)  # Get the html data from the URL
        except:
            print("[Error] Unable to load " + url)
            sys.exit(1)

        soup = BeautifulSoup(page.content, "html.parser")

        kijiji_ads = soup.find_all("div", {"class": "regular-ad"})  # Finds all ad trees in page html.

        third_party_ads = soup.find_all("div", {"class": "third-party"})  # Find all third-party ads to skip them
        for ad in third_party_ads:
            third_party_ad_ids.append(ad['data-ad-id'])

        exclude_list = toLower(exclude_list)  # Make all words in the exclude list lower-case
        for ad in kijiji_ads:  # Creates a dictionary of all ads with ad id being the keys.
            title = ad.find('a', {"class": "title"}).text.strip()  # Get the ad title
            ad_id = ad['data-ad-id']  # Get the ad id
            if not [False for match in exclude_list if
                    match in title.lower()]:  # If any of the title words match the exclude list then skip
                # if [True for match in checklist if match in title.lower()]:
                if ad_id not in old_ad_dict and ad_id not in third_party_ad_ids:  # Skip third-party ads and ads already found
                    print('[Okay] New ad found! Ad id: ' + ad_id)
                    ad_data = scrape_specific_ad(ad['data-vip-url'])  # Parse data from ad
                    if ad_data is not None:
                        ad_dict[ad_id] = ad_data
        url = soup.find('span', {'title': 'Next'})
        if url:
            url = 'https://www.kijiji.ca' + url['data-href']

    if ad_dict != {}:  # If dict not emtpy, write ads to text file and send email.
        WriteAds(ad_dict, filename)  # Save ads to file


def toLower(input_list):  # Rturns a given list of words to lower-case words
    output_list = list()
    for word in input_list:
        output_list.append(word.lower())
    return output_list


def main():  # Main function, handles command line arguments and calls other functions for parsing ads
    args = sys.argv
    url = args[1]
    if '-f' in args:
        filename = args.pop(args.index('-f') + 1)
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        args.remove('-f')
    if '-e' in args:
        exclude_list = args[args.index('-e') + 1:]
    else:
        exclude_list = list()

    old_ad_dict = ReadAds(filename)
    print("[Okay] Ad database succesfully loaded.")

    scrape(url, old_ad_dict, exclude_list, filename)


if __name__ == "__main__":
    main()
