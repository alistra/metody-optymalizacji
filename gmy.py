import optparse
import pymprog
from math import ceil
from itertools import chain, combinations
import time

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


parser = optparse.OptionParser()
parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False)
parser.add_option('-t', '--time', dest='time', action='store_true', default=False)
parser.add_option('-g', '--graph', dest='graph_file', metavar="FILE")
options, args = parser.parse_args()

class Dataset(object):
    def __init__(self, n, c, k, C, d=None):
        self.n = n
        self.c = c
        self.k = k
        self.C = C
        self.d = d
        self.V = range(1,n+1)
        self.E = c.keys()

    def solve_vrp(self):
        n, c, k, d, C, V, E = self.n, self.c, self.k, self.d, self.C, self.V, self.E
        def b(s):
            return int(ceil(float(sum(d[i] for i in s))/C))

        p = pymprog.model("vrp")
        x = p.var(E, 'x') # x created over index set E

        # set bounds
        for e in E:
            if 1 in e:
                0 <= x[e] <= 2
            else:
                0 <= x[e] <= 1

        # minimize the total travel distance
        p.min(sum(c[e]*x[e] for e in E), 'totaldist')

        p.st(sum(x[e] for e in E if e[0]==1) == 2*k)
        for i in V[1:]:
            adj = [e for e in E if i in e]
            if not adj:
                continue
            p.st(sum(x[e] for e in adj) == 2)
        for s in filter(lambda s: len(s)>1, powerset(V[1:])):
            p.st(sum(x[e] for e in E if (e[0] in s and e[1] not in s) or (e[0] not in s and e[1] in s)) >= 2*b(s))

        p.solve(float)
        if options.verbose:
            print "simplex done:", p.status()

        p.solve(int)

        if options.verbose:
            print(p.vobj())
            for e in E:
                if x[e].primal > 0:
                    print x[e].name, x[e].primal

        self.x = x

    def graph(self, filename):
        f = open(filename, 'w')
        lines = []
        for e in self.E:
            color = 'black'
            try:
                if self.x[e].primal > 0:
                    color = 'red'
            except AttributeError:
                pass
            lines.append('{0} -- {1} [label={2} color={3}]'.format(e[0], e[1], self.c[e], color))
        for v in self.V:
            if v in self.d:
                lines.append('{0} [label="{0} ({1})"]'.format(v, self.d[v]))

        lines = ['graph g {'] + lines + ['}']
        output = '\n'.join(lines)
        f.write(output)
        f.close()

class RandomDataset(Dataset):
    def __init__(self, n=4, k=1):
        import random
        d = {}
        c = {}
        C = 0
        for i in range(1, n+1):
            if i != 1:
                d[i] = random.randint(1, 100)
                C += d[i]
            for j in range(1, i):
                c[j,i] = random.randint(1, 100)
        
        super(RandomDataset, self).__init__(n=n, c=c, d=d, C=C, k=k)


d1 = Dataset(n = 16,
c = {(1,2):509, (1,3):501, (1,4):312, (1,5):1019, (1,6):736, (1,7):656, 
     (1,8): 60, (1,9):1039, (1,10):726, (1,11):2314, (1,12):479, 
     (1,13):448, (1,14):479, (1,15):619, (1,16):150, 
 (2,3):126, (2,4):474, (2,5):1526, (2,6):1226, (2,7):1133, 
     (2,8):532, (2,9):1449, (2,10):1122, (2,11):2789, (2,12):958, 
     (2,13):941, (2,14):978, (2,15):1127, (2,16):542, 
 (3,4):541, (3,5):1516, (3,6):1184, (3,7):1084, 
     (3,8):536, (3,9):1371, (3,10):1045, (3,11):2728, (3,12):913, 
     (3,13):904, (3,14):946, (3,15):1115, (3,16):499, 
 (4,5):1157, (4,6):980, (4,7):919, 
     (4,8):271, (4,9):1333, (4,10):1029, (4,11):2553, (4,12):751, 
     (4,13):704, (4,14):720, (4,15):783, (4,16):455, 
 (5,6):478, (5,7):583, 
     (5,8):996, (5,9):858, (5,10):855, (5,11):1504, (5,12):677, 
     (5,13):651, (5,14):600, (5,15):401, (5,16):1033, 
 (6,7):115, 
     (6,8):740, (6,9):470, (6,10):379, (6,11):1581, (6,12):271, 
     (6,13):289, (6,14):261, (6,15):308, (6,16):687, 
     (7,8):667, (7,9):455, (7,10):288, (7,11):1661, (7,12):177, 
     (7,13):216, (7,14):207, (7,15):343, (7,16):592, 
     (8,9):1066, (8,10):759, (8,11):2320, (8,12):493, 
     (8,13):454, (8,14):479, (8,15):598, (8,16):206, 
     (9,10):328, (9,11):1387, (9,12):591, 
     (9,13):650, (9,14):656, (9,15):776, (9,16):933, 
     (10,11):1697, 
     (10,12):333, (10,13):400, (10,14):427, (10,15):622, (10,16):610, 
     (11,12):1838, (11,13):1868, (11,14):1841, (11,15):1789, (11,16):2248, 
     (12,13): 68, (12,14):105, (12,15):336, (12,16):417, 
     (13,14): 52, (13,15):287, (13,16):406, 
     (14,15):237, (14,16):449, 
     (15,16):636},
k = 1,  # n of vehicles
C = 3,
d = {2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1, 11:1, 12:1, 13:1, 14:1, 15:1, 16:1})

d2 = Dataset(n=4,
    k = 1,
    C = 30,
    c = {(1,2): 4, (1,3): 5, (1,4): 7,
        (2,3): 61, (2,4): 2,
        (3,4): 5,
        },
    d = {2: 4, 3: 5, 4: 12})

for n in range(2, 20):
    for k in range(1, 5):
        start = time.clock()
        data = RandomDataset(n=n, k=k)
        try:
            data.solve_vrp()
        except RuntimeError:
            #print 'Infeasible'
            pass
        end = time.clock()
        if options.time: 
            print n, k, end-start

        if options.graph_file:
            data.graph('{0}_{1}_{2}.dot'.format(options.graph_file,n,k))


