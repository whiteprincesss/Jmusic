from pytube import YouTube
import os
from glob import glob
import subprocess
from selenium import webdriver
import chromedriver_autoinstaller
import warnings
import eyed3
from urllib import request
from tkinter import messagebox
import sqlite3
import getpass
from tkinter import *
from PIL import ImageTk
from selenium.webdriver.common.by import By

now_dir = os.getcwd()
user = getpass.getuser()

os.chdir(f'C:\\Users\\{user}\\AppData\\Local')
if not os.path.isdir('JMusic'):
    os.mkdir('JMusic')
os.chdir('JMusic')
    
# DB
conn = sqlite3.connect("playlist.db", isolation_level=None)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS songs \
    (Song name, Artist, standard file path)")
if not os.path.isfile('JMusic_index.dat'):
    f = open('JMusic_index.dat', 'w')
    f.write('0')
    f.close()


os.chdir(now_dir)

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

# 노래 다운 및 mp3로 전환 함수
def song_download(song_name, artist):
    search = song_name + artist

    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.youtube.com/results?search_query={search}')

    div = driver.find_element(By.ID, "dismissible")
    ytd = div.find_element(By.TAG_NAME, "ytd-thumbnail")

    atag = ytd.find_element(By.TAG_NAME, "a")
    video_url = atag.get_attribute('href')

    yt = YouTube(video_url)
    yt.streams.filter(only_audio=True).first().download()

    new_file = glob('*.mp4')[0]
    os.rename(new_file, f'{song_name}_{artist}.mp4')

    _filename = f'{song_name}_{artist}'
    _dir = ''

    messagebox.showinfo("검색 완료!","다운로드를 시작합니다.")
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
        etc_download(song_name, artist)
    else:
        messagebox.showerror('오류!','이미 재생목록에 존재합니다.')
        os.remove(input_name)
        
# 앨범 커버, 가사 다운 함수
def etc_download(song_name, artist):
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://www.melon.com/search/song/index.htm?q={song_name}+{artist}')
    try:
        # 노래 존재 여부
        div = driver.find_element(By.CSS_SELECTOR,".ellipsis")
        atag = div.find_element(By.TAG_NAME, "a")
        songid = atag.get_attribute('href')
        songid = songid.split(';')[-2].split('(')[-1][1:-2]
        driver = webdriver.Chrome(options=options)
        driver.get(f'https://www.melon.com/song/detail.htm?songId={songid}')
        
        # 노래 가사 저장
        lyric = driver.find_element(By.CSS_SELECTOR, '.lyric')
        os.chdir(now_dir)
        os.chdir('Lyrics')
        f = open(f'{song_name}_{artist}.txt', 'w', encoding='utf-8')
        f.write(lyric.text)
        f.close()

        # 앨범 썸네일 다운
        img = driver.find_element(By.CSS_SELECTOR, '.image_typeAll')
        img = img.find_element(By.TAG_NAME, 'img')
        img_url = img.get_attribute('src')

        os.chdir(now_dir)
        os.chdir('thumbnail')

        request.urlretrieve(img_url, f'{song_name}_{artist}.png')
        messagebox.showinfo("다운 완료!","다운로드를 완료했습니다.")
        c.execute(f"INSERT INTO songs \
            VALUES('{song_name}', '{artist}', '{now_dir}')")
    except:
        messagebox.showerror('오류!','노래가 없습니다.')
        os.remove(song_name+'_'+artist+'.mp3')
        os.chdir(now_dir)

    driver.close()

