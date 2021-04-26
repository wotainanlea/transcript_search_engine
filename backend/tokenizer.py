import pathlib
import parse_data
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

stoplist = set(pathlib.Path('data/stoplist.txt').read_text().split())


def tokenize(file, stemming):
    words = []
    for w in file.strip().split():
        if any(i.isdigit() for i in w):
            continue
        s = remove_punctuation(w.lower())
        for a in s:
            if a not in stoplist and "'" not in a:
                if not stemming:
                    words.append(a)
                else:
                    words.append(stemmer.stem(a))
    return words


def remove_punctuation(word):
    word = word.strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`—{|}~')
    word = word.replace('/', '-')
    word = word.replace('+', '-')
    word = word.replace(':', '-')
    word = word.replace('.', '-')
    words = word.split('-')
    res = []
    for word in words:
        if not word:
            continue
        word = word.strip('!"#$%&\'()*+,-./:;<=>?@[\\]^_`—{|}~')
        res.append(word)
    return res


def inverted_index(origin_data, field, stemming=True):
    posting_list = {}
    for talk_id, info in origin_data.items():
        words = tokenize(info[field], stemming)
        for word in words:
            if word in posting_list:
                posting_list[word].append(talk_id)
            else:
                posting_list[word] = [talk_id]
    return posting_list


if __name__ == "__main__":
    data = parse_data.read_from_csv()
    print(inverted_index(data, 'transcript'))