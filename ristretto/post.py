# coding: utf-8


import os
import codecs
import re
import datetime

import pprint as pp

import yaml 
import unidecode
    

class NotAPostException(Exception):
    pass
    
class PostIsDraftException(Exception):
    pass



class Post(object):

    def __init__(self, fname=None, settings=None, *args, **kwargs):
        
        self.s = settings
        
        self.fname = fname  # post file name
        self.title = None   # post title
        self.date = None    # post datestamp
        self.slug = None    # post slug
        self.status = None  # post status
        self.layout = None    # post type
        self.title_link = None  # post title link
        self.tags = []      # post tags
        self.categories = [] # post categories
        self.content = None # post content as a list of lines
        self.permalink = None
        self.comments = None
    
        if fname is not None:       
            self.parse_variables()

            if self.slug is None:
                self.slug = self.slugify(self.title)

            if self.permalink is None:
                self.permalink = "%s/%04d/%02d/%02d/%s" % (self.s.BLOG_URL, 
                    int(self.date.year), int(self.date.month), int(self.date.day), self.slug )

            if self.layout is None:
                self.type = self.s.POST_TYPE_POST
                

    def slugify(self, s):
        """
            Converts title to slug.
        """
        s = unidecode.unidecode(u"%s" % s).lower()
        return re.sub(r'\W+','-',s)   
    
    def convert_keys_to_lowercase(self, data):
        """
            Converts keys of a dict to lowercase.
        """
    
        result = {} 
        for key  in data.iterkeys():
            result[key.lower()] = data[key]
        return result 

    def set_status(self, published=False, publish=False, draft=True):

        if published: 
            self.status = self.s.POST_STATUS_PUBLISHED
            return

        if publish:  
            self.status = self.s.POST_STATUS_PUBLISH
            return

        if draft:  
            self.status = self.s.POST_STATUS_DRAFT
            return
            
            
    def convert_date(self, tmp):          
    
        # Check if date and time specified, or only date
        if isinstance(tmp, datetime.date):
            return datetime.datetime(tmp.year, tmp.month, tmp.day)
            
        if isinstance(tmp, datetime.datetime):
            return tmp
            
        # Date is a string
            
        if len(tmp.split(' ')) > 1:
            post_date = datetime.datetime.strptime(tmp, self.s.POST_DATETIME_FORMAT)
        else:
            # TODO:  check this, it will lead to problems...
            post_date = datetime.datetime.strptime(tmp, self.s.POST_DATE_FORMAT)
            
        return post_date


    def parse_variables(self):
        """
        Processes post parsing variables.
        Returns a dict with variables and a list with post content.
        """

        # Recognized variables are:
        # title:  post title, specified as a line containing the title followed by 
        #         a line containing POST_TITLE_DELIMITER
        # date:   datetime stamp
        # slug:   post slug
        # status: draft|published|publish

        regex = re.compile("----*(?P<header>.*?)----*(?P<content>.*)",re.MULTILINE|re.DOTALL)  
              
        input_file = codecs.open(self.fname, mode='r', encoding=self.s.INPUT_ENCODING)
        # Read lines stripping newline, if present
        lines = [line.rstrip() for line in input_file]
        input_file.close()
        
        s = '\n'.join(lines)
        
        r = regex.search(s)
        

        if r:
            results = r.groupdict()
            header = results['header']
            content = results['content']
        else:
            raise NotAPostException()
        
        # save post content    
        self.content = content
        
        
        # Parse header data
        try: 
            data = yaml.load(header)
        except yaml.YAMLError, exc:
            r = "Error parsing post header: \nFile: {0}\nMsg: {1}".format(self.fname, exc)
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                r = r + "\nError position: {0}:{1}".format(mark.line+1, mark.column+1)
            raise Exception(r)
            
            
        # Convert keys to lowercase
        data = self.convert_keys_to_lowercase(data)
        

