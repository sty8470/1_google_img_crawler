from selenium.webdriver.common.keys import Keys
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
from PyQt5.QtWidgets import *

import time 
import urllib
import random
import re

class GCrawler():
    def __init__(self, parent):
        self.parent = parent
        self.search_page = None
        self.search_bar = None
        self.body_element = None
        self.images = None
        self.valid_img_count = 1
        self.invalid_img_count = 1
        self.high_images = None
        self.real_image = None
        self.valid_num = None
    
    # 초기 드라이버 세팅하기
    def set_init_driver(self, chrome_options):
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        time.sleep(1)
    
    # 구글이미지 사이트 로딩하기
    def load_searching_page(self):
        self.img_search_page = 'https://www.google.co.kr/imghp'
        self.driver.get(url=self.img_search_page)
        self.driver.implicitly_wait(time_to_wait=10)
        
    # 검색어를 검색창에 입력하고 찾기
    def load_searching_item(self, search_key):
        self.search_bar = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
        for key in search_key.split():
                if ':' in key:
                    search_key = ' '.join(e for e in search_key.split()[1:])
        self.search_bar.send_keys(search_key)
        self.search_bar.send_keys(Keys.ENTER)
        self.driver.implicitly_wait(time_to_wait=5)
    
    # 찾는 개수중에서 숫자만 parsing해오기
    def validate_num_images(self, num):
        self.valid_num = re.findall(r'\d+', num)[0]
      
    
    # n번 만큼 전체 페이지 스크롤 내리기
    def scroll_down_body_page(self, n):
        self.body_element = self.driver.find_element(By.TAG_NAME, 'body')
        for i in range(n):
            self.body_element.send_keys(Keys.PAGE_DOWN)
            self.set_random_time_out()
    
    # 랜덤한 시간만큼 시간을 멈추게 하기
    def set_random_time_out(self):
        return time.sleep(random.uniform(0.3, 0.7))
    
    # 검색 된 사진 한장 한장 클릭하면서 HD 이미지 다운로드 하기
    def click_each_image_and_download_all(self, search_key, save_path, max_count):
        self.images = self.driver.find_elements(By.XPATH, '//*[@id="islrg"]/div/div/a[1]/div[1]/img')
        for image in self.images:
            if not self.parent.is_accepted:
                self.driver.quit()
                break
            try:
                image.click()
                time.sleep(0.5)
                self.high_images = self.driver.find_elements(By.XPATH, '//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div[1]/div[2]/div[2]/div/a/img')
                self.real_image = self.high_images[0].get_attribute('src')
                
                try:
                    urllib.request.urlretrieve(self.real_image, '{}'.format(save_path+'/'+search_key) + str(self.valid_img_count) +'.jpg')
                    self.valid_img_count += 1
                    if self.valid_img_count == 1:
                        print('Succeessfully download the {}st image!'.format(self.valid_img_count))
                    elif self.valid_img_count == 2:
                        print('Succeessfully download the {}nd image!'.format(self.valid_img_count))
                    else:
                        print('Succeessfully download the {}th image!'.format(self.valid_img_count))
                        if self.valid_img_count == int(''.join(filter(str.isdigit, max_count))):
                            print('All Images are Donwloaded Successfully as of now! --> Finishing the job')
                            break
                except:
                    self.invalid_img_count += 1
                    print('Failed to download the image!')
                    pass
            except:
                print('Failed to click the image!')
                pass
    
    def print_valid_num_imgs(self):
        print("There are {} number of valid images downloaded".format(self.valid_img_count))
    
    def print_invalid_num_imgs(self):
        print("There are {} number of images that fails to be downloaded".format(self.invalid_img_count))
    
    def run(self):
        self.set_init_driver(webdriver.ChromeOptions())
        self.load_searching_page()
        self.load_searching_item(self.parent.search_line_edit.text().strip())
        self.validate_num_images(self.parent.max_word_line_edit.text().strip())
        self.scroll_down_body_page(10)
        self.click_each_image_and_download_all(self.parent.search_line_edit.text(), self.parent.save_file_line_edit.text(),self.parent.max_word_line_edit.text())
        self.print_valid_num_imgs()
        self.print_invalid_num_imgs()
        self.parent.time_worker.working = False
        
        
    