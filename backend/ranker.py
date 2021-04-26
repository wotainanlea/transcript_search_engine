import math
import parse_data
import search

import tokenizer

talk_count = 4004
origin_data = parse_data.read_from_csv()
search_results = 20


# return a dictionary where key is term, value is frequency in the query text
def process_query(query, stemming=True):
    query_dict = {}
    words = tokenizer.tokenize(query, stemming)
    for w in words:
        count = 1
        if w in query_dict:
            count = query_dict[w] + 1
        query_dict[w] = count
    return query_dict


def get_documents(field, stemming):
    res = {}
    for doc_id in origin_data.keys():
        res[doc_id] = tokenizer.tokenize(origin_data[doc_id][field], stemming)
    return res


# return a dictionary where key is term, value is frequency in document and its id
def process_documents(query_dict, stemming, field):
    doc_dict = {}
    documents = get_documents(field, stemming)
    for key, value in documents.items():
        for term in value:
            if term in query_dict:
                if term in doc_dict:
                    count = 1
                    if key in doc_dict[term]:
                        count = doc_dict[term][key] + 1
                    doc_dict[term][key] = count
                else:
                    doc_dict[term] = {}
                    doc_dict[term][key] = 1
    return doc_dict


def get_df(query_dict, doc_dict):
    df_dict = {}
    for key in query_dict.keys():
        if key not in doc_dict:
            df_dict[key] = 0.0
        else:
            df_dict[key] = math.log10(talk_count / len(doc_dict[key]))
    return df_dict


def get_query_weight(query_dict, df_dict):
    query_weight_dict = {}
    for key in query_dict.keys():
        tf = 1 + math.log10(query_dict[key])
        query_weight_dict[key] = tf * df_dict[key]
    return query_weight_dict


def get_documents_weight(query_dict, doc_dict, df_dict):
    documents_weight_dict = {}
    for key in query_dict.keys():
        for doc_id in origin_data.keys():
            w = 0.0
            if key in doc_dict and doc_id in doc_dict[key]:
                tf = 1 + math.log10(doc_dict[key][doc_id])
                w = tf * df_dict[key]
            if doc_id not in documents_weight_dict:
                documents_weight_dict[doc_id] = {}
            documents_weight_dict[doc_id][key] = w
    return documents_weight_dict


def get_cosine_similarity(query_weight_dict, documents_weight_dict):
    sim_dict = {}
    q_length = 0.0
    for value in query_weight_dict.values():
        q_length += value ** 2
    q_length = math.sqrt(q_length)
    for doc_id in documents_weight_dict.keys():
        d_length = 0.0
        dot_product = 0.0
        for key, value in documents_weight_dict[doc_id].items():
            dot_product += value * query_weight_dict[key]
            d_length += value ** 2
        d_length = math.sqrt(d_length)
        if q_length == 0 or d_length == 0:
            sim_dict[doc_id] = 0.0
        else:
            sim_dict[doc_id] = dot_product / (q_length * d_length)
    return sim_dict


def rank_one(query, field):
    if field == "speaker":
        query_dict = process_query(query, False)
        doc_dict = process_documents(query_dict, False, field)
    else:
        query_dict = process_query(query)
        doc_dict = process_documents(query_dict, True, field)
    df_dict = get_df(query_dict, doc_dict)
    query_weight_dict = get_query_weight(query_dict, df_dict)
    documents_weight_dict = get_documents_weight(query_dict, doc_dict, df_dict)
    similarity = get_cosine_similarity(query_weight_dict, documents_weight_dict)
    candidates = {}
    for doc_id, sim in similarity.items():
        if sim > 0:
            candidates[doc_id] = sim
    return divide_relevant_levels(candidates)


def es_rank_one(query, field):
    candidates = search.general_search_query(query, field)
    return divide_relevant_levels(candidates)


def divide_relevant_levels(candidates):
    if not candidates:
        return [],[],[],[]
    max_sim = max(candidates.values())
    gap = max_sim / 4
    level1 = {}
    level2 = {}
    level3 = {}
    level4 = {}
    for tid, sim in candidates.items():
        doc_id = int(tid)
        views = origin_data[doc_id]['views']
        if sim >= 3 * gap:
            level1[doc_id] = views
        elif sim >= 2 * gap:
            level2[doc_id] = views
        elif sim >= gap:
            level3[doc_id] = views
        else:
            level4[doc_id] = views
    rank1 = sorted(level1, key=lambda k: level1[k], reverse=True)
    rank2 = sorted(level2, key=lambda k: level2[k], reverse=True)
    rank3 = sorted(level3, key=lambda k: level3[k], reverse=True)
    rank4 = sorted(level4, key=lambda k: level4[k], reverse=True)
    return rank1, rank2, rank3, rank4


def rank_all(query, method):
    if method == 'me':
        rank_title_tmp = rank_one(query, 'title')
        rank_speaker_tmp = rank_one(query, 'speaker')
        rank_description_tmp = rank_one(query, 'description')
        rank_transcript_tmp = rank_one(query, 'transcript')
    else:
        rank_title_tmp = es_rank_one(query, 'title')
        rank_speaker_tmp = es_rank_one(query, 'speaker')
        rank_description_tmp = es_rank_one(query, 'description')
        rank_transcript_tmp = es_rank_one(query, 'transcript')
    rank_title = [*rank_title_tmp[0], *rank_title_tmp[1], *rank_title_tmp[2]]
    rank_speaker = [*rank_speaker_tmp[0], *rank_speaker_tmp[1], *rank_speaker_tmp[2]]
    rank_description = [*rank_description_tmp[0], *rank_description_tmp[1]]
    rank_transcript = [*rank_transcript_tmp[0]]
    total_rank = rank_title.copy()
    tmp = total_rank.copy()
    for i in rank_speaker:
        if i not in tmp:
            total_rank.append(i)
    tmp = total_rank.copy()
    for i in rank_description:
        if i not in tmp:
            total_rank.append(i)
    tmp = total_rank.copy()
    for i in rank_transcript:
        if i not in tmp:
            total_rank.append(i)
    return total_rank


if __name__ == "__main__":
    # query = "New York Times"
    print(rank_one('best stats', 'title'))
    # print(origin_data[381]['description'])
    # print(origin_data[746]['title'])
