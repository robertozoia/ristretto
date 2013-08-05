# -*- encoding: utf-8 -*-

"""
    Ristretto
    
    A static blog generator.
    (c) 2012-today by Roberto Zoia Nesta
    roberto@zoia.org

"""

def usage():
    print(
    """
Ristretto.  A static blog generator written in Python.
    
usage: ristretto.py [options]
    
    Required options are:
    -s settings_file            Generate blog using settings_file 
    --settings=settings_file
    
    Other:
    -v                          Launch local web server for previewing blog.
    --preview    
    
    """)
    sys.exit()


if __name__=='__main__':

    import os
    import sys
    import getopt
    import importlib
    import logging
    import SimpleHTTPServer
    import SocketServer
    
    import updater

    # Parse command line arguments
    argv = sys.argv[1:]
    settings_file = None
    preview = None
    port = None
    
    try:
        opts, args = getopt.getopt(argv,
            "hs:vp=", ["help", "settings=", "preview", "port="]
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--settings"):
            settings_file = arg
        elif opt in ("-p", "--preview"):
            preview = True
        elif opt in ("-p", "--port"):
            port = arg
        
            
            
    if settings_file is None:
        usage()
        sys.exit(2)

    if os.path.exists(settings_file):
        import shared
        shared.blog_settings = os.path.splitext(settings_file)[0]
        import base_settings as settings
        
    else:
        print "Can't find settings file '%s'.  Exiting now..." % settings_file
        exit(1)

        
    if preview:
        if port:
            PORT = int(port)
        else:
            PORT = 8000
        
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(("", PORT), Handler)
    
        os.chdir(settings.WWW_DIR)    
        print("Ristretto serving at port {0}.  Visit http://localhost:{0} to preview your blog. \nCtrl-C to end server.".format(PORT))
        httpd.serve_forever()
        
        



    logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('----------------')
    logging.info('Logging started.')
    
    updater.Updater(settings=settings).update()
    
        
