"""Holt Google-Bewertungsschnitt und Anzahl für das Profil Ina Langer
und trägt sie in ina-langer.html ein. Wird von GitHub Actions täglich gestartet.
Benötigt das Repository-Secret GOOGLE_PLACES_API_KEY (Google Places API, New)."""
import datetime, json, os, re, sys, urllib.request

PLACE_ID = "ChIJHVvZmepXn0cRDlbZgkvTv4c"
FILE = "ina-langer.html"

def hole_daten():
    key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        print("Kein API-Schlüssel hinterlegt – nichts zu tun.")
        sys.exit(0)
    req = urllib.request.Request(
        f"https://places.googleapis.com/v1/places/{PLACE_ID}",
        headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": "rating,userRatingCount"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return float(d["rating"]), int(d["userRatingCount"])

def eintragen(html, rating, count, heute):
    score = f"{rating:.1f}".replace(".", ",")
    pct = f"{round(rating / 5 * 100)}%"
    neu = re.sub(r'(data-g="score">)[^<]*', rf"\g<1>{score}", html)
    neu = re.sub(r'style="--pct:[^"]*"( data-g="pct")', rf'style="--pct:{pct}"\1', neu)
    neu = re.sub(r'(data-g="count">)[^<]*', rf"\g<1>{count}", neu)
    alt = re.search(r'data-g="stand">([^<]*)', html)
    try:
        alter = (datetime.datetime.strptime(heute, "%d.%m.%Y") - datetime.datetime.strptime(alt.group(1), "%d.%m.%Y")).days
    except Exception:
        alter = 999
    if neu == html and alter < 7:
        return html  # nichts geändert und Datum frisch genug -> kein Commit
    return re.sub(r'(data-g="stand">)[^<]*', rf"\g<1>{heute}", neu)

if __name__ == "__main__":
    rating, count = hole_daten()
    html = open(FILE, encoding="utf-8").read()
    neu = eintragen(html, rating, count, datetime.date.today().strftime("%d.%m.%Y"))
    if neu != html:
        open(FILE, "w", encoding="utf-8").write(neu)
        print(f"Aktualisiert: {rating} Sterne, {count} Bewertungen")
    else:
        print(f"Unverändert: {rating} Sterne, {count} Bewertungen")
