# Trainings-Findings

Stand: 2026-06-11

## Ziel der Evaluation

Wir vergleichen alte und neu trainierte Modellstände für die binäre Klassifikation:

- `edible`
- `non_edible`

Das Modell ist nicht als finale Wegwerfentscheidung gedacht, sondern als Assistenzsystem im Business-Workflow:

1. Bildaufnahme oder Videoframe.
2. Freshify klassifiziert das Gesamtbild als `edible` oder `non_edible`.
3. Optional: Der MobileSAM-Detailmodus segmentiert Produktbereiche als Overlay.
4. Auffällige Fälle gehen in Human Review.

Deshalb ist nicht nur Accuracy wichtig. Je nach Business-Priorität sind andere Metriken entscheidend.

## Datensatzstand

Aktuelle Struktur:

```text
data/
  train/
    edible/<kategorie>/
    non_edible/<kategorie>/
  val/
    edible/<kategorie>/
    non_edible/<kategorie>/
  new_raw/
```

Unterstützte Kategorien:

- Banane
- Erdbeere
- Gurke
- Orange
- Paprika
- Zitrone

Train/Val-Verteilung:

| Split | Label | Gesamt | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train | edible | 235 | 80 | 22 | 40 | 56 | 27 | 10 |
| train | non_edible | 178 | 46 | 10 | 28 | 46 | 36 | 12 |
| val | edible | 34 | 9 | 5 | 7 | 6 | 5 | 2 |
| val | non_edible | 28 | 8 | 3 | 2 | 5 | 9 | 1 |

Gesamt:

| Split | edible | non_edible | Gesamt |
|---|---:|---:|---:|
| train | 235 | 178 | 413 |
| val | 34 | 28 | 62 |
| new_raw | 0 | 14 | 14 |

Wichtige Einordnung:

- `data/val` enthält beide Klassen und ist deshalb die wichtigste Quelle für Accuracy, Precision, Recall und Confusion Matrix.
- `data/new_raw` enthält aktuell nur 14 neue `non_edible` Smartphonebilder. Das ist ein zusätzlicher Real-World-Check, aber keine vollständige Accuracy-Messung.
- Der Datensatz ist klein und pro Kategorie ungleich verteilt.
- Zitrone und Erdbeere sind besonders schwach vertreten.
- Bei `val/non_edible` gibt es für Zitrone nur 1 Bild und für Gurke nur 2 Bilder. Einzelne Fehler können die Metriken stark bewegen.

## Modellartefakte im Repo

Alte Modellstände:

- `models/freshify_old_final_demo.keras`
- `models/freshify_old_standard_augmentation.keras`
- `models/freshify_old_background_augmentation.keras`

Neue Modellstände nach Re-Training auf dem aktuellen Datensatz:

- `models/freshify_new_no_augmentation.keras`
- `models/freshify_new_standard_augmentation.keras`
- `models/freshify_new_background_augmentation.keras`

Aktuelle Kompatibilitätsnamen:

- `models/freshify_final.keras`
- `models/freshify_standard_augmentation.keras`
- `models/freshify_background_augmentation.keras`

Hinweis: `freshify_final.keras` sollte erst nach bewusster Entscheidung auf ein Modell zeigen. Aktuell ist die Entscheidung noch fachlich zu treffen.

## Threshold

Alle folgenden Werte wurden mit Threshold `0.35` verglichen.

```text
probability_non_edible >= 0.35 -> non_edible
probability_non_edible < 0.35  -> edible
```

Ein niedriger Threshold macht das Modell vorsichtiger:

- weniger übersehene `non_edible` Bilder
- mehr essbare Bilder, die fälschlich als auffällig markiert werden

Für unseren Human-in-the-loop Use Case kann ein niedriger Threshold sinnvoll sein, aber nur solange die False Positives nicht zu hoch werden.

## Welche Metrik ist für welche Entscheidung wichtig?