def ui():
    # ui
    indexfile_path = f'C:\\Users\\{user}\\AppData\\Local\\JMusic\\JMusic_index.dat'
    r = open(indexfile_path, 'r')
    i = int(r.read())
    r.close()
    c.execute("SELECT * FROM songs")
    basic_info = c.fetchall()
    lastsong_index = len(basic_info)
    basic_info_1 = basic_info[i]
    song_name = str(basic_info_1[0])
    artist = str(basic_info_1[1])

    root = Tk()
    root.geometry('640x480+700+300')
    root.resizable(False, False)
    root.title('JMusic')

    # 이미지
    img = ImageTk.PhotoImage(file=f'{now_dir}/thumbnail/{song_name}_{artist}.png')
    label = Label(root, image=img)
    label.place(x=0, y=50)

    # 가사
    frame = Frame(root, width=50, height=100)
    frame.pack(side='right', pady=10)
    scrollbar = Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")
    list = Listbox(frame, yscrollcommand = scrollbar.set, width=40, height=100)
    f = open(f'{now_dir}/Lyrics/{song_name}_{artist}.txt', 'r', encoding='utf')
    lyrics = f.readlines()
    f.close()
    for i in range(len(lyrics)):
        list.insert(END, lyrics[i])
    list.pack(side='right', pady=10)
    scrollbar.config(command = list.yview)

    global if_play_song
    if_play_song = True

    # 검색 함수
    def song_searching():
        search_tk = Tk()
        search_tk.title("Search")
        search_tk.geometry('320x120+700+250')
        search_tk.resizable(False, False)

        def get_entry():
            get_song = song_entry.get()
            get_artist = artist_entry.get()
            search_tk.destroy()
            messagebox.showinfo("알림!",f"{get_artist}의 {get_song}을 검색합니다..")
            song_download(get_song, get_artist)

        Label(search_tk, text="노래 제목: ").place(x=20,y=20)
        Label(search_tk, text="가수: ").place(x=35,y=50)

        song_entry = Entry(search_tk)
        song_entry.place(x=90,y=20)
        artist_entry = Entry(search_tk)
        artist_entry.place(x=90,y=50)

        Button(search_tk, text="검색", command=get_entry).place(x=130,y=85)

        search_tk.mainloop()

    # 플레이리스트 수정 함수
    def change_playlist():
        chp = Tk()
        height = len(basic_info) * 30 + 13
        width = 300
        chp.geometry(f'{width}x{height}+700+250')
        chp.resizable(False, False)
        chp.title('플레이리스트 수정')

        def test():
            messagebox.showinfo('알림!','개발 중인 기능입니다.')

        Label(chp, text='번호', font=('','13', 'bold')).grid(column=0,row=0)
        Label(chp, text='제목', font=('','13', 'bold')).grid(column=1,row=0)
        Label(chp, text='가수', font=('','13', 'bold')).grid(column=2,row=0)

        for i in range(len(basic_info)):
            globals()[f'button{i}'] = i
            Label(chp, text=f'{i+1}',font=('','13', 'bold')).grid(column=0,row=i+1)
            Label(chp, text=f'{basic_info[i][0]}',font=('','13', 'bold')).grid(column=1,row=i+1)
            Label(chp, text=f'{basic_info[i][1]}',font=('','13', 'bold')).grid(column=2,row=i+1)
            globals()[f'button{i}'] = Button(chp, text=f'삭제_{i+1}',textvariable=i+1 ,command=test)
            globals()[f'button{i}'].grid(column=3,row=i+1)

        chp.mainloop()
    
    # 정지 함수
    def play_stop():
        global if_play_song
        if if_play_song == True:
            if_play_song = False
            btn_stop.config(text="재생")
        else:
            if_play_song = True
            btn_stop.config(text="정지")

    # 다음 함수
    def next():
        r = open(indexfile_path, 'r')
        i = int(r.read())
        r.close()
        i = i+1
        if i >= lastsong_index:
            messagebox.showinfo('알림!','마지막 노래입니다.')
        else:
            f = open(indexfile_path, 'w')
            f.write(str(i))
            f.close()
            root.destroy()
            ui()
            
    # 이전 함수
    def pre():
        r = open(indexfile_path, 'r')
        i = int(r.read())
        r.close()
        i = i-1
        if i < 0:
            messagebox.showinfo('알림!','처음 노래입니다.')
        else:
            f = open(indexfile_path, 'w')
            f.write(str(i))
            f.close()
            root.destroy()
            ui()

    # 메뉴 바
    menu= Menu(root)
    root.config(menu=menu)

    # 메뉴_플리
    playlist= Menu(menu)
    sub1 = Menu(playlist)
    sub2 = Menu(playlist)
    menu.add_cascade(label='노래', menu=playlist)
    playlist.add_cascade(label='재생목록', menu=sub1)
    sub1.add_command(label='재생목록 생성')
    sub1.add_command(label='재생목록 선택')
    playlist.add_cascade(label='플레이리스트', menu=sub2)
    sub2.add_command(label='플레이리스트 선택')
    sub2.add_command(label='플레이리스트 수정', command=change_playlist)

    # 메뉴_검색
    song_search= Menu(menu)
    menu.add_cascade(label='검색', menu=song_search)
    song_search.add_command(label='노래 검색', command=song_searching)

    # 제목 및 가수
    Label(root, text=song_name+' - '+artist, font=('','20', 'bold')).place(x=0, y=0)

    # 재생 바
    Button(root, text='이전', width=5, height=3, command=pre).place(x=60,y=370)
    btn_stop = Button(root, text='정지', width=5, height=3, command=play_stop)
    btn_stop.place(x=120,y=370)
    Button(root, text='다음', width=5, height=3, command=next).place(x=180,y=370)

    root.mainloop()
    
ui()