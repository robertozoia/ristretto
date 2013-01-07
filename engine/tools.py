# coding: utf-8


import os
import logging

def mkdirp(d):
	if not os.path.isdir(d):
		logging.info("Creating directory %s." % d)
		os.makedirs(d)