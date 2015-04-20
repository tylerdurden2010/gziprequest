#!/usr/bin/env python

from libmproxy import controller,proxy
from libmproxy.proxy.server import ProxyServer
import os,re
import zlib
noresult = "(\.jpg|\.gif|\.png|\.css|\.js$|\.ico)"
filter = re.compile(noresult,re.IGNORECASE)
yousitedomain = re.compile('.*\.yousite\.(com|cn)',re.IGNORECASE)
nosocketio = re.compile('\/socket\.io\/',re.IGNORECASE)

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

    def handle_request(self, flow):
        hid = (flow.request.host, flow.request.port)

        if flow.request.headers["Content-Encoding"] == ['gzip']:
            postdata = self.Decode_Request_Body(flow.request.content)
        else:
            if ("application/x-www-form-urlencoded; charset=UTF-8" in flow.request.headers["content-type"]):
                form = flow.request.get_form_urlencoded()
                form = list(form)
                payload = ''
                for i in range(len(form)):
                    payload = form[i][0] + "=" + form[i][1] +"*" + "&" + payload
                postdata = payload.replace('\n','\\n').strip('&')
            else:
                postdata = None

        if postdata:
            body = str(flow.request.method) + " "+ str(flow.request.path) + " HTTP/1.1\r\n" + str(flow.request.headers) + "\r\n" + postdata + "\r\n"
        else:
            body = str(flow.request.method) + " "+ str(flow.request.path) + " HTTP/1.1\r\n" + str(flow.request.headers) + "\r\n"
        if( self.Noporxy_request(flow.request.path,flow.request.host) ):
            pass
        else:
            self.Record_request(body,self.nametail,flow.request.host,flow.request.method,flow.request.path)

        flow.reply()

    def Record_request(self,content,nametail,hostname,method,path):
        filename = "/tmp/autotest/"+str(Record.nametail)+"."+str(method)+"."+hostname+path.replace('/','_')
        Record.nametail = Record.nametail + 1
        try:
            file = open(filename,"a")
            file.write(content)
            file.flush()
        except IOError,args:
            pass
        file.close()


    def Noporxy_request(self,url,hostname):
        oururl = str(url)
        result = filter.search(url) or (not yoursitedomain.search(hostname) ) or nosocketio.search(url)
        return result

    def Decode_Request_Body(self,data):
        if(not data):
            return ""
        result = zlib.decompress(data,16+zlib.MAX_WBITS)
        return result



config = proxy.ProxyConfig(port=9880)
server = ProxyServer(config)
m = Record(server)
m.run()