| Frage | Wichtigste Metriken |
|---|---|
| Übersehen wir verdorbene Lebensmittel? | Recall `non_edible`, False Negatives `non_edible` |
| Markieren wir zu viele gute Lebensmittel als schlecht? | False Positives `non_edible`, Recall `edible` |
| Ist das Modell insgesamt stabil auf dem Val Set? | Validation Accuracy, beide Recalls zusammen |
| Funktioniert es auf neuen Handyfotos? | Trefferquote auf `data/new_raw`, aber nur als Zusatzsignal |

## Business-Priorität

Für unseren geplanten Workflow ist ein False Negative kritischer als ein False Positive.

Begründung:

- False Negative: Ein tatsächlich verdorbenes Lebensmittel wird als `edible` durchgelassen.
- False Positive: Ein eigentlich essbares Lebensmittel wird als auffällig markiert und landet im Human Review.

Da nach dem Modell noch ein menschlicher Check vorgesehen ist, sind einige False Positives fachlich akzeptabler als übersehene `non_edible` Fälle. Das bedeutet aber nicht, dass False Positives egal sind. Wenn zu viele gute Lebensmittel im Review landen, wird der Prozess ineffizient und die Akzeptanz sinkt.

Praktische Zielrichtung:

- Priorität 1: `non_edible` Recall hoch halten.
- Priorität 2: False Positives so weit senken, dass Human Review realistisch bleibt.
- Priorität 3: Accuracy nicht isoliert betrachten, sondern zusammen mit Confusion Matrix und Kategoriefehlern.

## Direkter Alt-vs-Neu-Vergleich

Evaluation auf aktuellem `data/val` und `data/new_raw`, Threshold `0.35`.

| Stand | Modell | Val Accuracy | Precision non_edible | Recall non_edible | FN non_edible | FP non_edible | Recall edible | new_raw |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| alt | old final demo | 75.8% | 67.6% | 89.3% | 3 | 12 | 64.7% | 12/14 |
| alt | old standard augmentation | 80.6% | 75.0% | 85.7% | 4 | 8 | 76.5% | 6/14 |
| alt | old background augmentation | 85.5% | 80.6% | 89.3% | 3 | 6 | 82.4% | 7/14 |
| neu | new no augmentation | 71.0% | 61.4% | 96.4% | 1 | 17 | 50.0% | 10/14 |
| neu | new standard augmentation | 79.0% | 72.7% | 85.7% | 4 | 9 | 73.5% | 7/14 |
| neu | new background augmentation | 79.0% | 71.4% | 89.3% | 3 | 10 | 70.6% | 7/14 |

## Interpretation ohne Vorentscheidung

### Wenn Recall für non_edible maximal wichtig ist

Bestes Modell:

- `freshify_new_no_augmentation.keras`

Warum:

- höchster `non_edible` Recall auf `data/val`: 96.4%
- nur 1 False Negative bei `non_edible`

Problem:

- 17 False Positives bei `edible`
- nur 50.0% Recall für `edible`
- viele gute Lebensmittel würden als auffällig markiert

Das Modell ist also sehr vorsichtig, aber wahrscheinlich zu aggressiv.

### Wenn Balance im Validation Set wichtig ist

Bestes Modell:

- `freshify_old_background_augmentation.keras`

Warum:

- höchste Validation Accuracy: 85.5%
- guter `non_edible` Recall: 89.3%
- wenigste False Positives: 6
- bester `edible` Recall: 82.4%

Problem:

- auf `data/new_raw` nur 7/14
- Smartphone-Generalization wirkt schlechter als beim alten finalen Demo-Modell

Das Modell ist fachlich aktuell der beste Allrounder auf dem regulären Validation Split.

### Wenn Demo auf neuen Smartphonebildern wichtig ist

Bestes Modell:

- `freshify_old_final_demo.keras`

Warum:

- erkennt 12/14 neue `non_edible` Smartphonebilder
- guter `non_edible` Recall auf `data/val`: 89.3%

Problem:

- mehr False Positives als old background: 12 statt 6
- schlechtere Validation Accuracy: 75.8%
- schlechterer `edible` Recall: 64.7%

