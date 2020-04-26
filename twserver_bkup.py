'''
An updated version of this is now its own reposiroty here:
https://gitlab.com/panosfirbas/tiddlyp
That one implements git version control of the updated tiddlywiki, 
so if you want to keep this backup method, feel free to use (at your own risk)
this snippet. The cleanup function shouuuuuuld work and be safe, but
it won't hurt if you have an extra look in the code and make sure you know what it's doing
'''


#!/usr/bin/python3

import datetime, shutil, os, http.server
# import ssl

def cleanupBackups(src, keep_last_n=5):
    srcpath, srcfile = os.path.split(src)
    srcname, src_ext = os.path.splitext(srcfile)
    dstpath = os.path.join(srcpath,'twBackups')

    # datetime string to datetime object
    dtsTodto = lambda s: datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    # filename to datetime object
    fnTodto = lambda fn:  dtsTodto(fn.split('-')[1][:-5])

    # get the backuped files that correspond to srcname
    # original exception error bkupfile_list = [x for x in os.listdir(dstpath) if (fn.split('-')[0]==x)] replace with https://gitlab.com/panosfirbas/tiddlyp/-/blob/master/tiddlyserver.py
    bkupfile_list = [x for x in os.listdir(dstpath) if (x.split('-')[0]==srcname)]
    # this is a list of the filenames plus each filename's datetime object
    # (to allow sorting)
    sorted_list = sorted([(x,fnTodto(x)) for x in bkupfile_list], key=lambda y:y[1])

    # print("We have this many files: ",len(sorted_list))
    list_count=len(sorted_list)
    # print("To keep the last X, I need to delete the first", len(sorted_list)-keep_last_n)
    delete_first = len(sorted_list)-keep_last_n

    # print("I delete these:")
    # for t in sorted_list[:delete_first]:
    #   print(t)
    # print("I keep these:")
    # for t in sorted_list[-keep_last_n:]:
    #   print(t)

    #delete them:
    for thing in sorted_list[:delete_first]:
        fp = os.path.join( dstpath,thing[0] )
        if os.path.exists(fp):
            os.remove(fp)

def makebackup(src):
    (srcpath, srcfile) = os.path.split(src)
    (srcname, src_ext) = os.path.splitext(srcfile)

    tstamp=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dstpath = os.path.join(srcpath,'twBackups')
    if not os.path.exists(dstpath):
        os.mkdir(dstpath)
    shutil.copyfile(src, os.path.join(dstpath, srcname+'-'+tstamp+src_ext))

class ExtendedHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, 'OK')
        self.send_header('allow','GET,HEAD,POST,OPTIONS,CONNECT,PUT,DAV,dav')
        self.send_header('x-api-access-type','file')
        self.send_header('dav','tw5/put')
        self.end_headers()
    def do_PUT(self):
        print(self)
        path = self.translate_path(self.path)
        makebackup(path)
        cleanupBackups(path,5)
        with open(path, "wb") as dst:
            dst.write(self.rfile.read(int(self.headers['Content-Length'])))
        self.send_response(200, 'OK')
        self.end_headers()

# made a subfolder to serve from, so that the script itself is not served
# and neither are the backups
# orignal os.chdir(os.path.dirname(os.path.abspath(__file__))+"/served" )
os.chdir(os.path.dirname(os.path.abspath(__file__)))

theip = "localhost" # or localhost 
theport = 8080   #or any other port as far as I can tell
theserver = http.server.HTTPServer((theip,theport),ExtendedHandler)

# make it https. not for this personal copy and comment out import ssl 
# I configured this with letsencrypt keys, after some simple googling
# theserver.socket = ssl.wrap_socket (theserver.socket, 
#         keyfile="/path/to/key.pem", 
#         certfile='/path/to/cert.pem', server_side=True)
# 
theserver.serve_forever()
