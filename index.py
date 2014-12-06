import os
from flask import Flask, render_template, redirect, url_for
import requests

import logging
from logging import FileHandler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/phrase/<phrase>')
def run(phrase):
  # capitalization and spaces do not matter
  # --> http://www.reddit.com/r/holidaybullshit/comments/2of5a8/strings_and_images/
  path_to_cert = "/usr/lib/ssl/certs/ca-certificates.crt"  # heroku
  payload = {'q': phrase.lower().replace(' ','')}
  # make request to get json, ignore SSL stuff
  r = requests.get('https://ask.cardsagainsthumanity.com/single', params=payload, verify=False)
  try:
    imageID = r.json()['a']
    r = recordResult(phrase, imageID)
  except:
    pass
  return render_template('index.html', phrase=phrase, imageID=imageID, status=r.status_code)

def recordResult(phrase, imageID):
  print "we are here!"
  # http://mikeheavers.com/main/code-item/submitting_custom_form_data_to_a_google_spreadsheet_with_javascript
  formURL = "https://docs.google.com/forms/d/1J4BIqr06ZgOse-Eo7YpwGbdr3xRyIohgUSW2uq2iatk/formResponse"
  imageID_textbox = "entry.1503938973"
  phrase_textbox = "entry.1437664445"
  payload = {imageID_textbox: imageID, phrase_textbox: phrase}
  r = requests.post(formURL, params=payload)
  return r

if __name__ == "__main__":
  file_handler = FileHandler("debug.log","a")                                                  
  file_handler.setLevel(logging.WARNING)
  app.logger.addHandler(file_handler)

  app.run(debug=False)
