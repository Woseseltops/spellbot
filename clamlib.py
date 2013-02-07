import urllib, urllib2
import xml.dom.minidom as xml

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
        self.project_name = name;
        request = urllib2.Request(self.url + '/' + name)
        request.get_method = lambda: 'PUT'
        self.opener.open(request)

    def upload_text(self,name,text):
        self.name = name;
        request = urllib2.Request(self.url + '/'+ self.project_name +'/input/'+name);
        try:
            data = urllib.urlencode({'inputtemplate':'textinput','contents':text});
            self.opener.open(request,data)
            return True;
        except UnicodeEncodeError:
            return False;            

    def start_webservice(self,arguments):
        request = urllib2.Request(self.url + '/' + self.project_name + '/');
        data = urllib.urlencode(arguments);
        self.opener.open(request,data)

    def __getattr__(self,ready):
        request = urllib2.Request(self.url + '/' + self.project_name + '/');
        result = self.opener.open(request);
        total = '';
        for i in result:
            total += i;

        #Get completion from status element from xml
        elem = xml.parseString(total).getElementsByTagName('status')[0].getAttribute('completion');            
        if int(elem) > 98:
            return True;
        else:
            return False;

    def get_results(self):
        request = urllib2.Request(self.url + '/'+ self.project_name + '/output/' + self.name[:-3]+'xml');        
        result = self.opener.open(request);        

        total = '';
        for i in result:
            total += i;

        return total;

    def delete_project(self):
        
        request = urllib2.Request(self.url + '/' + self.project_name + '/')
        request.get_method = lambda: 'DELETE'
        self.opener.open(request)
