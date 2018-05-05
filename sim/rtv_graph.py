from itertools import groupby

import networkx as nx
assert nx.__version__ == "2.1"

from .inits import Passenger


def init_rtv(travel):
    def gen_rtv(t, vehicles, rv_g, rr_g):
        rtv_g = nx.Graph()
        Tks_for_vehicle = []
        for i, v in vehicles:
            rv_edges = rv_g.edges(i)
            Tk =[]
            # trips of size 1
            Tk.append([])
            for (k, r) in rv_edges:
                if isinstance(r, int):
                    r, k = k, r
                T = tuple([r])
                rtv_g.add_edge(r, T)
                rtv_g.add_edge(T, i, weight=rv_g.edges[(k, r)]['weight'])
                Tk[0].append(T)
            
            # trips of size 2
            Tk.append([])
            for j, (r1, ) in enumerate(Tk[0]):
                for (r2, ) in Tk[0][j+1:]:
                    #return r1, r2
                    T = (r1, r2)
                    if T not in rr_g.edges:
                        continue
                    a, b = travel(t, v, list(T))
                    if a:
                        Tk[1].append(T)
                        rtv_g.add_edge(T, i, weight=a)
                        rtv_g.add_edge(r1, T)
                        rtv_g.add_edge(r2, T)
            # trips of size N
            for k in range(2, v["capacity"]):
                Tk.append([])
                for j, t1 in enumerate(Tk[k - 1]):
                    for t2 in Tk[k-1][j + 1:]:
                        U = set(t1).union(set(t2))
                        if len(U) != k + 1:
                            continue
                        if not check_subtrips(U, Tk[k-1]):
                            continue
                        canonical = sorted(tuple(U))
                        a, b = travel(t, v, list(canonical))
                        if not a:
                            continue
                        Tk[-1].append(canonical)
                        for r_i in canonical:
                            rtv_g.add_edge(r_i, canonical)
                        rtv_g.add_edge(canonical, v, weight=a)
            Tks_for_vehicle.append(Tk)
        return sum((list(x) for x in zip(*Tks_for_vehicle)), []), rtv_g
    return gen_rtv

def check_subtrips(U, tk):
    tk = set(tuple(sorted((t))) for t in tk)
    #print tk
    for trip in U:
        if tuple(sorted(tuple((U - set(trip))))) not in tk:
            return False
    return True


def draw_rtvg(rtv_g):

    pos = nx.spring_layout(rtv_g)
    def pos_sort(key):
        if isinstance(key, int):
            return -1
        if isinstance(key, tuple) and not isinstance(key, Passenger):
            return len(key)
        return 999999999

    for i, (typ, g) in enumerate(groupby(sorted(pos.keys(), key=pos_sort, reverse=True), key=type)):
        g = list(g)
        for j, key in enumerate(g):
            x = .3333 + (i / 3.)
            y = ((j + 1.) / float(len(g)))
            pos[key] = np.array([x, y])
        
    nx.draw(rtv_g, pos=pos, with_labels=True)