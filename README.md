Făcut hărți (SVG cu injectare de CSS):
- `make_svg.py` - generează harta UAT-urilor din România pornind de la limite unităților administrativ-teritoriale în format geojson
- `make_map.py` - generează harta cu rezultatele prezențelor prelucrând csv-urile
- `make_map_diff.py` - generează harta cu voturile exprimate târziu (după 21) prelucrând csv-urile
- `make_winner.py` - generează harta cu câștigătorii per UAT (aproape complet automatizat - nu necesită prelucrare manuală după generare)
- `text-to-path.sh` - convertește textul din svg-uri în căi pentru o randare mai consistentă a acestuia

Hărțile generate pot necesita prelucrare manuală în Inkscape: convertit text în căi, adăugat titluri, pus unele legende.

`candidate_spec.csv` - folosit de `make_winner.py`. Câmpuri:
- nume candidat din csv (fără terminația `-voturi`)
- culoare de bază
- culoare pentru > 50%
- nume de afișat în legendă
