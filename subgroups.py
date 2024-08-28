from sympy.ntheory import divisors
from sympy.functions.combinatorial.numbers import totient
from collections import namedtuple

QuotientGroup = namedtuple('QuotientGroup', 'G1, G2, order')
# n_phi is the number of isomorphisms that exist
GoursatTuple = namedtuple('GoursatTuple', 'G1, G2, H1, H2, n_phi')

"""
    Compute the subgroups of a direct product of two cyclic groups with orders
    n and m.

    Algorithm by using Goursat's lemma and properties of cyclic groups.

    Ref: https://math.stackexchange.com/questions/485512/subgroups-of-a-direct-product
"""
def subgroups_of_cycle_product(n: int, m: int):
    quotients_a = subquotients(n)
    quotients_b = subquotients(m)
    # find all pairs with equal order
    pairs = [(a,b) for a in quotients_a for b in quotients_b if a.order == b.order]
    # create tuples
    tuples = [GoursatTuple(a.G1, a.G2, b.G1, b.G2, totient(a.order)) for (a,b) in pairs]
    # TODO: convert to subgroups
    return tuples

"""
    Find the subquotients of a cycle group of order n.
"""
def subquotients(n: int):
    return [QuotientGroup(a, b, a//b) for a in divisors(n) for b in divisors(a)]