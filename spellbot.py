import twython
import random

def search_tweets(query,api = None):
    """Returns 100 tweets with this query""";

    if api == None:
        api = twython.Twython();

    results = api.search(q='"'+query+'"');

    print(results[:2]);

api = twython.Twython();

def generate_response(username,original,correction):
    """Generates a response out of a correction""";

    responses = open('responses.txt','r').readlines();
    print(random.choice(responses).replace('$u',username).replace('$o',original).replace('$c',correction));    

##################

#Look for tweets for all queries
queries = open('queries.txt','r');
for q in queries:
    print(q);
    search_tweets(q[-1],api);

#Give all tweets to a spellingchecker

#Tweet the result in a random format
generate_response('@antalvdb','your','you\'re');
