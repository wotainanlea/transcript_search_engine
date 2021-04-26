from flask import Flask, jsonify, request
from flask_cors import CORS
import ranker
import search
import parse_data


app = Flask(__name__)
CORS(app)
origin_data = parse_data.read_from_csv()


def query_talks(method, field, query, slop):
    if method == "general":
        if field == "all":
            return ranker.rank_all(query, "es")
        else:
            tmp = ranker.es_rank_one(query, field)
            return [*tmp[0], *tmp[1], *tmp[2], *tmp[3]]
    else:
        if field == "all":
            return search.rank_all(query, slop)
        else:
            return search.rank_one(query, field, slop)


def get_all_talks():
    results = [i for i in range(0, 4005)]
    return generate_info(results)


def generate_info(results):
    infos = []
    for tid in results:
        tid = int(tid)
        info = {
            "title": origin_data[tid]["title"],
            "speaker": origin_data[tid]["speaker"],
            "url": origin_data[tid]["url"],
            "duration": origin_data[tid]["duration"],
            "views": origin_data[tid]["views"],
            "date": origin_data[tid]["published_date"],
            "description": origin_data[tid]["description"]
        }
        infos.append(info)
    return {"results": infos}


@app.route('/', methods=['GET'])
def home():
    return "Welcome to TED talks"


@app.route('/all', methods=['GET'])
def query_all_talks():
    return jsonify(get_all_talks())


@app.route('/search', methods=['GET'])
def search_query():
    method = request.args.get("method")
    field = request.args.get("field")
    slop = int(request.args.get("slop"))
    query = request.args.get("query")
    print(slop)
    result = generate_info(query_talks(method, field, query, slop))
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)