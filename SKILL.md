---
name: adaptive-multi-agent
description: Use when a task has several separable parts, when the user asks for multiple agents, an agent team, "mehrere Agenten", parallel work or specialised subagents, when subagents should rate their own difficulty and pick or change their model, or when a subagent reports that its part is harder than expected, keeps failing, or needs a stronger model.
---

# Adaptive Multi-Agent

Wie ein Orchester: Der Nutzer spricht nur mit dem Dirigenten (Hauptsitzung auf Fable 5.2 oder Opus 5.5). Der Dirigent zerlegt, verteilt, integriert und prüft; die Arbeit spielen die Agenten. Über das Modell stimmen sich beide ab: Der Dirigent schlägt eine Stufe vor, der Agent schätzt seine Teilaufgabe selbst ein und meldet die passende Stufe zurück, der Dirigent setzt sie um. Das Modell setzen kann nur der Dirigent, und nur beim Start eines Agenten.

Lokale Regeln zu Modellwahl oder Zahl paralleler Agenten (CLAUDE.md, andere Skills) gehen vor.

## Was technisch gilt (Claude Code, geprüft mit 2.1.323)

- `model` im Agent-Aufruf: `haiku`, `sonnet`, `opus`, `fable`. Der Wert im Aufruf schlägt Agentendefinition, `CLAUDE_CODE_SUBAGENT_MODEL` und Hauptmodell. Fehlt er, läuft der Agent meist auf dem teuren Hauptmodell.
- Ein laufender Agent kann sein Modell nicht wechseln. `SendMessage` setzt ihn auf demselben Modell fort. Stufenwechsel heißt immer: neuer Agent mit Übergabe.
- `subagent_type: "fork"` erbt das Hauptmodell, `model` wird ignoriert.
- Mehrere Agent-Aufrufe in einer Nachricht laufen gleichzeitig.

## Ablauf

1. **Ziel festlegen**: Ergebnis und Prüfkriterien in ein bis drei Sätzen.
2. **Selbst machen oder verteilen**: Bis etwa drei Werkzeug-Aufrufe, oder wenn der Auftrag länger wäre als die Arbeit: selbst erledigen, kein Agent.
3. **Zerlegen**: Teilaufgaben mit eigenem Ergebnis und eigenen Dateien. Keine zwei Agenten schreiben in dieselbe Datei. Unabhängige Teile in einer Nachricht starten, abhängige nacheinander. Höchstens vier gleichzeitig.
4. **Vorläufige Stufe** je Teil aus der Tabelle, `model` immer setzen.
5. **Auftrag** mit dem Baustein unten.
6. **Rückmeldung auswerten**: Selbsteinschätzung lesen. `ESKALATION`: neu starten. `KLÄRUNG`: entscheiden oder Nutzer fragen (siehe unten).
7. **Integrieren und prüfen**, Widersprüche selbst klären, Bericht mit Modell-Tabelle.

## Stufen

Je Kriterium 0 bis 2 Punkte: Umfang und Komplexität, Unsicherheit und fehlender Kontext, Abhängigkeiten, Folgen eines Fehlers, nötige Prüfung.

| Summe | Stufe | `model` |
|---|---|---|
| 0 bis 3 | einfach | `haiku` |
| 4 bis 6 | mittel | `sonnet` |
| 7 bis 10 | schwer | `opus` |
| `opus` nachweislich gescheitert, oder der Kern der ganzen Aufgabe | Spitze | `fable` |

