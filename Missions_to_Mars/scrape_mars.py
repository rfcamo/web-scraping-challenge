import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time



# DB Setup
# 

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()
    collection.drop()

    # Nasa Mars news
    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html,'lxml')
    news_title = news_soup.find("div",class_="content_title").text
    news_para = news_soup.find("div", class_="article_teaser_body").text

    # JPL Mars Space Images - Featured Image
    jurl = 'https://spaceimages-mars.com/'
    browser.visit(jurl)
    jhtml = browser.html
    jpl_soup = bs(jhtml,"html.parser")
    image_url = jpl_soup.find('img',class_='headerimage fade-in').get("src")
    title = jpl_soup.find('h1',class_='media_feature_title').text
    feature_url = jurl+image_url
    
    # Mars fact
    murl = "https://galaxyfacts-mars.com/"
    mars_facts = pd.read_html(murl)[0]
    mars_facts.reset_index(inplace=True)
    mars_facts.columns=["ID", "Properties", "Mars","Earth"]
    mars_fact_html = mars_facts.to_html(header=False, index=False)
   
    # Mars Hemispheres
    mhurl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mhurl)  
    mhtml = browser.html 
    mh_soup = bs(mhtml,"html.parser") 
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
            product_dict = {}
            titles = result.find('h3').text
            end_link = result.find("a")["href"]
            image_link = "https://astrogeology.usgs.gov/" + end_link    
            browser.visit(image_link)
            html = browser.html
            soup= bs(html, "html.parser")
            downloads = soup.find("div", class_="downloads")
            image_url = downloads.find("a")["href"]
            product_dict['title']= titles
            product_dict['image_url']= image_url
            hemisphere_image_urls.append(product_dict)

    # Close the browser after scraping
    browser.quit()


    # Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_para,
        'featured_image': feature_url,
		'fact_table': mars_fact_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jurl,
        'fact_url': murl,
        'hemisphere_url': mhurl,
        }
    collection.insert(mars_data)
