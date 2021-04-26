import pathlib
from elasticsearch import Elasticsearch
import tokenizer
import ranker
import parse_data

es = Elasticsearch([{'host': 'localhost', 'post': 9200}])
origin_data = parse_data.read_from_csv()


# input the specified query
# def exact_search_query(origin, field):
#     query = ' '.join(tokenizer.tokenize(origin, False))
#     res = es.search(index="cfc", body={
#         "query": {
#             "match_phrase": {
#                 field: query
#             }
#         }
#     })
#     retrieved = []
#     for hit in res["hits"]["hits"]:
#         retrieved.append(hit['_id'])
#     return retrieved

def exact_search_query(origin, field, slop):
    query = ' '.join(tokenizer.tokenize(origin, False))
    res = es.search(index="cfc", body={
        "query": {
            "match_phrase": {
                field: {
                    "query": query,
                    "slop": slop
                }
            }
        }
    })
    retrieved = {}
    for hit in res["hits"]["hits"]:
        retrieved[hit['_id']] = hit['_score']
    print(retrieved)
    return retrieved


def general_search_query(origin, field):
    if field == 'speaker':
        query = ' '.join(tokenizer.tokenize(origin, False))
    else:
        query = ' '.join(tokenizer.tokenize(origin, True))
    res = es.search(index="general", body={
        "query": {
            "match": {
                field: query
            }
        }
    })
    retrieved = {}
    for hit in res["hits"]["hits"]:
        retrieved[hit['_id']] = hit['_score']
    return retrieved


# initialize elastic search server
def exact_initialize_es():
    es.indices.create(index='cfc', ignore=400)
    for doc_id, contents in origin_data.items():
        speaker = contents['speaker']
        title = ' '.join(tokenizer.tokenize(contents['title'], False))
        description = ' '.join(tokenizer.tokenize(contents['description'], False))
        transcript = ' '.join(tokenizer.tokenize(contents['transcript'], False))
        es.index(index='cfc', id=doc_id, body={
            'speaker': speaker,
            'title': title,
            'description': description,
            'transcript': transcript
        })


def general_initialize_es():
    es.indices.create(index='general', ignore=400)
    for doc_id, contents in origin_data.items():
        print(doc_id)
        speaker = contents['speaker']
        title = ' '.join(tokenizer.tokenize(contents['title'], True))
        description = ' '.join(tokenizer.tokenize(contents['description'], True))
        transcript = ' '.join(tokenizer.tokenize(contents['transcript'], True))
        es.index(index='general', id=doc_id, body={
            'speaker': speaker,
            'title': title,
            'description': description,
            'transcript': transcript
        })


def rank_one(query, field, slop):
    res = exact_search_query(query, field, slop)
    # return sorted(res, key=lambda k: origin_data[int(k)]['views'], reverse=True)
    tmp = ranker.divide_relevant_levels(res)
    return [*tmp[0], *tmp[1], *tmp[2], *tmp[3]]


def rank_all(query, slop):
    res = rank_one(query, 'title', slop)
    rank_speaker = rank_one(query, 'speaker', slop)
    rank_description = rank_one(query, 'description', slop)
    rank_transcript = rank_one(query, 'transcript', slop)
    tmp = res.copy()
    for i in rank_speaker:
        if i not in tmp:
            res.append(i)
    tmp = res.copy()
    for i in rank_description:
        if i not in tmp:
            res.append(i)
    tmp = res.copy()
    for i in rank_transcript:
        if i not in tmp:
            res.append(i)
    return res


if __name__ == '__main__':
    # exact_initialize_es()
    general_initialize_es()
