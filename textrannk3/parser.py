#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import nltk
import string
import nltk.stem

stop_words_list = []
stop_words = open('../Single_Document_Summary/textrannk3/data/stop_words.txt').readlines()
for i in stop_words:
    stop_words_list.append(i.strip('\n'))
# print stop_words_list
def sentences_dealing(a_list):
    '''
    tokenizer = nltk.data.load('../punkt/{0}.pickle'.format('english'))
    original_sentences = tokenizer.tokenize(text.strip())    #分句
    '''
    original_sentences = []
    for sentence in a_list:
        original_sentences.append(sentence.strip())
    process_sentences = []
    sentences_cleaned = sentences_cleaning(original_sentences)
#   sentence_cleaning = []
    for sentence in original_sentences:
        if not isinstance(sentence, unicode):
            sentence = sentence.decode('utf-8')
#       sentence = sentence.lower()
#       print sentence
        sentence = re.sub(r"<([^>]+)>", "", sentence)
#       print sentence
#        sentence=re.sub('([%s])+' % re.escape(string.punctuation)," ", sentence)
#       print sentence
        sentence = re.sub(r"(\s)+", " ", sentence)
#       print sentence
        sentence = " ".join(w for w in sentence.split() if w not in stop_words_list)
#       print sentence
        sentence_nltk = ' '.join(nltk.stem.SnowballStemmer('english').stem(word) for word in sentence.split())
#       print "sentence_nltk:" + sentence_nltk
#       sentence_nltk = re.sub(r"[0-9]+","", sentence_nltk)
#       sentence_nltk = re.sub("[.,()/+]", " ", sentence)
#       sentence_nltk = " ".join(e for e in sentence_nltk.split() if len(e) >= 3)
#       print "sentence_nltk:" + sentence_nltk
#       print sentence_nltk
#       process_sentences.append(sentence.split())
        process_sentences.append(sentence_nltk)
    return process_sentences, original_sentences, sentences_cleaned


def sentences_cleaning(original_sentences):
    sentences_cleaned = []
    for sentence in original_sentences:
        if not isinstance(sentence, unicode):
            sentence = sentence.decode('utf-8')
        sentence = sentence.lower()
        #       print sentence
        sentence = re.sub(r"<([^>]+)>", "", sentence)
        #       print sentence
        sentence = re.sub('([%s])+' % re.escape(string.punctuation), " ", sentence)
        #       print sentence
        sentence = re.sub(r"(\s)+", " ", sentence)
        #       print sentence
        sentence = " ".join(w for w in sentence.split() if w not in stop_words_list)
        #       print sentence
        sentence_nltk = ' '.join(nltk.stem.SnowballStemmer('english').stem(word) for word in sentence.split())
        #       print sentence_nltk
        sentence_nltk = " ".join(e for e in sentence_nltk.split() if len(e) >= 3)
        #       print sentence_nltk
        sentence_nltk = re.sub(r"[0-9]+", "", sentence_nltk)
        #       print sentence_nltk
        sentences_cleaned.append(sentence_nltk.split())
    return sentences_cleaned



