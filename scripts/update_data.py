"""Genera data/rfef.json (RFEF → ligas → equipos, temporada 2026-27) y descarga los escudos a data/icons.

Equipos: artículos de Wikipedia «2026–27 La Liga», «2026–27 Segunda División» y «2026–27 Primera Federación».
Escudos de clubes: imagen principal (infobox) de cada artículo de la Wikipedia en inglés.
Logos de liga: propiedad P154 (logotipo) de Wikidata, servida desde Wikimedia Commons, o la imagen
principal del artículo de la liga en en.wikipedia cuando Wikidata no la tiene.
Wikimedia limita la descarga de originales, así que se piden miniaturas en tamaños estándar:
THUMB para los logos centrales (RFEF y ligas) y CREST, más pequeño, para los escudos de los equipos.
"""
import json
import time
import pathlib
import urllib.parse
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "rfef.json"
ICONS = OUT.parent / "icons"
# px; tamaños admitidos en https://www.mediawiki.org/wiki/Common_thumbnail_sizes
THUMB = 250
CREST = 120
UA = {"User-Agent": "rfef-dendrograma/1.0 (UOC PEC2)", "Accept": "*/*"}

ROOT = {"id": "rfef", "name": "Real Federación Española de Fútbol", "wiki": "Royal Spanish Football Federation"}
# (id, nombre, artículo en.wikipedia) — los filiales sin escudo propio usan el del primer equipo
LEAGUES = [
    {"id": "laliga", "name": "LaLiga EA Sports", "wikidata": "Q324867", "teams": [
        ("alaves", "Deportivo Alavés", "Deportivo Alavés"),
        ("athletic", "Athletic Club", "Athletic Bilbao"),
        ("atletico", "Atlético de Madrid", "Atlético Madrid"),
        ("barcelona", "FC Barcelona", "FC Barcelona"),
        ("betis", "Real Betis", "Real Betis"),
        ("celta", "RC Celta", "RC Celta de Vigo"),
        ("deportivo", "RC Deportivo", "Deportivo de La Coruña"),
        ("elche", "Elche CF", "Elche CF"),
        ("espanyol", "RCD Espanyol", "RCD Espanyol"),
        ("getafe", "Getafe CF", "Getafe CF"),
        ("levante", "Levante UD", "Levante UD"),
        ("malaga", "Málaga CF", "Málaga CF"),
        ("osasuna", "CA Osasuna", "CA Osasuna"),
        ("racing", "Racing de Santander", "Racing de Santander"),
        ("rayo", "Rayo Vallecano", "Rayo Vallecano"),
        ("realmadrid", "Real Madrid", "Real Madrid CF"),
        ("realsociedad", "Real Sociedad", "Real Sociedad"),
        ("sevilla", "Sevilla FC", "Sevilla FC"),
        ("valencia", "Valencia CF", "Valencia CF"),
        ("villarreal", "Villarreal CF", "Villarreal CF"),
    ]},
    # Wikidata solo enlaza el logo horizontal; se usa la versión vertical de Commons, como en LaLiga EA Sports
    {"id": "hypermotion", "name": "LaLiga Hypermotion", "wikidata": "Q35615",
     "logo": "LaLiga Hypermotion 2023 Vertical Logo.svg", "teams": [
        ("albacete", "Albacete BP", "Albacete Balompié"),
        ("almeria", "UD Almería", "UD Almería"),
        ("andorra", "FC Andorra", "FC Andorra"),
        ("burgos", "Burgos CF", "Burgos CF"),
        ("cadiz", "Cádiz CF", "Cádiz CF"),
        ("castellon", "CD Castellón", "CD Castellón"),
        ("celtafortuna", "Celta Fortuna", "Celta Fortuna"),
        ("ceuta", "AD Ceuta", "AD Ceuta FC"),
        ("cordoba", "Córdoba CF", "Córdoba CF"),
        ("eibar", "SD Eibar", "SD Eibar"),
        ("eldense", "CD Eldense", "CD Eldense"),
        ("girona", "Girona FC", "Girona FC"),
        ("granada", "Granada CF", "Granada CF"),
        ("laspalmas", "UD Las Palmas", "UD Las Palmas"),
        ("leganes", "CD Leganés", "CD Leganés"),
        ("mallorca", "RCD Mallorca", "RCD Mallorca"),
        ("oviedo", "Real Oviedo", "Real Oviedo"),
        ("realsociedadb", "Real Sociedad B", "Real Sociedad"),
        ("sabadell", "CE Sabadell", "CE Sabadell FC"),
        ("sporting", "Sporting de Gijón", "Sporting de Gijón"),
        ("tenerife", "CD Tenerife", "CD Tenerife"),
        ("valladolid", "Real Valladolid", "Real Valladolid"),
    ]},
    # Liga dividida en grupos: RFEF → liga → grupo → equipos
    {"id": "federacion", "name": "Primera Federación", "wiki": "Primera Federación", "groups": [
        ("grupo1", "Grupo 1", [
            ("arenas", "Arenas Club", "Arenas Club de Getxo"),
            ("aviles", "Real Avilés Industrial", "Real Avilés Industrial"),
            ("barakaldo", "Barakaldo CF", "Barakaldo CF"),
            ("bilbaoathletic", "Bilbao Athletic", "Bilbao Athletic"),
            ("cacereno", "CP Cacereño", "CP Cacereño"),
            ("coria", "CD Coria", "CD Coria"),
            ("cultural", "Cultural Leonesa", "Cultural y Deportiva Leonesa"),
            ("fabril", "RC Deportivo Fabril", "Deportivo Fabril"),
            ("extremadura", "CD Extremadura", "CD Extremadura"),
            ("logrones", "UD Logroñés", "UD Logroñés"),
            ("lugo", "CD Lugo", "CD Lugo"),
            ("merida", "AD Mérida", "Mérida AD"),
            ("mirandes", "CD Mirandés", "CD Mirandés"),
            ("ourense", "UD Ourense", "UD Ourense"),
            ("ponferradina", "SD Ponferradina", "SD Ponferradina"),
            ("pontevedra", "Pontevedra CF", "Pontevedra CF"),
            ("ferrol", "Racing de Ferrol", "Racing de Ferrol"),
            ("realunion", "Real Unión", "Real Unión"),
            ("unionistas", "Unionistas de Salamanca", "Unionistas de Salamanca CF"),
            ("zamora", "Zamora CF", "Zamora CF"),
        ]),
        ("grupo2", "Grupo 2", [
            ("aguilas", "Águilas FC", "Águilas FC"),
            ("alcorcon", "AD Alcorcón", "AD Alcorcón"),
            ("algeciras", "Algeciras CF", "Algeciras CF"),
            ("antequera", "Antequera CF", "Antequera CF"),
            ("atleticomadrileno", "Atlético Madrileño", "Atlético Madrid"),
            ("cartagena", "FC Cartagena", "FC Cartagena"),
            ("europa", "CE Europa", "CE Europa"),
            ("gimnastic", "Gimnàstic de Tarragona", "Gimnàstic de Tarragona"),
            ("hercules", "Hércules CF", "Hércules CF"),
            ("huesca", "SD Huesca", "SD Huesca"),
            ("ibiza", "UD Ibiza", "UD Ibiza"),
            ("jaen", "Real Jaén", "Real Jaén"),
            ("torremolinos", "Juventud de Torremolinos", "Juventud de Torremolinos CF"),
            ("murcia", "Real Murcia", "Real Murcia"),
            ("majadahonda", "Rayo Majadahonda", "CF Rayo Majadahonda"),
            ("castilla", "Real Madrid Castilla", "Real Madrid CF"),
            ("santandreu", "UE Sant Andreu", "UE Sant Andreu"),
            ("teruel", "CD Teruel", "CD Teruel"),
            ("villarrealb", "Villarreal CF B", "Villarreal CF B"),
            ("zaragoza", "Real Zaragoza", "Real Zaragoza"),
        ]),
    ]},
]


