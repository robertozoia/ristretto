# coding: utf-8


import os
import argparse
import importlib

def main():
	pass


if __name__=='__main__':
	

	parser = argparse.ArgumentParser()
	parser.add_argument("settings", help="The settings file for the blog to be baked.")
	parser.parse_args()
	args = parser.parse_args()
	settings_file = args.settings

	if settings_file.endswith('.py'):
		settings_file = os.path.split(os.path.splitext(settings_file)[0])[1]

	i = importlib.import_module(settings_file)
	print i.BLOG_URL

