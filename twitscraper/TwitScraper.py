import time
import json
import re

import requests

# Exception to throw when scraping sentiment and volume fails
class SVScrapeException(Exception): pass

# Exception to throw when scraping twits fails
class TwitScrapeException(Exception): pass


class TwitScraper(object):

	def __init__(self, symbols: list = [], hydrate: bool = False):
		self._sentiment = {}
		self._volume = {}
		self._twits = {}
		self._urls = {
			'sentiment': 'https://stocktwits.com/symbol',
			'messages': [
				'https://api.stocktwits.com/api/2/streams/symbol',
				'https://api.stocktwits.com/api/2/streams/symbol/ric'
			]
		}
		self._symbols = symbols
		if hydrate:
			self.hydrate()

	def symbols(self) -> list:
		"""Return a list of valid symbols"""
		return self._symbols

	def hydrate(self):
		"""Hydrate scraper with sentiment, volume, and twits"""
		invalid = []
		for symbol in self.symbols():
			try:
				self.pull_sentiment_volume(symbol)
			except SVScrapeException as e:
				self._sentiment[symbol] = None
				self._volume[symbol] = None
				print("Error scraping sentiment and volume: %s" % e)
			except Exception as e:
				self._sentiment[symbol] = None
				self._volume[symbol] = None
				print("Error scraping sentiment and/or volume: %s" % e)

			try:
				self.pull_twits(symbol)
			except TwitScrapeException as e:
				self._twits[symbol] = None
				print("Error scraping Twits: %s" % e)
			except Exception as e:
				self._twits[symbol] = None
				print("Error scraping twits: %s" % e)

			
			if self._sentiment[symbol] == None and self._volume[symbol] == None and self._twits[symbol] == None:
				invalid.append(symbol)

		# Remove invalid symbols
		[self._symbols.remove(symbol) for symbol in invalid]
			


	def pull_sentiment_volume(self, symbol: str):
		"""Scrape Sentiment and Volume for `symbol`"""
		data = requests.get("%s/%s" % (self._urls['sentiment'], symbol))
		if data.status_code != 200:
			raise SVScrapeException("Unable to scrape symbol: %s" % symbol)

		matches = re.search(r"\"sentimentChange\"\:(.*)\,\"volumeChange\"\:(.*)\,\"lastUpdated", data.text)
		(self._sentiment[symbol], self._volume[symbol]) = matches.group(1), matches.group(2)

	def pull_twits(self, symbol: str):
		"""Scrape twits for `symbol`"""
		for url in self._urls['messages']:
			data = requests.get("%s/%s.json" % (url, symbol))
			if data.status_code == 200:
				break

		if data.status_code != 200:
			raise TwitScrapeException("Unable to scrape symbol: %s" % symbol)
		
		self._twits[symbol] = json.loads(data.text)['messages']

	def parse_twit(self, twit: dict) -> tuple:
		"""Parse the relevant values out of a given twit"""
		# Keys: 'id', 'body', 'created_at', 'user', 'source', 'symbols',  'conversation', 'links', 'likes', 'reshares', 'mentioned_users', 'entities'
		body = twit['body']
		likes = twit['likes']['total'] if 'likes' in twit.keys() else 0
		username = twit['user']['username']
		return body, likes, username

	def print_twits(self, symbol: str):
		"""Print out the currently stored twits for `symbol`"""
		print('----------------------')
		print("Twits for %s:" % symbol)
		print('----------------------')
		for twit in self._twits[symbol]:
			(body, likes, username) = self.parse_twit(twit)
			print("Message: %s" % body)
			print("Likes: %d" % likes)
			print("Author: %s" % username)
			print('=================================')

	def print_sentiment_volume(self, symbol: str):
		"""Print out the currently stored sentiment and volume for `symbol`"""
		if symbol not in self._sentiment.keys() or symbol not in self._volume.keys(): return
		print('----------------------')
		print("%s Sentiment Change: %s%%" % (symbol, self._sentiment[symbol]))
		print("%s Volume Change: %s%%" % (symbol, self._volume[symbol]))
		print('----------------------')

	def get_twits(self, symbol: str) -> list:
		"""Get list of twits for `symbol`"""
		if symbol in self.symbols() and symbol in self._twits.keys():
			return self._twits[symbol]
		return []

	def get_sentiment_volume(self, symbol: str) -> tuple:
		"""Get sentiment and volume for `symbol`"""
		sentiment = self._sentiment[symbol] if symbol in self.symbols() and symbol in self._sentiment.keys() else ""
		volume = self._volume[symbol] if symbol in self.symbols() and symbol in self._volume.keys() else ""
		return (sentiment, volume)

	def add_symbol(self, symbol: str):
		"""Add new symbol to scrapers list"""
		if symbol not in self._symbols:
			self._symbols.append(symbol)