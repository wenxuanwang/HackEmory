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
		self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
		self.src = hex(abs(hash(str(self.pid) + "#" + self.title)))[2:]
		try:
			self.url = url_for('showPost', pid=self.pid)
		except:
			self.url = ""

def _fetch_items():
	return OrderedDict(sorted([(int(each[0]), PicItem(*each)) for each in postdb.execute("select * from picitem").fetchall()], 
					key=lambda x: x[1].timestamp))
_posts = _fetch_items()

@app.route('/')
def index():
	global _posts
	_posts = _fetch_items()
	return render_template('index.html', posts=_posts.values())

@app.route('/post/<pid>')
def showPost(pid):
	post = _posts[int(pid)]
	tags = zip(*postdb.execute("select tag from tags where pid=?", [pid]).fetchall())[0]
	return render_template('post.html', pic=post, tags=tags)

if __name__ == '__main__':
	app.run()


