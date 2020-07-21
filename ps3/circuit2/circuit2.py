#!/usr/bin/env python

import json   # Used when TRACE=jsonp
import os     # Used to get the TRACE environment variable
import re     # Used when TRACE=jsonp
import sys    # Used to smooth over the range / xrange issue.

# Python 3 doesn't have xrange, and range behaves like xrange.
if sys.version_info >= (3,):
    xrange = range

# Circuit verification library.

class Wire(object):
  """A wire in an on-chip circuit.
  
  Wires are immutable, and are either horizontal or vertical.
  """
  
  def __init__(self, name, x1, y1, x2, y2):
    """Creates a wire.
    
    Raises an ValueError if the coordinates don't make up a horizontal wire
    or a vertical wire.
    
    Args:
      name: the wire's user-visible name
      x1: the X coordinate of the wire's first endpoint
      y1: the Y coordinate of the wire's first endpoint
      x2: the X coordinate of the wire's last endpoint
      y2: the Y coordinate of the wire's last endpoint
    """
    # Normalize the coordinates.
    if x1 > x2:
      x1, x2 = x2, x1
    if y1 > y2:
      y1, y2 = y2, y1
    
    self.name = name
    self.x1, self.y1 = x1, y1
    self.x2, self.y2 = x2, y2
    self.object_id = Wire.next_object_id()
    
    if not (self.is_horizontal() or self.is_vertical()):
      raise ValueError(str(self) + ' is neither horizontal nor vertical')
  
  def is_horizontal(self):
    """True if the wire's endpoints have the same Y coordinates."""
    return self.y1 == self.y2
  
  def is_vertical(self):
    """True if the wire's endpoints have the same X coordinates."""
    return self.x1 == self.x2
  
  def intersects(self, other_wire):
    """True if this wire intersects another wire."""
    # NOTE: we assume that wires can only cross, but not overlap.
    if self.is_horizontal() == other_wire.is_horizontal():
      return False 
    
    if self.is_horizontal():
      h = self
      v = other_wire
    else:
      h = other_wire
      v = self
    return v.y1 <= h.y1 and h.y1 <= v.y2 and h.x1 <= v.x1 and v.x1 <= h.x2
  
  def __repr__(self):
    # :nodoc: nicer formatting to help with debugging
    return('<wire ' + self.name + ' (' + str(self.x1) + ',' + str(self.y1) + 
           ')-(' + str(self.x2) + ',' + str(self.y2) + ')>')
  
  def as_json(self):
    """Dict that obeys the JSON format restrictions, representing the wire."""
    return {'id': self.name, 'x': [self.x1, self.x2], 'y': [self.y1, self.y2]}

  # Next number handed out by Wire.next_object_id()
  _next_id = 0
  
  @staticmethod
  def next_object_id():
    """Returns a unique numerical ID to be used as a Wire's object_id."""
    id = Wire._next_id
    Wire._next_id += 1
    return id

class WireLayer(object):
  """The layout of one layer of wires in a chip."""
  
  def __init__(self):
    """Creates a layer layout with no wires."""
    self.wires = {}
  
  def wires(self):
    """The wires in the layout."""
    self.wires.values()
  
  def add_wire(self, name, x1, y1, x2, y2):
    """Adds a wire to a layer layout.
    
    Args:
      name: the wire's unique name
      x1: the X coordinate of the wire's first endpoint
      y1: the Y coordinate of the wire's first endpoint
      x2: the X coordinate of the wire's last endpoint
      y2: the Y coordinate of the wire's last endpoint
    
    Raises an exception if the wire isn't perfectly horizontal (y1 = y2) or
    perfectly vertical (x1 = x2)."""
    if name in self.wires:
        raise ValueError('Wire name ' + name + ' not unique')
    self.wires[name] = Wire(name, x1, y1, x2, y2)
  
  def as_json(self):
    """Dict that obeys the JSON format restrictions, representing the layout."""
    return { 'wires': [wire.as_json() for wire in self.wires.values()] }
  
  @staticmethod
  def from_file(file):
    """Builds a wire layer layout by reading a textual description from a file.

    Args:
      file: a File object supplying the input

    Returns a new Simulation instance."""

    layer = WireLayer()

    while True:
      command = file.readline().split()
      if command[0] == 'wire':
        coordinates = [float(token) for token in command[2:6]]
        layer.add_wire(command[1], *coordinates)
      elif command[0] == 'done':
        break

    return layer


