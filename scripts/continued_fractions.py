def continued_fraction_encode(x, max_terms=20):
    """Encode a number as a continued fraction."""
    terms = []
    for _ in range(max_terms):
        a = int(x)
        terms.append(a)
        x -= a
        if x < 1e-9:
            break
        x = 1 / x
    return terms

def continued_fraction_decode(terms):
    """Decode a continued fraction [a0; a1, a2, ...] back to a number."""
    if not terms:
        return 0.0
    x = 0.0
    for term in reversed(terms[1:]):
        x = 1 / (term + x)
    return terms[0] + x


def _convergents(terms):
    """Compute successive convergents p_k / q_k for a continued fraction."""
    convergents = []
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    for a in terms:
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2
        convergents.append((p, q))
        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q
    return convergents


def _parse_value(raw: str) -> float:
    """Parse a CLI value argument as a float, a fraction (p/q), or an expression."""
    raw = raw.strip()
    if "/" in raw:
        num, _, den = raw.partition("/")
        return float(num) / float(den)
    try:
        return float(raw)
    except ValueError:
        # Fall back to evaluating simple arithmetic expressions like "pi" or "22/7".
        import math
        return float(eval(raw, {"__builtins__": {}}, {"pi": math.pi, "e": math.e}))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compute and analyze the continued fraction representation of a number."
    )
    parser.add_argument("value", help="Number or expression to analyze (e.g. 3.14159, 22/7, pi)")
    parser.add_argument("--depth", type=int, default=15, help="Maximum number of terms (default: 15)")
    args = parser.parse_args()

    x = _parse_value(args.value)
    terms = continued_fraction_encode(x, max_terms=args.depth)
    reconstructed = continued_fraction_decode(terms)
    convergents = _convergents(terms)

    print(f"Value:            {x}")
    print(f"Continued frac.:  [{terms[0]}; {', '.join(str(t) for t in terms[1:])}]")
    print(f"Terms:            {terms}")
    print(f"Reconstructed:    {reconstructed}")
    print(f"Abs. error:       {abs(x - reconstructed):.3e}")
    print("Convergents (p/q):")
    for i, (p, q) in enumerate(convergents):
        approx = p / q if q else float("inf")
        print(f"  [{i}] {p}/{q} = {approx}")
