from bs4 import BeautifulSoup as bs
from splinter import Browser
import requests
import re
import pandas as pd
import time

# Create a funtion that returns the Soup object
def create_soup(html):
    return bs(html,'html.parser')

# Create a function that returns Browser object
def init_browser():
    executable_path = {'executable_path':'/usr/local/bin/chromedriver'}
    return Browser('chrome',**executable_path,headless=False)

def scrape():
    # --------------------------Start of Scraping Nasa Mars News
    url = 'https://mars.nasa.gov/news/'
    # Create browser object
    browser = init_browser()
    browser.visit(url)
    time.sleep(2)
    # Create Soup object
    html = browser.html
    soup = create_soup(html)
    # Scrape to get news title and content
    news = soup.find('ul',class_='item_list')
    news_title = news.find('div',class_='content_title').text
    news_p = soup.find('ul',class_='item_list').find('div',class_='article_teaser_body').text
    browser.quit()
    # --------------------------End of Scraping Nasa Mars News

    # --------------------------Start of Scraping JPL Mars Space Images
    base_url = "https://www.jpl.nasa.gov"
    scrape_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

    # Create Browser object
    browser = init_browser()
    browser.visit(scrape_url)

    # Create Soup object
    html = browser.html
    soup = create_soup(html)

    # Scrape the webpage
    featured_image_url = ( soup.find('article')['style']
                        .replace('background-image: url(\'','')
                        .replace('\');','')
                        )# Using replace to extract only the URL

    # Build complete URL
    featured_image_url = base_url + featured_image_url

    browser.quit()
    # --------------------------End of Scraping JPL Mars Space Images

    # --------------------------Start of Scraping Mars Weather twitter account
    url = 'https://twitter.com/marswxreport?lang=en'

    # Create soup object
    html = requests.get(url).text
    soup = create_soup(html)

    # Scrape the website - Assuming that if the text contains low,high and pressure it is related to weather
    mars_weather = soup.find_all(string=re.compile('low.*high.*\n.*\npressure.*'))[0]

    # Scraping Mars Facts Webpage
    url = 'https://space-facts.com/mars/'

    # Create a DataFrame to read the HTML table
    mars_df = pd.read_html(url)[0]
    mars_df.columns = ['description','value']
    mars_df['description'] = mars_df['description'].str.replace(':','')

    # Create index on description column
    mars_df.set_index('description',inplace=False)

    # Convert the DataFrame to HTML table
    html_data = mars_df.to_html(index=False).replace('\n','')
    # --------------------------End of Scraping Mars Weather twitter account

    # --------------------------Start of Scraping USGS Astrogeology site
    base_url = 'https://astrogeology.usgs.gov'
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # Create soup object
    html = requests.get(url).text
    soup = create_soup(html)

    # Retrieve the items
    items = soup.find_all('div',class_='item')

    # Dictionary and list to retrieve the results of scraping
    title_url_dict = {}
    hemisphere_image_urls = []

    for item in items:
        title = item.a.h3.text
        img_url = base_url + item.a['href']
        
        # Create soup object for the image URL to scrape the webpage
        html = requests.get(img_url).text
        img_soup = create_soup(html)
        
        # Get the image url string from the src attribute of the image
        full_img_url = base_url + img_soup.find('img',class_='wide-image')['src']
        
        # Update dictionary with the results
        title_url_dict = {'title':title,'img_url':full_img_url}
        
        # Update list
        hemisphere_image_urls.append(title_url_dict)
    # --------------------------End of Scraping USGS Astrogeology site

    return_dict={
        'News_Title':news_title,
        'News_Text':news_p,
        'JPL_Img':featured_image_url,
        'Mars_Weather':mars_weather,
        'Mars_Facts':html_data,
        'Mars_Hemisphere':hemisphere_image_urls
    }

    return return_dict

