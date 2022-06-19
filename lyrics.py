from pytube import YouTube
import os
from glob import glob
import subprocess
from selenium import webdriver
import chromedriver_autoinstaller
import warnings
import eyed3
import time


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

lyric = driver.find_element_by_css_selector('.lyric')
f = open(f'{song}_{artist}.txt', 'w')
f.write(lyric.text)
f.close()