class emptynode:
    def __init__(self, node):
        self.height = 0
        self.subnum = 0
        self.parent = node


class Node:
    def __init__(self, key):
        """

        :rtype: object
        """
        self.key = key
        self.lchild = self.rchild = emptynode(self)
        self.parent = None
        self.height = 1
        self.subnum = 1

class Root:
    def __init__(self):
        self.lchild = None

class RangeIndex(object):
    """Array-based range index implementation."""

    def __init__(self):
        """Initially empty range index."""
        self.root = Root()

    def left_rotate(self, x):
        # a = x.lchild
        y = x.rchild
        b = y.lchild
        # c = y.rchild

        x.rchild = b
        y.lchild = x
        b.parent = x
        y.parent = x.parent
        x.parent = y
        y.subnum = x.subnum
        x.subnum = x.lchild.subnum + x.rchild.subnum + 1
        if y.parent.lchild == x:
            y.parent.lchild = y
        elif y.parent.rchild == x:
            y.parent.rchild = y
        x.height = max(x.lchild.height, x.rchild.height) + 1
        y.height = max(x.height, y.rchild.height) + 1

    def right_rotate(self, y):
        x = y.lchild
        # c = y.rchild
        # a = x.lchild
        b = x.rchild

        x.rchild = y
        y.lchild = b
        b.parent = y
        x.parent = y.parent
        y.parent = x
        x.subnum = y.subnum
        y.subnum = y.lchild.subnum + y.rchild.subnum + 1
        if x.parent.lchild == y:
            x.parent.lchild = x
        elif x.parent.rchild == y:
            x.parent.rchild = x
        y.height = max(y.lchild.height, y.rchild.height) + 1
        x.height = max(x.lchild.height, x.rchild.height) + 1

    def rebalance(self, cur):
        if cur == self.root:
            if type(cur.lchild) == emptynode:
                self.root = Root()
            return
        if type(cur) == emptynode:
            self.rebalance(cur.parent)
            return
        x = cur.lchild
        y = cur.rchild
        cur.subnum = x.subnum + y.subnum + 1
        if x.height - y.height > 1:
            if x.lchild.height >= x.rchild.height:
                self.right_rotate(cur)
            else:
                self.left_rotate(x)
                self.right_rotate(cur)
        elif y.height - x.height > 1:
            if y.rchild.height >= y.lchild.height:
                self.left_rotate(cur)
            else:
                self.right_rotate(y)
                self.left_rotate(cur)

        cur.height = max(cur.lchild.height, cur.rchild.height) + 1
        cur.subnum = cur.lchild.subnum + cur.rchild.subnum + 1
        self.rebalance(cur.parent)
        return

    def add(self, key):
        """Inserts a key in the range index."""
        if key is None:
            raise ValueError('Cannot insert nil in the index')
        newnode = Node(key)
        if self.root.lchild is None:
            self.root.lchild = newnode
            newnode.parent = self.root
            return
        else:
            now, prev = self.root.lchild, self.root
            while type(now) != emptynode:
                prev = now
                now.subnum += 1
                if now.key > newnode.key:
                    now = now.lchild
                elif now.key < newnode.key:
                    now = now.rchild
                else:
                    raise ValueError('Cannot insert same wire more than once')
            # found a position of None, and prev is its parent
            if prev == self.root:
                self.root.lchild = newnode
                newnode.parent = self.root
                return
            newnode.parent = prev
            if prev.key > newnode.key:
                prev.lchild = newnode
            else:
                prev.rchild = newnode
            height = 1
            iterator = newnode
            while iterator != self.root.lchild:
                iterator = iterator.parent
                height += 1
                if height > iterator.height:
                    iterator.height = height
            self.rebalance(newnode)


    def search(self, key):
        iterator = self.root.lchild
        if self.root.lchild == None:
            raise ValueError('empty list')
        # a = type(iterator) != emptynode and iterator.key != key
        while type(iterator) != emptynode and iterator.key != key:
            # prev = iterator
            # a1 = iterator.key < key
            if iterator.key > key:
                iterator = iterator.lchild
            elif iterator.key < key:
                iterator = iterator.rchild
            else:
                return iterator
            # elif iterator.key == key:
            #     return iterator
            # else:
            #     raise ValueError('Not found value')
        return iterator
        # if type(iterator) == emptynode or iterator is None:
        #     raise ValueError('Not found value')
        # else:
        #     return iterator

    def remove(self, key):
        tbr = self.search(key)
        x = tbr.lchild
        y = tbr.rchild
        cur_subnum = self.root.lchild.subnum
        if type(x) == emptynode:
            if tbr.parent.lchild == tbr:
                tbr.parent.lchild = y
            elif tbr.parent.rchild == tbr:
                tbr.parent.rchild = y
            else:
                raise ValueError('not pair')
            x.parent = tbr.parent
            y.parent = tbr.parent
            # if type(self.search(key)) != emptynode:
            #     raise ValueError('wrong remove')
            self.rebalance(y)
            # if self.root.lchild.subnum - cur_subnum != -1:
            #     raise ValueError('delete more than one')
        elif type(y) == emptynode:
            if tbr.parent.lchild == tbr:
                tbr.parent.lchild = x
            elif tbr.parent.rchild == tbr:
                tbr.parent.rchild = x
            else:
                raise ValueError('not pair')
            x.parent = tbr.parent
            y.parent = tbr.parent
            # if type(self.search(key)) != emptynode:
            #     raise ValueError('wrong remove')
            self.rebalance(x)
            # if self.root.lchild.subnum - cur_subnum != -1:
            #     raise ValueError('delete more than one')
        else:
            # x and y are both not empty
            iterator, prev = y.lchild, y
            while type(iterator) != emptynode:
                prev = iterator
                iterator = iterator.lchild
            parent = prev.parent
            if parent == tbr:
                prev.lchild = tbr.lchild
                tbr.lchild.parent = prev
                prev.parent = tbr.parent
                if tbr == tbr.parent.lchild:
                    tbr.parent.lchild = prev
                elif tbr == tbr.parent.rchild:
                    tbr.parent.rchild = prev
                prev.height = max(prev.lchild.height, prev.rchild.height) + 1
                # if type(self.search(key)) != emptynode:
                #     raise ValueError('wrong remove')
                self.rebalance(prev)
                # if self.root.lchild.subnum - cur_subnum != -1:
                #     raise ValueError('delete more than one')
            else:
                prev.lchild = tbr.lchild
                tbr.lchild.parent = prev
                prev.parent.lchild = prev.rchild
                prev.rchild.parent = prev.parent
                prev.rchild = tbr.rchild
                tbr.rchild.parent = prev
                prev.parent = tbr.parent
                if tbr == tbr.parent.lchild:
                    tbr.parent.lchild = prev
                else:
                    tbr.parent.rchild = prev
                parent.height = max(parent.lchild.height, parent.rchild.height) + 1
                # if type(self.search(key)) != emptynode:
                #     raise ValueError('wrong remove')
                self.rebalance(parent)
                # if self.root.lchild.subnum - cur_subnum != -1:
                #     raise ValueError('delete more than one')


    def addlist(self, cur, first_key, last_key):
        if type(cur) == emptynode:
            return []
        if cur is None:
            return []
        # return [cur.key] + self.addlist(cur.rchild, first_key, last_key) + self.addlist(cur.lchild, first_key, last_key)
        elif first_key > cur.key:
            return self.addlist(cur.rchild, first_key, last_key)
        elif last_key < cur.key:
            return self.addlist(cur.lchild, first_key, last_key)
        elif first_key <= cur.key <= last_key:
            return [cur.key] + self.addlist(cur.rchild, first_key, last_key) + self.addlist(cur.lchild, first_key, last_key)
        else:
            return []

    def list(self, first_key, last_key):
        return self.addlist(self.root.lchild, first_key, last_key)

    def get_rank(self, key):
        iterator = self.root.lchild
        rank = 0
        flag = False
        while type(iterator) != emptynode and iterator is not None:
            if iterator.key < key:
                rank = rank + iterator.lchild.subnum + 1
                iterator = iterator.rchild
            elif iterator.key > key:
                iterator = iterator.lchild
            elif iterator.key == key:
                rank = rank + iterator.lchild.subnum + 1
                flag = True
                break
        return rank, flag


    def count(self, first_key, last_key):
        rank_low, flag_low = self.get_rank(first_key)
        rank_high, flag_high = self.get_rank(last_key)
        if flag_low:
            if flag_high:
                addition = 1
            else:
                addition = 0
        else:
            if flag_high:
                addition = 1
            else:
                addition = 0
        return rank_high - rank_low + addition



