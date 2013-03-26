import praw
import clamlib
import random
import time
import xml.dom.minidom as xml
import cgi

def find_errors(webservice,tweet,username,password):

    fowlt = clamlib.Connection("http://webservices-lst.science.ru.nl/"+webservice,username,password);
    fowlt.start_project('redditbot'+str(random.randrange(10000)));
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

def get_passwords(filename):

    lines = open(filename,'r').readlines();
    passwords = {};

    for n,i in enumerate(lines):
        if i[0] == '#':
            passwords[i[1:].strip()] = lines[n+1].strip();

    return passwords;

def generate_response(responses,username,original,correction):
    """Generates a response out of a correction""";

    responses = open(responses,'r').readlines();
    return random.choice(responses).replace('$u',username).replace('$o',original).replace('$c',correction);    

def add_footer(message):
    """Adds a general footer to explain the bot""";

    return message + '\n---\n^This ^is ^a ^bot ^that ^corrects ^spelling. ^For ^more ^info, ^see [^this ^webpage](http://www.fowlt.net/redditbot)^.'; 

def correct_titles(thread,prefab_errors):
    """Tries to find errors in the title and posts them if certain enough""";

    title = thread.title;
    op = thread.author;

    found_possible_error = False;
    for i in prefab_errors:
        if i in title:
            found_possible_error = True;
            break;

    if not found_possible_error:
        return;

    errors = find_errors('fowlt',title,passwords['fowlt_username'],passwords['fowlt_password']);
	    
    for i in errors:
        if i['confidence'] > .97 and i['original'] in prefab_errors:
            response = generate_response('/scratch/wstoop/spellbot/responses-redditbot.txt',str(op),i['original'],i['suggestion']);

            print(title);
            print(response);

#            thread.add_comment(add_footer(response));

            break;

def correct_comments(thread,prefab_errors):
    """Tries to find errors in the comments and posts them if certain enough""";

    try:
        print '# Searching in thread '+str(thread.title);
    except UnicodeEncodeError:
        return;   

    first_level_comments = thread.comments;

    for i in first_level_comments[:50]:
        try:
            author = i.author;
            message = i.body;
        except AttributeError:
            print('#  Problem, skipping');
            continue;

        found_possible_error = False;
        for j in prefab_errors:
            if j in message:
                found_possible_error = True;
                break;

        if found_possible_error == False or str(author) == 'fowlt':
            print('#  Skipping comment');
            continue;

        print('#  Checking comment for errors because of '+j);

        errors = find_errors('fowlt',message,passwords['fowlt_username'],passwords['fowlt_password']);  

        for j in errors:
            if j['confidence'] > .97 and j['original'] in prefab_errors:
                response = generate_response('/scratch/wstoop/spellbot/responses-redditbot.txt',str(author),j['original'],j['suggestion']);
    
                print(message);
                print(response);

#                i.reply(add_footer(response));
    
                break;

        second_level_comments = i.replies;

        for j in second_level_comments:

            try:
                author = j.author;
                message = j.body;
            except AttributeError:
                print('#  Problem, skipping');
                continue;

            found_possible_error = False;
            for k in prefab_errors:
                if k in message:
                    found_possible_error = True;
                    break;

            if not found_possible_error or str(author) == 'fowlt':
                print('#  Skipping comment');
                continue;
    
            print('#  Checking comment for errors because of '+k);

            errors = find_errors('fowlt',message,passwords['fowlt_username'],passwords['fowlt_password']);
	    
            for k in errors:
                if k['confidence'] > .97 and k['original'] in prefab_errors:
                    response = generate_response('/scratch/wstoop/spellbot/responses-redditbot.txt',str(author),k['original'],k['suggestion']);
    
                    print(message);
                    print(response);

#                   j.reply(add_footer(response));
    
                    break;
            

############ Scripts #################

passwords = get_passwords('/scratch/wstoop/spellbot/passwords.txt');
errors = open('/scratch/wstoop/spellbot/errors-redditbot.txt').readlines();
errors = [i.strip() for i in errors];

#Log in
reddit = praw.Reddit(user_agent='Fowlt bot v1.0');
reddit.login('fowlt','F0wlty');
print('# Logged in');

#Get thread titles for all subreddits
subreddits = open('/scratch/wstoop/spellbot/subreddits.txt','r');

for i in subreddits:

    print('# Checking subreddit: '+i.strip());

    subreddit = reddit.get_subreddit(i.strip());
    for thread in subreddit.get_hot(limit=20):

        correct_titles(thread,errors);
        correct_comments(thread,errors);

    subreddit = reddit.get_subreddit(i.strip());
    for thread in subreddit.get_top_from_hour(limit=20):
        
        correct_titles(thread,errors);
        correct_comments(thread,errors);

#Bijhouden welke threads al gehad

