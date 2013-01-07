# coding: utf-8


import os
import codecs
from datetime import datetime

import pprint as pp



class Post(object):


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
				self.date = datetime.fromtimestamp(os.path.getmtime(self.fname))

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
				post_date = datetime.strptime(tmp, self.s.POST_DATETIME_FORMAT)
			else:
				# TODO:  check this, it will lead to problems...
				post_date = datetime.strptime(tmp, self.s.POST_DATE_FORMAT)
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


