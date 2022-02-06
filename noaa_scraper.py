#link to libraries neede by this notebook
import os
import numpy as np

from html.parser import HTMLParser  
from urllib import parse
from urllib.request import urlopen  
from urllib.request import urlretrieve

#following are needed for the progress bar
from ipywidgets import FloatProgress
from IPython.display import display

#use glob to download filenames from a directoery
from glob import glob

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        if 'text/html' in response.getheader('Content-Type'):
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return '',self.links #htmlString, self.links
        if 'text/plain' in response.getheader('Content-Type'):
            return url,[]
        else:
            return "",[]

# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def noaa_spider(url, word, maxPages):  
    if not os.path.isdir('data'):
        os.mkdir('data')
        
    pagesToVisit = [url]
    textfiles = [];
    numberVisited = 0
    foundWord = False
    urlsVisited = set() 
    foundFiles = set()

    progressBar = FloatProgress(min=0, max=maxPages)
    display(progressBar)
    progressBar.value = 0
    
    # The main loop. Create a LinkParser and get all the links on the page.
    # Also search the page for the word or string
    # In our getLinks function we return the web page
    # (this is useful for searching for the word)
    # and we return a set of links from that web page
    # (this is useful for where to go next)
    while numberVisited < maxPages and pagesToVisit != [] and not foundWord:

        # Start from the beginning of our collection of pages to visit:
        url = pagesToVisit[0]
        
        pagesToVisit = pagesToVisit[1:]
        #try:
            #print(numberVisited, "Visiting:", url)
        parser = LinkParser()

        if url not in urlsVisited:
            urlsVisited.add(url)
            if '.txt' in url:
                if word in url:
                    textfiles = textfiles + [url]
                    foundFiles.add(url)
                    print("FOUND ", url)
                    name='./data/'+url.split('/')[-1]
                    
                    if not os.path.isfile(name):
                        print('downloading...',name)
                        urlretrieve(url,name)
                    else:
                        print('file exists...',name)
            else:
                numberVisited = numberVisited +1
                progressBar.value = numberVisited
                data, links = parser.getLinks(url)  
                # Add the pages that we visited to the end of our collection
                # of pages to visit:
                pagesToVisit = pagesToVisit + links
    return foundFiles

def read_data_column(filename, col=8):
    f = open(filename, 'r')
    filename
    air_temperature = []
    for row in f:
        data = row.split()
        temp = float(data[col])
        if(temp < -9000): # Check for valid data
            #print('IsNan')
            if(air_temperature == []): # First point in serise
                temp = 0 
            else:
                temp=air_temperature[-1] #Repeat previous data point
        else:
            temp = temp*9.0/5.0+32
        if(temp != []):
            air_temperature.append(temp)
    f.close()
    return air_temperature

def get_airtemperature_from_files():
  #Read all Tif images in current directory

  files = glob('./data/*.txt');
  files.sort();
  progressBar = FloatProgress(min=0, max=len(files))
  display(progressBar)
  progressBar.value = 0
  air_temperature = []
  for filename in files:
      progressBar.value = progressBar.value + 1
      print('reading...',filename)
      air_temperature = air_temperature + read_data_column(filename)

  return air_temperature

def get_noaa_temperatures(url, name, maxdepth=100):
  #Now call the main noaa_spider function and search for the word hpc
  files = noaa_spider(url, name, 100)  
  return get_airtemperature_from_files()

print(f"running as {__name__}")
