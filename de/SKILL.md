---
name: adaptive-multi-agent
description: Use when a task has several separable parts, when the user asks for multiple agents, an agent team, "mehrere Agenten" or parallel work, when any subagent is about to be started, when routine work would run on the largest model, when a subagent says its part needs a stronger model, or when the user wants to save tokens.
---

# Adaptive Multi-Agent

Ziel: Token sparen und Ergebnisse maximieren. Jede Teilarbeit läuft auf dem günstigsten Modell, das sie sicher schafft, und nichts gilt ohne Prüfung als fertig.

Wie ein Orchester: Der Nutzer spricht nur mit dem Dirigenten (Hauptsitzung auf Fable 5.2 oder Opus 5.5). Der Dirigent zerlegt, verteilt, integriert und prüft; die Arbeit spielen die Agenten. Über das Modell stimmen sich beide ab: Der Dirigent schlägt eine Stufe vor, der Agent schätzt seine Teilaufgabe selbst ein und meldet die passende Stufe zurück, der Dirigent setzt sie um. Das Modell setzen kann nur der Dirigent, und nur beim Start eines Agenten.

Lokale Regeln zu Modellwahl oder Zahl paralleler Agenten (CLAUDE.md, andere Skills) gehen vor. Liegt neben dieser Datei eine `local.md`, lies sie zuerst: Ihre Regeln gelten zusätzlich und gehen vor.

## Kurzweg

1. Kleine Aufgabe (etwa drei Werkzeug-Aufrufe): selbst erledigen, kein Agent.
2. Sonst: in Teile mit getrennten Dateien zerlegen, jedem Agenten Namen, `model` und den Auftrags-Baustein geben.
3. Jede EINSCHÄTZUNG lesen, nur bei ESKALATION neu starten, prüfen, berichten, wer worauf lief.

## Was technisch gilt (Claude Code, geprüft mit 2.1.323)

- `model` im Agent-Aufruf: `haiku`, `sonnet`, `opus`, `fable`. Der Wert im Aufruf schlägt Agentendefinition, `CLAUDE_CODE_SUBAGENT_MODEL` und Hauptmodell. Fehlt er, läuft der Agent meist auf dem teuren Hauptmodell.
- Ein laufender Agent kann sein Modell nicht wechseln. `SendMessage` setzt ihn auf demselben Modell fort. Stufenwechsel heißt immer: neuer Agent mit Übergabe.
- `subagent_type: "fork"` erbt das Hauptmodell, `model` wird ignoriert.
- Mehrere Agent-Aufrufe in einer Nachricht laufen gleichzeitig.

## Ablauf: feste Reihenfolge

Die Phasen laufen immer in dieser Folge. Keine Phase wird übersprungen, eine kleine Aufgabe durchläuft sie nur kürzer.

1. **Lage**: Ziel und Prüfkriterien in ein bis drei Sätzen. Den echten Stand nachsehen (Dateien, Tests), nicht aus Notizen annehmen.
2. **Selbst oder verteilen**: Bis etwa drei Werkzeug-Aufrufe, oder wenn der Auftrag länger wäre als die Arbeit: selbst erledigen, kein Agent. Jeder Agent-Start kostet einen festen Sockel an Token (Systemkontext, Einlesen); Verteilen lohnt nur, wenn die Arbeit sonst den Kontext des Dirigenten füllen würde oder parallel laufen kann.
3. **Plan**: Teilaufgaben mit eigenem Ergebnis und eigenen Dateien, nummeriert und in Wellen geordnet. Zuerst, was andere blockiert (Fehler, fehlende Grundlage), dann der Rest. Gemischte Teile nach Art der Arbeit trennen (erst Recherche, dann Umsetzung), nicht nach Thema. Keine zwei Agenten schreiben in dieselbe Datei.
4. **Besetzung**: je Teil Name, vorläufige Stufe aus der Tabelle, `model` immer gesetzt, Auftrag mit dem Baustein unten.
5. **Ausführen in Wellen**: Alle Teile einer Welle in einer Nachricht starten (höchstens vier gleichzeitig). Die nächste Welle startet erst, wenn die vorige ausgewertet ist: Selbsteinschätzung lesen, `ESKALATION` neu starten, `KLÄRUNG` entscheiden oder Nutzer fragen.
6. **Prüfen**: Tests, Quellen, bei schweren Teilen unabhängiger Prüfer. Mängel gehen als neue Welle zurück in Phase 5.
7. **Bericht**: Ergebnisse zusammenführen, Widersprüche selbst klären, Tabelle mit Agent und Modell.

