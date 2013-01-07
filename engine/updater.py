# coding: utf-8



#
# Directory structure
# /drafts:  directory containing post's drafts
# /drafts/_preview
# /drafts/_publishnow 
# /posts 
# /cache

import os
import glob
import shutil
import codecs
import logging
import re
import datetime
from operator import itemgetter

import markdown
from smartypants import smartyPants as smartypants
import PyRSS2Gen

from jinja2 import Environment, FileSystemLoader


from post import Post
import tools

import pprint as pp


class Updater(object):

	def __init__(self, settings, *args, **kwargs):

		self.s = settings

		self.base_dir = settings.BASE_DIR
		self.drafts_dir = settings.DRAFTS_DIR
		self.posts_dir = settings.POSTS_DIR
		self.www_dir = settings.WWW_DIR

		# Init Jinja2
		self.j2 = Environment(loader=FileSystemLoader(self.s.TEMPLATES_DIR, encoding=self.s.INPUT_ENCODING))


	def update(self, force_publish=False):

		self.publish_drafts()
		self.publish_pages(force_publish=True)
		self.publish_404(force_publish=True)
		self.publish_500(force_publish=True)

		np = self.need_publishing(self.posts_dir)

		if np:
			self.publish_permalinks(posts=[Post(p, self.s) for p in np])
			self.publish_index_pages()
			self.publish_monthly_archive(posts=[ Post(p, self.s) for p in np])
			self.publish_tags(posts=[Post(p, self.s) for p in np])
			self.publish_rss()

		else:
			self.publish_permalinks(force_publish=True)
			self.publish_index_pages()
			self.publish_monthly_archive(force_publish=True)
			self.publish_tags(force_publish=True)
			self.publish_rss()


	def prepare_post(self, post):

		post.title = smartypants(post.title)
		post.content = smartypants(markdown.markdown(post.content, 
			extensions=self.s.MD_EXTENSIONS,
			extension_configs=self.s.MD_EXTENSION_CONFIGS,
			output_format=self.s.MD_OUTPUT_FORMAT,
		))


	def publish_drafts(self):

		self.process_drafts()
		self.process_publish_now()


	def process_drafts(self):
		"""
		Traverse drafts dir looking for posts to publish
		"""		

		tools.mkdirp(self.s.DRAFTS_PUBLISH_NOW_DIR)


		for f in os.listdir(self.s.DRAFTS_DIR):
			if f.endswith(self.s.MD_EXT):

				# skip files scheduled for publishing
				if os.path.exists(os.path.join(self.s.DRAFTS_PUBLISH_NOW_DIR, f)): continue


				# Create post instance from file
				logging.info("Creating post instance from file %s." % f)
				post = Post(os.path.join(self.s.DRAFTS_DIR, f), self.s)

				if post.status and (post.status.upper() == self.s.POST_STATUS_PUBLISH.upper()):

					post.normalize()
					self.prepare_post(post)

					template = self.j2.get_template(self.s.PERMALINK_TEMPLATE)
					html = template.render(
						blog_title=self.s.BLOG_TITLE,
						blog_url=self.s.BLOG_URL,
						blog_description=self.s.BLOG_DESCRIPTION,
						post=post, 
						prev_page_url=None,
						next_page_url=None,
					)

					fname = "%s%s" % (os.path.splitext(os.path.split(f)[1])[0], self.s.HTML_EXT)

					self.write_html(self.s.DRAFTS_PREVIEW_DIR, fname, html)
					logging.info("Wrote preview post to %s" % fname)


	def process_publish_now(self):
		
		for f in os.listdir(self.s.DRAFTS_PUBLISH_NOW_DIR):
			if f.endswith(self.s.MD_EXT):


				source_file = os.path.join(self.s.DRAFTS_PUBLISH_NOW_DIR, f)

				post = Post(source_file, self.s)
				post.set_status(published=True)
				post.normalize()

				if post.type.lower()==self.s.POST_TYPE_PAGE.lower():

					dest_fname = "%s%s" % (post.slug, self.s.MD_EXT)
					dest_dir = self.s.PAGES_DIR
					tools.mkdirp(dest_dir)

					try:
						shutil.copy(source_file, os.path.join(dest_dir, dest_fname))
						os.remove(source_file)
					except IOError as e:
						logging.error('Could not move file %s to %s. Error: %s.' % (source_file, 
							os.path.join(dest_dir, dest_fname), e))

					
				else:
					sequence = self.get_next_sequence(post.date.year, post.date.month, post.date.day)
					# output filename has form YYYYMMDD-p##-slug.md
					if sequence > self.s.MAX_POSTS_PER_DAY:
						raise Exception("Max posts per day is 99.  Got %d posts for %04d-%02d-%02d." % 
								sequence, post.date.year, post.date.month, post.date.day
							)


					dest_fname = "%04d%02d%02d-p%02d-%s%s" % (post.date.year, 
						post.date.month, post.date.day, 
						sequence,
						post.slug, self.s.MD_EXT)


					# copy post to posts dir YYYY/MM
					dest_dir = os.path.join(self.s.POSTS_DIR, "%04d" % post.date.year, "%02d" % post.date.month)

					tools.mkdirp(dest_dir)

					try:
						shutil.copy(source_file, os.path.join(dest_dir, dest_fname))
						os.remove(source_file)
					except IOError as e:
						logging.error('Could not move file %s to %s. Error: %s.' % (source_file, 
							os.path.join(dest_dir, dest_fname), e))



	def write_html(self, dname, fname, html):

		tools.mkdirp(dname)

		# write post
		outf = codecs.open(os.path.join(dname, fname), "w", encoding=self.s.OUTPUT_ENCODING)
		outf.write(html)
		outf.close()



	def publish_pages(self, posts=None, force_publish=False):
		
		if force_publish:
			posts = [Post(os.path.join(self.s.PAGES_DIR, f), self.s) for f in os.listdir(self.s.PAGES_DIR) if f.endswith(self.s.MD_EXT)]

		for post in posts:

			post.content = smartypants(self.md_to_html(post.content))
			post.title = smartypants(post.title)

			html_fname = "%s%s" % (post.slug, self.s.HTML_EXT)
			html_dir = os.path.join(self.s.WWW_DIR, self.s.WWW_PAGES_URL)
			html_full_path = os.path.join(html_dir, html_fname)

			tools.mkdirp(html_dir)
			# TODO: check dir owner/permission
			self.write_single_post_to_file(post=post, fname=html_full_path, template=self.s.PAGES_TEMPLATE)



	def get_next_sequence(self, year, month, day):

		seq = []
		s = "%04d%02d%02d-*%s"  % (year, month, day, self.s.MD_EXT)


		for f in glob.glob(os.path.join(self.s.POSTS_DIR, 
				"%04d" % int(year), "%02d" % int(month), s)):
			# get all sequence numbers for date
			head, tail = os.path.split(f)
			seq.append(int(tail[10:12]))

		if seq:
			seq.sort()
			result = seq[-1] + 1
		else:
			result = 1

		return result


	def need_publishing(self, posts_dir):
		"""
		Returns a list of files that need republishing.
		"""

		result = []

		for root, dirs, files in os.walk(posts_dir):
			# print "root: %s dirs: %s files: %s" % (root, dirs, files)
			if files:
				for f in files:
					if os.path.splitext(f)[1] == self.s.MD_EXT:
						# only process .md files
						if self.post_needs_publishing(root, f):
							result.append(os.path.join(root, f))

		return result


	def post_needs_publishing(self, posts_dir, fname):

		# Posts needs publishing if:
		# - html permalink does not exists
		# - html permalink is older than post .md file

		result = False

		md_full_path = os.path.join(posts_dir, fname)
		post = Post(md_full_path, self.s)
		year = post.date.year
		month = post.date.month
		day = post.date.day

		html_fname = "%s%s" % (post.slug, self.s.HTML_EXT)
		html_full_path = os.path.join(self.s.WWW_DIR, "%04d" % int(year), "%02d" % int(month),
			"%02d" % int(day), html_fname)

		if os.path.exists(html_full_path):
			dt_md = os.path.getmtime(md_full_path)
			dt_html = os.path.getmtime(html_full_path)

			if dt_md > dt_html:
				result = True
		else:
			result = True

		return result




	def publish_permalinks(self, posts=None, force_publish=False):


		if force_publish:
			file_posts = self.get_all_file_posts_by_date()
			
			posts = [ Post(f, self.s) for f in self.get_all_file_posts_by_date()]

		for post in posts:
			post.content = smartypants(self.md_to_html(post.content))
			post.title = smartypants(post.title)


		for p in posts:
			html_fname = "%s%s" % (p.slug, self.s.HTML_EXT)
			html_dir = os.path.join(self.www_dir, 
				"%04d" % int(p.date.year), 
				"%02d" % int(p.date.month),
				"%02d" % int(p.date.day))
			html_full_path = os.path.join(html_dir, html_fname)

			tools.mkdirp(html_dir)
			# TODO: check dir owner/permission
			self.write_single_post_to_file(post=p, fname=html_full_path, template=self.s.PERMALINK_TEMPLATE)


	def write_single_post_to_file(self, post, fname, template):

		template = self.j2.get_template(template)

		if post:
			post.title = smartypants(post.title)
			post.content = smartypants(self.md_to_html(post.content))

		html = template.render(
			blog_title=self.s.BLOG_TITLE,
			blog_url=self.s.BLOG_URL,
			blog_description=self.s.BLOG_DESCRIPTION,
			post=post,
			pages=self.get_all_pages_permalinks(),
			archive=self.get_monthly_archives_permalinks()
		)

		# write post
		output_file = codecs.open(fname, "w", encoding=self.s.OUTPUT_ENCODING)
		output_file.write(html)
		output_file.close()

		logging.info("Wrote post to %s." % fname)


	def write_posts_to_file(self, posts, dir, fname, template, 
					prev_page_url=None, next_page_url=None, tag=None):

		tools.mkdirp(dir)

		output_fname = os.path.join(dir, fname)

		# Render template
		template = self.j2.get_template(template)
		
		html = template.render(
			blog_title=self.s.BLOG_TITLE,
			blog_url=self.s.BLOG_URL,
			blog_description=self.s.BLOG_DESCRIPTION,
			posts=posts,
			prev_page_url=prev_page_url,
			next_page_url=next_page_url,
			tag=tag,
			pages=self.get_all_pages_permalinks(),
			archive=self.get_monthly_archives_permalinks()
		)

		# write post
		output_file = codecs.open(output_fname, "w", encoding=self.s.OUTPUT_ENCODING)
		output_file.write(html)
		output_file.close()

		logging.info("Wrote %d posts to %s." % (len(posts), output_fname))


	def md_to_html(self, text):
		
		html = markdown.markdown(text, 
				extensions=self.s.MD_EXTENSIONS,
				#extension_configs=self.s.MD_EXTENSION_CONFIGS,
				output_format=self.s.MD_OUTPUT_FORMAT,
			)

		return html

	def publish_index_pages(self):

		file_posts = self.get_all_file_posts_by_date()
		
		posts = [ Post(f, self.s) for f in self.get_all_file_posts_by_date()]

		for post in posts:
			post.content = smartypants(self.md_to_html(post.content))
			post.title = smartypants(post.title)


		first_post = 0
		last_post = first_post + self.s.POSTS_PER_PAGE
		page_number = 0
		dest_fname = self.s.INDEX_PAGE
		dest_dir = self.s.WWW_DIR
		prev_page_url = None
		next_page_url = None


		while first_post < len(posts):

			p = posts[first_post:last_post]

			if page_number == 0:
				local_fname = dest_fname
			else:
				local_fname = "%s-%d%s" % (os.path.splitext(dest_fname)[0], page_number, self.s.HTML_EXT )

			# Pagination
			if len(posts) <= last_post:
				# No next page
				next_page_url = None
			else:
				next_page_url = "%s-%d%s" % (os.path.splitext(self.s.INDEX_PAGE)[0], page_number + 1, self.s.HTML_EXT)

			if first_post - self.s.POSTS_PER_PAGE < 0:
				prev_page_url = None
			else:
				if page_number == 1:
					prev_page_url = self.s.INDEX_PAGE
				else:
					prev_page_url = "%s-%d.html" % (os.path.splitext(self.s.INDEX_PAGE)[0], page_number - 1)
			

			self.write_posts_to_file(
				posts=p,
				fname=local_fname,
				dir=dest_dir,
				template=self.s.INDEX_TEMPLATE,
				prev_page_url=prev_page_url,
				next_page_url=next_page_url,
			)

			logging.info("Wrote posts %d-%d to %s." % (first_post, last_post, local_fname))

			first_post = last_post
			last_post = first_post + self.s.POSTS_PER_PAGE
			page_number = page_number + 1 




	def get_all_file_posts_by_date(self):

		tmp = {}

		for root, dirs, files in os.walk(self.s.POSTS_DIR):
			# print "root: %s dirs: %s files: %s" % (root, dirs, files)
			if files:
				for f in files:
					if os.path.splitext(f)[1] == self.s.MD_EXT:
						tmp[f] = os.path.join(root, f)

		result = [ tmp[key] for key in reversed(sorted(tmp.iterkeys())) ]

		return result


	def get_all_pages_permalinks(self):
		"""
		Returns a list containing blog pages. Each page is a dict:
			'url': page permalink
			'title': page title
		"""
		# links are generated from pages .md files, not from .html rendered files
		pages = [Post(os.path.join(self.s.PAGES_DIR, f), self.s) for f in os.listdir(self.s.PAGES_DIR) if f.endswith(self.s.MD_EXT)]

		result = []
		for post in pages:
			page_url = os.path.join('/', self.s.WWW_PAGES_URL, "%s%s" % (post.slug, self.s.HTML_EXT))
			page_title = smartypants(post.title)
			result.append({ 'url': page_url, 'title': page_title })

		return result

	def get_monthly_archives_permalinks(self):
		"""
		Returns a list containing:
			'date':  datatime stamp for month
			'url' :  month's index permalink
		
		Results in list are ordered by date.

		"""

		result = []

		for root, dirs, files in os.walk(self.s.POSTS_DIR):
			if files:
				contains_MD = False
				for f in files:
					if os.path.splitext(f)[1]==self.s.MD_EXT:
						contains_MD = True
						break
				if contains_MD:
					# Generate month archive permalink for this month
					head, month = os.path.split(root)
					month = int(month)
					year = int(os.path.split(head)[1])

					permalink = os.path.join('/', "%04d" % year, "%02d" % month, self.s.ARCHIVE_PAGE)
					timestamp = datetime.date(year, month, 1)
					result.append({
						'url': permalink,
						'date': timestamp
					})

		result = reversed(sorted(result, key=itemgetter('date')))
		return result


	def publish_monthly_archive(self, posts=None, force_publish=False):
		
		if force_publish:
			file_posts = self.get_all_file_posts_by_date()
			
			posts = [ Post(f, self.s) for f in self.get_all_file_posts_by_date()]

		for post in posts:
			post.content = smartypants(self.md_to_html(post.content))
			post.title = smartypants(post.title)



		c_month = None
		c_year = None
		batch = []
		publish = False

		for post in posts:

			if (c_month != post.date.month) or (c_year != post.date.year):
				if batch:

					dest_dir = os.path.join(self.s.WWW_DIR, "%04d" % c_year, "%02d" % c_month )
					tools.mkdirp(dest_dir)
					fname = self.s.ARCHIVE_PAGE

					self.write_posts_to_file(
						posts=batch,
						fname=fname,
						dir=dest_dir,
						template=self.s.ARCHIVE_TEMPLATE,
						prev_page_url=None,
						next_page_url=None
					)

				batch = [ ]
				c_month = post.date.month
				c_year = post.date.year

			batch.append(post)

		if batch:

			dest_dir = os.path.join(self.s.WWW_DIR, "%04d" % c_year, "%02d" % c_month )
			tools.mkdirp(dest_dir)
			fname = self.s.ARCHIVE_PAGE

			self.write_posts_to_file(
				posts=batch,
				fname=fname,
				dir=dest_dir,
				template=self.s.ARCHIVE_TEMPLATE,
				prev_page_url=None,
				next_page_url=None
			)

		# Write archive index page
		self.write_single_post_to_file(
			post=None,
			fname=os.path.join(self.s.WWW_DIR, self.s.ARCHIVE_INDEX_PAGE),
			template=self.s.ARCHIVE_INDEX_TEMPLATE,
		)


	def publish_tags(self, posts=None, force_publish=False):
		
		if force_publish:
			file_posts = self.get_all_file_posts_by_date()
			
			posts = [ Post(f, self.s) for f in file_posts]


		for post in posts:
			post.content = smartypants(self.md_to_html(post.content))
			post.title = smartypants(post.title)


		tagged = {} 

		for post in posts:
			for tag in post.tags:
				if tag not in tagged:
					tagged[tag.strip()] = [post ,]
				else:
					tagged[tag.strip()].append(post)


		for tag in tagged.iterkeys():
			# no pagination yet...
			dest_dir = os.path.join(self.s.TAGGED_DIR, tag.strip())
			tools.mkdirp(dest_dir)

			self.write_posts_to_file(
				posts=tagged[tag],
				fname=self.s.TAGGED_PAGE,
				dir=dest_dir,
				template=self.s.TAGGED_TEMPLATE,
				prev_page_url=None,
				next_page_url=None,
				tag=tag
			)

	def publish_404(self, force_publish=False):
		self.write_single_post_to_file(
			post=None, 
			fname=os.path.join(self.s.WWW_DIR, self.s.ERR_404_PAGE),
			template=self.s.ERR_404_TEMPLATE
		)

	def publish_500(self, force_publish=False):
		self.write_single_post_to_file(
			post=None, 
			fname=os.path.join(self.s.WWW_DIR, self.s.ERR_500_PAGE),
			template=self.s.ERR_500_TEMPLATE
		)



	def publish_rss(self):

		file_posts = self.get_all_file_posts_by_date()
		posts = [Post(f, self.s) for f in file_posts ]

		post_items = []

		for post in posts:
			post_items.append(PyRSS2Gen.RSSItem(
				title=post.title,
				link=post.permalink,
				description=smartypants(self.md_to_html(post.content)),
				guid=PyRSS2Gen.Guid(post.permalink),
				pubDate=post.date
			))

		rss = PyRSS2Gen.RSS2(
			title = self.s.BLOG_TITLE,
			link = self.s.BLOG_URL,
			description = self.s.BLOG_DESCRIPTION,
			lastBuildDate = datetime.datetime.now(),
			items = post_items
		)

		dest_fname = os.path.join(self.s.WWW_DIR, self.s.RSS_FILE)

		rss.write_xml(open(dest_fname, "w"), encoding=self.s.OUTPUT_ENCODING)







if __name__=='__main__':

	import argparse
	import importlib

	# Parse command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("settings", help="The settings file for the blog to be baked.")
	parser.parse_args()
	args = parser.parse_args()
	settings_file = args.settings

	if os.path.exists(settings_file):
		module = os.path.splitext(settings_file)[0]
		settings = importlib.import_module(module)
	else:
		print "Can't find settings file '%s'.  Exiting now..." % settings_file
		exit(1)


	logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')
	logging.info('----------------')
	logging.info('Logging started.')
	
	updater = Updater(settings=settings)
	updater.update()
		
