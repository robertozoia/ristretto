# coding: utf-8

# settings.py

#
# BLOG: example.com
#

##
## Essential settings
##
BLOG_TITLE = 'The Example Blog'
BLOG_URL = 'http://example.com'
BLOG_DESCRIPTION = 'Sparse thoughts by Yours Truly'

# post in main page
POSTS_PER_PAGE = 5

# Base dir for directory structure 
BASE_DIR = '/Users/yourstruly/blog/'


##
## Fined-grained configuration.
## Don't need to modify this section, everything will work fine with 
## default values.
##

#
# urls
#
WWW_ARCHIVE_URL = BLOG_URL
WWW_PAGES_URL = 'pages'
WWW_MEDIA_URL = 'media'
WWW_STATIC_URL = 'static'
WWW_TAGGED_URL = 'tag'
WWW_POSTS_URL = 'posts'
WWW_TEMPLATES_URL = 'templates'
WWW_SERVER_ROOT = 'www'



#
# Template files
#
PERMALINK_TEMPLATE = 'permalink.html'
SINGLE_POST_TEMPLATE = 'permalink.html'
INDEX_TEMPLATE = 'front_page.html'
PAGES_TEMPLATE = 'page.html'
ARCHIVE_TEMPLATE = "monthly_archive.html"		# monthly archives
ARCHIVE_INDEX_TEMPLATE = "archive_index.html"	# index page for monthly archives
ERR_404_TEMPLATE = 'err_404.html'
ERR_500_TEMPLATE = 'err_500.html'
TAGGED_TEMPLATE = 'tags.html'

#
#  html pages
# 
INDEX_PAGE = 'index.html'		# frontpage
ARCHIVE_PAGE = "index.html" 	# monthly archives
ARCHIVE_INDEX_PAGE = "archive.html"
TAGGED_PAGE = 'index.html'

# Error pages
ERR_404_PAGE = '404.html'
ERR_500_PAGE = '500.html'