def download(url, tries=5):
    # Wikimedia limita la frecuencia de peticiones (HTTP 429): se espera y se reintenta
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as res:
                return res.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(int(e.headers.get("Retry-After", 5 * (i + 1))) + 5)


def api(base, **params):
    return json.loads(download(f"{base}?{urllib.parse.urlencode({'format': 'json', **params})}"))


def wiki_images(titles, size=THUMB):
    """Miniatura de la imagen principal de cada artículo de en.wikipedia, por título pedido."""
    out = {}
    for i in range(0, len(titles), 40):
        q = api("https://en.wikipedia.org/w/api.php", action="query", prop="pageimages", piprop="thumbnail", pithumbsize=size,
                pilicense="any", redirects=1, titles="|".join(titles[i:i + 40]))["query"]
        alias = {r["to"]: r["from"] for r in q.get("redirects", []) + q.get("normalized", [])}
        for p in q["pages"].values():
            if "thumbnail" in p:
                out[alias.get(p["title"], p["title"])] = p["thumbnail"]["source"].split("?")[0]
    return out


def wikidata_logo(qid, name=None):
    if name is None:
        claims = api("https://www.wikidata.org/w/api.php", action="wbgetclaims", entity=qid, property="P154")["claims"]
        name = claims["P154"][0]["mainsnak"]["datavalue"]["value"]
    pages = api("https://commons.wikimedia.org/w/api.php", action="query", prop="imageinfo", iiprop="url", iiurlwidth=THUMB,
                titles=f"File:{name}")["query"]["pages"]
    return next(iter(pages.values()))["imageinfo"][0]["thumburl"].split("?")[0]


