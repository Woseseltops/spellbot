import urllib, urllib2

class Connection():
    """Creates an authorized session for CLAM webservices""";

    def __init__(self,url,user,password):

        self.url = url
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm();
        passman.add_password(None, url, user, password);
        authhandler = urllib2.HTTPDigestAuthHandler(passman);
        self.opener = urllib2.build_opener(authhandler);
        urllib2.install_opener(self.opener);

    def start_project(self,name):
        request = urllib2.Request(self.url + '/spellbot')
        request.get_method = lambda: 'PUT'
        self.opener.open(request)

    def upload_text(self,name,text):
        self.name = name;
        request = urllib2.Request(self.url + '/spellbot/input/'+name);
        data = urllib.urlencode({'inputtemplate':'textinput','contents':text});
        self.opener.open(request,data)

    def start_webservice(self):
        request = urllib2.Request(self.url + '/spellbot/');
        data = urllib.urlencode({'sensitivity':'0.5','donate':'1'});
        self.opener.open(request,data)

    def __getattr__(self,ready):
        print('hoi');
        request = urllib2.Request(self.url + '/spellbot/');
        result = self.opener.open(request);
        for i in result:
            print(i);        
