from itertools import combinations
import requests
import time
import string
import json

def checkMulti():
  for i,j,k in combinations(range(1,501)*3, 3):
    payload = {"q1": i, "q2": j, "q3": k, "q4": i+j+k}
    r = requests.get("https://ask.cardsagainsthumanity.com/multi", params=payload, verify=False)

    outcome = bool(r.text.encode('utf-8') != '<h2>Stop guessing.</h2>')
    print i, j, k, "|", outcome
    open("multi_output_text.txt","a").write("%d, %d, %d | %s\n" % (i, j, k, outcome))
    time.sleep(1)

def checkPairs():
  mappings = {}
  chars = string.lowercase + ''.join(map(str, range(10)))
  for i, j in combinations(chars*2, 2):
    payload = {"q": "%s%s" % (i, j)}
    r = requests.get('https://ask.cardsagainsthumanity.com/single', params=payload, verify=False)
    imageID = r.json()['a']
    mappings["%s%s" % (i, j)] = imageID
    time.sleep(1)
  return mappings

pairMappings = checkPairs()
with open('pairMappings.dump', 'w+') as out:
  json.dump(pairMappings, out, sort_keys=True, indent=4, separators=(',', ': '))

def checkRepeatedSequences():
  mappings = {}
  chars = string.lowercase + ''.join(map(str, range(10)))
  for char in chars:
    for i in range(1,15):
      payload = {"q": char*i}
      r = requests.get('https://ask.cardsagainsthumanity.com/single', params=payload, verify=False)
      imageID = r.json()['a']
      mappings["%s%s" % (char, i)] = imageID
      time.sleep(1)
  return mappings

sequenceMappings = checkRepeatedSequences()
with open('sequenceMappings.dump', 'w+') as out:
  json.dump(sequenceMappings, out, sort_keys=True, indent=4, separators=(',', ': '))

