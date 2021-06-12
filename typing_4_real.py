from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging
from time import sleep

text_bar = "Track-ticker"
driver = webdriver.Firefox()
driver.get("https://www.keybr.com/multiplayer")

try:
    window = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, text_bar)))
except TimeoutException:
    print("408 Request TeImeout")

while True:
    compete = driver.find_element_by_class_name(text_bar)
    while compete != "GO!":
        compete = driver.find_element_by_class_name(text_bar).text
    
    type_text = driver.find_element_by_class_name("TextInput-fragment")
    text = type_text.text
    actions = ActionChains(driver)

    prev_char = "f" 
    for c in text:
        print("Char = {}".format(c))
        if prev_char == "↵" and c == "\n":
            continue

        if c == "↵":
            actions.send_keys(Keys.ENTER)
        elif c == "␣":
            actions.send_keys(Keys.SPACE)
        else:
            actions.send_keys(c)
        prev_char = c

    actions.perform()
    sleep(0.1)