Das Modell wirkt auf den neuen Handyfotos stark, ist aber im regulären Validation Set weniger ausgewogen.

## Warum verlieren die neuen Modelle?

Mehr Daten oder ein Re-Training müssen nicht automatisch besser sein. Plausible Gründe:

1. Der Datensatz wurde größer, aber nicht automatisch besser balanciert.
   - Train hat jetzt 413 Bilder, aber Kategorien und Labels sind weiterhin ungleich verteilt.
   - Banane und Orange dominieren stärker als Zitrone und Erdbeere.
   - Das Modell kann dadurch leichter Muster lernen, die für dominante Kategorien gut sind, aber nicht sauber generalisieren.

2. Die Validation bleibt klein.
   - `data/val` hat nur 62 Bilder.
   - Einzelne Bilder können die Metriken deutlich verschieben.
   - Besonders schwache Kategorien wie Zitrone oder Gurke non_edible sind kaum abgesichert.

3. Die neuen Trainingsbilder verändern die Entscheidungsgrenze.
   - Das alte finale Modell war offenbar besser auf die neuen Smartphonebilder kalibriert.
   - Das Re-Training mit zusätzlichen Main-Daten kann die Gewichtung stärker Richtung Kaggle-/Dataset-Look verschoben haben.
   - Dadurch kann die Performance auf `data/new_raw` sinken, obwohl das Training mehr Bilder sieht.

4. Der Backbone ist eingefroren.
   - Nur der kleine Klassifikationskopf wird trainiert.
   - Wenn neue Daten visuell anders sind, kann der Kopf nur begrenzt adaptieren.
   - Fine-Tuning der letzten MobileNetV2-Blöcke könnte helfen, erhöht aber Overfitting-Risiko.

5. Threshold und Class Weights verstärken den Trade-off.
   - Class Weights geben `non_edible` mehr Gewicht.
   - Threshold `0.35` markiert zusätzlich schneller `non_edible`.
   - Beim neuen No-Augmentation-Modell sieht man das klar: sehr hoher `non_edible` Recall, aber 17 False Positives.

6. Augmentation ist aktuell nicht gleich echte Background-Augmentation.
   - `freshify_new_background_augmentation.keras` nutzt im Training stärkere Online-Augmentation.
   - Die generierten Bilder aus `generated/background_aug` wurden in diesem Re-Training nicht zusätzlich als Trainingsdaten eingemischt.
   - Außerdem ist `generated/background_aug` selbst unausgewogen, daher wäre ein blindes Einmischen riskant.

## Konkretere Fehleranalyse

Die neuen Modelle verlieren nicht überall gleich. Bei Threshold `0.35` sieht man auf `data/val` besonders:

| Modell | Auffällige Schwächen |
|---|---|
| old final demo | viele False Positives bei `edible`, besonders Banane, Erdbeere, Gurke und Paprika |
| old background augmentation | insgesamt stärkster Val-Split, aber Paprika bleibt schwierig |
| new no augmentation | sehr aggressiv Richtung `non_edible`; `edible/paprika` 0/5 korrekt, `edible` Recall nur 50.0% |
| new standard augmentation | solide, aber kein Fortschritt gegenüber old background |
| new background augmentation | starker Einbruch bei `edible/gurke` 1/7 korrekt; dadurch viele gute Gurken fälschlich auffällig |

Das spricht gegen einen simplen Trainingsfehler wie "Labels komplett vertauscht". Das Problem wirkt eher wie eine schlechte Kalibrierung und ein Daten-/Domain-Shift:

- Das Modell erkennt viele `non_edible`-Bilder, aber markiert zu viele `edible`-Bilder als auffällig.
- Mehr Trainingsdaten haben die Entscheidungsgrenze verändert, aber nicht automatisch robuster gemacht.
- Einzelne Kategorien mit wenig oder visuell einseitigen Bildern ziehen die Metriken stark.
- Die neuen Trainingsdaten können stärker nach Kaggle-/Dataset-Look aussehen, während `new_raw` echte Smartphonebilder sind.
- Das Training optimiert EarlyStopping aktuell auf Keras-`val_recall` mit Standard-Threshold `0.5`, wir bewerten aber fachlich mit Threshold `0.35`. Das kann bedeuten, dass die gespeicherte beste Epoche nicht die beste Epoche für unseren real verwendeten Threshold ist.

