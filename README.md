# Generare hărți electorale România

Pe baza datelor din CSV-urile de la [https://prezenta.roaep.ro/](https://prezenta.roaep.ro/)

Am scripturi de făcut hărți (SVG cu injectare de CSS):
- `make_svg.py` - generează harta UAT-urilor din România pornind de la limite unităților administrativ-teritoriale în format geojson
- scripturi de generare hărți cu rezultate (aproape complet automatizat - nu necesită prelucrare manuală după generare, doar o eventuală bibilire a unor parametrii listați la începutul fișierelor)
    - `make_map.py` - generează harta cu rezultatele prezențelor prelucrând csv-urile
    - `make_map_diff.py` - generează harta cu voturile exprimate târziu (după 21) prelucrând csv-urile
    - `make_winner.py` - generează harta cu câștigătorii per UAT (afișează la stdout un șablon adecvat pentru `candidate_spec.csv`)
- `text-to-path.sh` - convertește textul din svg-uri în căi pentru o randare mai consistentă a acestuia

`candidate_spec.csv` - folosit de `make_winner.py`. Câmpuri:
- nume candidat din csv (fără terminația `-voturi`)
- culoare de bază
- culoare pentru > 50%
- nume de afișat în legendă
