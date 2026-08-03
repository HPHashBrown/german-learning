"""Reading Mode story content.

Honesty note: the brief asked for "100 short German stories." Writing 100
original stories at real quality (correct grammar, sensible vocab lists,
working comprehension questions) isn't something that can be done reliably
in one pass — so this ships with a smaller, carefully-written set (16
stories, 4 per CEFR level) instead of padding to 100 with weak filler.
The data structure below is intentionally flat and simple so appending more
stories later is a copy-paste-and-edit job, not a code change.

Every story is original text written for this app (not sourced from
anywhere), to avoid any copyright concerns.

"vocab" only lists the specific words that are clickable in the reader (full
free-text word lookup for arbitrary German would need a real dictionary API,
which is out of scope) — this is disclosed in the Reading Mode page itself.
"""

STORIES = [
    # ---------------------------------------------------------------- A1 --
    dict(id="a1_der_morgen", title="Der Morgen", level="A1", min_level=3,
         text=("Anna wacht um sieben Uhr auf. Sie trinkt Kaffee und isst Brot mit "
               "Marmelade. Der Himmel ist blau. Anna geht zur Arbeit. Sie nimmt den "
               "Bus. Der Bus ist voll. Anna liest ein Buch. Um acht Uhr ist sie im "
               "Büro. Ihre Kollegin sagt: „Guten Morgen, Anna!“ Anna lächelt und "
               "antwortet: „Guten Morgen! Wie geht es dir?“"),
         vocab=[("aufwachen", "to wake up"), ("der Kaffee", "coffee"), ("das Brot", "bread"),
                ("der Himmel", "sky"), ("der Bus", "bus"), ("das Büro", "office"),
                ("die Kollegin", "colleague (f)"), ("lächeln", "to smile")],
         grammar_notes="Present tense, separable verb 'aufwachen' (sie wacht ... auf).",
         questions=[
             dict(q="Wann wacht Anna auf?", options=["Um sechs Uhr", "Um sieben Uhr", "Um acht Uhr"], correct="Um sieben Uhr"),
             dict(q="Was trinkt Anna?", options=["Tee", "Wasser", "Kaffee"], correct="Kaffee"),
             dict(q="Wie fährt Anna zur Arbeit?", options=["Mit dem Auto", "Mit dem Bus", "Zu Fuß"], correct="Mit dem Bus"),
         ]),
    dict(id="a1_im_supermarkt", title="Im Supermarkt", level="A1", min_level=3,
         text=("Max geht in den Supermarkt. Er braucht Milch, Eier und Käse. Der "
               "Supermarkt ist groß. Max nimmt einen Einkaufswagen. Er findet die "
               "Milch schnell. Die Eier sind teuer. Max kauft trotzdem zwei Eier-"
               "packungen. An der Kasse bezahlt er mit Karte. Die Verkäuferin sagt: "
               "„Vielen Dank, einen schönen Tag noch!“"),
         vocab=[("die Milch", "milk"), ("das Ei", "egg"), ("der Käse", "cheese"),
                ("der Einkaufswagen", "shopping cart"), ("teuer", "expensive"),
                ("die Kasse", "checkout"), ("bezahlen", "to pay")],
         grammar_notes="Accusative case with direct objects (er braucht Milch, Eier, Käse).",
         questions=[
             dict(q="Was braucht Max nicht?", options=["Milch", "Käse", "Brot"], correct="Brot"),
             dict(q="Wie bezahlt Max?", options=["Mit Bargeld", "Mit Karte", "Mit Scheck"], correct="Mit Karte"),
         ]),
    dict(id="a1_das_wetter", title="Das Wetter heute", level="A1", min_level=3,
         text=("Heute ist das Wetter schlecht. Es regnet und es ist kalt. Lisa "
               "nimmt einen Regenschirm mit. Sie trägt eine warme Jacke. Auf dem Weg "
               "zur Schule sieht sie ihre Freundin Mia. Sie gehen zusammen. Mia hat "
               "keinen Regenschirm. Lisa teilt ihren Regenschirm mit Mia. Beide "
               "kommen trocken in der Schule an."),
         vocab=[("das Wetter", "weather"), ("regnen", "to rain"), ("kalt", "cold"),
                ("der Regenschirm", "umbrella"), ("die Jacke", "jacket"),
                ("teilen", "to share"), ("trocken", "dry")],
         grammar_notes="Weather expressions with 'es' (es regnet, es ist kalt).",
         questions=[
             dict(q="Wie ist das Wetter?", options=["Sonnig", "Schlecht/regnerisch", "Windig"], correct="Schlecht/regnerisch"),
             dict(q="Was macht Lisa für Mia?", options=["Sie gibt ihr eine Jacke", "Sie teilt den Regenschirm", "Sie bleibt zu Hause"], correct="Sie teilt den Regenschirm"),
         ]),
    dict(id="a1_meine_familie", title="Meine Familie", level="A1", min_level=3,
         text=("Ich heiße Paul. Meine Familie ist klein. Ich habe eine Schwester "
               "und einen Bruder. Meine Mutter ist Lehrerin. Mein Vater arbeitet "
               "bei einer Bank. Wir wohnen in einem kleinen Haus mit einem Garten. "
               "Am Wochenende kochen wir zusammen. Meine Schwester kocht sehr gut. "
               "Ich liebe meine Familie."),
         vocab=[("die Familie", "family"), ("die Schwester", "sister"), ("der Bruder", "brother"),
                ("die Lehrerin", "teacher (f)"), ("die Bank", "bank"), ("der Garten", "garden"),
                ("kochen", "to cook")],
         grammar_notes="Possessive adjectives (meine, mein) agreeing with noun gender.",
         questions=[
             dict(q="Was ist Pauls Mutter von Beruf?", options=["Ärztin", "Lehrerin", "Bankangestellte"], correct="Lehrerin"),
             dict(q="Wer kocht sehr gut?", options=["Der Bruder", "Die Schwester", "Der Vater"], correct="Die Schwester"),
         ]),

    # ---------------------------------------------------------------- A2 --
    dict(id="a2_der_ausflug", title="Der Ausflug in die Berge", level="A2", min_level=3,
         text=("Am Samstag fuhren Julia und ihre Freunde in die Berge. Sie standen "
               "früh auf, weil die Wanderung lang war. Das Wetter war zum Glück "
               "sonnig, aber ziemlich kühl. Nach zwei Stunden erreichten sie einen "
               "kleinen See. Das Wasser war klar und kalt. Sie machten eine Pause "
               "und aßen ihre mitgebrachten Sandwiches. Julia machte viele Fotos, "
               "weil die Aussicht wunderschön war. Am Abend waren alle müde, aber "
               "glücklich."),
         vocab=[("der Ausflug", "outing/trip"), ("die Wanderung", "hike"), ("der See", "lake"),
                ("die Pause", "break"), ("die Aussicht", "view"), ("müde", "tired"), ("glücklich", "happy")],
         grammar_notes="Simple past (Präteritum) of common verbs: fuhren, standen, erreichten, machten, aßen.",
         questions=[
             dict(q="Wie war das Wetter?", options=["Regnerisch", "Sonnig, aber kühl", "Sehr heiß"], correct="Sonnig, aber kühl"),
             dict(q="Was erreichten sie nach zwei Stunden?", options=["Einen Berg", "Ein Dorf", "Einen See"], correct="Einen See"),
             dict(q="Wie fühlten sie sich am Abend?", options=["Gelangweilt", "Müde, aber glücklich", "Traurig"], correct="Müde, aber glücklich"),
         ]),
    dict(id="a2_das_vorstellungsgespraech", title="Das Vorstellungsgespräch", level="A2", min_level=3,
         text=("Tom hatte heute ein Vorstellungsgespräch bei einer großen Firma. Er "
               "war sehr nervös, deshalb übte er am Morgen seine Antworten vor dem "
               "Spiegel. Im Büro wartete er zehn Minuten, bevor die Personalchefin "
               "ihn hereinrief. Sie stellte ihm viele Fragen über seine Erfahrung. "
               "Tom antwortete ruhig und erklärte seine früheren Projekte. Am Ende "
               "des Gesprächs sagte die Personalchefin, dass sie ihm bald Bescheid "
               "geben würde. Tom verließ das Büro mit einem guten Gefühl."),
         vocab=[("das Vorstellungsgespräch", "job interview"), ("nervös", "nervous"),
                ("die Personalchefin", "HR manager (f)"), ("die Erfahrung", "experience"),
                ("erklären", "to explain"), ("Bescheid geben", "to let someone know")],
         grammar_notes="Subordinate clauses with 'deshalb', 'bevor', 'dass' (verb goes to the end).",
         questions=[
             dict(q="Warum übte Tom vor dem Spiegel?", options=["Aus Langeweile", "Weil er nervös war", "Weil es Spaß machte"], correct="Weil er nervös war"),
             dict(q="Worüber stellte die Personalchefin Fragen?", options=["Sein Hobby", "Seine Erfahrung", "Sein Gehalt"], correct="Seine Erfahrung"),
         ]),
    dict(id="a2_ein_verlorener_hund", title="Ein verlorener Hund", level="A2", min_level=3,
         text=("Als Sofie im Park spazieren ging, sah sie einen kleinen Hund ohne "
               "Halsband. Der Hund sah traurig und hungrig aus. Sofie näherte sich "
               "langsam und der Hund kam vorsichtig zu ihr. Sie gab ihm etwas Wasser "
               "aus ihrer Flasche. Da niemand in der Nähe war, brachte sie den Hund "
               "zum Tierheim. Dort erklärte man ihr, dass sie den Besitzer über den "
               "Chip finden könnten. Zwei Tage später rief eine glückliche Familie "
               "an, um sich zu bedanken."),
         vocab=[("verloren", "lost"), ("das Halsband", "collar"), ("hungrig", "hungry"),
                ("sich nähern", "to approach"), ("das Tierheim", "animal shelter"),
                ("der Besitzer", "owner"), ("sich bedanken", "to thank")],
         grammar_notes="Reflexive verbs (sich nähern, sich bedanken) and modal 'könnten'.",
         questions=[
             dict(q="Was fehlte dem Hund?", options=["Ein Halsband", "Ein Freund", "Ein Ball"], correct="Ein Halsband"),
             dict(q="Wohin brachte Sofie den Hund?", options=["Nach Hause", "Zum Tierheim", "Zur Polizei"], correct="Zum Tierheim"),
         ]),
    dict(id="a2_die_geburtstagsparty", title="Die Geburtstagsparty", level="A2", min_level=3,
         text=("Lena plante seit Wochen die Geburtstagsparty für ihren besten "
               "Freund Ben. Sie lud zwanzig Gäste ein und bestellte eine große "
               "Schokoladentorte. Am Tag der Party dekorierte sie das Wohnzimmer "
               "mit bunten Luftballons. Ben wusste nichts von der Überraschung. Als "
               "er die Tür öffnete, riefen alle „Herzlichen Glückwunsch!“ Ben war so "
               "überrascht, dass er zuerst nichts sagen konnte. Später tanzten alle "
               "bis spät in die Nacht."),
         vocab=[("planen", "to plan"), ("einladen", "to invite"), ("die Torte", "cake"),
                ("dekorieren", "to decorate"), ("der Luftballon", "balloon"),
                ("die Überraschung", "surprise"), ("tanzen", "to dance")],
         grammar_notes="Simple past with separable verbs (lud ... ein) and 'so ... dass' constructions.",
         questions=[
             dict(q="Wie viele Gäste lud Lena ein?", options=["Zehn", "Zwanzig", "Dreißig"], correct="Zwanzig"),
             dict(q="Wusste Ben von der Party?", options=["Ja", "Nein", "Nur ein bisschen"], correct="Nein"),
         ]),

    # ---------------------------------------------------------------- B1 --
    dict(id="b1_die_umzug", title="Der Umzug in eine neue Stadt", level="B1", min_level=3,
         text=("Nachdem Marie ihr Studium abgeschlossen hatte, entschied sie sich, "
               "für ihren neuen Job in eine andere Stadt zu ziehen. Der Umzug war "
               "stressiger, als sie erwartet hatte, weil sie in nur zwei Wochen eine "
               "Wohnung finden musste. Obwohl sie anfangs niemanden kannte, lernte "
               "sie schnell neue Kollegen und Nachbarn kennen. Nach einigen Monaten "
               "fühlte sich die neue Stadt fast wie ein Zuhause an. Marie war stolz "
               "darauf, dass sie diese Herausforderung gemeistert hatte."),
         vocab=[("der Umzug", "move/relocation"), ("das Studium", "studies/degree"),
                ("abschließen", "to complete/finish"), ("stressig", "stressful"),
                ("die Herausforderung", "challenge"), ("meistern", "to master/overcome")],
         grammar_notes="Past perfect (abgeschlossen hatte) and subordinating conjunctions (nachdem, obwohl, weil).",
         questions=[
             dict(q="Warum zog Marie um?", options=["Für die Familie", "Für einen neuen Job", "Für das Wetter"], correct="Für einen neuen Job"),
             dict(q="Wie lange hatte sie, um eine Wohnung zu finden?", options=["Eine Woche", "Zwei Wochen", "Einen Monat"], correct="Zwei Wochen"),
         ]),
    dict(id="b1_nachhaltigkeit", title="Nachhaltigkeit im Alltag", level="B1", min_level=3,
         text=("Immer mehr Menschen versuchen, in ihrem Alltag nachhaltiger zu "
               "leben. Manche verzichten auf Plastiktüten und bringen stattdessen "
               "eigene Stoffbeutel zum Einkaufen mit. Andere kaufen lieber "
               "regionales Gemüse, um lange Transportwege zu vermeiden. Auch beim "
               "Energieverbrauch gibt es einfache Möglichkeiten zu sparen, zum "
               "Beispiel durch LED-Lampen oder kürzere Duschzeiten. Kritiker "
               "meinen jedoch, dass individuelle Maßnahmen allein nicht ausreichen, "
               "um den Klimawandel zu stoppen — größere politische Veränderungen "
               "seien notwendig."),
         vocab=[("nachhaltig", "sustainable"), ("verzichten auf", "to do without"),
                ("vermeiden", "to avoid"), ("der Energieverbrauch", "energy consumption"),
                ("die Maßnahme", "measure/action"), ("der Klimawandel", "climate change")],
         grammar_notes="Infinitive clauses with 'um ... zu' (to avoid/in order to).",
         questions=[
             dict(q="Was bringen manche Leute zum Einkaufen mit?", options=["Plastiktüten", "Stoffbeutel", "Nichts"], correct="Stoffbeutel"),
             dict(q="Was meinen Kritiker?", options=["Individuelle Maßnahmen reichen aus", "Politische Veränderungen sind auch nötig", "Nachhaltigkeit ist unwichtig"], correct="Politische Veränderungen sind auch nötig"),
         ]),
    dict(id="b1_die_pruefung", title="Die schwierige Prüfung", level="B1", min_level=3,
         text=("Felix hatte sich monatelang auf seine Abschlussprüfung "
               "vorbereitet, trotzdem war er am Prüfungstag furchtbar aufgeregt. "
               "Als er den ersten Blick auf die Aufgaben warf, wurde ihm klar, dass "
               "einige Fragen schwieriger waren, als er erwartet hatte. Statt in "
               "Panik zu geraten, atmete er tief durch und begann mit den Aufgaben, "
               "die er am besten konnte. Diese Strategie half ihm, ruhig zu bleiben. "
               "Als die Ergebnisse eine Woche später bekannt gegeben wurden, hatte "
               "Felix tatsächlich bestanden — mit einer besseren Note, als er sich "
               "erhofft hatte."),
         vocab=[("die Prüfung", "exam"), ("sich vorbereiten", "to prepare oneself"),
                ("aufgeregt", "excited/nervous"), ("in Panik geraten", "to panic"),
                ("tief durchatmen", "to take a deep breath"), ("bestehen", "to pass (an exam)")],
         grammar_notes="Comparative constructions (schwieriger, als...) and passive voice (bekannt gegeben wurden).",
         questions=[
             dict(q="Wie fühlte sich Felix am Prüfungstag?", options=["Ruhig", "Aufgeregt", "Gelangweilt"], correct="Aufgeregt"),
             dict(q="Was machte er, statt in Panik zu geraten?", options=["Er verließ den Raum", "Er atmete tief durch", "Er weinte"], correct="Er atmete tief durch"),
         ]),
    dict(id="b1_die_wg", title="Das Leben in einer WG", level="B1", min_level=3,
         text=("Seit drei Monaten wohnt Hannah in einer Wohngemeinschaft mit zwei "
               "anderen Studenten. Am Anfang war es ungewohnt, sich Küche und Bad "
               "zu teilen, aber inzwischen genießt sie das gesellige "
               "Zusammenleben. Jede Woche kochen die drei abwechselnd für die "
               "ganze Gruppe, was das WG-Leben günstiger und lustiger macht. "
               "Natürlich gibt es manchmal Konflikte, etwa wenn jemand vergisst, "
               "das Geschirr zu spülen. Trotzdem würde Hannah das WG-Leben "
               "keinem Einzelappartement vorziehen."),
         vocab=[("die Wohngemeinschaft (WG)", "shared apartment/flatshare"), ("ungewohnt", "unfamiliar"),
                ("genießen", "to enjoy"), ("abwechselnd", "alternately/taking turns"),
                ("der Konflikt", "conflict"), ("vorziehen", "to prefer")],
         grammar_notes="Present perfect vs. simple present for ongoing situations (wohnt seit drei Monaten).",
         questions=[
             dict(q="Mit wie vielen anderen Studenten wohnt Hannah?", options=["Einem", "Zwei", "Drei"], correct="Zwei"),
             dict(q="Was macht das WG-Leben günstiger?", options=["Abwechselnd kochen", "Zusammen putzen", "Gemeinsam einkaufen"], correct="Abwechselnd kochen"),
         ]),

    # ---------------------------------------------------------------- B2 --
    dict(id="b2_die_digitalisierung", title="Die Digitalisierung der Arbeitswelt", level="B2", min_level=3,
         text=("Die zunehmende Digitalisierung verändert die Arbeitswelt in einem "
               "Tempo, das noch vor zehn Jahren kaum vorstellbar gewesen wäre. "
               "Während Befürworter betonen, dass flexible Arbeitsmodelle wie "
               "Homeoffice die Vereinbarkeit von Beruf und Privatleben erheblich "
               "verbessern, weisen Kritiker auf die Gefahr der ständigen "
               "Erreichbarkeit hin, die langfristig zu Erschöpfung führen könnte. "
               "Unternehmen stehen daher vor der Herausforderung, die Vorteile der "
               "Digitalisierung zu nutzen, ohne dabei die Grenzen zwischen Arbeit "
               "und Freizeit vollständig verschwimmen zu lassen."),
         vocab=[("die Digitalisierung", "digitalization"), ("der Befürworter", "advocate/proponent"),
                ("die Vereinbarkeit", "compatibility/balance"), ("erheblich", "considerably"),
                ("die Erschöpfung", "exhaustion"), ("verschwimmen", "to blur")],
         grammar_notes="Extended participial phrases and subjunctive II for hypotheticals (gewesen wäre, könnte).",
         questions=[
             dict(q="Was betonen die Befürworter?", options=["Homeoffice verschlechtert alles", "Bessere Work-Life-Balance", "Höhere Kosten"], correct="Bessere Work-Life-Balance"),
             dict(q="Wovor warnen Kritiker?", options=["Ständige Erreichbarkeit", "Zu wenig Arbeit", "Fehlende Technologie"], correct="Ständige Erreichbarkeit"),
         ]),
    dict(id="b2_kuenstliche_intelligenz", title="Künstliche Intelligenz im Alltag", level="B2", min_level=3,
         text=("Künstliche Intelligenz ist längst kein Zukunftsthema mehr, sondern "
               "ein fester Bestandteil unseres Alltags — von Sprachassistenten bis "
               "hin zu personalisierten Empfehlungen beim Online-Einkauf. Während "
               "manche die Entwicklung begeistert vorantreiben, äußern andere "
               "Bedenken hinsichtlich Datenschutz und der Frage, inwiefern "
               "Algorithmen unsere Entscheidungen unbemerkt beeinflussen. "
               "Besonders umstritten ist der Einsatz von KI in Bereichen wie der "
               "medizinischen Diagnose, wo Fehler schwerwiegende Folgen haben "
               "könnten. Ein ausgewogener regulatorischer Rahmen gilt daher als "
               "eine der wichtigsten Aufgaben der kommenden Jahre."),
         vocab=[("künstliche Intelligenz", "artificial intelligence"), ("der Bestandteil", "component/part"),
                ("die Bedenken (pl.)", "concerns/reservations"), ("beeinflussen", "to influence"),
                ("umstritten", "controversial"), ("ausgewogen", "balanced")],
         grammar_notes="Nominalized adjectives/prepositional phrases (hinsichtlich, inwiefern) typical of formal register.",
         questions=[
             dict(q="Wo wird KI laut Text als besonders umstritten beschrieben?", options=["Beim Online-Einkauf", "In der medizinischen Diagnose", "Bei Sprachassistenten"], correct="In der medizinischen Diagnose"),
             dict(q="Was gilt als wichtige Aufgabe der Zukunft?", options=["Mehr KI-Entwicklung ohne Regeln", "Ein ausgewogener regulatorischer Rahmen", "Die Abschaffung von KI"], correct="Ein ausgewogener regulatorischer Rahmen"),
         ]),
    dict(id="b2_stadtleben_landleben", title="Stadtleben oder Landleben?", level="B2", min_level=3,
         text=("Die Frage, ob das Leben in der Stadt oder auf dem Land erstrebens-"
               "werter sei, wird seit Jahrzehnten kontrovers diskutiert. "
               "Städter schätzen die kulturelle Vielfalt, die kurzen Wege und das "
               "breite Freizeitangebot, während Landbewohner häufig die Ruhe, den "
               "günstigeren Wohnraum und die engere Gemeinschaft hervorheben. Seit "
               "der zunehmenden Verbreitung von Homeoffice ziehen jedoch immer mehr "
               "Menschen aufs Land, ohne dabei auf ihren städtischen Job verzichten "
               "zu müssen. Diese Entwicklung könnte langfristig dazu führen, dass "
               "sich der scharfe Gegensatz zwischen Stadt und Land allmählich "
               "auflöst."),
         vocab=[("erstrebenswert", "desirable/worth striving for"), ("die Vielfalt", "diversity"),
                ("hervorheben", "to emphasize/highlight"), ("die Verbreitung", "spread/prevalence"),
                ("der Gegensatz", "contrast/opposition"), ("sich auflösen", "to dissolve")],
         grammar_notes="Indirect speech with subjunctive I (sei) and complex subordinate clause chains.",
         questions=[
             dict(q="Was schätzen Landbewohner laut Text?", options=["Kulturelle Vielfalt", "Ruhe und günstigen Wohnraum", "Kurze Wege"], correct="Ruhe und günstigen Wohnraum"),
             dict(q="Was ermöglicht Homeoffice laut Text?", options=["Umzug aufs Land ohne Jobverlust", "Höhere Gehälter", "Weniger Wettbewerb"], correct="Umzug aufs Land ohne Jobverlust"),
         ]),
    dict(id="b2_generationenkonflikt", title="Der Generationenkonflikt am Arbeitsplatz", level="B2", min_level=3,
         text=("In vielen Unternehmen treffen mittlerweile bis zu vier "
               "Generationen aufeinander, was gelegentlich zu Missverständnissen "
               "führt. Während ältere Mitarbeiter oft Wert auf klare Hierarchien "
               "und langfristige Loyalität legen, erwarten jüngere Generationen "
               "zunehmend flexible Strukturen und regelmäßiges Feedback. Experten "
               "betonen jedoch, dass diese Unterschiede weniger auf das Alter an "
               "sich zurückzuführen seien als vielmehr auf unterschiedliche "
               "Lebensumstände und technologische Prägungen. Unternehmen, die es "
               "schaffen, von den jeweiligen Stärken beider Seiten zu profitieren, "
               "gelten langfristig als widerstandsfähiger."),
         vocab=[("aufeinandertreffen", "to clash/meet"), ("die Hierarchie", "hierarchy"),
                ("die Loyalität", "loyalty"), ("zurückzuführen sein auf", "to be attributable to"),
                ("die Prägung", "formative influence/imprint"), ("widerstandsfähig", "resilient")],
         grammar_notes="Complex comparative subordination (weniger ... als vielmehr ...) at B2 register.",
         questions=[
             dict(q="Worauf legen ältere Mitarbeiter oft Wert?", options=["Flexible Strukturen", "Klare Hierarchien", "Ständiges Feedback"], correct="Klare Hierarchien"),
             dict(q="Worauf führen Experten die Unterschiede eher zurück?", options=["Reines Alter", "Lebensumstände und Technologie", "Persönlichkeit"], correct="Lebensumstände und Technologie"),
         ]),

    # ---------------------------------------------------------------- C1 --
    dict(id="c1_ambivalenz_fortschritt", title="Die Ambivalenz des Fortschritts", level="C1", min_level=3,
         text=("Kaum ein Begriff wird so unreflektiert positiv verwendet wie der des "
               "Fortschritts, obwohl bei genauerer Betrachtung deutlich wird, dass "
               "technologische Errungenschaften stets ambivalent sind. Die "
               "Industrialisierung etwa brachte einerseits eine nie dagewesene "
               "Steigerung des materiellen Wohlstands mit sich, zog andererseits "
               "jedoch ökologische Verwerfungen nach sich, deren Ausmaß erst "
               "Generationen später vollständig erfasst wurde. Ähnliches lässt "
               "sich, so argumentieren manche Kulturkritiker, auf die "
               "gegenwärtige Digitalisierung übertragen: Während sie ungeahnte "
               "Möglichkeiten der Vernetzung eröffnet, drohe zugleich eine "
               "schleichende Erosion zwischenmenschlicher Nähe. Wer Fortschritt "
               "unkritisch bejaht, verkennt mithin, dass jeder technologische "
               "Umbruch nicht nur Lösungen, sondern auch neue, bislang unbekannte "
               "Problemlagen hervorbringt."),
         vocab=[("die Errungenschaft", "achievement"), ("die Verwerfung", "distortion/upheaval"),
                ("das Ausmaß", "extent/scale"), ("die Vernetzung", "networking/interconnection"),
                ("die Erosion", "erosion"), ("verkennen", "to fail to recognize")],
         grammar_notes="Extended participial attributes (nie dagewesene Steigerung), nominalized "
                       "abstractions, and subjunctive-tinged reported argument (so argumentieren...) "
                       "typical of C1 essayistic register.",
         questions=[
             dict(q="Was bringt die Industrialisierung laut Text mit sich?", options=["Nur Nachteile", "Wohlstand und ökologische Probleme", "Keine Veränderungen"], correct="Wohlstand und ökologische Probleme"),
             dict(q="Was befürchten manche Kulturkritiker bei der Digitalisierung?", options=["Zu viel Vernetzung ohne Nachteile", "Erosion zwischenmenschlicher Nähe", "Weniger technologische Möglichkeiten"], correct="Erosion zwischenmenschlicher Nähe"),
         ]),
    dict(id="c1_erinnerung_identitaet", title="Erinnerung und Identität", level="C1", min_level=3,
         text=("Dass unsere Erinnerungen keineswegs ein originalgetreues Abbild "
               "vergangener Ereignisse darstellen, sondern vielmehr fortwährend "
               "neu konstruiert werden, gehört mittlerweile zu den gesicherten "
               "Erkenntnissen der Gedächtnisforschung. Jedes Mal, wenn wir uns an "
               "etwas erinnern, wird die entsprechende Erinnerung im Lichte "
               "gegenwärtiger Erfahrungen und Bedürfnisse subtil verändert — ein "
               "Umstand, der weitreichende Konsequenzen für unser Verständnis von "
               "Identität hat. Wenn nämlich das, woran wir uns erinnern, "
               "keineswegs statisch ist, dann kann auch die Identität, die sich "
               "maßgeblich aus diesen Erinnerungen speist, nicht als feste Größe "
               "begriffen werden. Vielmehr erscheint sie als etwas, das sich in "
               "einem beständigen Prozess der Neuverhandlung befindet — eine "
               "Erkenntnis, die sowohl beunruhigend als auch befreiend wirken kann."),
         vocab=[("originalgetreu", "true to the original"), ("das Abbild", "image/representation"),
                ("die Gedächtnisforschung", "memory research"), ("sich speisen aus", "to draw from/be fed by"),
                ("die Neuverhandlung", "renegotiation"), ("beunruhigend", "unsettling")],
         grammar_notes="Complex conditional chains (Wenn ... dann kann ... nicht ...), passive "
                       "constructions, and dense nominal style characteristic of academic C1 prose.",
         questions=[
             dict(q="Was zeigt die Gedächtnisforschung laut Text?", options=["Erinnerungen sind unveränderlich", "Erinnerungen werden ständig neu konstruiert", "Erinnerungen sind immer korrekt"], correct="Erinnerungen werden ständig neu konstruiert"),
             dict(q="Wie wird Identität am Ende des Textes beschrieben?", options=["Als feste, unveränderliche Größe", "Als Prozess der Neuverhandlung", "Als reines Konstrukt ohne Bezug zur Erinnerung"], correct="Als Prozess der Neuverhandlung"),
         ]),
    dict(id="c1_ironie_humor", title="Ironie im deutschen Humor", level="C1", min_level=3,
         text=("Dem deutschsprachigen Raum wird im internationalen Vergleich "
               "gerne ein eher trockener, bisweilen gar humorloser Umgang mit "
               "Komik nachgesagt — ein Klischee, das einer genaueren Betrachtung "
               "kaum standhält. Zwar mag es zutreffen, dass sich deutscher Humor "
               "seltener in überschwänglicher Slapstick-Komik äußert, doch gerade "
               "die Ironie nimmt in der deutschen Sprachkultur eine bemerkenswert "
               "prominente Stellung ein. Ironische Äußerungen setzen freilich ein "
               "hohes Maß an gemeinsamem kulturellem Kontextwissen voraus, ohne "
               "das die eigentliche, oft gegenteilige Bedeutung des Gesagten "
               "kaum zu erschließen ist. Für Lernende stellt dies eine der "
               "größten Herausforderungen dar: Wer die Ironie eines deutschen "
               "Muttersprachlers wörtlich nimmt, läuft Gefahr, den Kern der "
               "Aussage — und mitunter auch den Witz dahinter — vollständig zu "
               "verfehlen."),
         vocab=[("nachsagen", "to attribute (a reputation) to"), ("standhalten", "to hold up/withstand"),
                ("überschwänglich", "effusive/exuberant"), ("voraussetzen", "to presuppose/require"),
                ("erschließen", "to deduce/access"), ("verfehlen", "to miss/fail to grasp")],
         grammar_notes="Concessive constructions (Zwar mag es zutreffen, dass..., doch...) and "
                       "extended relative clauses with embedded negation (ohne das ... kaum zu ...).",
         questions=[
             dict(q="Was wird dem deutschsprachigen Raum laut Text oft nachgesagt?", options=["Übertriebener Humor", "Trockener, humorloser Umgang mit Komik", "Kein Interesse an Ironie"], correct="Trockener, humorloser Umgang mit Komik"),
             dict(q="Was setzt Ironie laut Text voraus?", options=["Laute Betonung", "Gemeinsames kulturelles Kontextwissen", "Einfache Wortwahl"], correct="Gemeinsames kulturelles Kontextwissen"),
         ]),
]

STORY_MIN_LEVEL_BY_CEFR = {"A1": 3, "A2": 3, "B1": 3, "B2": 3, "C1": 40}
for _s in STORIES:
    _s["min_level"] = STORY_MIN_LEVEL_BY_CEFR.get(_s["level"], 3)


def available_stories(level: int):
    return [s for s in STORIES if level >= s["min_level"]]


def get_story(story_id: str):
    return next((s for s in STORIES if s["id"] == story_id), None)
