from pytube import YouTube
import os
from glob import glob
import subprocess
from selenium import webdriver
import chromedriver_autoinstaller
import warnings
import eyed3
import time
from urllib import request

warnings.filterwarnings("ignore")
chromedriver_autoinstaller.install()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

artist = '아이유'
song = '너의 의미'

driver = webdriver.Chrome(options=options)
driver.get(f'https://www.melon.com/search/total/index.htm?q={song}+{artist}')

div = driver.find_element_by_css_selector('.ellipsis')
atag = div.find_element_by_tag_name('a')
songid = atag.get_attribute('href')
songid = songid.split(';')[-2].split('(')[-1][1:-2]
driver = webdriver.Chrome(options=options)
driver.get(f'https://www.melon.com/song/detail.htm?songId={songid}')

img = driver.find_element_by_css_selector('.image_typeAll')
img = img.find_element_by_tag_name('img')
img_url = img.get_attribute('src')

request.urlretrieve(img_url, f'{artist}_{song}.jpg')

driver.close()