Dem Nutzer vor Phase 5 den Plan in Kurzform zeigen (Welle, Agent, Teilaufgabe, Modell) und ohne Rückfrage starten, außer ein Schritt ist nicht umkehrbar.

## Beispiel

Aufgabe: „CSV-Export für das Rechnungswerkzeug bauen, dokumentieren und die fehlschlagenden Rundungstests beheben.“

| Welle | Agent | Teilaufgabe | Punkte | Modell |
|---|---|---|---|---|
| 1 | Geige 1 | Export-Modul mit Tests, nur neue Dateien | 1+0+1+1+1 = 4 | `sonnet` |
| 1 | Harfe | API-Abschnitt im README | 0+0+1+1+1 = 3 | `haiku` |
| 1 | Cello | Rundungsfehler im Geld-Code | 1+2+1+2+2 = 8 | `opus` |
| 2 | Pauke | unabhängige Prüfung der Korrektur | – | `sonnet` |

Cello stellt fest, dass ein Test der schriftlichen Rundungsregel widerspricht, und meldet KLÄRUNG. Der Dirigent entscheidet, dass die Regel gilt, schreibt das in den nächsten Auftrag, und Cello macht fertig. Pauke rechnet die Beträge nach und meldet einen fehlenden Test. Der Dirigent ergänzt ihn, lässt die Tests laufen und berichtet.

Schwache Fassung derselben Arbeit: drei Agenten ohne `model` (alle auf dem Hauptmodell), die Korrektur auf das Wort des Autors hin abgenommen.

## Stufen

Je Kriterium 0 bis 2 Punkte: Umfang und Komplexität, Unsicherheit und fehlender Kontext, Abhängigkeiten, Folgen eines Fehlers, nötige Prüfung.

| Summe | Stufe | `model` |
|---|---|---|
| 0 bis 3 | einfach | `haiku` |
| 4 bis 6 | mittel | `sonnet` |
| 7 bis 10 | schwer | `opus` |
| `opus` nachweislich gescheitert, oder der Kern der ganzen Aufgabe | Spitze | `fable` |

Immer das günstigste Modell, das die Qualität sicher schafft. „Wichtig“ oder „eilig“ hebt die Stufe nicht. Folgen eines Fehlers = 2 (Geld, Kundendaten, Produktion, nicht umkehrbar): mindestens `sonnet` und unabhängige Prüfung. Passt ein Teil in zwei Stufen: zerlegen, der teure Teil bleibt klein. Ist ein Modell nicht verfügbar: nächstes verfügbares darunter nehmen und es einmal im Bericht sagen. Vor einem `fable`-Agenten den Nutzer fragen.

Dirigent auf Fable 5.2 oder Opus 5.5: Die Hauptsitzung ist die teuerste Stufe. Sie plant, schreibt Aufträge, entscheidet und prüft Stichproben; Lesen, Suchen, Zählen und Umsetzen nach Plan gibt sie ab. `fable` als Agent ist die Ausnahme, nicht der Ersatz für `opus`. Ist `fable` im Konto nicht verfügbar, endet die Leiter bei `opus`, darüber übernimmt der Dirigent selbst.

## Namen im Orchester

Jeder Agent bekommt einen Namen nach seiner Rolle, mehrere gleiche werden durchgezählt (Geige 1, Geige 2). Der Name steht vorn in `description` („Geige 1: CSV-Export“), im Auftrag („Du bist Geige 1“) und im Bericht. So sieht der Nutzer, wer was spielt. Ein neu gestarteter Agent behält den Namen und bekommt das neue Modell dazu („Cello, neu gestartet auf `opus`“).

