import twython
import random
import urllib2
import clamlib
import time
import xml.dom.minidom as xml
import cgi
import random

def search_tweets(query,api = None):
    """Returns some tweets with this query""";

    if api == None:
        api = twython.Twython();

    results = api.search(q=query)['statuses'];

    return results;

def find_errors(tweet,username,password):
    fowlt = clamlib.Connection("http://webservices-lst.science.ru.nl/fowlt",username,password);
    fowlt.start_project('spellbot'+str(random.randrange(10000)));
    text_uploaded = fowlt.upload_text('input.txt',tweet);

    if text_uploaded:
        fowlt.start_webservice({'sensitivity':'0.5','donate':'1'});

        while not fowlt.ready:
            time.sleep(2);

        results = fowlt.get_results();
        errors = xml_to_errorlist(results);
    else:
        errors = [];

    fowlt.delete_project();

    return errors;

def xml_to_errorlist(inp):

    def get_content(node):

        for j in node.childNodes:
            if j.nodeType == j.TEXT_NODE:
                return cgi.escape(j.data).encode('ascii','xmlcharrefreplace').decode();    

    parsed_data = xml.parseString(inp);
    output_corrections = [];

    words = parsed_data.getElementsByTagName('w');

    #Try to find regular errors
    for i in words:
        original_text = get_content(i.getElementsByTagName('t')[0]);

        corrections = i.getElementsByTagName('correction')
        for j in corrections:
            correction = get_content(j.getElementsByTagName('t')[0]);
            confidence = j.getAttribute('confidence');

            #Manual fix for alot
            if original_text == 'alot':
                correction = 'a lot';

            output_corrections.append({'original':original_text,'suggestion':correction,
                                       'confidence':confidence});
            break;

    corrections = parsed_data.getElementsByTagName('correction');

    #Try to find space errors
    for i in corrections:
        current = i.getElementsByTagName('current');

        if len(current) > 0: #If current is there, this is a space error

            current = current[0].getElementsByTagName('t');
            original_text = '';

            for j in current:
                original_text += get_content(j) + ' ';

            suggestion = i.getElementsByTagName('suggestion');
            suggestion = suggestion[0].getElementsByTagName('t');
            correction = '';

            for j in suggestion:
                correction += get_content(j) + ' ';

            confidence = i.getAttribute('confidence');
            output_corrections.append({'original':original_text.strip(),'suggestion':correction.strip(),
                                           'confidence':confidence});
            
    return output_corrections;

def generate_response(username,original,correction):
    """Generates a response out of a correction""";

    responses = open('responses.txt','r').readlines();
    print('Found possible tweet:');
    print(random.choice(responses).replace('$u',username).replace('$o',original).replace('$c',correction));    

def get_passwords(filename):

    lines = open(filename,'r').readlines();
    passwords = {};

    for n,i in enumerate(lines):
        if i[0] == '#':
            passwords[i[1:].strip()] = lines[n+1].strip();

    return passwords;

##################

passwords = get_passwords('passwords.txt');

api = twython.Twython(app_key=passwords['app_key'],
            app_secret=passwords['app_secret'],
            oauth_token=passwords['oauth_token'],
            oauth_token_secret=passwords['oauth_token_secret'])

#Look for tweets for all queries
queries = open('queries.txt','r');
for q in queries:    
    q = q.strip();
    print('Looking for tweets with',q);
    if len(q) > 0:
        tweets = search_tweets(q,api);

    #Give all tweets to a spellingchecker
#    tweets = [{'text':'I make alot of misakes','user':{'screen_name':'wessel'}},{'text':'spellch ecker','user':{'screen_name':'wessel'}}];

    for tweet in tweets:
        print(tweet['text']);
        errors = find_errors(tweet['text'],passwords['fowlt_username'],passwords['fowlt_password']);
        print(errors);

        if len(errors) > 0:

            error = errors[0];

            #Tweet the result in a random format
            generate_response('@'+tweet['user']['screen_name'],error['original'],error['suggestion']);

#Alleen als heel confident
#Runons en splits gaan nog niet goed
