from sympy import igcd
from sympy.ntheory import divisors
from sympy.functions.combinatorial.numbers import totient
from sympy.combinatorics import CyclicGroup, Coset, PermutationGroup, Permutation
from typing import NamedTuple
import networkx as nx

class QuotientGroup(NamedTuple):
    G1: int
    G2: int
    order: int

class GoursatTuple(NamedTuple):
    G1: int
    G2: int
    H1: int
    H2: int
    order: int

TupleSubgroup = list[tuple[Permutation, Permutation]]

def subgroups_of_cycle_product_order(n: int, m: int)  -> list[TupleSubgroup]:
    assert n > 0 and m > 0, "orders must be positive"
    # shortcut the trivial products
    if n == 1:
        return [[(Permutation(0), e) for e in g.elements] for g in subgroups_of_cyclic_order(m).values()]
    if m == 1:
        return [[(e, Permutation(0)) for e in g.elements] for g in subgroups_of_cyclic_order(n).values()]
    G = CyclicGroup(n)
    H = CyclicGroup(m)
    return subgroups_of_cycle_product(G, H)


def subgroups_of_cycle_product(G: PermutationGroup, H: PermutationGroup) -> list[TupleSubgroup]:
    """
    Compute the subgroups of a direct product of two cyclic groups with orders
    n and m.

    Algorithm developed using the idea derived from Goursat's lemma in [1] and 
    simplifications from properties of cyclic groups.

    Ref: [1] https://math.stackexchange.com/questions/485512/subgroups-of-a-direct-product
    """
    assert G.is_cyclic and H.is_cyclic, "Groups must be cyclic"
    
    subgroups: list[TupleSubgroup] = []
    o_G = G.order()
    g = G.generators[0]
    o_H = H.order()
    h = H.generators[0]

    tuples = _generate_tuples(o_G, o_H)
    for t in tuples:
        # subgroup of G with order n can be gnerated by g**(G.order()/n) where g is a generator of G
        G1 = G.subgroup([g**(o_G//t.G1)])
        G2 = G.subgroup([g**(o_G//t.G2)])
        H1 = H.subgroup([h**(o_H//t.H1)])
        H2 = H.subgroup([h**(o_H//t.H2)])
        # this is probably slow but numbers should all be small
        # add max statement for case where order = 1
        coprimes = [i for i in range(1, max(t.order, 2)) if igcd(i, t.order) == 1]
        assert len(coprimes) == totient(t.order), f'Error finding coprimes, expected {totient(t.order)}, found {len(coprimes)}'

        for j in coprimes:
            f: Isomorphism = (G1.generators[0], H1.generators[0]**j)
            sub = _subgroup_from_tuple(G1, G2, H1, H2, f)
            subgroups.append(sub)
    return subgroups


def _generate_tuples(n: int, m: int) -> list[GoursatTuple]:
    """
        Generate tuples that correspond to subgroups as per [1]
    """
    quotients_G = _subquotients(n)
    quotients_H = _subquotients(m)
    # find all pairs with equal order
    pairs = [(a,b) for a in quotients_G for b in quotients_H if a.order == b.order]
    # create tuples
    return [GoursatTuple(a.G1, a.G2, b.G1, b.G2, a.order) for (a,b) in pairs]


def _subquotients(n: int) -> list[QuotientGroup]:
    """
    Find the subquotients of a cycle group of order n.
    """
    return [QuotientGroup(a, b, a//b) for a in divisors(n) for b in divisors(a)]


Isomorphism = tuple[Permutation, Permutation]
"""An isomorphism between two cyclic groups where the first generator is mapped to the second."""

def _subgroup_from_tuple(G1: PermutationGroup, G2: PermutationGroup, H1: PermutationGroup, H2: PermutationGroup, f: Isomorphism) -> TupleSubgroup:
    """
    Initially:
        Select generator of G1 g.
        Identify all generators of H1 in distinct cosets of H2.
        generators will all be of the form h^a where h is a generator and a is coprime to the order of H1.
    There should be a number of these equal to the number of isomorphisms from G1/G2 -> H1/H2
    For each isomorphism G1/G2 -> H1/H2 that exists:
        Select isomorphism f by selecting a generator h of H1 to map g onto.
        Generate cosets of G2 by multiplying by g.
        Pair them with the cosets of H2 generated by multiplication by h.
        (i.e. f((g^n)G2) = (h^n)H2 for all n).
        Enumerate all pairs of elements in each pair of cosets.
    """
    g = f[0]
    h = f[1]
    assert G1.is_cyclic and H1.is_cyclic, "Groups must be cyclic"
    assert G1.contains(g) and H1.contains(h), "Isomorphism generators must be from G1 and H1"

    # iterating up to index should generate all cosets
    index = G1.order()//G2.order()
    coset_maps = {Coset(g**i, G2, G1): Coset(h**i, H2, H1) for i in range(index)}

    # make sure the cosets cover the whole group
    coset_coverage = {e for coset in coset_maps.keys() for e in coset.as_list()}
    assert coset_coverage == set(G1.elements), "Failure generating cosets of G2 in G1"
    coset_coverage = {e for coset in coset_maps.values() for e in coset.as_list()}
    assert coset_coverage == set(H1.elements), "Failure generating cosets of H2 in H1"

    elements = []
    for k,v in coset_maps.items():
        pairs = [(a,b) for a in k.as_list() for b in v.as_list()]
        elements.extend(pairs)
    return elements


def subgroups_of_cyclic_order(n: int) -> dict[int, PermutationGroup]:
    """
    Return a dictionary of all subgroups of the cyclic group of order n.
    Dict keys are the group orders and values are the permutation groups.
    Includes the trivial group and entire group.
    """
    return subgroups_of_cyclic_group(CyclicGroup(n))


def subgroups_of_cyclic_group(G: PermutationGroup) -> dict[int, PermutationGroup]:
    """
    Return a dictionary of all subgroups of the given cyclic group G.
    Dict keys are the group orders and values are the permutation groups.
    Includes the trivial group and G itself.
    """
    assert G.is_cyclic, "G must be a cyclic group"
    o = G.order()
    g = G.generators[0]
    # subgroups are all cycles with order that divide the group order.
    # they can be generated by powers of the group generator.
    return {o//i : G.subgroup([g**i]) for i in divisors(o)}


def enumerate_cosets(G: PermutationGroup, H: PermutationGroup) -> list[Coset]:
    """
    Generate an explicit list of cosets of H in G.
    Includes H itself.
    """
    representatives = G.coset_transversal(H)
    cosets = []
    for g in representatives:
        cosets.append(Coset(g,H,G))
    return cosets


def generate_hasse_graph(l: list[TupleSubgroup]):
    ls = [set(e) for e in l]
    edges = [(a,b) for a in range(len(ls)) for b in range(len(ls)) if a != b and ls[b].issubset(ls[a])]
    g = nx.DiGraph(edges)
    return nx.transitive_reduction(g)