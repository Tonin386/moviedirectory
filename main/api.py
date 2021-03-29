from django.utils.translation import get_language
import urllib, urllib.parse, urllib.request
from unidecode import unidecode
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
	url += "i=" + urllib.parse.quote(md_id);
	if plot:
		url += "&plot=full"
	if md_type != "none":
		url += "&type=" + md_type

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())
	logger.info(response)

	if response['Response'] == 'True':
		response['poster_path'] = get_poster(md_id)
		response['media_type'] = "movie"
		response['release_date'] = response['Year']
		response['title'] = response['Title']
		response['imdbid'] = md_id

	return response

def make_request_by_title(md_title, plot, md_type="none"): #Returns array with request answer
	print("make_request_by_title called")
	url = "http://www.omdbapi.com/?apikey="
	key = config.get('imdb_api', 'key')
	url += key + "&"
	url += "t=" + md_title
	if plot:
		url += "&plot=full"
	if md_type != "none":
		url += "&type=" + md_type 

	url = url.replace(" ", "%20")
	url = unidecode(url)

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())
	logger.info(response)

	return response

def make_request_multilang_title_search(md_title, page=1):
	print("make_request_multilang_title_search called")
	language = get_language()
	key = config.get('tmdb_api', 'key')
	query = md_title
	url = "https://api.themoviedb.org/3/search/multi?query=%s&api_key=%s&language=%s&include_adult=false&page=%d" % (query, key, language,page)

	url = url.replace(" ", "%20")
	url = unidecode(url)

	f = urllib.request.urlopen(url)
	response = json.loads(f.read())
	logger.info(response)

	if response["results"] != []:
		if int(response["total_pages"]) > page and page < 5:
			response["results"] += make_request_multilang_title_search(md_title, page+1)['results']

	return response

def make_request_search(md_title, md_type="none", page=1):
	print("make_request_search called")

	response = {}

	md_title = urllib.parse.quote(md_title)

	id_response = make_request_by_id(md_title, 0)
	if id_response['Response'] == 'True':
		response['Search'] = {}
		response['Search']['results'] = [id_response]
	else:
		response['Search'] = make_request_multilang_title_search(md_title)
		for i in range(0, len(response['Search']['results'])):
			response['Search']['results'][i]['imdbid'] = get_imdb_id(response['Search']['results'][i]['id'], response['Search']['results'][i]['media_type'])


	return response

def get_titles(imdb_id):
	print("get_titles called")
	key = config.get('tmdb_api', 'key')
	languages = ['fr-FR', 'de-DE', 'ru-RU', 'en-US']
	translations = {}
	for language in languages:
		url = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=%s&external_source=imdb_id" % (imdb_id, key, language)
		response = json.loads(urllib.request.urlopen(url).read())
		return_key = ""
		key_type = ""
		if response['movie_results'] != []:
			return_key = "movie_results"
			key_type = "title"
		elif response['tv_results'] != []:
			return_key = "tv_results"
			key_type = "name"

		translations[language] = response[return_key][0][key_type]
		translations["original_title"] = response[return_key][0]['original_' + key_type]

	return translations

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

def get_imdb_id(movie_id, media_type):
	print("get_imdb_id called")
	key = config.get('tmdb_api', 'key')
	url = "https://api.themoviedb.org/3/%s/%d/external_ids?api_key=%s" % (media_type, movie_id, key)

	imdb_id = json.loads(urllib.request.urlopen(url).read())['imdb_id']

	return imdb_id