## Schwache Kategorien

Es gibt zwei Arten von Schwäche:

1. Zu wenig Daten.
2. Viele Fehler im aktuellen Modellvergleich.

Schwach nach Datenmenge:

- `zitrone`: train nur 10 `edible` und 12 `non_edible`; val nur 2 `edible` und 1 `non_edible`
- `erdbeere`: train nur 22 `edible` und 10 `non_edible`; val nur 5 `edible` und 3 `non_edible`
- `gurke/non_edible`: val nur 2 Bilder, daher kaum stabile Aussage möglich

Schwach nach Modellfehlern:

- `paprika`: bleibt in mehreren Modellen schwierig, besonders bei der Trennung von `edible` und `non_edible`
- `gurke/edible`: beim neuen Background-Modell nur 1/7 korrekt
- `erdbeere`: kleine Datenbasis und wechselhafte Ergebnisse

Für Augmentation heißt das:

- Zuerst Kategorien mit wenig Daten und/oder vielen Fehlern priorisieren: Zitrone, Erdbeere, Paprika, Gurke.
- Nicht nur `non_edible` augmentieren. Für weniger False Positives brauchen wir auch gute `edible` Beispiele.
- Generated-Daten pro Label/Kategorie balancieren, sonst verschiebt sich der Bias weiter.

## Generated-/Background-Daten

Aktueller Stand `generated/background_aug`:

| Label | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|
| edible | 18 | 2 | 10 | 16 | 0 | 0 |
| non_edible | 20 | 0 | 0 | 12 | 10 | 8 |

Das ist für ein sauberes Background-Experiment noch nicht gut genug.

Problem:

- Es fehlen komplette Kombinationen, z.B. `edible/paprika`, `edible/zitrone`, `non_edible/erdbeere`, `non_edible/gurke`.
- Wenn wir diese generierten Daten blind einmischen, verstärken wir neue Verzerrungen.
- Background-Augmentation sollte pro Kategorie und Label möglichst gleichmäßig erzeugt werden.

Sinnvoller nächster Schritt:

1. Generated-Daten nur aus `train` erzeugen, nicht aus `val`.
2. Pro Label/Kategorie ungefähr gleich viele Background-Augmentations erzeugen.
3. Generated-Daten nicht in `val` mischen.
4. Ein echtes Experiment trainieren:
   - Baseline mit echten Bildern
   - Standard-Augmentation
   - echte Background-Augmentation mit zusätzlich eingemischten generated Train-Bildern
5. Danach alle Modelle auf demselben unveränderten `val` und zusätzlich auf `new_raw` vergleichen.

## Umgang mit `new_raw`

`new_raw` einfach komplett nach `val/non_edible` zu verschieben wäre methodisch nur teilweise richtig.

Warum es helfen kann:

- Die 14 Bilder sind echte Smartphonebilder und passen besser zum späteren Use Case.
- Das reguläre `val/non_edible` ist klein, daher würden zusätzliche echte Bilder die Aussagekraft verbessern.

Warum es riskant ist:

- `new_raw` enthält nur `non_edible`. Dadurch wird `val` einseitiger.
- Wenn wir genau diese Bilder zur Modellentscheidung benutzen, wird daraus schnell ein Demo-Test statt ein neutraler Holdout.
- Für Accuracy brauchen wir auch passende neue `edible` Smartphonebilder. Sonst messen wir nur die Trefferquote für `non_edible`, aber keine echte Gesamt-Accuracy.

Empfehlung:

- Kurzfristig `new_raw` als separaten Real-World-Holdout behalten und im README klar so nennen.
- Für die nächste saubere Evaluation einen neuen Ordner anlegen, z.B. `data/holdout_real_world/edible` und `data/holdout_real_world/non_edible`.
- Dort echte Smartphonebilder beider Klassen sammeln.
- Wenn wir `new_raw` in eine offizielle Evaluation aufnehmen, dann nur zusammen mit neuen `edible` Smartphonebildern und danach nicht mehr als Trainingsdaten verwenden.