class TracedRangeIndex(RangeIndex):
  """Augments RangeIndex to build a trace for the visualizer."""
  
  def __init__(self, trace):
    """Sets the object receiving tracing info."""
    RangeIndex.__init__(self)
    self.trace = trace
  
  def add(self, key):
    self.trace.append({'type': 'add', 'id': key.wire.name})
    RangeIndex.add(self, key)
  
  def remove(self, key):
    self.trace.append({'type': 'delete', 'id': key.wire.name})
    RangeIndex.remove(self, key)
  
  def list(self, first_key, last_key):
    result = RangeIndex.list(self, first_key, last_key)
    self.trace.append({'type': 'list', 'from': first_key.key,
                       'to': last_key.key,
                       'ids': [key.wire.name for key in result]}) 
    return result
  
  def count(self, first_key, last_key):
    result = RangeIndex.count(self, first_key, last_key)
    self.trace.append({'type': 'list', 'from': first_key.key,
                       'to': last_key.key, 'count': result})
    return result

class ResultSet(object):
  """Records the result of the circuit verifier (pairs of crossing wires)."""
  
  def __init__(self):
    """Creates an empty result set."""
    self.crossings = []
  
  def add_crossing(self, wire1, wire2):
    """Records the fact that two wires are crossing."""
    self.crossings.append(sorted([wire1.name, wire2.name]))
  
  def write_to_file(self, file):
    """Write the result to a file."""
    for crossing in self.crossings:
      file.write(' '.join(crossing))
      file.write('\n')

