from billing import line_total, invoice_total, split_payment


def test_line_total_half_up():
    assert line_total(1, 2.675) == 2.68


def test_line_total_discount():
    assert line_total(3, 19.99, 10) == 53.97


def test_invoice_total_small_lines():
    assert invoice_total([(1, 0.335), (1, 0.335)], vat_rate=0) == 0.67


def test_invoice_total_vat():
    assert invoice_total([(2, 10.00)], vat_rate=19) == 23.80


def test_split_payment_sums_to_total():
    parts = split_payment(100.00, 3)
    assert parts == [33.34, 33.33, 33.33]
    assert round(sum(parts), 2) == 100.00
