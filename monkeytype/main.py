from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput.keyboard import Controller, Key
from time import sleep
from random import randint

class MonkeyType:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://monkeytype.com/")
        self.keyboard = Controller()
        WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "word")))
        self.style()
        self.start()
    
    def style(self):
        self.mode = self.driver.find_element_by_xpath("//div[@class='text-button' and @mode='words']")
        self.mode.click()
        sleep(1)
        self.word_count = self.driver.find_element_by_xpath("//div[@class='text-button' and @wordcount='100']")
        self.word_count.click()
        sleep(1)

    def type(self):
        words = self.driver.find_elements_by_class_name("word")

        for word in words:
            self.keyboard.type(word.text)
            self.keyboard.press(Key.space)
            self.keyboard.release(Key.space)
    
    def start(self):
        times = randint(1, 3)
        for _ in range(times): 
            self.type()
            sleep(1)
            self.driver.refresh()
            sleep(1)
        self.driver.quit()

typist = MonkeyType()
