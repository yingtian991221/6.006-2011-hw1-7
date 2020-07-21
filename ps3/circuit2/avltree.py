tobeop = [1, 2, 3]

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
        a = x.lchild
        y = x.rchild
        b = y.lchild
        c = y.rchild

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
        c = y.rchild
        a = x.lchild
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
        while type(iterator) != emptynode and iterator.key != key:
            # prev = iterator
            if iterator.key > key:
                iterator = iterator.lchild
            elif iterator.key < key:
                iterator = iterator.rchild
            else:
                return iterator
        if iterator is None:
            raise ValueError('Not found value')
        else:
            return iterator

    def remove(self, key):
        tbr = self.search(key)
        if tbr.subnum == 1 and tbr.parent == self.root:
            self.root = Root()
            return
        x = tbr.lchild
        y = tbr.rchild
        if type(x) == emptynode:
            if tbr.parent.lchild == tbr:
                tbr.parent.lchild = y
            elif tbr.parent.rchild == tbr:
                tbr.parent.rchild = y
            else:
                raise ValueError('not pair')
            x.parent = tbr.parent
            y.parent = tbr.parent
            self.rebalance(y)
        elif type(y) == emptynode:
            if tbr.parent.lchild == tbr:
                tbr.parent.lchild = x
            elif tbr.parent.rchild == tbr:
                tbr.parent.rchild = x
            else:
                raise ValueError('not pair')
            x.parent = tbr.parent
            y.parent = tbr.parent
            self.rebalance(x)
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
                else:
                    tbr.parent.rchild = prev
                prev.height = max(prev.lchild.height, prev.rchild.height) + 1
                self.rebalance(prev)
            else:
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
                self.rebalance(parent)


    def addlist(self, cur, first_key, last_key):
        if type(cur) == emptynode:
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
        while type(iterator) != emptynode:
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


ri = RangeIndex()
ri.add(-50)
ri.add(-100)
ri.add(0)
ri.remove(-50)
ri.add(20)
ri.add(-80)
ri.remove(-100)
ri.remove(0)
ri.remove(-80)


print(ri)
