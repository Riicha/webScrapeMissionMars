
# coding: utf-8
# #Web Scraping  Mission to Mars
# ## Step 1 - Scraping

# Dependencies
import pandas as pd
from splinter import Browser
import requests

import time

from bs4 import BeautifulSoup
from selenium import webdriver

import tweepy
import TweepyCredentials # twitter keys and tokens
import pymongo

import logging # imported for logging
from datetime import datetime

# create logger with 'mars_application'
logger = logging.getLogger('mars_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('mars.log')
fh.setLevel(logging.DEBUG)
# add the handlers to the logger
logger.addHandler(fh)

def unauthorized():
    errmsg = "Please supply credentials for twitter to get weather details."
    return errmsg

# Setting up splinter
def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

# Define a function 
def scrape():
    browser = init_browser()
    # create mars dict that we can insert into mongo
    mars = {}

#---------------------------------------------------------------------------------#
    # URL of NASA Mars News to be scraped for latest news and paragraph title
#---------------------------------------------------------------------------------#

    url_NASA_Mars_News = 'https://mars.nasa.gov/news/'
    browser.visit(url_NASA_Mars_News)
    time.sleep(1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

#---------------------------------------------------------------------------------#
    # Latest News Title from NASA Mars News Site
#---------------------------------------------------------------------------------#

    news_title = news_soup.find_all('div', class_='content_title')

#---------------------------------------------------------------------------------#
    # Latest News Paragraph Text from NASA Mars News Site
#---------------------------------------------------------------------------------#
    news_p = news_soup.find_all('div', class_='article_teaser_body')


#---------------------------------------------------------------------------------#
    # # Adding latest news and paragraph title to the dictionary
#---------------------------------------------------------------------------------#
    mars['news_title'] = news_title[0].text
    mars['news_p'] = news_p[0].text

    # JPL Mars Space Images - Featured Image
#---------------------------------------------------------------------------------#
    # URL of JPL Mars Space Image to be scraped for featured image
#---------------------------------------------------------------------------------#
    url_JPL_images = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_JPL_images)

#---------------------------------------------------------------------------------#
    # Browse through the pages
 #---------------------------------------------------------------------------------#
    time.sleep(1)

    # Click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()
    time.sleep(2)


    # Click the more info button
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()
    time.sleep(2)


    # Using BeautifulSoup create an object and parse with 'html.parser'
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')


    # find the relative image url
    img_url_rel = img_soup.find('figure', class_='lede').find('img')['src']
    img_url_rel

    # Use the base url to create an absolute url
    baseUrl = 'https://www.jpl.nasa.gov'
    featured_image_url = baseUrl + img_url_rel
    featured_image_url

    # Adding featured image url to the dictionary
    mars['featured_image_url'] = featured_image_url

#---------------------------------------------------------------------------------#
    # Mars Weather

    # Twitter API Keys
    consumer_key = TweepyCredentials.consumer_key
    consumer_secret = TweepyCredentials.consumer_secret
    access_token = TweepyCredentials.access_token
    access_token_secret = TweepyCredentials.access_token_secret


    # Setup Tweepy API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#---------------------------------------------------------------------------------#
    # Target User
    target_user = "@MarsWxReport"

    try:
        # Retrive the latest tweet
        tweet = api.user_timeline(target_user)
        mars_weather = tweet[0]['text']
    except Exception as ex:
        logger.info(ex)
        mars_weather = unauthorized()


    # Adding Mars weather from the latest rweet  to the dictionary
    mars['mars_weather'] = mars_weather
#---------------------------------------------------------------------------------#
#    Mars Facts

    # URL of Mars facts to scrape the table containing facts about the planet
#---------------------------------------------------------------------------------#
    url_Mars_Facts = 'https://space-facts.com/mars/'
    
    df = pd.read_html(url_Mars_Facts)[0]
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    table = df.to_html()
    table = table.replace('\n', '')

    mars['facts'] = table
    

 #---------------------------------------------------------------------------------#

    # Mars Hemispheres
    
    # Scapping of  USGS Astrogeology site to obtain high resolution images for each of Mars hemispheres.
#---------------------------------------------------------------------------------#

    hemispheresurl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemisphereBaseUrl = 'https://astrogeology.usgs.gov'
    browser.visit(hemispheresurl)
    soup = BeautifulSoup(browser.html,'html5lib')
    hemispheres = soup.find_all('div', class_='item')
    
    # Create an empty list to hold dictionaries of hemisphere title with the image url string
    hemisphere_image_urls = []
    hemispheredict = {}

    # Loop through those links, click the link, find the sample anchor, return the href
    for hemisphere in hemispheres:
        
        hemisphereLink = hemisphere.find("a",class_="product-item")['href']

        browser.visit(hemisphereBaseUrl + hemisphereLink)
        soup = BeautifulSoup(browser.html, 'html.parser')

        # Get Hemisphere title
        title = soup.find('title').text
        hemisphereTitle = title.split('|')
        hemisphereTitle = hemisphereTitle[0].replace(' Enhanced ','')
        imgUrl = soup.find('img',class_='wide-image').get('src')
        imgUrl = hemisphereBaseUrl + imgUrl
        hemispheredict = {"title": hemisphereTitle, "img_url":imgUrl}
        
        
        # Append hemisphere object to list
        hemisphere_image_urls.append(hemispheredict)

    # Set the hemispheres
    mars["hemispheres"] = hemisphere_image_urls

    browser.quit()

  
    return mars
