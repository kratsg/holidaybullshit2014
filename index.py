import os
from flask import Flask, render_template, redirect, url_for, request, send_file
import requests
from urlparse import urlparse

import pymongo

from cStringIO import StringIO

import logging
from logging import FileHandler

app = Flask(__name__)

MONGO_URL = os.environ.get('MONGOHQ_URL')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def dbconn():
  if MONGO_URL:
    conn = pymongo.Connection(MONGO_URL)
    # get the database
    db = conn[urlparse(MONGO_URL).path[1:]]
  else:
    conn = pymongo.Connection('localhost', 27017)
    db = conn['test']
  return db

def testdb():
  db = dbconn()
  db.test_collection.insert({"testdoc":"totaltest"})
  print db.test_collection.find()[0]

def get_cache(phrase):
  db = dbconn()
  res = db.phrases.find_one({ phrase: {"$exists": "true"} })
  if res:
    # exists
    db.phrases.update({"_id": res['_id']}, {"$inc": {"requests": 1}})
    try:
      return res[phrase], res['requests']
    except:
      res = db.phrases.find_one({"_id": res['_id']})
      return res[phrase], res['requests']-1
  else:
    # does not exist
    return None, 0

def set_cache(phrase, imageID):
  db = dbconn()
  res = db.phrases.insert({phrase: imageID, "requests": 1})
  return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image/<imageID>')
def redirectToImage(imageID):
  doRedirect = request.args.get('redirect')
  if doRedirect == "false" or doRedirect == None or doRedirect != "true":
    doRedirect = False
  try:
    imageID = int(imageID)
  except:
    return redirect(url_for('.index'))

  imageURL = 'http://dopp0jlzdkkkq.cloudfront.net/single/%d.jpg' % imageID
  if doRedirect:
    return redirect(imageURL)
  else:
    image = StringIO(requests.get(imageURL).content)
    image.seek(0)
    return send_file(image, attachment_filename='%d.jpg' % imageID, mimetype='image/jpeg'), 200
 
@app.route('/phrase/<phrase>')
def run(phrase):
  # capitalization and spaces do not matter
  # --> http://www.reddit.com/r/holidaybullshit/comments/2of5a8/strings_and_images/
  # fucking stop 9GAG army from spamming
  if is_number(phrase):
    return redirect(url_for('.index'))
  # normalize the phrase
  phrase = phrase.lower().replace(' ','')

  # check if we've cached it
  cache, counts = get_cache(phrase)
  if cache:
    imageID = cache
    status_code = 'cache'
    num_requests = counts
  else:
    payload = {'q': phrase}
    # make request to get json, ignore SSL stuff
    r = requests.get('https://ask.cardsagainsthumanity.com/single', params=payload, verify=False)
    try:
      imageID = r.json()['a']
      r = recordResult(phrase, imageID)
      status_code = r.status_code
      num_requests = 0
      # log in the cache for future reference
      set_cache(phrase, imageID)
    except:
      return redirect(url_for('.index'))
  return render_template('index.html', phrase=phrase, imageID=imageID, status=status_code, num_requests=num_requests)


def recordResult(phrase, imageID):
  # http://mikeheavers.com/main/code-item/submitting_custom_form_data_to_a_google_spreadsheet_with_javascript
  formURL = "https://docs.google.com/forms/d/1J4BIqr06ZgOse-Eo7YpwGbdr3xRyIohgUSW2uq2iatk/formResponse"
  imageID_textbox = "entry.1503938973"
  phrase_textbox = "entry.1437664445"
  payload = {imageID_textbox: "%03d" % imageID, phrase_textbox: phrase}
  r = requests.post(formURL, params=payload)
  return r

if __name__ == "__main__":
  file_handler = FileHandler("debug.log","a")                                                  
  file_handler.setLevel(logging.WARNING)
  app.logger.addHandler(file_handler)

  app.run(debug=False)
