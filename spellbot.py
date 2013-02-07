import twython
import random
import urllib2
import clamlib
import time
import xml.dom.minidom as xml
import cgi
import random
import sys

def search_tweets(query,api = None):
    """Returns some tweets with this query""";

    if api == None:
        api = twython.Twython();

    results = api.search(q=query)['statuses'];

    return results;

def find_errors(webservice,tweet,username,password):
    fowlt = clamlib.Connection("http://webservices-lst.science.ru.nl/"+webservice,username,password);
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

            try:
                confidence = float(j.getAttribute('confidence'));
            except ValueError:
                confidence = 0.0;

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

            try:
                confidence = float(i.getAttribute('confidence'));
            except ValueError:
                confidence = 0.0;

            output_corrections.append({'original':original_text.strip(),'suggestion':correction.strip(),
                                           'confidence':confidence});
            
    return output_corrections;

def generate_response(responses,username,original,correction):
    """Generates a response out of a correction""";

    responses = open(responses,'r').readlines();
    return random.choice(responses).replace('$u',username).replace('$o',original).replace('$c',correction);    

def get_passwords(filename):

    lines = open(filename,'r').readlines();
    passwords = {};

    for n,i in enumerate(lines):
        if i[0] == '#':
            passwords[i[1:].strip()] = lines[n+1].strip();

    return passwords;

def clean_tweet(tweet,severity=2):
    """Removes links, hastags, smilies, addressees""";

    result = tweet.replace('\n','');

    if severity > 1:
        triggers = ['@','#','http',':',';'];

        words = result.split();
        clean_words = [];

        for i in words:
            found_trigger = False;
            
            for j in triggers:
                if j in i:
                    found_trigger = True;
                    break;

            if found_trigger:
                continue;

            clean_words.append(i);

            result = ' '.join(clean_words);

    return result;

######## Scripts starts here ############################3

try:
    webservice = sys.argv[1];
    queries = sys.argv[2];
    responses = sys.argv[3];
    passwords = sys.argv[4];
    check_confidence = sys.argv[5];
except:
    print('spellbot.py [webservice] [queries] [responses] [passwords] [check_confidence (y/n)]');
    sys.exit('Quit');

passwords = get_passwords(passwords);

api = twython.Twython(app_key=passwords['app_key'],
            app_secret=passwords['app_secret'],
            oauth_token=passwords['oauth_token'],
            oauth_token_secret=passwords['oauth_token_secret'])

#Look for tweets for all queries
queries = open(queries,'r');
for q in queries:    
    q = q.strip();
    print('Looking for tweets with',q);
    if len(q) > 0:
        tweets = search_tweets(q,api);

    found_error = False;

    #Check all tweets for errors
    for tweet in tweets:
        errors = find_errors(webservice,clean_tweet(tweet['text']),passwords['fowlt_username'],passwords['fowlt_password']);

        #See if errors were found
        if len(errors) > 0:

            error = errors[0];

            for error in errors:
                print(error['confidence']);                
                #If confident enough, tweet the result in a random format
                if error['confidence'] > .98 or check_confidence == 'n':
                    found_error = True;

                    #response = generate_response('@'+tweet['user']['screen_name'],error['original'],error['suggestion'])
                    response = generate_response(responses,'@...',error['original'],error['suggestion'])
                    api.updateStatus(status=response);

                    print(tweet['text']);
                    print(response);
                    break;

        if found_error:
            break;
