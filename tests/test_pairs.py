from fx_utils.pairs import MAJORS, unique_currency_pairs


def test_28_unique_pairs_from_8_currencies():
    pairs = unique_currency_pairs(MAJORS)
    assert len(pairs) == 28
    assert len(set(pairs)) == 28


def test_no_pair_repeats_a_currency_with_itself():
    pairs = unique_currency_pairs(MAJORS)
    assert all(a != b for a, b in pairs)


def test_every_currency_appears_in_exactly_seven_pairs():
    pairs = unique_currency_pairs(MAJORS)
    counts = {c: 0 for c in MAJORS}
    for a, b in pairs:
        counts[a] += 1
        counts[b] += 1
    assert all(count == 7 for count in counts.values())
