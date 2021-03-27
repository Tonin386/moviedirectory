import urllib, urllib.parse, urllib.request
from pprint import pprint
import configparser
import logging
import json

logger = logging.getLogger('movie_api')

config = configparser.ConfigParser()
config.read('config.ini')

def make_request_by_id(md_id, plot, md_type="none"): #Returns array with request answer
	print("make_request_by_id called")
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
	logger.info(response)

	response['Poster'] = get_poster(md_id)

	return response

def make_request_by_title(md_title, plot, md_type="none", year=-1): #Returns array with request answer
	print("make_request_by_title called")
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
	logger.info(response)

	# response['Poster'] = get_poster(response['id'])

	return response

def make_request_search(md_title, md_type="none", page=1, year=-1):
	print("make_request_search called")
	url = "http://www.omdbapi.com/?apikey="
	key = config.get('imdb_api', 'key')
	url += key + "&"
	url += "s=" + urllib.parse.quote(md_title)
	url += "&page=" + str(page)
	if md_type != "none":
		url += "&type=" + md_type 
	if year != -1:
		url += "&y=" + str(year)

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())
	logger.info(response)

	if "Search" in response.keys():
		if int(response['totalResults']) > len(response['Search']) + 10 * (page-1):
			response['Search'] += make_request_search(md_title, page=page+1)['Search']

	return response

def get_poster(imdb_id):
	print("get_poster called")
	key = config.get('tmdb_api', 'key')
	url = "https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id" % (imdb_id, key)
	response = json.loads(urllib.request.urlopen(url).read())
	return_key = ""
	if response['movie_results'] != []:
		return_key = "movie_results"
	elif response['tv_results'] != []:
		return_key = "tv_results"
	else:
		return "None"
	
	return "http://image.tmdb.org/t/p/original" + response[return_key][0]['poster_path']

def get_translated_plots(imdb_id):
	print("get_translated_plots called")
	key = config.get('tmdb_api', 'key')
	languages = ['fr-FR', 'de-DE', 'ru-RU', 'en-US']
	translations = {}
	for language in languages:
		url = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=%s&external_source=imdb_id" % (imdb_id, key, language)
		response = json.loads(urllib.request.urlopen(url).read())
		return_key = ""
		if response['movie_results'] != []:
			return_key = "movie_results"
		elif response['tv_results'] != []:
			return_key = "tv_results"

		translations[language] = response[return_key][0]['overview']

	return translations