class TracedResultSet(ResultSet):
  """Augments ResultSet to build a trace for the visualizer."""
  
  def __init__(self, trace):
    """Sets the object receiving tracing info."""
    ResultSet.__init__(self)
    self.trace = trace
    
  def add_crossing(self, wire1, wire2):
    self.trace.append({'type': 'crossing', 'id1': wire1.name,
                       'id2': wire2.name})
    ResultSet.add_crossing(self, wire1, wire2)

class KeyWirePair(object):
  """Wraps a wire and the key representing it in the range index.
  
  Once created, a key-wire pair is immutable."""
  
  def __init__(self, key, wire):
    """Creates a new key for insertion in the range index."""
    self.key = key
    if wire is None:
      raise ValueError('Use KeyWirePairL or KeyWirePairH for queries')
    self.wire = wire
    self.wire_id = wire.object_id

  def __lt__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key < other.key or
            (self.key == other.key and self.wire_id < other.wire_id))
  
  def __le__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key < other.key or
            (self.key == other.key and self.wire_id <= other.wire_id))  

  def __gt__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key > other.key or
            (self.key == other.key and self.wire_id > other.wire_id))
  
  def __ge__(self, other):
    # :nodoc: Delegate comparison to keys.
    return (self.key > other.key or
            (self.key == other.key and self.wire_id >= other.wire_id))

  def __eq__(self, other):
    # :nodoc: Delegate comparison to keys.
    return self.key == other.key and self.wire_id == other.wire_id
  
  def __ne__(self, other):
    # :nodoc: Delegate comparison to keys.
    return self.key != other.key or self.wire_id != other.wire_id

  def __hash__(self):
    # :nodoc: Delegate comparison to keys.
    return hash([self.key, self.wire_id])

  def __repr__(self):
    # :nodoc: nicer formatting to help with debugging
    return '<key: ' + str(self.key) + ' wire: ' + str(self.wire) + '>'

class KeyWirePairL(KeyWirePair):
  """A KeyWirePair that is used as the low end of a range query.
  
  This KeyWirePair is smaller than all other KeyWirePairs with the same key."""
  def __init__(self, key):
    self.key = key
    self.wire = None
    self.wire_id = -1000000000

class KeyWirePairH(KeyWirePair):
  """A KeyWirePair that is used as the high end of a range query.
  
  This KeyWirePair is larger than all other KeyWirePairs with the same key."""
  def __init__(self, key):
    self.key = key
    self.wire = None
    # HACK(pwnall): assuming 1 billion objects won't fit into RAM.
    self.wire_id = 1000000000