## Wie bekommen wir mit mehr Daten bessere Accuracy?

Die Daten müssen gezielter besser werden, nicht nur mehr.

Priorität 1: Label-Qualität prüfen

- Stimmt jedes Label wirklich mit den Labeling-Regeln überein?
- Sind "unschön, aber essbar" Bilder eventuell zu oft als `non_edible` gelandet?
- Sind Bilder mit sichtbarer Fäule/Schimmel eventuell zu mild als `edible` gelabelt?

Priorität 2: Pro Kategorie ausbalancieren

- Besonders schwach: Zitrone und Erdbeere.
- In `val/non_edible` sind Gurke und Zitrone zu klein, um stabile Aussagen zu machen.
- Ziel wäre pro Kategorie und Label mindestens eine kleine, aber ähnliche Menge echter Bilder.

Priorität 3: Echte Smartphonebilder ergänzen

- Nicht nur `non_edible`, sondern auch `edible`.
- Gleiche Aufnahmebedingungen wie Demo/Use Case: Handy, Tisch, Küche, Kiste, wechselnde Lichtverhältnisse.
- Damit testen wir den Domain Gap wirklich.

Priorität 4: Training an die Evaluation angleichen

- EarlyStopping nicht blind auf `val_recall` bei Threshold `0.5` optimieren, wenn wir später Threshold `0.35` benutzen.
- Entweder Threshold in der Evaluation bewusst als Modellparameter dokumentieren oder Threshold-Sweep auf `val` machen.
- Optional danach leichtes Fine-Tuning der letzten MobileNetV2-Blöcke testen, aber erst nach Datenbereinigung.

Priorität 5: Generated-Daten nur kontrolliert einsetzen

- Generated Backgrounds sollen Robustheit gegen Hintergründe verbessern.
- Sie ersetzen keine echten Smartphonebilder.
- Sie sollten balanciert pro Label/Kategorie erzeugt und nur in `train` verwendet werden.

## Data-Improvement-Checkliste

Ziel ist nicht maximal viele Bilder, sondern ein konsistenterer Trainingssatz mit besserer Balance und weniger Labelrauschen.

### 1. Labels prüfen

Besonders prüfen:

- `data/train/edible/paprika`
- `data/train/non_edible/paprika`
- `data/train/edible/gurke`
- `data/train/edible/erdbeere`
- `data/train/non_edible/erdbeere`
- `data/train/edible/zitrone`
- `data/train/non_edible/zitrone`

Regel:

- leicht unansehnlich, Druckstellen, braune Stellen -> eher `edible`
- Schimmel, Schleim, deutliche Fäule, unsicher -> `non_edible`
- unklare Fälle lieber aussortieren statt falsch labeln

### 2. Kaggle gezielt ergänzen

Wenn keine Zeit für neue echte Smartphonebilder bleibt, dann Kaggle nur gezielt nutzen.

Notierte Zusatzquellen:

- Lemon Quality Dataset: https://www.kaggle.com/datasets/yusufemir/lemon-quality-dataset
- Pexels: zusätzliche `edible/zitrone` Bilder
- Strawberry Dataset: https://www.kaggle.com/datasets/abdulbasit31/strawberry-dataset
- Fresh vs Rotten Fruit Images: https://www.kaggle.com/datasets/abdulrafeyyashir/fresh-vs-rotten-fruit-images
- Fruit and Vegetable Disease / Healthy vs Rotten: https://www.kaggle.com/datasets/muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten

Priorität:

| Priorität | Kategorie/Label | Warum |
|---|---|---|
| 1 | `zitrone/edible` und `zitrone/non_edible` | kleinste Datenbasis |
| 2 | `erdbeere/non_edible` | nur 10 Train-Bilder |
| 3 | `erdbeere/edible` | ebenfalls klein |
| 4 | `gurke/non_edible` | Val sehr klein, Robustheit unsicher |
| 5 | `paprika/edible` | häufige False Positives |

