import twython
import random
import urllib2
import clamlib
import time
import xml.dom.minidom as xml
import cgi

def search_tweets(query,api = None):
    """Returns 100 tweets with this query""";

    if api == None:
        api = twython.Twython();

    results = api.search(q="#india",rpp="50");

    print(results[:2]);

def find_errors(tweet):

    fowlt = clamlib.Connection("http://webservices-lst.science.ru.nl/fowlt",'wstoop','n3ush00rn');
    fowlt.start_project('spellbot');
    fowlt.upload_text('input.txt',tweet);
    fowlt.start_webservice();

    while not fowlt.ready:
        time.sleep(2);

    results = fowlt.get_results();
    errors = xml_to_errorlist(results);

    fowlt.delete_project();

    return errors;

def xml_to_errorlist(inp):

    def get_content(node):

        for j in node.childNodes:
            if j.nodeType == j.TEXT_NODE:
                return cgi.escape(j.data).encode('ascii','xmlcharrefreplace').decode();    

    parsed_data = xml.parseString(inp);
    words = parsed_data.getElementsByTagName('w');
    output_corrections = [];

    for i in words:
        original_text = get_content(i.getElementsByTagName('t')[0]);

        corrections = i.getElementsByTagName('correction')
        for j in corrections:
            correction = get_content(j.getElementsByTagName('t')[0]);
            output_corrections.append({'original':original_text,'suggestion':correction});
            break;

    return output_corrections;

def generate_response(username,original,correction):
    """Generates a response out of a correction""";

    responses = open('responses.txt','r').readlines();
    print(random.choice(responses).replace('$u',username).replace('$o',original).replace('$c',correction));    

##################

api = twython.Twython();

#Look for tweets for all queries
queries = open('queries.txt','r');
#for q in queries:
#    print(q);
#    search_tweets(q[-1],api);

#Give all tweets to a spellingchecker
tweets = ['I think I understad what your saying']

for tweet in tweets:
    errors = find_errors(tweet);

    if len(errors) > 0:

        error = errors[0];
        #Tweet the result in a random format
        generate_response('@antalvdb',error['original'],error['suggestion']);

#Arguments weg uit clamlib
#Runons en splits gaan nog niet goed
