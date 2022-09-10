from pytube import YouTube
import os
from glob import glob
import subprocess
from selenium import webdriver
import chromedriver_autoinstaller
import warnings
import eyed3
from urllib import request

if not os.path.isdir('Songs'):
    os.mkdir('Songs')
if not os.path.isdir('Lyrics'):
    os.mkdir('Lyrics')
if not os.path.isdir('thumbnail'):
    os.mkdir('thumbnail')

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
os.rename(new_file, f'{song_name}_{artist}.mp4')

_filename = song_name
_dir = ''

input_name = f'{_filename}.mp4'
output_name = f'{_filename}.mp3'

if os.path.isfile(output_name) == False:
    subprocess.call(['ffmpeg', '-i', os.path.join(_dir, input_name), '-vn', '-b:a', '192k',
                    os.path.join(_dir, output_name)])

    os.remove(input_name)
    audiofile = eyed3.load(f"{os.getcwd()}/{output_name}")
    audiofile.tag.artist  = artist

    audiofile.tag.save()

    driver.close()

    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.melon.com/search/song/index.htm?q={song_name}+{artist}')
    try:
        # 노래 존재 여부
        div = driver.find_element_by_css_selector('.ellipsis')
        atag = div.find_element_by_tag_name('a')
        songid = atag.get_attribute('href')
        songid = songid.split(';')[-2].split('(')[-1][1:-2]
        driver = webdriver.Chrome(options=options)
        driver.get(f'https://www.melon.com/song/detail.htm?songId={songid}')
        
        # 노래 가사 저장
        lyric = driver.find_element_by_css_selector('.lyric')
        os.chdir('..')
        os.chdir('Lyrics')
        f = open(f'{song_name}_{artist}.txt', 'w', encoding='utf-8')
        f.write(lyric.text)
        f.close()

        # 앨범 썸네일 다운
        img = driver.find_element_by_css_selector('.image_typeAll')
        img = img.find_element_by_tag_name('img')
        img_url = img.get_attribute('src')

        os.chdir('..')
        os.chdir('thumbnail')

        request.urlretrieve(img_url, f'{song_name}_{artist}.png')
    except:
        print('노래가 없습니다.')
        os.remove(output_name)
else:
    print('이미 재생목록에 존재합니다.')
    os.remove(input_name)

driver.close()