Leitlinie:

- lieber 10-20 gute Bilder pro schwacher Kombination als viele unklare Bilder
- keine Kategorien außerhalb Banane, Erdbeere, Gurke, Orange, Paprika, Zitrone
- keine Bilder verwenden, bei denen das Label nicht eindeutig ist
- neue Kaggle-Bilder zunächst nur in `train`, nicht in `val`

### 3. Generated Backgrounds verbessern

Aktuell fehlen in `generated/background_aug` mehrere Kombinationen. Vor einem neuen Background-Experiment sollten wir mindestens diese Lücken schließen:

- `edible/paprika`
- `edible/zitrone`
- `non_edible/erdbeere`
- `non_edible/gurke`

Leitlinie:

- pro Label/Kategorie ähnlich viele generated Bilder
- nur aus `train`-Bildern erzeugen
- keine generated Bilder in `val`
- Background-Augmentation separat als Experiment speichern, nicht mit Baseline vermischen

### 4. Nächster Trainingsvergleich

Nach Datenbereinigung sollten wir wieder exakt drei Modelle trainieren:

1. `no_augmentation`
2. `standard_augmentation`
3. echte `background_augmentation` mit zusätzlich eingemischten generated Train-Bildern

Alle drei werden gleich bewertet:

- gleicher `data/val` Split
- gleicher Threshold `0.35`
- zusätzlich `data/new_raw` als Real-World-Check
- Fokus auf `recall_non_edible`, False Negatives und akzeptable False Positives

### 5. Entscheidungskriterium

Ein neues Modell ist nur besser, wenn es mindestens eine dieser Verbesserungen schafft:

- `recall_non_edible` bleibt gleich hoch oder steigt
- False Negatives sinken
- False Positives sinken, ohne `non_edible` Recall stark zu verlieren
- Kategoriefehler bei Paprika/Gurke/Erdbeere/Zitrone werden stabiler

Nur höhere Accuracy reicht nicht, wenn dadurch mehr verdorbene Lebensmittel übersehen werden.

## Data-Quality-Check nach Ergänzung

Stand: 2026-06-12

Neue Daten wurden gezielt in `data/train` ergänzt. `data/val` blieb unverändert.

Train-Verteilung vor Cleanup:

| Label | Gesamt | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|---:|
| edible | 271 | 80 | 27 | 44 | 56 | 37 | 27 |
| non_edible | 211 | 46 | 23 | 38 | 46 | 36 | 22 |

Train-Verteilung nach Cleanup:

| Label | Gesamt | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|---:|
| edible | 265 | 78 | 27 | 42 | 54 | 37 | 27 |
| non_edible | 201 | 42 | 23 | 36 | 42 | 36 | 22 |

Aktuelle Val-Verteilung:

| Label | Gesamt | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|---:|
| edible | 34 | 9 | 5 | 7 | 6 | 5 | 2 |
| non_edible | 28 | 8 | 3 | 2 | 5 | 9 | 1 |

Technischer Check vor Cleanup:

- 0 nicht-lesbare Bilder
- 0 Bilder unter 100 px
- 8 Nicht-Bild-Dateien in `data/train`, darunter `.DS_Store` und eine `.html` Datei
- 16 exakte Bild-Duplikate
- Davon 5 exakte Train-Val-Duplikate

Technischer Check nach Cleanup:

- 0 nicht-lesbare Bilder
- 0 Nicht-Bild-Dateien
- 0 exakte Bild-Duplikate
- 0 exakte Train-Val-Duplikate

Bewertung:

- Die neuen Ergänzungen verbessern die schwachen Train-Kategorien deutlich.
- Besonders Zitrone, Erdbeere, Gurke und Paprika sind im Training jetzt besser abgedeckt.
- `data/val` ist weiterhin sehr klein, besonders `val/non_edible/gurke` und `val/non_edible/zitrone`.
- Train-Val-Duplikate sollten vor einem finalen Vergleich entfernt werden, weil sie die Val-Metriken künstlich verbessern können.
- Train-Train-Duplikate sind weniger kritisch, können aber einzelne Beispiele übergewichten.

