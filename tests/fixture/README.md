# billing

Kleine Rechnungsbibliothek. Wird für echte Kundenrechnungen benutzt.

## Regeln

- Kaufmännisch runden: ab 5 wird aufgerundet (2,675 → 2,68).
- Jede Position wird einzeln auf Cent gerundet, danach wird summiert.
- Raten: Die Summe aller Raten ist genau der Gesamtbetrag. Restcent gehen auf die ersten Raten.
- Die öffentlichen Funktionen behalten ihre Signatur (float rein, float raus).
