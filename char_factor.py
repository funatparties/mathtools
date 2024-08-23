from sympy.ntheory import factorint

"""
    Uses the factorisation method described by Daniel Shanks (1978) to produce
    the characteristic factors of the (Euler) totient of an integer n.

    This is equivalent to finding the primary decomposition of the modulo
    multiplication group M_n. The primary decomposition of M_n is precisely the 
    cyclic groups with orders given by these factors.

    For an integer n, factor as 2^m * p_i^a_i * ... where p_i are odd primes.
    if m >= 2, add the factor <2>, then add <2^(m-2)> if m > 2.
    Add the prime power factors of (p_i - 1), then add <p_i^(a_i - 1)> if a_i > 1.
"""
def shanks_factorisation(n: int) -> dict[int, list[int]]:
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


"""
    Reduces the characteristic factors to a shorter form by combining coprime
    elements.

    This is equivalent to converting a primary decomposition to an invariant factor
    decomposition.
"""
def reduce_char_factors(characteristic_factors: dict[int, list[int]]) -> list[int]:
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
        

def factors(n: int):
    return reduce_char_factors(shanks_factorisation(n))

"""
    Shanks factorisation as above but returns in list form
"""
def shanks_factorisation_list(n: int) -> list[int]:
    characteristic_factors = []
    prime_factors = factorint(n)

    # for any power of 2:
    #   add 2 for 2^2
    #   add 2 * 2^(a-2) for 2^a, a>2
    #   nothing otherwise
    pow_2 = prime_factors.pop(2, 0)
    if pow_2 >= 2:
        characteristic_factors.append(2)
    if pow_2 > 2:
        characteristic_factors.append(2**(pow_2 - 2))

    # for each odd prime:
    #   pull out and factor (p - 1)
    #   add each to char factors
    #   add p^a-1 to char factors if a > 1
    for (p,a) in prime_factors.items():
        if a > 1:
            characteristic_factors.append(p**(a-1))
        lead_term_factors = factorint(p - 1)
        for (q,b) in lead_term_factors.items():
            characteristic_factors.append(q**b)

    return characteristic_factors