| Rolle | Name |
|---|---|
| Lesen, Suchen, Zählen | Flöte |
| Recherche, Quellen | Klarinette |
| Umsetzen, Code, Uploads | Geige |
| Texte, Doku | Harfe |
| Schwerer Kern, Architektur, Fehlersuche | Cello |
| Unabhängige Prüfung | Pauke |

## Auftrags-Baustein

Jeder Auftrag enthält: Ziel, schon Geklärtes, genaue Dateien oder Ordner (und was tabu ist), erwartetes Ergebnis, Prüfkriterien. Dazu wörtlich:

```
Du bist <Name>. Du läufst auf dem Modell: <haiku|sonnet|opus|fable>. Du kannst es nicht selbst wechseln.
Schritt 1, vor jeder Änderung: Lies das Nötige und bewerte NUR deine eigene Teilaufgabe,
nicht das Projekt drumherum. Fünf Kriterien, je 0-2 Punkte:
1 Umfang und Komplexität, 2 Unsicherheit, 3 Abhängigkeiten,
4 Folgen, wenn DEIN Ergebnis falsch ist, 5 nötige Prüfung.
Summe 0-3 = haiku, 4-6 = sonnet, 7-10 = opus.
Liegt die nötige Stufe über deinem Modell: ändere nichts, STATUS ESKALATION.
Kannst du zwei Vorgaben nicht zugleich erfüllen: ändere nichts dazu, STATUS KLÄRUNG.
Bleibt derselbe Fehler nach zwei Versuchen: STATUS ESKALATION.
Fehler oder Widersprüche außerhalb deines Auftrags halten dich nicht auf: arbeite fertig
und nenne sie unter "Nebenbefund".

Deine Antwort beginnt immer mit:
EINSCHÄTZUNG: <fünf Punktwerte> = <Summe> -> nötig: <Modell>; ich laufe auf: <Modell>
STATUS: FERTIG | ESKALATION | KLÄRUNG
FERTIG: Ergebnis, geänderte Dateien, wie geprüft (Befehl + Ausgabe), was nur angenommen
und nicht geprüft ist, Nebenbefund.
ESKALATION: Ziel, Erkenntnisse (Datei:Zeile), was versucht wurde und warum es scheiterte,
mögliche Richtungen, offene Punkte, gewünschtes Modell und Grund in einem Satz.
KLÄRUNG: die zwei Vorgaben (Datei:Zeile), was jede Wahl bedeutet, deine Empfehlung.
Antworte knapp: nur Ergebnis und Belege, keine Datei-Inhalte, kein Nacherzählen des Auftrags.
```

## Eskalation und Rückstufung

- **Agent meldet ESKALATION**: neuen Agenten auf dem gewünschten Modell starten, höchstens eine Stufe pro Schritt über dem Bedarf. Der Auftrag enthält den ESKALATION-Block als Übergabe, damit nichts doppelt gelesen wird. Hat der erste Agent Dateien halb geändert: erst Stand klären.
- **Agent meldet KLÄRUNG**: Ein Widerspruch in den Vorgaben braucht eine Entscheidung, kein stärkeres Modell. Der Dirigent entscheidet oder fragt den Nutzer; die Entscheidung geht in den nächsten Auftrag.
- **Eskalation gegenprüfen**: Passt die gemeldete Punktsumme nicht zur Teilaufgabe (etwa hohe „Folgen“ bei reiner Beschreibung), startet der Dirigent nicht höher, sondern schärft den Auftrag.
- **Höchstens zwei Eskalationen** je Teilaufgabe. Scheitert auch die höhere Stufe, ist der Teil meist falsch zugeschnitten, nicht das Modell zu schwach: neu zerlegen. Danach übernimmt der Dirigent selbst oder fragt den Nutzer. Nie denselben Auftrag unverändert auf demselben Modell wiederholen.
- **Fertige Agenten bekommen keine neue Aufgabe.** `SendMessage` nur für Unfertiges oder Fehlendes. Eine Nachricht erreicht einen laufenden Agenten erst, wenn er pausiert: alles Nötige gehört in den ersten Auftrag.
- **Zeile EINSCHÄTZUNG fehlt**: per `SendMessage` nur diese Zeile nachfordern, nicht neu starten.
- **Agent meldet eine niedrigere Stufe**: weiterlaufen lassen, nicht neu starten. Für die nächsten ähnlichen Teile die Stufe senken.
- Im Bericht steht „neu gestartet auf `opus`“, nie „Modell gewechselt“.

