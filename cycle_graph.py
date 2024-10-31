from collections import OrderedDict
from sympy.combinatorics import PermutationGroup, Permutation, CyclicGroup
import networkx as nx
import matplotlib.pyplot as plt

def generate_maximal_cycles(G: PermutationGroup):
    """
    Generate the maximal cycles of the group.

    Have not yet proved correctness but seems right.

    1. take element of highest order
    2. generate cycle
    3. remove elements that occur in cycle
    4. repeat until all elements gone
    """
    cycles = []
    # elements sorted by order
    elements = OrderedDict(sorted({e:e.order() for e in G.elements}.items(), key=lambda item:item[1]))
    i = 0
    while len(elements) > 0:
        i += 1
        (g, order) = elements.popitem(last=True)
        #print(f'Iteration {i}: generating cycle for {g}')
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
    g = nx.Graph()

    for cycle in cycles:
        # edge for each adjacent pair
        g.add_edges_from([(str(cycle[i]), str(cycle[i+1])) for i in range(len(cycle) - 1)])
        g.add_edge(str(cycle[-1]), str(cycle[0]))
    return g