from collections import OrderedDict
from sympy.combinatorics import PermutationGroup, Permutation, CyclicGroup
import igraph as ig
import matplotlib.pyplot as plt

"""
    Generate the maximal cycles of the group.

    Have not yet proved correctness but seems good.

    1. take element of highest order
    2. generate cycle
    3. remove elements that occur in cycle
    4. repeat until all elements gone
"""
def generate_maximal_cycles(G: PermutationGroup):
    cycles = []
    # elements sorted by order
    elements = OrderedDict(sorted({e:e.order() for e in G.elements}.items(), key=lambda item:item[1]))
    i = 0
    while len(elements) > 0:
        i += 1
        (g, order) = elements.popitem(last=True)
        print(f'Iteration {i}: generating cycle for {g}')
        #sanity check
        assert (g**order).is_identity, f'Order for permuation {g} is incorrect, {g}**{order}={g**order} which is not identity'

        cycle = [g**i for i in range(order)]
        cycles.append(cycle)

        # remove generated elements
        elements = OrderedDict(sorted({k:v for (k,v) in elements.items() if k not in cycle}.items(), key=lambda item:item[1]))
    return cycles


def generate_permuation_cycle(g: Permutation):
    return [g**i for i in range(g.order())]


def generate_graph_from_cycles(cycles: list[list[Permutation]]):
    g = ig.Graph()
    # need to add vertices first or igraph freaks out
    vs = set([str(e) for cycle in cycles for e in cycle])
    # does strange things if you pass a set
    g.add_vertices(list(vs))

    for cycle in cycles:
        print(f'Adding {cycle} to graph')
        edges = [(str(cycle[i]), str(cycle[i+1])) for i in range(len(cycle) - 1)]
        edges.append((str(cycle[-1]), str(cycle[0])))
        g.add_edges(edges)
    return g


def test_plot(graph: ig.Graph):
    fig, ax = plt.subplots(figsize=(5,5))
    ig.plot(
        graph,
        target=ax,
        layout="fruchterman_reingold",
        vertex_size=30,
        vertex_color="steelblue",
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        # vertex_label=g.vs["name"],
        vertex_label_size=7.0,
    )
    plt.show()


def test():
    c = generate_maximal_cycles(CyclicGroup(2)*CyclicGroup(4))
    g = generate_graph_from_cycles(c)
    test_plot(g)