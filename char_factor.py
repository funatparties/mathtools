from sympy.ntheory import factorint

"""
    Returns the characteristic factors of n.
"""
def char_factors(n: int):
    return reduce_char_factors(shanks_factorisation(n))


def shanks_factorisation(n: int) -> dict[int, list[int]]:
    """
    Uses the factorisation method described in [1] to produce
    the characteristic factors of the (Euler) totient of an integer n.

    This is equivalent to finding the primary decomposition of the modulo
    multiplication group M_n. The primary decomposition of M_n is precisely the 
    cyclic groups with orders given by these factors.

    1. For an integer n, factor as 2^m * p_i^a_i * ... where p_i are odd primes.
    2. If m >= 2, add the factor 2, then add 2^(m-2) if m > 2.
    3. Add the prime power factors of (p_i - 1), then add p_i^(a_i - 1) if a_i > 1.

    Ref: [1] Shanks, D. Solved and Unsolved Problems in Number Theory, 2nd ed. p. 93, 1978.
    """
    characteristic_factors = dict()
    # add a new factor p^a
    def _add_index(p, a):
        if p not in characteristic_factors:
            characteristic_factors[p] = [a]
        else:
            characteristic_factors[p].append(a)

    prime_factors = factorint(n)

    # for powers of 2:
    #   add 2 * 2^(a-2) for 2^a, a>=2
    pow_2 = prime_factors.pop(2, 0)
    if pow_2 >= 2:
        _add_index(2, 1)
    if pow_2 > 2:
        _add_index(2, pow_2 - 2)

    # for each odd prime:
    #   pull out and factor (p - 1)
    #   add each to char factors
    #   add p^a-1 to char factors if a > 1
    for (p,a) in prime_factors.items():
        if a > 1:
            _add_index(p, a - 1)
        lead_term_factors = factorint(p - 1)
        for (q,b) in lead_term_factors.items():
            _add_index(q, b)

    return {k:sorted(v) for (k,v) in characteristic_factors.items()}


def reduce_char_factors(characteristic_factors: dict[int, list[int]]) -> list[int]:
    """
    Reduces the characteristic factors to a shorter form by combining coprime
    elements.

    This is equivalent to converting a primary decomposition to an invariant factor
    decomposition.
    """
    reduced_factors = []
    while len(characteristic_factors) > 0:
        product = 1
        # multiply highest powers of each prime together
        for key in characteristic_factors:
            product *= key**(characteristic_factors[key].pop(-1))
        reduced_factors.append(product)
        # filter out any primes with no powers left
        characteristic_factors = {k:v for (k,v) in characteristic_factors.items() if len(v) > 0}
        
    return sorted(reduced_factors)
