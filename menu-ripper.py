# Utility to rip dining hall menus
# (c) 2014 Matt LaRose

# TODO: 
# Handle if they have yesterday's menu up still
# Open just one browser window
# Paresky Sunday brunch now called lunch. Lots of fucked up stuff now
# handle driscoll "Grill" and Mission "Deli" ??
# Whitmans' doesn't have breakfast listed anymore??
# Finish food blacklist

# USEFUL LINKS:
# http://docs.seleniumhq.org/docs/04_webdriver_advanced.jsp
# http://selenium-python.readthedocs.org/en/latest/locating-elements.html

from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# List of foods we don't want to appear as an entree, because they
# aren't entrees. Titles have to go in here too because it is cleaner
# than trying to parse it, since the titles aren't treated like titles
# in the page source. 
blacklist = ['Entrees','Vegetarian Delight','Sauce', \
                 'Marinara Sauce','Quinoa']

def normalize(m):
    # Function to sift through tags, keeping non-blacklisted items
    normal = []
    for i in m:
        ok = True
        for b in blacklist:
            # i.text is unicode, so convert to str
            if str(i.text).rstrip().find(b) > -1:
                ok = False
        if ok:
            normal.append(str(i.text))
    return normal

def menus(halls):   # Takes a dict of the form hall: [meals]
    all_menus = {}  # Returns a similar dict
    driver = webdriver.Firefox()   # Opens a Firefox window
    for hall in halls:
        print(hall)
        all_menus[hall] = {}       # Will return this
        for meal in halls[hall]:   # Go through each of the hall's meals
            all_menus[hall][meal] = {}
            print("Scanning {} {}".format(hall, meal))
            try:
                # Wait for page to load the link we want
                driver.get("http://dining.williams.edu")
                Wait(driver, 100).until(EC.presence_of_element_located((
                            By.PARTIAL_LINK_TEXT, hall)))
                driver.find_element_by_partial_link_text(hall).click()
            except:
                pass
            try:
                Wait(driver, 100).until(EC.presence_of_element_located((
                            By.PARTIAL_LINK_TEXT, meal)))
                # Open the meal's page. (If something breaks, look here)
                driver.find_element_by_partial_link_text(meal).click()
                sleep(3)  # Dining site is touchy so don't rush it
                source = driver.page_source
            except:
                pass
            # This is somehwat hacky. Only food items on the page are hoverable
            getItems = lambda s : s.findAll('td',{'class':'cbo_nn_itemHover'})
            # Get vegetarian section
            veg = source[source.find('Vegetarian'):source.find('Entrees')]
            veg_items = getItems(BeautifulSoup(veg))
            veg_menu = normalize(veg_items)
            all_menus[hall][meal]['Vegetarian'] = veg_menu
            # Get entrees section
            entrees = source[source.find('Entrees'):source.find('Vegetables')]
            entree_items = getItems(BeautifulSoup(entrees))
            entree_menu = normalize(entree_items)
            all_menus[hall][meal]['Entrees'] = entree_menu
    driver.quit() # Close Firefox
    return all_menus

if __name__ == '__main__':
    # Allows for customizability of what meals you want to search
    # for a given dining hall. Whitmans has been changing stuff
    # up a lot lately, so this will come in handy.
    halls = {"Whitmans'"    : ["LUNCH", "DINNER"],
             "Driscoll"     : ["LUNCH", "DINNER"],
             "Mission Park" : ["LUNCH", "DINNER"] }
        
    # Rough outline for traversing through this
    all_menus = menus(halls)
    for menu in all_menus:
        print(menu, all_menus[menu])
        print