Konkrete Bereinigung vor neuem Training:

1. Nicht-Bild-Dateien aus `data/train` entfernen.
2. Exakte Duplikate entfernen, besonders wenn ein Bild sowohl in `train` als auch in `val` liegt.
3. Danach lokal ein neues Dataset-Manifest erzeugen.
4. Dann Baseline ohne Augmentation neu trainieren.

Durchgeführt:

- Nicht-Bild-Dateien entfernt.
- Exakte Duplikate entfernt.
- Train-Val-Duplikate entfernt.
- Dataset-Manifest neu erzeugt mit 528 Bildern.
- Neues Baseline-Modell ohne Augmentation trainiert:
  - `models/freshify_baseline_after_data_cleanup.keras`

## Neues Baseline-Training nach Datenbereinigung

Training:

- Train: 466 Bilder
- Val: 62 Bilder
- Augmentation: keine
- Backbone: MobileNetV2 eingefroren
- Class Weights:
  - `edible`: 0.879
  - `non_edible`: 1.159

Keras EarlyStopping hat auf Epoche 1 zurückgesetzt, weil dort der höchste `val_recall` erreicht wurde.

Threshold-Vergleich auf `data/val`:

| Threshold | Accuracy | Precision non_edible | Recall non_edible | FN non_edible | FP non_edible | Recall edible |
|---:|---:|---:|---:|---:|---:|---:|
| 0.35 | 71.0% | 61.9% | 92.9% | 2 | 16 | 52.9% |
| 0.40 | 74.2% | 65.0% | 92.9% | 2 | 14 | 58.8% |
| 0.45 | 77.4% | 68.4% | 92.9% | 2 | 12 | 64.7% |
| 0.50 | 80.6% | 73.5% | 89.3% | 3 | 9 | 73.5% |

`data/new_raw`:

| Threshold | non_edible erkannt |
|---:|---:|
| 0.35 | 10/14 |
| 0.45 | 10/14 |
| 0.50 | 9/14 |

Einordnung:

- Die Datenbereinigung und gezielte Datenergänzung haben das neue Baseline-Modell stabiler gemacht als der vorherige neue No-Augmentation-Stand.
- Bei Threshold `0.35` ist das Modell weiterhin zu aggressiv und erzeugt 16 False Positives.
- Threshold `0.45` ist ein interessanter Recall-orientierter Kompromiss: 92.9% `non_edible` Recall bei 12 False Positives.
- Threshold `0.50` ist ausgewogener: 80.6% Accuracy, 89.3% `non_edible` Recall und 9 False Positives.
- Das Modell schlägt den alten Background-Allrounder noch nicht klar, ist aber eine brauchbare neue Baseline für die nächste gezielte Augmentation.

## Baseline mit `new_raw` im Training

Stand: 2026-06-12

Die 14 Bilder aus `data/new_raw` wurden als `non_edible` in `data/train` aufgenommen:

- Paprika: 6 Bilder
- Banane: 5 Bilder
- Zitrone: 3 Bilder

Wichtig: `data/new_raw` ist damit kein unabhängiger Testdatensatz mehr. Für eine echte Real-World-Aussage brauchen wir danach einen neuen Holdout mit beiden Klassen.

Train-Verteilung nach Aufnahme von `new_raw`:

| Label | Gesamt | Banane | Erdbeere | Gurke | Orange | Paprika | Zitrone |
|---|---:|---:|---:|---:|---:|---:|---:|
| edible | 265 | 78 | 27 | 42 | 54 | 37 | 27 |
| non_edible | 215 | 47 | 23 | 36 | 42 | 42 | 25 |

Training:

- Modell: `models/freshify_baseline_with_new_raw.keras`
- Augmentation: keine
- Train: 480 Bilder
- Val: 62 Bilder
- EarlyStopping: beste Epoche 4