## Lange Aufgaben: Stand in einer Datei

Bei mehr als zwei Wellen, oder wenn die Arbeit eine Sitzung überdauern kann, führt der Dirigent eine Stand-Datei `.orchestra/<aufgabe>.md` im Projekt: Ziel und Prüfkriterien, Plan mit Wellen, je Teil Agent, Modell und Status, Entscheidungen aus KLÄRUNG, Eskalationen. Er aktualisiert sie nach jeder Welle. Nach einer Unterbrechung oder Kontext-Kürzung liest er zuerst diese Datei und setzt dort fort. Große Ergebnisse schreiben Agenten in Dateien und melden nur den Pfad.

## Token sparen

- Der Dirigent liest keine Dateien, die ein Agent lesen kann. Er bekommt Schlussfolgerungen, keine Auszüge.
- Aufträge nennen Pfade statt Inhalte einzukopieren. Übergaben sind der ESKALATION-Block, nicht der ganze Verlauf.
- Jeder Neustart kostet das Einlesen noch einmal: nur bei ESKALATION neu starten, nie zur Rückstufung.
- Ein Agent mit klarem Auftrag ist billiger als zwei mit überlappendem. Kein Agent „zur Sicherheit“.
- Der unabhängige Prüfer läuft nur bei schweren oder folgenreichen Teilen, sonst reicht der Testlauf.

## Prüfung

Eine Selbsteinschätzung oder „FERTIG“ ist kein Nachweis. Der Dirigent lässt Tests laufen, liest die Ausgabe oder prüft Quellen selbst nach. Er vergleicht die geänderten Dateien mit den erlaubten (in Git: `git diff --name-only`). Bei schweren oder folgenreichen Teilen prüft ein **unabhängiger Agent** (neu gestartet, nicht der Autor, mindestens `sonnet`): Er bekommt Ziel, Prüfkriterien und das Ergebnis, nicht die Begründung des Autors, und soll Annahmen angreifen und Fehlerfälle suchen.

## Bericht

| Agent | Teilaufgabe | vorläufig | Selbsteinschätzung | gelaufen auf | Prüfung |
|---|---|---|---|---|---|

Dazu: Ergebnis, was geprüft wurde und wie, was offen ist. Der Bericht endet mit einer Zeile: „Nicht geprüft: …“ (oder „Nicht geprüft: nichts“).

## Ausreden und was stattdessen gilt

| Ausrede | Richtig |
|---|---|
| „`model` lasse ich weg, der Standard passt“ | immer setzen; der Standard ist das teure Hauptmodell |
| „Alles auf Opus, zur Sicherheit“ | Stufe aus der Punktsumme; Sicherheit kommt aus der Prüfung, nicht aus dem Modell |
| „Ich schreibe dem Agenten, er soll gründlicher denken“ | ein laufender Agent behält sein Modell; neuer Agent mit Übergabe |
| „Verteilen ist sauberer“ bei drei Aufrufen | selbst erledigen; jeder Agent-Start kostet einen festen Sockel |
| „Die kommen sich nicht in die Quere“ bei einer Datei | Dateien je Agent trennen oder nacheinander |
| „Der Prüfer soll wissen, warum der Autor es so gemacht hat“ | nur Ziel, Kriterien, Ergebnis |
| „Eine Eskalation noch“ (die dritte) | der Teil ist falsch zugeschnitten: neu zerlegen, übernehmen oder fragen |
| „Der Agent hat FERTIG gemeldet“ | die Prüfung selbst laufen lassen |
