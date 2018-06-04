#!/usr/bin/python

# Shitpostbot 5000 is a bot that finds all the files in a target slack instance, 
# gets all the ones older than one week, posts them to a target instagram, and 
# then deletes them from slack. 
#
# This was created to manage the "running out of space for files" problem on the
# Totenkitten Empire Slack. Hail the Eternal Empire! For Glory and Empire!

# sudo -H pip install slacker
from slacker import Slacker
#sudo -H pip install instagram-python
from InstagramAPI import InstagramAPI

#This file isn't in source control for some very obvious reasons. It looks like this:
# #Instagram user and password
# insta_user = 
# insta_pwd = 
#
# #Slack username and password
# slack_token = 
# Only, you know, with passwords in it

import passwords

import time
import datetime
import pprint
import requests
import shutil
import os
from PIL import Image, ImageOps

# Stolen from https://github.com/kfei/slack-cleaner/blob/master/slack_cleaner/utils.py
class TimeRange():
	def __init__(self, start_time, end_time):
		def parse_ts(t):
			try:
				_time = time.mktime(time.strptime(t, "%Y%m%d"))
				return str(_time)
			except:
				return '0'
		
		self.start_ts = parse_ts(start_time)
		# Ensure we have the end time since slack will return in different way
		# if no end time supplied
		self.end_ts = parse_ts(end_time)
		if self.end_ts == '0':
			self.end_ts = str(time.time())


#Log into slack, return a slack instance for getting the files
def init_slack():
	slack = Slacker(passwords.slack_token)
	return slack

def init_insta():
	ig_api = InstagramAPI(passwords.insta_user, passwords.insta_pwd)
	ig_api.login()
	return ig_api

def get_slack_file(url, fname):
	auth_payload = {"Authorization":"Bearer {}".format(passwords.slack_token)}
	r = requests.get(url, headers=auth_payload, stream=True)
	if r.status_code == 200:
		with open(fname, 'wb') as outfile:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, outfile)
		return True
	return False

def put_ig_file(instagram, fname, cap="Uploaded by Shitpostbot 5000! Confusion to our Enemies!"):
	file = "resized_{}".format(fname)

	#Pad and resize to fit on Instagram
	with Image.open(fname) as img:
		width, height = img.size
		new_size = max(width, height)
		delta_w = new_size - width
		delta_h = new_size - height
		new_im = ImageOps.expand(img, (delta_w//2, delta_h//2, delta_w-(delta_w//2), delta_h-(delta_h//2)))
		new_im = new_im.resize([1024,1024], Image.ANTIALIAS)	
		new_im.save(file)

	#Put it on Instagram
	retval = ig.uploadPhoto(file, caption=cap)

	#Clean up
	os.remove(fname)
	os.remove(file)

	return retval

if __name__ == '__main__':

	pp = pprint.PrettyPrinter(indent=4)
	
	slack = init_slack()
	ig = init_insta()

	#Set up a time range of "older than one week"
	one_week_ago = datetime.datetime.now() - datetime.timedelta(weeks=1)
	one_week_ago = one_week_ago.strftime("%Y%m%d")

	time_range = TimeRange(None, one_week_ago)

	#Get a list of channels to prevent posting stuff from #nyan11
	res = slack.channels.list().body
	banned = ["nyan11"]
	banned_ids = []
	if res["ok"]:
		for channel in res["channels"]:
			if channel['name'] in banned:
				banned_ids.append(channel['id'])

	#Get the file list
	has_more = True
	while has_more:
		res = slack.files.list(user=None, ts_from=time_range.start_ts, ts_to=time_range.end_ts, types="images", page=1).body

		#Check for an OK response
		if res["ok"]:
			#See how many pages of files we have
			files = res['files']
			current_page = res['paging']['page']
			total_pages = res['paging']['pages']
			print "Processing page {} of {}".format(current_page, total_pages)
			has_more = current_page < total_pages
			page = current_page + 1

			#For every file
			for f in files:
				#If it's not in a banned channel
				for channel in f["channels"]:
					if channel not in banned_ids:
						#Now we see about posting it to IG and deleting it
						resp = get_slack_file(f["url_private"], f['name'])
						if resp:
							
							comment = "From Shitpostbot 5000!"
							try:
								comment = f["initial_comment"]["comment"]
							except:
								#Probably a keyerror, do nothing
								pass

							#Always returns false, but throws an exception if it fails	
							put_ig_file(ig, f['name'], comment)

							try:
								slack.files.delete(f['id'])
							except:
								print "Failed to delete:"
								pp.pprint(f)
								sys.exit(-1)
							

		elif not res["ok"] and res["headers"]["Retry-After"]:
			#Rate limited, delay and retry
			delay = int(res["headers"]["Retry-After"])
			delay += 2 #Just to be sure
			print "Rate limited, retrying in {} seconds".format(delay)
			time.sleep(delay)
		
		else:
			#Unknown error
			print "Slack done fucked up."
			pp.pprint(res)
			sys.exit(-1)

	#Only care about image file types for instagram

	#For each file in the file list

	#Post to instagram

	#If instagram post successful, delete the file
