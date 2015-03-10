import urllib
import urllib2
import time
from bs4 import BeautifulSoup
import random


# Magic Constants
URL_SEARCH = ['http://www.google.de/search?',
              'http://ajax.googleapis.com/ajax/services/search/web?']
VALUES = {'q': '',  # We will put our query string here later
          'ie': 'UTF-8',
          'hl': 'en',
          'safe': 'off'}
BROWSERS = (
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.48 Safari/525.19',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648)',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.5) Gecko/2008121621 Ubuntu/8.04 (hardy) Firefox/3.0.5',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-us) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
)
# Google dislike being browsed by programs

EMPTY_QUERIES = set(['"', '""', ''])



def _real_search(query, url=URL_SEARCH[0], values=VALUES, browsers=BROWSERS):
    # add the query term to the values
    # potential point of failure when extending to other search engines
    values['q'] = query

    data = urllib.urlencode(values)

    request = urllib2.Request(url + data)

    request.add_header('User-Agent', random.choice(browsers))  

    response = urllib2.urlopen(request)

    html = response.read()  # this should be the required html page

    response.close()

    return html


def search(query, literal):
    """
    This function is specfic to search on Google
    that is, this will require changes for other search engines
    or if google decides to do something crazy

    input: string
    literal: if True, *will convert* the string to a literal string, else normal
    output: int
    """
    if query in EMPTY_QUERIES:
        return "EMPTY QUERY"

    if literal:
        if query[0] != '"':
            query = '"' + query

        if query[-1] != '"':
            query = query + '"'

    html_result = _real_search(query)

    soup = BeautifulSoup(html_result)
    result_stat_tag = soup.find(id='resultStats')  # Magic Constant

    """
    sample result_stat_tag
    >>> <div class="sd" id="resultStats">About 47,100,000 results</div>

    """

    stat = result_stat_tag.string.split(' ')[1]

    return int(stat.replace(',', ''))  # remove commas and make into int

def search_from_file(file_path, literal, separator=',', out_ext='.txt', sleep=True):
    """
    no error handling here
    
    file_path has to be absolute/complete path to the file

    expecting input file at path file_path; with data as "<query>" on each line
    and considers each line to be one query. 
    if double qoutes are not there, they will be added automgically
    
    file_path: string; *full path to file with extension*
    literal: if True, *will convert* the string to a literal string, else normal
    separator: set to set separator for file
    out_ext: extension of output file (no gaurantee for fancy files)
    output: None

    """
    file_in_name = ''
    with open(file_path, "r+") as file_in:
        queries = file_in.read().splitlines()
        file_in_name = file_in.name

    # fancy file_out naming; set your own if causing problems
    file_out_name = file_in_name[: len(file_in_name) - len(file_in_name.split('.')[-1]) -1 ] \
                     + "_out" + out_ext


    # Calculate time to sleep
    if sleep:
        print ""
        print "The program will execute with random sleeps"
        print "Since Google doesn't like robots, this trick might work"
        print ""
        print "Estimated minimum execution time for the input : %s seconds"%str(len(queries) * 5)
        print ""
        sleep_time = raw_input("If you can wait that long, press ENTER, else input some time in seconds ")
        if sleep_time == '':
            sleep_time = 5
        else:
            for num_tries in range(5):
                try:
                    if sleep_time == '':
                        sleep_time = 5
                    else:
                        sleep_time = int(sleep_time) / float(len(queries))
                    break
                except ValueError:
                    print "Please enter a valid string, or press ENTER to continue with default"
                    sleep_time = raw_input("You have %s tries left "%(5 - num_tries))

    print ""
    print "Running"

    query_count_pairs = []
    for i, query in enumerate(queries):
        search_count = search(query, literal=literal)
        query_count_pairs.append(query + separator + str(search_count))
        time.sleep(sleep_time * random.choice([0, 1]))

    with open(file_out_name, "w") as file_out:
        file_out.write('\n'.join(query_count_pairs))

    print ""
    print "Done"
    print "Output file saved at: "
    print file_out_name

