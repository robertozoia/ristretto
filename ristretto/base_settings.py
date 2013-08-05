# -*- encoding: utf-8 -*-

import os
import importlib

import shared


# List of variables that get imported from blog-specific settings module
# (could import from module's dir(), but it is safer to import only 
# known variables)

setting_vars = [
    'BLOG_TITLE', 
    'BLOG_URL', 
    'BLOG_DESCRIPTION',
    'POSTS_PER_PAGE',
    'BASE_DIR', 
    'BLOG_URL', 
    'BASE_DIR', 
    'WWW_ARCHIVE_URL', 
    'WWW_PAGES_URL',
    'WWW_MEDIA_URL',
    'WWW_STATIC_URL', 
    'WWW_TAGGED_URL',
    'WWW_POSTS_URL', 
    'WWW_TEMPLATES_URL', 
    'WWW_SERVER_ROOT',
    'PERMALINK_TEMPLATE', 
    'SINGLE_POST_TEMPLATE',
    'INDEX_TEMPLATE',
    'PAGES_TEMPLATE',
    'ARCHIVE_TEMPLATE',
    'ARCHIVE_INDEX_TEMPLATE', 
    'ERR_404_TEMPLATE', 
    'ERR_500_TEMPLATE', 
    'TAGGED_TEMPLATE',
    'INDEX_PAGE',
    'ARCHIVE_PAGE',
    'ARCHIVE_INDEX_PAGE',
    'TAGGED_PAGE',
    'ERR_404_PAGE',
    'ERR_500_PAGE',
]

s = importlib.import_module(shared.blog_settings)

# import blog_settings variables into module namespace
for key in setting_vars:
    globals()[key] = s.__dict__[key]


# Logging
LOG_FILE = "ristretto.log"

# RSS feed file
RSS_FILE = 'rss.xml'

#
# Directories
#

# Directory for drafts in .md format
DRAFTS_DIR = os.path.join(BASE_DIR, 'drafts')
DRAFTS_PREVIEW_DIR = os.path.join(DRAFTS_DIR, '_preview') 
DRAFTS_PUBLISH_NOW_DIR = os.path.join(DRAFTS_DIR, '_publishnow')

# Directory for processed posts in .md format
POSTS_DIR =  os.path.join(BASE_DIR, WWW_POSTS_URL)

# published for processed pages in .md format
PAGES_DIR = os.path.join(BASE_DIR, WWW_PAGES_URL)

# Directory for media used in posts
MEDIA_DIR = os.path.join(BASE_DIR, WWW_MEDIA_URL)

# Directory for static files (i.e., js libraries, css, etc.)
STATIC_DIR = os.path.join(BASE_DIR, WWW_STATIC_URL)

# base directory for published .html files
WWW_DIR = os.path.join(BASE_DIR, WWW_SERVER_ROOT)

# dir under base www_dir for published monthly archives 
ARCHIVE_DIR = WWW_DIR

# Tags
TAGGED_DIR = os.path.join(WWW_DIR, WWW_TAGGED_URL)

# Templates
TEMPLATES_DIR = os.path.join(BASE_DIR, WWW_TEMPLATES_URL)




#
# Post rendering
#

# Extension for markdown and html files
MD_EXT = '.md'
HTML_EXT = '.html'

# Encoding
INPUT_ENCODING = 'utf-8'
OUTPUT_ENCODING = 'utf-8'

# Markdown configuration
MD_EXTENSIONS = ['extra', 'codehilite']
MD_EXTENSION_CONFIGS = { 

}
MD_OUTPUT_FORMAT = 'html5'

#
# Post header variables
#

POST_HEADER_DELIMITER = '---'

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

POST_DATE_FORMAT = '%Y-%m-%d'				# 2012-12-19 
POST_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'   # 2012-12-19 20:10:12

MAX_POSTS_PER_DAY = 99

