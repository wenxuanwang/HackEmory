from flask import Flask, url_for, render_template, request, redirect
from werkzeug.utils import secure_filename
from collections import OrderedDict
import sqlite3
import re
import os
import json
from datetime import datetime

app = Flask(__name__)
postconn = sqlite3.connect('local.db')
postdb = postconn.cursor()

class PicItem(object):

	def __init__(self, pid, title, descrip, ext, timestamp=None):
		self.pid = int(pid)
		self.title = title
		self.descrip = descrip or ""
		self.ext = ext
		self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M") if timestamp else datetime.now()
		self.src = hex(abs(hash(str(self.pid) + "#" + self.title)))[2:]
		try:
			self.url = url_for('showPost', pid=self.pid)
		except:
			self.url = ""

def _fetch_items(lists=None):
	if not lists:
		lists =  postdb.execute("select * from picitem").fetchall()
	return OrderedDict(sorted([(int(each[0]), PicItem(*each)) for each in lists], 
					key=lambda x: x[1].timestamp))
_posts = _fetch_items()

def _allowed_ext(ext):
	return ext in 'jpg:jpeg:png:gif:bmp'.split(':')


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'file' not in request.files or request.files['file'].filename == '':
			flash('Please submit files!')
		else:
			file = request.files['file']
			ext = file.filename.rsplit('.', 1)[1].lower()
			if file and _allowed_ext(ext):
				pid = postdb.execute('select max(pid) from picitem').fetchone()[0] + 1
				new_item = PicItem(pid, request.form['title'], request.form['descrip'],
					ext)
				file.save("static//images//{}.{}".format(new_item.src, new_item.ext) )
				postdb.execute("insert into picitem values(?,?,?,?,?)", 
					[new_item.pid, new_item.title, new_item.descrip, new_item.ext, new_item.timestamp.strftime("%Y-%m-%d %H:%M")])
				postconn.commit()
	global _posts
	_posts = _fetch_items()
	return render_template('index.html', posts=_posts.values(), main=True)

@app.route('/post/<pid>', methods=['GET', 'POST'])
def showPost(pid):
	if request.method == "POST":
		if 'delete' in request.form:
			return redirect('/delete/' + pid)
		tag = request.form['newTag']
		if tag:
			postdb.execute('insert into tags values (?, ?)', [pid, tag])
			postconn.commit()
	post = _posts[int(pid)]
	try:
		tags = zip(*postdb.execute("select distinct(tag) from tags where pid=?", [pid]).fetchall())[0]
	except:
		tags = []
	return render_template('post.html', pic=post, tags=tags)

@app.route('/tag/<tag>')
def showTag(tag):
	posts = _fetch_items(postdb.execute("select * from picitem where pid in (select distinct(pid) from tags where tag=?)", [tag]).fetchall())
	return render_template('index.html', posts=posts.values(), main=False)

@app.route('/delete/<pid>')
def do_delete(pid):
	postdb.execute("delete from picitem where pid = ?", [pid])
	postdb.execute("delete from tags where pid = ?", [pid])
	postconn.commit()
	return redirect("/")

if __name__ == '__main__':
	app.run()
	SAVE_PATH = os.path.abspath("static\\images")