def save_icon(node_id, url):
    # Si ya hay un icono guardado (p. ej. un SVG de una descarga anterior) se reutiliza
    icon = next(ICONS.glob(f"{node_id}.*"), None)
    if icon is None:
        ext = pathlib.Path(urllib.parse.urlparse(url).path).suffix.lower() or ".png"
        icon = ICONS / f"{node_id}{ext}"
        icon.write_bytes(download(url))
        time.sleep(3)
    return f"data/icons/{icon.name}"


def all_teams(lg):
    return lg.get("teams", []) + [t for _, _, teams in lg.get("groups", []) for t in teams]


def main():
    ICONS.mkdir(parents=True, exist_ok=True)
    titles = [ROOT["wiki"]] + [lg["wiki"] for lg in LEAGUES if "wiki" in lg] + [t[2] for lg in LEAGUES for t in all_teams(lg)]
    images = wiki_images(titles)
    crests = wiki_images(titles, CREST)

    def teams(rows):
        return [{"id": tid, "name": name, "icon": save_icon(tid, crests[wiki])} for tid, name, wiki in rows]

    tree = {"id": ROOT["id"], "name": ROOT["name"], "icon": save_icon(ROOT["id"], images[ROOT["wiki"]]), "children": []}
    for lg in LEAGUES:
        logo = images[lg["wiki"]] if "wiki" in lg else wikidata_logo(lg["wikidata"], lg.get("logo"))
        children = ([{"id": gid, "name": name, "children": teams(rows)} for gid, name, rows in lg["groups"]]
                    if "groups" in lg else teams(lg["teams"]))
        tree["children"].append({"id": lg["id"], "name": lg["name"], "icon": save_icon(lg["id"], logo), "children": children})

    OUT.write_text(json.dumps({"season": "2026-27", **tree}, ensure_ascii=False, indent=2))
    print(f"{OUT} · {sum(len(all_teams(lg)) for lg in LEAGUES)} equipos")


if __name__ == "__main__":
    main()
