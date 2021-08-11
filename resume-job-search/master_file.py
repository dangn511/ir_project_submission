import csv
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import re
import nltk

nltk.download('punkt')

from nltk.tokenize import word_tokenize
import pickle, json
import pandas as pd
import random
from nltk.stem import PorterStemmer

from rank_bm25 import *
from gensim.parsing.preprocessing import STOPWORDS
from gensim.parsing.preprocessing import remove_stopwords


def preprocess_document(document):
    '''
    Preprocess document

    Args:
        document: String containing the document's text

    Returns:
        Preprocessed string
    '''
    document = re.sub(r'[^ -~]+', ' ', document)  # replace characters that aren't printable ascii with a space
    document = re.sub(r'[^\w\s]', '',
                      document)  # replace non-word characters (A-Z, 0-9, _) and non-whitespace characters with nothing
    document = document.lower()
    lemmatizer = WordNetLemmatizer()
    document = ' '.join([lemmatizer.lemmatize(word) for word in document.split()])
    document = ' '.join([word for word in document.split() if word not in stopwords.words('english')])
    # print(document)
    return document


def tokenize_document(document, preprocess=False):
    '''
    Convert document to a list of tokens

    Args:
        document: String containing the document's text
        preprocess: Boolean indicating whether the document should be preprocessed

    Returns:
        List of tokens
    '''
    # document = document.replace('"', '\'') # replace " with '
    # document = document.replace('"', '""') # to escape the " in the csv # does not work satisfactorily

    if preprocess:
        document = preprocess_document(document)

    return document.split()


def retrieve_results(search_query, postings_list_file_path, threshold=5):
    '''
    Return documents that match the search query.

    Args:
        search_query:
        postings_list_file_path:

    Returns:
        TODO
    '''
    query_text = tokenize_document(search_query, preprocess=True)
    query_text_set = list(set(query_text))

    index_list = []

    with open(postings_list_file_path) as postings_list_file:
        for row in csv.reader(
                postings_list_file):  # [['word1', 'doc_id1 doc_id2 doc_id3'], ['word2', 'doc_id1 doc_id4'], ...]
            index_list.append(row)

    index_list_terms = [index[0] for index in index_list]

    doc_ids = []

    for word in query_text_set:
        if word in index_list_terms:
            doc_ids.append(index_list[index_list_terms.index(word)][1].split())

    matches = {}
    for i in doc_ids:
        for j in i:
            if j not in matches.keys():
                matches[j] = 1
            else:
                matches[j] += 1

    results = [doc for doc in matches.keys() if matches[doc] >= threshold]

    return results


'''
This is the part that take in the result from retrieve_results and return the real listing
'''


def stopwords_remove(lst):
    lst1 = list()
    for str in lst:
        text_tokens = word_tokenize(str)
        tokens_without_sw = [word for word in text_tokens if not word in all_stopwords_gensim]
        str_t = " ".join(tokens_without_sw)
        lst1.append(str_t)

    return lst1


def spl_chars_removal(lst):
    lst1 = list()
    for element in lst:
        str = ""
        str = re.sub("[^A-Za-z0-9]+", " ", element)
        lst1.append(str)
    return lst1


def remove_non_ascii(sentence):
    temp_str = sentence.encode('ascii', errors='ignore').decode("utf-8")
    result = " ".join(temp_str.split())
    return result


ps = PorterStemmer()


def sentence_stemmer(sentence):
    return [ps.stem(word) for word in sentence]


with open("resume_list_stemmed.pickle", "rb") as input_file:
    resume_list = pickle.load(input_file)

with open("id_job_desc_tokenized.pickle", "rb") as input_file_job:
    job_list = pickle.load(input_file_job)

with open("job_desc_tokenized.pickle", "rb") as input_file_job:
    job_desc_docs_stemmed = pickle.load(input_file_job)

with open('id_job_desc_raw.pickle', "rb") as input_file_job:
    job_list_raw = pickle.load(input_file_job)


def retrieve_from_query(query):
    relevant_docs = retrieve_results(query, 'index_list.csv', threshold=10)

    tokenized_corpus = [job_list[i] for i in relevant_docs]
    bm25 = BM25Okapi(tokenized_corpus)

    df_best = pd.DataFrame(columns=["resume", "job"])
    df_worst = pd.DataFrame(columns=["resume", "job"])

    raw_query = query

    query = remove_non_ascii(raw_query)
    query = remove_stopwords(query).split()
    query = spl_chars_removal(query)
    tokenized_query = sentence_stemmer(query)
    
    results = {}
    for count, item in enumerate(top_15_matches):
        result_id = relevant_docs[item]
        data_point = {
            'job-{}'.format(15-count): {
                'result id': '{}'.format(result_id),
                'description': job_list_raw[result_id],
                'rank': 15-count,
                'url': 'https://www.jobstreet.com.sg/en/job/{}'.format(result_id)
                }
            }
        results.update(data_point)
    
    return results