#         print("---\nData: {0}\n---".format(data))

        #        
        # Required variables
        #
        
        try:
            self.status = data['status']
        except KeyError, e:
            raise Exception("A required key is missing: {0}.".format(e))

        
        if self.status.lower() == self.s.POST_STATUS_DRAFT.lower():
            raise PostIsDraftException()
                    
        try:
            self.title = data['title']
            self.date = data['date']
            self.layout = data['layout']
        except KeyError, e:
            raise Exception("A required key is missing: {0}.".format(e))

        try:
            self.slug = data['slug']
        except KeyError:
            self.slug = self.slugify(self.title)
            
        # Convert date to datetime object

        self.date = self.convert_date(self.date)
                
        
        # Optional variables
        self.tags = data.get('tags', [])    
        self.categories = data.get('categories', [])
        self.comments = data.get('comments', None)
        self.title_link = data.get('title_link', None)
        

    
    def build_header(self):
        """
            Returns a dict with header variables.
        """
        err_str = "build_header error: '{0}' is not defined."
        
        r = {}

        # Required variables
        if self.title:
            r['title'] = self.title
        else:
            raise Exception(err_str.format('title'))
        
        if self.slug:
            r['slug'] = self.slug
        else:
            raise Exception(err_str.format('slug'))
            
        if self.date:
            r['date'] = self.date
        else:
            raise Exception(err_str.format('date'))

        if self.status:
            r['status'] = self.status
        else:
            raise Exception(err_str.format('status'))
        
        if self.layout:
            r['layout'] = self.layout
        else:
            raise Exception(err_str.format('layout'))
            
        if self.permalink:
            r['permalink'] = self.permalink
        else:
            raise Exception(err_str.format('permalink'))     
        
        # Optional variables
        if self.tags:  r['tags'] = self.tags
        if self.categories: r['categories'] = self.categories
        if self.comments:  r['comments'] = self.comments
        if self.title_link:  r['title_link'] = self.title_link
        
        result = yaml.safe_dump(r, default_flow_style=False)
        
        return result
            

    def normalize(self):
        """
        Rewrites post in normalized format
        """
        outf = codecs.open(self.fname, "w", encoding=self.s.OUTPUT_ENCODING)
        
        outf.write(u"{0}\n".format(self.s.POST_HEADER_DELIMITER))
        outf.write(self.build_header())
        outf.write(u"{0}\n".format(self.s.POST_HEADER_DELIMITER))
        
        outf.write(u"{0}\n".format(self.content))

        outf.close()





    
