"""Rechnungsberechnung. Alle Beträge in Euro (float rein, float raus)."""


def line_total(qty, unit_price, discount_pct=0):
    gross = qty * unit_price
    return round(gross - gross * discount_pct / 100, 2)


def invoice_total(lines, vat_rate=19):
    net = sum(line_total(*line) for line in lines)
    vat = round(net * vat_rate / 100, 2)
    return round(net + vat, 2)


def split_payment(total, n):
    part = round(total / n, 2)
    return [part] * n
