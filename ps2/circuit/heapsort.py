to_be_sorted = [1, 2, 3, 4, 5, 6, 7, 8]


class make_heap():
    def __init__(self):
        self.heap = []

    def min_heapify(self):
        i = 1
        length = len(self.heap)
        while i <= length // 2:
            left = i * 2 - 1
            right = i * 2
            if left < length and self.heap[i - 1] < self.heap[left]:
                small = i - 1
            else:
                small = left
            if right < length and self.heap[small] > self.heap[right]:
                small = right
            if small == i - 1:
                return
            else:
                temp = self.heap[small]
                self.heap[small] = self.heap[i - 1]
                self.heap[i - 1] = temp
                i = small + 1

    def insert(self, num):
        self.heap.append(num)
        i = len(self.heap) - 1
        if i == -1:
            print("already null")
            return
        while self.heap[i] < self.heap[i // 2]:
            temp = self.heap[i]
            self.heap[i] = self.heap[i // 2]
            self.heap[i // 2] = temp
            i = i // 2

    def pop(self):
        if len(self.heap) == 0:
            return None
        temp = self.heap[0]
        self.heap[0] = self.heap[len(self.heap) - 1]
        self.heap.pop(len(self.heap) - 1)
        self.min_heapify()
        return temp


    def find_min(self):
        return self.heap[0]


a = make_heap()
for i in range(len(to_be_sorted)):
    a.insert(to_be_sorted[i])
a.insert(3)
b = a.pop()
while b != None:
    print(b)
    b = a.pop()