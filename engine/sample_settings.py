# coding: utf-8

# sample_settings.py
"""
Sample settings file for baked blogging.
"""
#
# BLOG:  example.com
#

import os

BLOG_TITLE = 'Example dot com blog'
BLOG_URL = 'http://example.com'
BLOG_DESCRIPTION = 'by truly yours'

POSTS_PER_PAGE = 5

# Logging
LOG_FILE = "examplecom.log"

#
# directories under BASE_DIR
#

#
# Directories
#

# Base dir for directory structure 
# This local directory on your computer is where your posts in markdown 
# format reside, and where the system renders them into html.
BASE_DIR = '/Users/somebody/Dropbox/Apps/example.com/'

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

########################################################################
#  Internal configuration variables.  Don't need to touch this
########################################################################

# Extension for markdown and html files
MD_EXT = '.md'
HTML_EXT = '.html'

# Encoding
INPUT_ENCODING = 'utf8'
OUTPUT_ENCODING = 'utf8'

# Markdown configuration
MD_EXTENSIONS = ['extra', 'codehilite']
MD_EXTENSION_CONFIGS = { 
	# 'footnotes': [('PLACE_MARKER', '----------' )],
}
MD_OUTPUT_FORMAT = 'html5'


# Directory for drafts in .md format
DRAFTS_DIR = os.path.join(BASE_DIR, 'drafts')
DRAFTS_PREVIEW_DIR = os.path.join(DRAFTS_DIR, '_preview') 
DRAFTS_PUBLISH_NOW_DIR = os.path.join(DRAFTS_DIR, '_publishnow')

# Directory for processed posts in .md format
POSTS_DIR =  os.path.join(BASE_DIR, 'posts')

# published for processed pages in .md format
PAGES_DIR = os.path.join(BASE_DIR, 'pages')

# Directory for media used in posts
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

# Directory for static files (i.e., js libraries, css, etc.)
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# base directory for published .html files
WWW_DIR = os.path.join(BASE_DIR, 'www')

# dir under base www_dir for published monthly archives 
ARCHIVE_DIR = WWW_DIR

# Tags
TAGGED_DIR = os.path.join(WWW_DIR, 'tag')

# Templates
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

#
#  html pages
# 
INDEX_PAGE = 'index.html'				# frontpage
ARCHIVE_PAGE = "index.html" 			# monthly archives
ARCHIVE_INDEX_PAGE = "archive.html" 	# monthly archive index
TAGGED_PAGE = 'index.html'				# tag index page

# Error pages
ERR_404_PAGE = '404.html'
ERR_500_PAGE = '500.html'

# RSS
RSS_FILE = 'rss.xml'

#
# urls
#
WWW_ARCHIVE_URL = BLOG_URL
WWW_PAGES_URL = 'pages'
WWW_MEDIA_URL = 'media'
WWW_STATIC_URL = 'static'
WWW_TAGGED_URL = 'tag'

#
# POST Variables
#

POST_DATE_LABEL = 'Date'  # Date label
POST_SLUG_LABEL = 'Slug'  # Slug
POST_TITLE_DELIMITER = '----------'

POST_STATUS_LABEL = 'Status'
POST_STATUS_PUBLISHED = 'Published'
POST_STATUS_PUBLISH = 'Publish'
POST_STATUS_DRAFT = 'Draft'

POST_TYPE_LABEL = 'Type'
POST_TYPE_PAGE = 'Page'
POST_TYPE_POST = 'Post'
POST_TAG_LABEL = 'Tags'
POST_CATEGORY_LABEL = 'Categories'
POST_TITLELINK_LABEL = 'Link'

# Date and datetime format.  This is not for displaying the date on website, 
# but for parsing and writing .md files
POST_DATE_FORMAT = '%Y-%m-%d'				# 2012-12-19 
POST_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'   # 2012-12-19 20:10:12

# must be two digits, or code will break
MAX_POSTS_PER_DAY = 99

