#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from lxml import html
import requests
from bs4 import BeautifulSoup
import datetime
import urllib
import hashlib
import csv
from time import sleep
import unicodecsv

class Scraper:

    def __init__(self):
        self.base_url = "http://websta.me/tag/{0}"

        self.expressions = {
            'images': '//a[@class="mainimg"]//img/@src',
            'post_count': '//p[@class="tag_photo_count"]/text()',
            'wrapper': '//div[@class="photoeach clearfix"]/*',
            'username': '//a[@class="username"]/text()',
            'comment': './div[@class="commentbox"]//strong',
            'hashtag': './div[@class="commentbox"]//strong//a',
            'profile_picture': './a[@class="profimg"]'
        }

    def scrape(self, tag):
        url = self.base_url.format(tag)
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data)

        for link in soup.find_all('a'):
            print(link.get('href'))

    def start_scraping(self, tag, verbose=False):
        url = self.base_url.format(tag)
        page = requests.get(url)
        print page.status_code
        # Raw data
        tree = html.fromstring(page.text)

        # Total post count
        total_posts = tree.xpath(self.expressions['post_count'])

        elements = tree.find_class("photoeach clearfix")
        for element in elements:
            username = element.find_class('username')[0].text
            fullname = element.find_class('fullname')[0].text
            type = element.find_class('filter')[0].text
            comment = element.xpath(self.expressions['comment'])[0].text
            hashtags = [tag.text.encode('utf-8') for tag in element.xpath(self.expressions['hashtag'])]

            # Profile picture
            profile_picture_url = element.find_class('profimg')[0].xpath('./img/@src')[0]
            profile_picture_file_name = self.save_image(profile_picture_url, 'profile_pictures')

            # Photo
            photo_url = element.find_class('mainimg')[0].xpath('./img/@src')[0]
            photo_file_name = self.save_image(photo_url, 'photos', resolution='high')

            likes = element.find_class('likes')
            time_since_raw = element.find_class('time')[0].text
            time_parsed = str(self.parse_time(time_since_raw))
            # Location
            location_name = element.find_class('location')
            if len(location_name) >= 1:
                location_name = location_name[0].xpath('./a')[0].text
            else:
                location_name = ''

            # Likes
            if len(likes) >= 1:
                likes = [like.text.encode('utf-8') for like in likes[0].xpath('./ul//li//a')]
            else:
                likes = ''

            data = [username, fullname, type, comment, hashtags, profile_picture_url, profile_picture_file_name,
                               photo_url, photo_file_name, likes, time_since_raw, time_parsed, location_name]

            data = ['' if obj==None else data for obj in data]
            self.write_to_file(data, "rf15")
            if verbose:
                print '='*4 + ' NEW PHOTO ' + '='*4
                print "Username: {0}".format(username)
                print "Full name: {0}".format(fullname)
                print "Type: {0}".format(type)
                print "Hashtags: {0}".format(hashtags)
                print "Profile picture url: {0}".format(profile_picture_url)
                print "Picture url: {0}".format(photo_url)
                print "Likes: {0}".format(likes)
                print "Time since: {0}".format(time_since_raw)
                print "Parsed time: {0}".format(time_parsed)
                print "Location name: {0}".format(location_name)



        if verbose:
            print "Total posts: {0}".format(total_posts)

    def parse_time(self, raw_time):
        if 'min' in raw_time:
            return datetime.datetime.now() - datetime.timedelta(minutes=int(raw_time[:-3]))
        elif 'h' in raw_time:
            return datetime.datetime.now() - datetime.timedelta(hours=int(raw_time[:-1]))

    def save_image(self, url, folder, resolution=None):

        # If resolution is set, change the url parameter
        if resolution == 'medium':
            url = url.replace('s320x320', 'm640x640')
        elif resolution == 'high':
            url = url.replace('s320x320', 'l1280x1280')

        hex = hashlib.md5()
        hex.update(url)
        name = hex.hexdigest()
        urllib.urlretrieve(url, "{path}/{filename}.jpg".format(path=folder, filename=name))
        return name

    def write_to_file(self, data, tag):
        file = 'csvs/' + str(tag) +'.csv'
        with open(file, 'w') as fp:
            a = unicodecsv.writer(fp, delimiter=str(','), encoding='utf-8')
            a.writerow(data)

    def start(self):
        tags = []
        stop = False
        while stop:
            tag = raw_input('Please input tag to scrape')
            stop = True if tag.lower() == "no" else tags.append(tag)


scraper = Scraper()

while True:
    scraper.start_scraping("rf15", verbose=True)
    sleep(2)