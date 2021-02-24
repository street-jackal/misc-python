from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re

# Root login URL
url = "redacted.for.privacy.com"

# Dictionary for storing schedule data scraped from timecard site.
# Keys are days of the week
# Values are arrays with 0th element set to a tuple representing 
# the numbers the site uses to code days of the week 
week = {"Monday":[(0,1)], 
        "Tuesday":[(2,3)],
        "Wednesday":[(4,5)], 
        "Thursday":[(6,7)], 
        "Friday":[(8,9)], 
        "Saturday":[(10,11)], 
        "Sunday":[(12,13)]}
        
def read_data_from_URL(address):
    """
    Input: (string) URL of site to be scraped 
    Output: None. Uses Selenium to walk through login process and navigate to page that we need to scrape
            Iterates through days of the week and adds time in/out data to 'week' dictionary
            key that matches the regex + numeric code at index 0 of each entry.
    """
    login_field = "login-form_username"
    login_name = "username@login.com"
    password_field = "login-form_password"
    password_value = "password1234"
    first_button = "verifUseridBtn"
    second_button = "signBtn"
    third_button = "Update My Timecard"
    fourth_button = "UI4_ctBody_UCTodaysActivities_btnTimeSheet"

    # Enter login credentials and click login buttons
    browser = webdriver.Chrome()
    browser.get(address)
    login = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, login_field)))
    login.send_keys(login_name)
    button1 = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, first_button)))
    button1.click()
    password = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, password_field)))
    password.send_keys(password_value)
    button2 = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, second_button)))
    button2.click()

    # Now that we're logged in, click the button to take us to the timecard page
    button3 = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, third_button)))
    button3.click()

    # Now that we're logged in, click the button to take us to the timecard page
    button4 = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, fourth_button)))
    button4.click()    

    # Now that we're at the timecard page, extract the data we need with BS4
    wait = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'div')))
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    # Actually extract the timecard data we need
    for day in week:
        for i in range(2):
            for match in soup.find_all('div', id=re.compile(f"INTIMEtm_{week[day][0][i]}")):
                week[day].append(match.text.strip().lstrip("0"))
            for match in soup.find_all('div', id=re.compile(f"OUTTIMEtm_{week[day][0][i]}")):
                week[day].append(match.text.strip().lstrip("0"))

def print_data_from_dict():
    """
    Prints the data from week dictionary after it's populated via read_data_from_URL.
    Formatting is specific to this client's needs.
    """
    for day in week:
        if len(week[day]) > 1: # ignore days where there were no hours logged
            dailyHours = f"{day}: "
            for i in range(1, len(week[day]), 2):
                dailyHours += " - ".join(week[day][i:i+2])
                if i < len(week[day]) - 2: # don't add slashes if it's the last work period of the day
                    dailyHours += "  //  "
            print(dailyHours)
        else:
            print(f"Didn't find any data for {day}.")

# run the program
read_data_from_URL(url)
print_data_from_dict()
