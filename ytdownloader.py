from pytube import YouTube
import os
from glob import glob
import subprocess
from selenium import webdriver
import chromedriver_autoinstaller
import warnings
import eyed3

try:
    os.mkdir('Songs')
except:
    pass

os.chdir('Songs')

warnings.filterwarnings("ignore")
chromedriver_autoinstaller.install()
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

song_name = input('노래 제목: ')
artist = input('가수: ')
search = song_name + artist

driver = webdriver.Chrome(options=options)
driver.get(f'https://www.youtube.com/results?search_query={search}')

div = driver.find_element_by_id('dismissible')
ytd = div.find_element_by_tag_name('ytd-thumbnail')

atag = ytd.find_element_by_tag_name('a')
video_url = atag.get_attribute('href')

yt = YouTube(video_url)
stream = yt.streams.filter(only_audio=True).all()
yt.streams.filter(only_audio=True).first().download()
title = yt.title

new_file = glob('*.mp4')[0]
os.rename(new_file, f'{song_name}.mp4')

_filename = song_name
_dir = ''

input_name = f'{_filename}.mp4'
output_name = f'{_filename}.mp3'

subprocess.call(['ffmpeg', '-i', os.path.join(_dir, input_name), '-vn', '-b:a', '192k',
                os.path.join(_dir, output_name)])

os.remove(input_name)
audiofile = eyed3.load(f"{os.getcwd()}/{output_name}")
audiofile.tag.artist  = artist

audiofile.tag.save()

