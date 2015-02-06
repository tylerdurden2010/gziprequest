from libmproxy import controller, proxy
import os,re
import zlib
noresult = "(\.jpg|\.gif|\.png|\.css|\.js$|\.ico)"

filter = re.compile(noresult,re.IGNORECASE)

class Record(controller.Master):
#file name 
    nametail = 0
    def __init__(self, server):
        controller.Master.__init__(self, server)
        self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        #hid = (msg.host, msg.port)
        #print msg.host
        if msg.headers["Content-Encoding"] == ['gzip']:
            #print msg.headers["Content-Encoding"]
            postdata = self.Encode_Request_Body(msg.content)
        else:
            postdata = str(msg.content)

        body = str(msg.method) + " "+ str(msg.path) + " HTTP/1.1\r\n" + str(msg.headers) + "\r\n" + postdata + "\r\n"
        #print body
        if( self.Noporxy_request(msg.path) ):
            pass
        else:
            #self.Record_request(body,self.nametail,msg.host)
            print postdata
        

        msg.reply()
    def handle_response(self,msg):
        print msg.content
        msg.reply()

    def Record_request(self,content,nametail,hostname):
        filename = "/tmp/request."+hostname+'.'+str(Record.nametail)
        Record.nametail = Record.nametail + 1
        try:
            file = open(filename,"a")
            file.write(content)
            file.flush()
            
        except IOError,args:
            pass
        file.close()
    

    def Noporxy_request(self,url):
        oururl = str(url)
        result = filter.search(url)
        return result

    def Decode_Request_Body(self,data):
        if(not data):
            return ""
        return zlib.decompress(data,16+zlib.MAX_WBITS)
    
    def Encode_Request_Body(self,data):
        if(not data):
            return ""
        return zlib.compress(data,zlib.Z_BEST_COMPRESSION)

config = proxy.ProxyConfig(cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"))


server = proxy.ProxyServer(config, 8089)
m = Record(server)
m.run()