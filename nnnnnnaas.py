import json
from random import choice

from dicttoxml import dicttoxml
from flask import Flask, request, Response, jsonify, render_template
from redis import Redis

app = Flask(__name__)

MAX_LENGTH = 500000

FORMATS = {"xml": lambda ret: Response(dicttoxml(ret), mimetype="application/xml"),
           "json": lambda ret: jsonify(response=ret),
           "txt": lambda ret: Response("\n\n".join(["".join(x) for x in ret]), mimetype="text/plain"),
           "html": lambda ret: render_template("gimme.html", ret=ret, choice=choice)}

TEXTS = {"nano": ["NANO"], "hakase": ["HAKASE"], "adore": ["NANO", "HAKASE"], "asie": ["ASIE"], "hakasie": ["HAKASIE"],
         "tap": ["*taps asie's head*", "dlaczego mogę ją tapować po łebku?"]}

count_cache = Redis()


def repeater(texts: list, paragraphs: int = 1, repeats: int = 6) -> list:
    if sum([len(x) for x in texts]) * paragraphs * repeats > MAX_LENGTH:
        return [["baka hentai"]]
    count_cache.incr("nnnnnnaas:"+json.dumps(texts), paragraphs*repeats)
    ret = []
    for _ in range(paragraphs):
        for text in texts:
            ret.append([text] * repeats)
    return ret


@app.route("/")
def index() -> Response:
    return render_template("landing.html", formats=sorted(FORMATS.keys()), texts=sorted(TEXTS.keys()), limit=MAX_LENGTH)


@app.route("/api/data.json")
def api_json() -> Response:
    return jsonify(formats=list(FORMATS), texts=list(TEXTS))


def gimme(texts: list, target: str) -> Response:
    ret = repeater(texts=texts, paragraphs=request.values.get("paragraphs", 1, type=int),
                   repeats=request.values.get("repeats", 6, type=int))
    try:
        return FORMATS[target](ret)
    except KeyError:
        return Response("Format not recognized", mimetype="text/plain")


for text in TEXTS:
    for target in FORMATS:
        app.add_url_rule("/%s.%s" % (text, target), view_func=gimme, defaults=dict(target=target, texts=TEXTS[text]),
                         methods=["GET", "POST"])

if __name__ == '__main__':
    app.run(debug=True)