Evaluation auf `data/val`:

| Threshold | Accuracy | Precision non_edible | Recall non_edible | FN non_edible | FP non_edible | Recall edible |
|---:|---:|---:|---:|---:|---:|---:|
| 0.35 | 79.0% | 71.4% | 89.3% | 3 | 10 | 70.6% |
| 0.45 | 88.7% | 86.2% | 89.3% | 3 | 4 | 88.2% |
| 0.50 | 90.3% | 89.3% | 89.3% | 3 | 3 | 91.2% |

Einordnung gegen wichtige alte/neue Stände:

| Modell | Threshold | Val Accuracy | Recall non_edible | FN non_edible | FP non_edible | Bemerkung |
|---|---:|---:|---:|---:|---:|---|
| old final demo | 0.35 | 75.8% | 89.3% | 3 | 12 | stark auf altem `new_raw`-Check, aber mehr FP |
| old background augmentation | 0.35 | 85.5% | 89.3% | 3 | 6 | bisher bester Allrounder ohne `new_raw` im Training |
| baseline after cleanup | 0.50 | 80.6% | 89.3% | 3 | 9 | sauberer Datensatz, aber noch nicht besser |
| baseline with new_raw | 0.50 | 90.3% | 89.3% | 3 | 3 | aktuell stärkste Val-Balance, aber neuer Holdout fehlt |

Vorläufiges Fazit:

- Die Aufnahme von `new_raw` ins Training verbessert die Kalibrierung deutlich.
- Bei Threshold `0.50` erreicht die neue Baseline die beste Validation Accuracy und die wenigsten False Positives bei gleichem `non_edible` Recall.
- Da `new_raw` jetzt im Training ist, brauchen wir zwingend einen neuen Real-World-Testdatensatz, bevor wir von echter Real-World-Generalization sprechen.
- Gezielte Augmentation bleibt sinnvoll, aber erst als nächstes Experiment gegen diese neue Baseline.

## Aktuelle Entscheidungslage

Aktuell stärkster Stand auf `data/val`:

- `models/freshify_baseline_with_new_raw.keras`
- empfohlener Threshold: `0.50`

Warum:

- höchste Validation Accuracy: 90.3%
- gleicher `non_edible` Recall wie die besten alten Modelle: 89.3%
- deutlich weniger False Positives: 3 statt 6 bis 12
- ausgeglichenere `edible`- und `non_edible`-Performance

Wichtige Einschränkung:

- `data/new_raw` ist jetzt Trainingsmaterial.
- Deshalb gibt es aktuell keinen unabhängigen Real-World-Holdout mehr.
- Die neue Baseline ist auf `data/val` stark, aber Real-World-Generalization muss mit neuen Bildern geprüft werden.

## Empfehlung für die Präsentation

Besser nicht sagen:

> Wir haben einfach mehr Daten genommen und das Modell ist automatisch besser.

Besser:

> Wir haben zuerst Datenqualität und Labelstruktur verbessert, Duplikate entfernt und eigene Smartphonebilder gezielt in die kritische Klasse `non_edible` aufgenommen. Dadurch wurde die neue Baseline auf dem Validation Split deutlich stabiler. Da diese Smartphonebilder jetzt im Training sind, brauchen wir für eine echte Real-World-Aussage als nächsten Schritt einen neuen unabhängigen Holdout mit `edible` und `non_edible` Bildern.

## Nächste Schritte

1. Neuen Real-World-Holdout aufbauen:
   - `data/holdout_real_world/edible/<kategorie>/`
   - `data/holdout_real_world/non_edible/<kategorie>/`
2. `freshify_baseline_with_new_raw.keras` auf diesem Holdout prüfen.
3. Danach gezielte Augmentation als Experiment gegen diese Baseline testen:
   - zuerst schwache/problematische Kategorien
   - nur in `train`
   - `val` und neuer Holdout bleiben unverändert
4. Falls die neue Baseline final genutzt werden soll, `models/freshify_final.keras` bewusst auf diesen Stand setzen.
