# Quora Challenge: Typeahead
# Ishaan Gulrajani (igul@mit.edu)

import sys

def add(type, id, score, data):
  entries[id] = dict(
    id = id,
    type = type, 
    score = score, 
    data = data
  )

def delete(id):
  del entries[id]

def unsorted_query(result_count, query):
  matches = []
  # iterate through entries in reverse order so that in the sorted query, more recent items are higher-ranked
  i = len(entries) - 1
  for id in entries:
    if len(matches) >= result_count: break
    result_match = True
    for prefix in query:
      match = False
      for token in entries[id]['data']:
        if token.startswith(prefix):
          match = True
          break
      if not match:
        result_match = False
        break
    if result_match: matches.append(entries[id])
    i -= 1

  return matches

def query(result_count, query):
  matches = unsorted_query(result_count, query)
  print ' '.join([match['id'] for match in sorted(matches, reverse=True, key=lambda entry: entry['score'])])

# boosts = [['topic','9.99'], ...]
def wquery(result_count, boosts, query):
  matches = unsorted_query(result_count, query)

  def boosted_score(entry):
    score = entry['score']
    for boost in boosts:
      if boost[0] in ('user','topic','question','board'):
        if entry['type']==boost[0]:
          score *= float(boost[1])
      elif entry['id']==boost[0]:
        score *= float(boost[1])
    return score

  print ' '.join( [match['id'] for match in sorted(matches, reverse=True, key=lambda entry: boosted_score(entry)) ])

# for debug purposes only
def debug():
  print repr(entries)

entries = {}

for line in iter(sys.stdin.readline, ''):
    line = line.strip().split()
    if line[0]=='ADD':
      add(line[1], line[2], float(line[3]), [word.lower() for word in line[4:]] )
    elif line[0]=='DEL':
      delete(line[1])
    elif line[0]=='DEBUG': # for debug purposes only
      debug()
    elif line[0]=='QUERY':
      query(int(line[1]), [word.lower() for word in line[2:]])
    elif line[0]=='WQUERY':
      wquery(
        int(line[1]),
        [boost.split(':') for boost in line[3:3+int(line[2])]],
        [word.lower() for word in line[3+int(line[2]):]]
      )