Immer das günstigste Modell, das die Qualität sicher schafft. „Wichtig“ oder „eilig“ hebt die Stufe nicht. Folgen eines Fehlers = 2 (Geld, Kundendaten, Produktion, nicht umkehrbar): mindestens `sonnet` und unabhängige Prüfung. Passt ein Teil in zwei Stufen: zerlegen, der teure Teil bleibt klein.

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
FERTIG: Ergebnis, geänderte Dateien, wie geprüft (Befehl + Ausgabe), Nebenbefund.
ESKALATION: Ziel, Erkenntnisse (Datei:Zeile), bisherige Versuche und ihr Ergebnis,
offene Punkte, gewünschtes Modell und Grund in einem Satz.
KLÄRUNG: die zwei Vorgaben (Datei:Zeile), was jede Wahl bedeutet, deine Empfehlung.
Antworte knapp: nur Ergebnis und Belege, keine Datei-Inhalte, kein Nacherzählen des Auftrags.
```

## Eskalation und Rückstufung

- **Agent meldet ESKALATION**: neuen Agenten auf dem gewünschten Modell starten, höchstens eine Stufe pro Schritt über dem Bedarf. Der Auftrag enthält den ESKALATION-Block als Übergabe, damit nichts doppelt gelesen wird. Hat der erste Agent Dateien halb geändert: erst Stand klären.
- **Agent meldet KLÄRUNG**: Ein Widerspruch in den Vorgaben braucht eine Entscheidung, kein stärkeres Modell. Der Dirigent entscheidet oder fragt den Nutzer; die Entscheidung geht in den nächsten Auftrag.
- **Eskalation gegenprüfen**: Passt die gemeldete Punktsumme nicht zur Teilaufgabe (etwa hohe „Folgen“ bei reiner Beschreibung), startet der Dirigent nicht höher, sondern schärft den Auftrag.
- **Höchstens zwei Eskalationen** je Teilaufgabe. Danach übernimmt der Dirigent selbst oder fragt den Nutzer. Nie denselben Auftrag unverändert auf demselben Modell wiederholen.
- **Zeile EINSCHÄTZUNG fehlt**: per `SendMessage` nur diese Zeile nachfordern, nicht neu starten.
- **Agent meldet eine niedrigere Stufe**: weiterlaufen lassen, nicht neu starten. Für die nächsten ähnlichen Teile die Stufe senken.
- Im Bericht steht „neu gestartet auf `opus`“, nie „Modell gewechselt“.

## Token sparen

- Der Dirigent liest keine Dateien, die ein Agent lesen kann. Er bekommt Schlussfolgerungen, keine Auszüge.
- Aufträge nennen Pfade statt Inhalte einzukopieren. Übergaben sind der ESKALATION-Block, nicht der ganze Verlauf.
- Jeder Neustart kostet das Einlesen noch einmal: nur bei ESKALATION neu starten, nie zur Rückstufung.
- Ein Agent mit klarem Auftrag ist billiger als zwei mit überlappendem. Kein Agent „zur Sicherheit“.
- Der unabhängige Prüfer läuft nur bei schweren oder folgenreichen Teilen, sonst reicht der Testlauf.

## Prüfung

Eine Selbsteinschätzung oder „FERTIG“ ist kein Nachweis. Der Dirigent lässt Tests laufen, liest die Ausgabe oder prüft Quellen selbst nach. Bei schweren oder folgenreichen Teilen prüft ein **unabhängiger Agent** (neu gestartet, nicht der Autor, mindestens `sonnet`): Er bekommt Ziel, Prüfkriterien und das Ergebnis, nicht die Begründung des Autors, und soll Annahmen angreifen und Fehlerfälle suchen.

## Bericht

| Agent | Teilaufgabe | vorläufig | Selbsteinschätzung | gelaufen auf | Prüfung |
|---|---|---|---|---|---|

Dazu: Ergebnis, was geprüft wurde und wie, was offen ist.

## Häufige Fehler

| Fehler | Richtig |
|---|---|
| `model` weggelassen | immer setzen |
| Alles auf dem stärksten Modell, „zur Sicherheit“ | Stufe aus der Punktsumme |
| Agent per `SendMessage` „hochstufen“ | neuer Agent mit Übergabe |
| Kleine Aufgabe verteilt | selbst erledigen |
| Zwei Agenten an derselben Datei | Dateien je Agent trennen oder nacheinander |
| Prüfer bekommt die Begründung des Autors | nur Ziel, Kriterien, Ergebnis |
| Dritte Eskalation | Dirigent übernimmt oder fragt |
