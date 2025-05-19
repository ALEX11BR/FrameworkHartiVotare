# Generare hărți electorale România

Pe baza datelor din CSV-urile de la [https://prezenta.roaep.ro/](https://prezenta.roaep.ro/), cu scripturi de făcut hărți (SVG cu injectare de CSS) generez hărți electorale.

![Alegerile parlamentare 2024 - Camera Deputaților - câștigători per UAT](./harti/voturi-uat-dep-2024.svg)

Fișierele din repository:
- `make_svg.py` - generează la stdout harta UAT-urilor din România pornind de la limite unităților administrativ-teritoriale în format geojson
- scripturi de generare hărți cu rezultate (aproape complet automatizat - nu necesită prelucrare manuală după generare, doar o eventuală bibilire a unor parametrii listați la începutul fișierelor)
    - `make_map.py` - generează harta cu rezultatele prezențelor prelucrând csv-urile
    - `make_map_diff.py` - generează harta cu voturile exprimate târziu (după 21) prelucrând csv-urile
    - `make_winner.py` - generează harta cu câștigătorii per UAT (afișează la stdout un șablon adecvat pentru informațiile despre candidați, indicând ce praguri se văd pe hartă și necesită culori specificate)
- `text-to-path.sh` - convertește textul din svg-uri în căi pentru o randare mai consistentă a acestuia
- `harti` generate prin scripturile de mai sus
- `info-candidati` - informații despre candidații de la un set de alegeri în format csv - folosit de `make_winner.py`. Câmpuri:
    - nume candidat din csv cu informații (fără terminația `-voturi`)
    - culorile folosite, în funcție de prag
    - nume de afișat în legendă
- `info-voturi` - CSV-urile de la ROAEP
- fișiere `.geojson` cu date brute despre UAT-uri
    - cele ce nu sunt cu `wgs84` folosesc coordonate conform `Romania_double_stereo.wkt`
