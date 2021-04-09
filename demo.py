from twitscraper import TwitScraper

def main():
	scraper = TwitScraper(['HOGE.X', 'Doesnt exist', 'SAFEMOON.X', 'Fake'], False)
	scraper.hydrate()
	for symbol in scraper.symbols():
		scraper.print_sentiment_volume(symbol)
		scraper.print_twits(symbol)

if __name__ == '__main__':
	main()