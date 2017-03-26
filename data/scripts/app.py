import flask
import subprocess
import threading
import time
import uuid
import re
import codecs
import os
import feedparser

class MusicPlayer(threading.Thread):
	def __init__(self, station):
		threading.Thread.__init__(self)

		self.station = station
		self.process = None
		self.running = True
	
	def run(self):
		self.process = subprocess.Popen(['mplayer', self.station])
		
		while self.running:
			time.sleep(0.5)

		self.process.terminate()
		self.process.kill()


app = flask.Flask(__name__)


active_radio = None
stored_volume = None

@app.route('/play_file')
def play_file():
	global active_radio

	url = flask.request.args.get('url')

	if active_radio is not None:
		active_radio.running = False

	try:
		active_radio = MusicPlayer(url)
		active_radio.start()
	except:
		pass
	
	return flask.jsonify({"status": "OK"})

@app.route('/stop_player')
def stop_player():
	global active_radio

	if active_radio is not None:
		active_radio.running = False

	# make sure that all mplayers are getting killed in case something
	# is still running
	subprocess.call(['killall', 'mplayer'])
	
	return flask.jsonify({"status": "OK"})

@app.route('/play_podcast_latest')
def play_podcast_latest():
	global active_radio

	url = flask.request.args.get('url')

	if active_radio is not None:
		active_radio.running = False
	try:
		d = feedparser.parse(url)
		if len(d.entries) > 0:
			enc = d.entries[0].enclosures
			
			if len(enc) > 0:
				active_radio = MusicPlayer(enc[0]['href'])
				active_radio.start()
				return flask.jsonify({"status": "OK"})
	except:
		pass
	
	return flask.jsonify({"status": "ERROR"})

@app.route('/volume_up/<int:level>')
def volume_up(level):
	subprocess.call(['amixer', 'sset', 'PCM', str(level) + '+'])
	return flask.jsonify({"status": "OK"})

@app.route('/volume_down/<int:level>')
def volume_down(level):
	subprocess.call(['amixer', 'sset', 'PCM', str(level) + '-'])
	return flask.jsonify({"status": "OK"})

@app.route('/volume_set')
def volume_set():
	level = flask.request.args.get('level')
	subprocess.call(['amixer', 'sset', 'PCM', level + '%'])
	return flask.jsonify({"status": "OK"})

@app.route('/volume_store')
def volume_store():
	global stored_volume

	res = subprocess.check_output(['amixer', 'get', 'PCM'])
	for line in res.splitlines():
		m = re.search(r'\[(\d+)\%\]', line)
		if m is not None:
			stored_volume = m.group(1)
	
	return flask.jsonify({"status": "OK"})

@app.route('/volume_restore')
def volume_restore():
	global stored_volume

	if stored_volume is not None:
		subprocess.call(['amixer', 'sset', 'PCM', str(stored_volume) + '%'])
	
	return flask.jsonify({"status": "OK"})