class PostOld(object):


    def __init__(self, fname=None, settings=None, *args, **kwargs):
        """
        Construct a new post from file fname.
        """

        self.s = settings

        self.fname = fname  # post file name
        self.title = None   # post title
        self.date = None    # post datestamp
        self.slug = None    # post slug
        self.status = None  # post status
        self.type = None    # post type
        self.title_link = None  # post title link
        self.tags = []      # post tags
        self.categories = [] # post categories
        self.content = None # post content as a list of lines
        self.permalink = None

        if fname is not None:       
            self.parse_variables()

            if self.slug is None:
                # if slug not explicity present, use filename for slug
                self.slug = os.path.splitext(os.path.split(self.fname)[1])[0]

            if self.date is None:
                # if no date/time specified, use file date/time
                self.date = datetime.datetime.fromtimestamp(os.path.getmtime(self.fname))

            if self.permalink is None:
                self.permalink = "%s/%04d/%02d/%02d/%s" % (self.s.BLOG_URL, 
                    int(self.date.year), int(self.date.month), int(self.date.day), self.slug )

            if self.type is None:
                self.type = self.s.POST_TYPE_POST


    def set_status(self, published=False, publish=False, draft=True):

        if published: 
            self.status = self.s.POST_STATUS_PUBLISHED
            return

        if publish:  
            self.status = self.s.POST_STATUS_PUBLISH
            return

        if draft:  
            self.status = self.s.POST_STATUS_DRAFT
            return


    def parse_variables(self):
        """
        Processes post parsing variables.
        Returns a dict with variables and a list with post content.
        """

        # Recognized variables are:
        # title:  post title, specified as a line containing the title followed by 
        #         a line containing POST_TITLE_DELIMITER
        # date:   datetime stamp
        # slug:   post slug
        # status: draft|published|publish



        input_file = codecs.open(self.fname, mode='r', encoding=self.s.INPUT_ENCODING)
        # Read lines stripping newline, if present
        lines = [line.rstrip() for line in input_file]
        input_file.close()

        has_title = False
        has_date = False
        has_slug = False
        has_status = False
        has_tags = False
        has_categories = False
        has_type = False
        has_title_link = False
        has_categories = False
        has_comments = False

        # Process file, line by line
        last_line = ""
        post_content = []

        for line in lines:

            # check for title
            if not has_title:
                post_title = self.get_title_or_none(line, last_line)

                if post_title is not None:
                    # Remove title line from buffer
                    post_content.pop()
                    self.title = post_title
                    has_title = True
                    last_line = line
                    continue

            if not has_date:
                post_date = self.get_date_from_line_or_none(line)
                if post_date is not None:
                    self.date = post_date
                    last_line = line
                    has_date = True
                    continue

            # check for slug
            if not has_slug:
                post_slug = self.get_slug_from_line_or_none(line)

                if post_slug is not None:
                    self.slug = post_slug
                    last_line = line
                    has_slug = True
                    continue

            # check for status
            if not has_status:
                post_status = self.get_status_from_line_or_none(line)
                if post_status is not None:
                    self.status = post_status
                    last_line = line
                    has_status = True
                    continue

            # check for tags
            if not has_tags:
                post_tags = self.get_tags_from_line_or_none(line)

                if post_tags is not None:
                    self.tags = post_tags
                    last_line = line
                    has_tags = True
                    continue

            # check for categories
            if not has_categories:
                post_categories = self.get_categories_from_line_or_none(line)

                if post_categories is not None:
                    self.categories = post_categories
                    last_line = line
                    has_categories = True
                    continue


            # check for type
            if not has_type:
                post_type = self.get_type_from_line_or_none(line)
                if post_type is not None:
                    self.type = post_type
                    has_type = True
                    last_line = line
                    continue

            if not has_title_link:
                post_title_link = self.get_title_link_from_line_or_none(line)
                if post_title_link is not None:
                    self.title_link = post_title_link
                    has_title_link = True
                    last_line = line
                    continue


            # temporary code for post importing 
            if not has_comments:
                tmp = self._get_label_value_from_line_or_none('comments', line)
                if tmp is not None:
                    has_comments = True
                    last_line = line
                    continue

            last_line = line

            # if line contains no variable, add to post content buffer
            post_content.append(line)

        self.content = '\n'.join(post_content)


    ##
    ## Line processing
    ###

    def _get_label_value_from_line_or_none(self, label, line):

        r = None
        if line.startswith("%s:" % label) or line.startswith("%s:" % label.lower()):
            r = line[len(label)+1:].strip()

        return r


    def get_title_or_none(self, line, last_line):
        """
        Tests if post title delimiter is present and returns title if found.
        """
        if line[:len(self.s.POST_TITLE_DELIMITER)] == self.s.POST_TITLE_DELIMITER:
            title = last_line.strip()
            return title
        else:
            return None


    def get_date_from_line_or_none(self, line):
        """
        Parses date from line
        """
        # Get post date from date label

        if line.startswith("%s:" % self.s.POST_DATE_LABEL) or line.startswith("%s:" % self.s.POST_DATE_LABEL.lower()):
            tmp = line[len(self.s.POST_DATE_LABEL)+1:].strip()
            
            # Check if date and time specified, or only date
            if len(tmp.split(' ')) > 1:
                post_date = datetime.datetime.strptime(tmp, self.s.POST_DATETIME_FORMAT)
            else:
                # TODO:  check this, it will lead to problems...
                post_date = datetime.datetime.strptime(tmp, self.s.POST_DATE_FORMAT)
            return post_date
        else:
            return None



    def get_slug_from_line_or_none(self, line):
        r =  self._get_label_value_from_line_or_none(self.s.POST_SLUG_LABEL, line)
        return r

    
    def get_status_from_line_or_none(self, line):
        r = self._get_label_value_from_line_or_none(self.s.POST_STATUS_LABEL, line)
        return r


    def get_tags_from_line_or_none(self, line):
        r = self._get_label_value_from_line_or_none(self.s.POST_TAG_LABEL, line)
        if r is not None:
            r = [ t.strip() for t in r.split(',')]
            

        return r

    def get_categories_from_line_or_none(self, line):
        r = self._get_label_value_from_line_or_none(self.s.POST_CATEGORY_LABEL, line)
        if r is not None:
            r = [t.strip() for t in r.split(',')]
        return r


    def get_type_from_line_or_none(self, line):
        r = self._get_label_value_from_line_or_none(self.s.POST_TYPE_LABEL, line)
        return r

    def get_title_link_from_line_or_none(self, line):
        r = self._get_label_value_from_line_or_none(self.s.POST_TITLELINK_LABEL, line)
        return r


    def normalize(self):
        """
        Rewrites post in normalized format
        """
        outf = codecs.open(self.fname, "w", encoding=self.s.OUTPUT_ENCODING)
        
        if self.title:  
            outf.write(u"%s\n" % self.title)
            outf.write(u"%s\n" % self.s.POST_TITLE_DELIMITER)
        
        if self.date:
            outf.write(u"%s: %s\n" 
                % (self.s.POST_DATE_LABEL, self.date.strftime(self.s.POST_DATETIME_FORMAT)))

        if self.slug:
            outf.write(u"%s: %s\n" % (self.s.POST_SLUG_LABEL, self.slug))

        if self.status:
            outf.write(u"%s: %s\n" % (self.s.POST_STATUS_LABEL, self.status))

        if self.type:
            outf.write(u"%s: %s\n" % (self.s.POST_TYPE_LABEL, self.type))

        if self.title_link:
            outf.write(u"%s: %s\n" % (self.s.POST_TITLELINK_LABEL, self.title_link))

        if self.tags:
            outf.write(u"%s: %s\n" % (self.s.POST_TAG_LABEL, ", ".join(self.tags)))

        if self.categories:
            outf.write(u"%s: %s\n" % (self.s.POST_CATEGORY_LABEL, ", ".join(self.categories)))

        outf.write(u"%s\n" % self.content)

        outf.close()


