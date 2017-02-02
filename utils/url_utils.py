import urllib,urllib2

def download_from_url(url,save_path):
	urllib.urlretrieve(url,save_path)