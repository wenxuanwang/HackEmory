from flask import Flask, url_for, render_template
from collections import OrderedDict
import sqlite3
import re
import json
from datetime import datetime

app = Flask(__name__)
postdb = sqlite3.connect('local.db').cursor()

class PicItem(object):

	def __init__(self, pid, title, descrip, ext, timestamp):
		self.pid = int(pid)
		self.title = title
		self.descrip = descrip or ""
		self.ext = ext
		self.timestamp = datetime.strptime("%Y-%m-%d %H:%M", timestamp)
		self.src = hex(abs(hash(str(self.pid) + "#" + self.title)))[2:]

@app.route('/')
def index():
	posts = sorted([PicItem(*each) for each in postdb.execute("select * from picitem").fetchall()], 
					key=lambda x: x.timestamp)
	return render_template('index.html', posts=posts)

if __name__ == '__main__':
	app.run()


