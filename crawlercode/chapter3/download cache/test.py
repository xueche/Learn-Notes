import urlparse

url = 'http://example.webscraping.com/places/default/index/2'
components = urlparse.urlparse(url)
print components.scheme, '\n', components.netloc, '\n', components.path, '\n', \
    components.params, '\n', components.query, '\n', components.fragment