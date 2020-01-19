import urllib, urllib.parse, urllib.request
from pprint import pprint
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')

def make_request_by_id(md_id, plot, md_type="none"): #Returns array with request answer
	url = "http://www.omdbapi.com/?apikey="
	key = config.get('imdb_api', 'key')
	url += key + "&"
	url += "i=" + md_id;
	if plot:
		url += "&plot=full"
	if md_type != "none":
		url += "&type=" + md_type 

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())

	return response

def make_request_by_title(md_title, plot, md_type="none", year=-1): #Returns array with request answer
	url = "http://www.omdbapi.com/?apikey="
	key = config.get('imdb_api', 'key')
	url += key + "&"
	url += "t=" + md_title
	if plot:
		url += "&plot=full"
	if year != -1:
		url += "&y=" + str(year)
	if md_type != "none":
		url += "&type=" + md_type 

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())

	return response

def make_request_search(md_title, md_type="none", page=1, year=-1):
	url = "http://www.omdbapi.com/?apikey="
	key = config.get('imdb_api', 'key')
	url += key + "&"
	url += "s=" + md_title
	url += "&page=" + str(page)
	if md_type != "none":
		url += "&type=" + md_type 
	if year != -1:
		url += "&y=" + str(year)

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())

	return response