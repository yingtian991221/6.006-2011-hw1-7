import imagematrix

class ResizeableImage(imagematrix.ImageMatrix):
    def best_seam(self):
        # raise NotImplemented
        # ccc = self.energy(0, 639)
        totseam = [[0 for i in range(self.width)] for j in range(self.height)]
        parent = [[0 for i in range(self.width)] for j in range(self.height)]
        # parent = [[0] * self.width] * self.height
        for i in range(self.width):
            totseam[0][i] = self.energy(i, 0)
            parent[0][i] = i
        for i in range(1, self.height):
            aaa = min(totseam[i-1][0], totseam[i-1][1])
            # bbb = self.energy(639, i)
            totseam[i][0] = min(totseam[i-1][0], totseam[i-1][1]) + self.energy(0, i)
            parent[i][0] = 0 if totseam[i-1][0] < totseam[i-1][1] else 1
            totseam[i][self.width-1] = min(totseam[i-1][self.width-2],
                                         totseam[i-1][self.width-1]) \
                                       + self.energy(self.width-1, i)
            parent[i][self.width-1] = self.width-1 \
                if totseam[i-1][self.width-1] < totseam[i-1][self.width - 2] else self.width-2
            for j in range(1, self.width - 1):
                curwin = [totseam[i-1][j-1], totseam[i-1][j], totseam[i-1][j+1]]
                totseam[i][j], parent[i][j] = min(curwin) + self.energy(j, i),\
                                              j - 1 + curwin.index(min(curwin))
        bestseam = []
        minind, mintot = 0, totseam[self.height-1][0]
        for j in range(0, self.width):
            if totseam[self.height-1][j] < mintot:
                mintot = totseam[self.height-1][j]
                minind = j
        j = minind
        for i in range(self.height, 0, -1):
            bestseam.insert(0, (j, i-1))
            j = parent[i-1][j]
        return bestseam


    def remove_best_seam(self):
        self.remove_seam(self.best_seam())