class CrossVerifier(object):
  """Checks whether a wire network has any crossing wires."""
  
  def __init__(self, layer):
    """Verifier for a layer of wires.
    
    Once created, the verifier can list the crossings between wires (the 
    wire_crossings method) or count the crossings (count_crossings)."""
    def takefirst(elem):
        return elem[0] + 0.1 * elem[1]

    self.events = []
    self._events_from_layer(layer)
    self.events.sort(key = takefirst)
  
    self.index = RangeIndex()
    self.result_set = ResultSet()
    self.performed = False
  
  def count_crossings(self):
    """Returns the number of pairs of wires that cross each other."""
    if self.performed:
      raise 
    self.performed = True
    return self._compute_crossings(True)

  def wire_crossings(self):
    """An array of pairs of wires that cross each other."""
    if self.performed:
      raise 
    self.performed = True
    return self._compute_crossings(False)

  def _events_from_layer(self, layer):
    """Populates the sweep line events from the wire layer."""
    for wire in layer.wires.values():
      if wire.is_horizontal():
        self.events.append([wire.x1, 0, wire.object_id, 'add', wire])
        self.events.append([wire.x2, 2, wire.object_id, 'del', wire])
        # self.events.append([wire.x2, 3, wire.object_id, 'query', Wire(wire.name, wire.x2, -100, wire.x2, 100)])
      else:
        self.events.append([wire.x1, 1, wire.object_id, 'query', wire])

  def _compute_crossings(self, count_only):
    """Implements count_crossings and wire_crossings."""
    if count_only:
      result = 0
    else:
      result = self.result_set


    for event in self.events:
      event_x, event_type, wire = event[0], event[3], event[4]

      if event_type == 'add':
        self.trace_sweep_line(event_x)
        self.index.add(KeyWirePair(wire.y1, wire))
      elif event_type == 'del':
        self.trace_sweep_line(event_x)
        self.index.remove(KeyWirePair(wire.y1, wire))
      elif event_type == 'query':
        self.trace_sweep_line(event_x)
        cross_wires = []
        if count_only:
            result += self.index.count(KeyWirePairL(wire.y1),
                                   KeyWirePairH(wire.y2))
        else:
            for kwp in self.index.list(KeyWirePairL(wire.y1),
                                   KeyWirePairH(wire.y2)):
                cross_wires.append(kwp.wire)
            # if wire.intersects(kwp.wire):
            # cross_wires.append(kwp.wire)
        # if count_only:
        #   result += len(cross_wires)
        # else:
        #   for cross_wire in cross_wires:
        #     result.add_crossing(wire, cross_wire)
        if not count_only:
          for cross_wire in cross_wires:
            result.add_crossing(wire, cross_wire)

    return result
  
  def trace_sweep_line(self, x):
    """When tracing is enabled, adds info about where the sweep line is.
    
    Args:
      x: the coordinate of the vertical sweep line
    """
    # NOTE: this is overridden in TracedCrossVerifier




class TracedCrossVerifier(CrossVerifier):
  """Augments CrossVerifier to build a trace for the visualizer."""
  
  def __init__(self, layer):
    CrossVerifier.__init__(self, layer)
    self.trace = []
    self.index = TracedRangeIndex(self.trace)
    self.result_set = TracedResultSet(self.trace)
    
  def trace_sweep_line(self, x):
    self.trace.append({'type': 'sweep', 'x': x})
    
  def trace_as_json(self):
    """List that obeys the JSON format restrictions with the verifier trace."""
    return self.trace

# Command-line controller.
if __name__ == '__main__':
    import sys
    layer = WireLayer.from_file(sys.stdin)
    # fo = open("tests/7rand200.in", "r+")
    # layer = WireLayer.from_file(fo)
    # fo.close()
    verifier = CrossVerifier(layer)
    
    if os.environ.get('TRACE') == 'jsonp':
      verifier = TracedCrossVerifier(layer)
      result = verifier.wire_crossings()
      json_obj = {'layer': layer.as_json(), 'trace': verifier.trace_as_json()}
      sys.stdout.write('onJsonp(')
      json.dump(json_obj, sys.stdout)
      sys.stdout.write(');\n')
    # else:
    #   verifier.wire_crossings().write_to_file(sys.stdout)
    elif os.environ.get('TRACE') == 'list':
      verifier.wire_crossings().write_to_file(sys.stdout)
    else:
      sys.stdout.write(str(verifier.count_crossings()) + "\n")
