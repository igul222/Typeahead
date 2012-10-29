import sys

class Item:
  """A possible search result."""
  items_created = 0 # this is used to track the order in which items are created (on which we need to sort later)

  def __init__(self, type, id, raw_score, tokens):
    self.creation_order_id = Item.items_created
    Item.items_created += 1

    self.type = type
    self.id = id
    self.raw_score = raw_score
    self.tokens = tokens

  def score_with_boosts(self, boosts):
    """Return the item's raw score multiplied by all applicable boosts.
    boosts = [['topic','9.99'], ...]
    """
    score = self.raw_score
    type_boosts_allowed = True
    for boost in boosts:
      if boost[0] in ('user','topic','question','board') and type_boosts_allowed:
        if self.type==boost[0]:
          score *= float(boost[1])
      else:
        if type_boosts_allowed: type_boosts_allowed = False
        if self.id==boost[0]:
          score *= float(boost[1])
    return score


class Node:
  """A node in the trie used to search for Items.
  An Item is stored in the trie at all the nodes corresponding its tokens and their prefixes.
  """ 

  def __init__(self):
    self.children = {}
    self.items = dict()

  def next_child_along_path(self, path):
    """Return the child of this node corresponding to the first letter of path.
    If that node doesn't exist yet, create it.
    """
    child_key = path[0]
    if not child_key in self.children: 
      self.children[child_key] = Node()
    return self.children[child_key]

  def child_at_path(self, path):
    """Return the descendant of this node at the end of path.
    (that is, the child path[0]'s child path[1]'s child path[2], etc.)"""
    child = self
    while path:
      child = child.next_child_along_path(path)
      path = path[1:]
    return child

  def add_item(self, item):
    """Add the given item to this node and all appropriate descendants (based on the item's tokens)"""
    for token in item.tokens:
      self.__add_item_along_path(item, token)

  def delete_item(self, item):
    """Delete the given item from this node and all appropriate descendants (based on the item's tokens)"""
    for token in item.tokens:
      self.__delete_item_along_path(item, token)

  def __add_item_along_path(self, item, path):
    self.items[item.id] = item
    if path: self.next_child_along_path(path).__add_item_along_path(item, path[1:])

  def __delete_item_along_path(self, item, path):
    if item.id in self.items: del self.items[item.id]
    if path: self.next_child_along_path(path).__delete_item_along_path(item, path[1:])

trie = Node() # the root node of the trie

def unsorted_query(tokens):
  """Return a list of all matches to the query in the trie."""
  items = trie.child_at_path(tokens[0]).items
  for token in tokens[1:]:
    token_items = trie.child_at_path(token).items
    items = {id:items[id] for id in items if id in token_items}
  return items.values()

def add(type, id, raw_score, tokens):
  """Process an ADD command."""
  trie.add_item(Item(type, id, raw_score, tokens))

def delete(id):
  """Process a DEL command."""
  if id in trie.items: trie.delete_item(trie.items[id])

def sorted_query_with_boosts(result_count, tokens, boosts=[]):
  """Process the QUERY and WQUERY commands."""
  matches = unsorted_query(tokens)
  # Sort by creation order first, then boosted score
  matches = sorted(matches, reverse=True, key=lambda item: item.creation_order_id)
  matches = sorted(matches, reverse=True, key=lambda item: item.score_with_boosts(boosts))
  print ' '.join([match.id for match in matches[0:result_count]])


# This loop reads STDIN line-by-line and dispatches each command (invalid commands, like the first line, are ignored)
for line in iter(sys.stdin.readline, ''):
  line = line.strip().split()
  
  if line[0]=='ADD':
    add(
      type=line[1], 
      id=line[2], 
      raw_score=float(line[3]), 
      tokens=[word.lower() for word in line[4:]]
    )

  elif line[0]=='DEL':
    delete(id=line[1])
  
  elif line[0]=='QUERY':
    sorted_query_with_boosts(
      result_count=int(line[1]), 
      tokens=[word.lower() for word in line[2:]]
    )
  
  elif line[0]=='WQUERY':
    sorted_query_with_boosts(
      result_count=int(line[1]),
      boosts=[boost.split(':') for boost in line[3:3+int(line[2])]],
      tokens=[word.lower() for word in line[3+int(line[2]):]]
    )