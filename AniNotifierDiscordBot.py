# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 21:09:26 2018

@author: user
"""

import os
import datetime
import discord
import asyncio
import sqlite3
import random
import requests
import time
import traceback
import youtube_dl
from discord.ext import commands
from bs4 import BeautifulSoup

import ehapi


dbname = "anime.db"
db = sqlite3.connect(dbname)
c = db.cursor()

client = discord.Client()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False

def check_update():
    r = requests.get('https://ani.gamer.com.tw/')
    r.encoding = 'gzip'

    line = r.text.split('\n')

    find = '付費比例'

    count = 0
    for s in line:
        if find in s:
            del line[count+1:]

        count +=1

    title = "newanime-title"
    vol = "newanime-vol"
    datee = "newanime-date"
    URL = "data-look"

    for i in range(len(line)):
        if line[i].find(title) > 0:
            a = line[i].find('>')
            b = line[i].find('<',1)
            nameTXT = line[i][a+1:b]

            cursor = c.execute("SELECT ID,NAME from ANIME")
            for row in cursor:
                if row[1] == nameTXT:
                    ids = row[0]

                    a = line[i-5].find('?sn')
                    b = line[i-5].find(' data-look')
                    urlTXT = line[i-5][a+3:b-1]

                    a = line[i+2].find('>')
                    b = line[i+2].find('<',1)
                    volTXT = line[i+2][a+1:b]


                    a = line[i+3].find('>')
                    b = line[i+3].find('<',1)
                    dateTXT = line[i+3][a+1:b]



                    c2 = c.execute("SELECT VOL,URL from ANIME where ID="+str(ids))
                    for rr in c2:
                        if rr[0] != volTXT:
                            volexi = False
                            c3 = c.execute("SELECT VOL from VOLLIST where ANIID="+str(ids))
                            for rrr in c3:
                                if rr[0] == rrr[0]:
                                    volexi = True
                                    break
                            if not volexi:
                                volforupdate = volTXT.split()
                                db.execute("INSERT INTO VOLLIST (ANIID,VOL,URL) VALUES (?, ?, ?)",(str(ids),volforupdate[1],urlTXT));
                                db.commit()

                            db.execute("UPDATE ANIME SET URL =? where ID=?",(urlTXT,str(ids)))
                            db.commit()

                            db.execute("UPDATE ANIME SET VOL =? where ID=?",(volTXT,str(ids)))
                            db.commit()

                            db.execute("UPDATE ANIME SET DATE =? where ID=?",(dateTXT,str(ids)))
                            db.commit()

                            db.execute("UPDATE ANIME SET STATE =? where ID=?",('1',str(ids)))
                            db.commit()

                            break
            break




@client.event
async def on_ready():
    print('啟動成功。')
    print('------')


@client.event
async def on_message(message):

    #await parse_exlinks(message)


    upurl = "https://ani.gamer.com.tw/animeVideo.php?sn="
    twitter = 'https://twitter.com/'
    pixiv = 'https://www.pixiv.net/member_illust.php?illust_id='
    pixiv_member = 'https://www.pixiv.net/member.php?id='

    if message.author.id == '277015599379382273' and message.channel.id == '550369458539986965':
        await client.send_message(client.get_channel('384320278395879426'), message.content)

    if message.author.id == '277015599379382273' and message.channel.id == '560709158014287873':
        await client.send_message(client.get_channel('386603626967072768'), message.content)


    if message.content.startswith('!p') and message.channel.id == '546259834928889856':
        tmpTXT = message.content
        content = tmpTXT.split()
        if content[0] == ('!pm'):
            pixivmemberurl = pixiv_member + content[len(content)-1]
            await client.send_message(message.channel, pixivmemberurl)
        elif content[0] == ('!pixiv'):
            await client.send_message(message.channel, "P網址指令:\n\n!p:後面加上作品id，會連結作品的網址。\n\n!pm:後面加上作者id，會連結作者的網址。")
        elif content[0] == ('!p'):
            pixivurl = pixiv + content[len(content)-1]+'&mode=medium'
            await client.send_message(message.channel, pixivurl)


    if message.content.startswith('play'):
        if message.author.id == '277015599379382273':
            author = message.author
            voice_channel = author.voice.voice_channel
            tmpTXT = message.content
            content = tmpTXT.split('play ')

            author = message.author
            voice_channel = author.voice.voice_channel
            if voice_channel is not None:
                if client.is_voice_connected(message.server):
                    for connection in tuple(client.voice_clients):
                        if connection.server is message.server:
                            await connection.disconnect()
                a = await client.join_voice_channel(voice_channel)
                player = a.create_ffmpeg_player(content[1])
                player.start()

                if player.is_done():
                    await client.send_message(message.channel,'{} '.format(author.mention) + content[1]+ ' 播放完畢。')
                    player.stop()
        else:
            await client.send_message(message.channel,'{} 我只為古見唱歌。'.format(message.author.mention))


    if message.content == ('ㄎㄅ'):
        await client.send_message(message.channel,'https://imgur.com/Y5ExNxz')


    if message.content == ('胖胖召喚!'):

        if random.randint(0,1):
            idco = '<@277636190818271242>'
            await client.send_message(message.channel, summon+' %s ！' % idco )
        else:
            await client.send_message(message.channel,'{} 你沒有胖胖召喚的資格。'.format(message.author.mention))

    if message.content == ('兔子召喚!'):

        if random.randint(0,1):
            rabbit = '<@196158304580272129>'
            test = '<@506440412496396289>'
            await client.send_message(message.channel, summon+' %s ！' % rabbit )
        else:
            await client.send_message(message.channel,'{} 你沒有兔子召喚的資格。'.format(message.author.mention))
    if message.content.startswith('!刀劍'):
        idstr = '3'
        if message.content == ('!刀劍'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)
        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break



    elif message.content.startswith('!輝夜'):
        idstr = '4'
        if message.content == ('!輝夜'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)
        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break

    elif message.content.startswith('!魔法少女'):
        idstr = '7'
        if message.content == ('!魔法少女'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)
        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break

    elif message.content.startswith('!JOJO'):
        idstr = '10'
        if message.content == ('!JOJO'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)
        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break


    elif message.content.startswith('!萌王') or message.content.startswith('!史萊姆'):
        idstr = '21'
        if message.content == ('!萌王') or message.content == ('!史萊姆'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)
        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break


    elif message.content.startswith('!上野') or message.content.startswith('!笨拙'):
        idstr = '23'
        if message.content == ('!上野') or message.content == ('!笨拙'):
            cursor = c.execute("SELECT NAME,VOL,DATE,URL from ANIME where ID="+idstr)
            for row in cursor:
                a = row[0]+'\n最新集數: '+row[1]+'\n最後更新時間: '+row[2]+'\n'+upurl+row[3]
            await client.send_message(message.channel, a)

        else:
            tmpTXT = message.content
            content = tmpTXT.split()
            cursor = c.execute("SELECT VOL,URL from VOLLIST where ANIID="+idstr)
            for row in cursor:
                if content[len(content)-1] == row[0]:
                    ala = upurl+row[1]
                    await client.send_message(message.channel, ala)
                    break


    elif message.content == ('!自我介紹'):
        await client.send_message(message.channel, '我是只野仁人2.2，請多指教。')
"""
@client.event
async def checking():
"""

async def parse_exlinks(message):
    galleries = ehapi.get_galleries(message.content)
    if galleries:
        logger(message, ", ".join([gallery['token'] for gallery in galleries]))
        if len(galleries) > 5:  # don't spam chat too much if user spams links
            await client.send_message(message.channel,embed=embed_titles(galleries))
        else:
            for gallery in galleries:
                await client.send_message(message.channel,embed=embed_full(gallery))
def embed_titles(exmetas):
    link_list = [create_markdown_url(exmeta['title'], create_ex_url(exmeta['gid'], exmeta['token'])) for exmeta in
                 exmetas]
    msg = "\n".join(link_list)
    return discord.Embed(description=msg,
                         colour=EH_COLOUR)


# pretty discord embeds for small amount of links
def embed_full(exmeta):
    em = discord.Embed(title=BeautifulSoup(exmeta['title'], "html.parser").string,
                       url=create_ex_url(exmeta['gid'], exmeta['token']),
                       timestamp=datetime.datetime.utcfromtimestamp(int(exmeta['posted'])),
                       description=BeautifulSoup(exmeta['title_jpn'], "html.parser").string,
                       colour=EH_COLOUR)
    em.set_image(url=exmeta['thumb'])
    em.set_thumbnail(url=G_CATEGORY[exmeta['category']])
    em.set_footer(text=exmeta['filecount'] + " pages")
    em.add_field(name="rating", value=exmeta['rating'])
    em = process_tags(em, exmeta['tags'])
    return em


# put our tags from the EH JSON response into the discord embed
def process_tags(em, tags):
    tag_dict = {'male': [], 'female': [], 'parody': [], 'character': [], 'misc': []}
    for tag in tags:
        if ":" in tag:
            splitted = tag.split(":")
            if splitted[0] in tag_dict:
                tag_dict[splitted[0]].append(BeautifulSoup(splitted[1], "html.parser").string)
        else:
            tag_dict['misc'].append(tag)

    def add_field(ex_tag):
        if tag_dict[ex_tag]:
            em.add_field(name=ex_tag, value=', '.join(tag_dict[ex_tag]))

    add_field("male")
    add_field("female")
    add_field("parody")
    add_field("character")
    add_field("misc")
    return em


# make a markdown hyperlink
def create_markdown_url(message, url):
    return "[" + BeautifulSoup(message, "html.parser").string + "](" + url + ")"


# make a EH url from it's gid and token
def create_ex_url(gid, g_token):
    return "https://exhentai.org/g/" + str(gid) + "/" + g_token + "/"


# crude, but using Docker so ¯\_(ツ)_/¯
def logger(message, contents):
    print(contents)



async def isupdate():
    await client.wait_until_ready()
    time_count = 0
    while True:
        if time_count % 10 == 0:

            check_update()

            chh = c.execute("SELECT ID,STATE from ANIME")
            for row in chh:
                if row[1] == '1':
                    idd = row[0]
                    chh2 = c.execute("SELECT NAME,VOL,URL from ANIME where ID=" + str(idd))
                    for row2 in chh2:
                        upname = row2[0]
                        upvol = row2[1]
                        upurl = "https://ani.gamer.com.tw/animeVideo.php?sn="+row2[2]
                    await client.send_message(client.get_channel('384320278395879426'),'更新通知\n' + upname + ' 已更新' + upvol + '\n' +upurl)

                    db.execute("UPDATE ANIME SET STATE =? where ID=?",('0',str(idd)))
                    db.commit()

        time_count += 1
        await asyncio.sleep(60) # task runs every 60 seconds



client.loop.create_task(isupdate())
#client.run(earbot)
client.run('token')
