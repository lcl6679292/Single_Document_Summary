# _*_ coding:utf-8 __*_
import math
import re
from collections import Counter
import nltk


def get_words_score(bag_of_sentences, keywords, phrase_list):  # 获取词与短语的评分
    words_score = {}
    words = set()
    for bag_of_sentence in bag_of_sentences:
        for word in bag_of_sentence:
            words.add(word)
    IDF_of_words = get_IDF_of_words(bag_of_sentences, words)
    keywords_score = get_keywords_score(words, keywords)
    phrase_score = get_phrase_score(phrase_list)
    phrase_process_list = phrase_score.keys()
    for word in words:
        words_score[word] = keywords_score[word] * IDF_of_words[word]
        if word in phrase_process_list:
            words_score[word] *= phrase_score[word]
#   word = "1-slot spucch format"
#   print IDF_of_words[word], keywords_score[word], phrase_score[word], words_score[word]
    return words_score


def get_keywords_score(words, keywords):  # 获取关键词与关键短语集合
    keywords_score_of_words = {}
    keywords_weight = 4.0
    number_weight = 4.0
    keyword = [word.lower() for word in keywords]
    for word in words:
        if word in keyword:
            keywords_score_of_words[word] = keywords_weight
        else:
            keywords_score_of_words[word] = 1.0
        if re.search("[\d]", word) != None:
            keywords_score_of_words[word] *= number_weight
#   for i in keywords_score_of_words.items():
#       print i
    return keywords_score_of_words


def get_phrase_score(phrase_list):
    phrase_score = {}
    keywords_weight = 4.0
    for phrase in phrase_list:
        phrase_process = ' '.join(nltk.stem.SnowballStemmer('english').stem(word) for word in phrase.split())
        if sum(1 for c in phrase if c.isupper()) > 1:
            phrase_score[phrase_process] = keywords_weight
        else:
            phrase_score[phrase_process] = 1.0
        phrase_len = phrase_process.count(" ")+1
        phrase_score[phrase_process] *= 1
    return phrase_score


def get_IDF_of_words(bag_of_sentences, words):
    IDF_of_words = {}
    sentence_num = len(bag_of_sentences)
#   print sentence_num
    for word in words:
#       print "word:", word
        num = 0
        for bag_of_sentence in bag_of_sentences:
            if word in bag_of_sentence:
                num += 1.0
#       print num
        IDF_of_words[word] = math.log((sentence_num/num), 2)
#       print "IDF:", IDF_of_words[word]
    return IDF_of_words


# 以上为词打分部分，以下为短语抽取部分


def get_keywords(original_sentences):
    keywords = set()
    for sentence in original_sentences:
        word_list = re.split("[.,;?!\"\"\'\' ]", sentence)
        for word in word_list:
            if re.search("[A-Z]{2,}", word) != None:
                keywords.add(word)
#    for word in keywords:
#        print "keyword:", word
    return keywords


def get_phrase_list(original_sentences):  # 获取短语列表，短语从长到短排列
    semi_sentences = []
    word_lists = []
    POS_lists = []
    phrase_len = {}
    for sentence in original_sentences:
        semi_sentence = re.split("[.,;?!\"\"\'\']", sentence)
        for semi_sent in semi_sentence:
            if semi_sent != "":
                semi_sentences.append(semi_sent.strip())
#   for sen in semi_sentences:
#       print "sen:" + str(sen)
    for semi_sentence in semi_sentences:
        word_lists.append([word for word in semi_sentence.split()])
    for word_list in word_lists:
        POS_list = []
        for pos in nltk.pos_tag(word_list):
            POS_list.append(pos[1])
        POS_lists.append(POS_list)
    phrase_set = get_n_grams_set(word_lists, POS_lists)
    for phrase in phrase_set:
        phrase_len[phrase] = phrase.count(" ") + 1
    sorted_phrase_len = sorted(phrase_len.items(), key=lambda x: x[1], reverse=True)
    phrase_list = [phrase[0] for phrase in sorted_phrase_len]
    return phrase_list


def get_n_grams_set(word_lists, POS_lists):
    all_n_grams_list = []
    phrase_set = set()
    POS_of_phrase = {}
    POS_pattern = ["NN NN", "JJ NN", "NNS NN", "NNP NN", "CD NN", "VBN NN", "JJ NN NN", "VBP VBN IN", "NNP NNP",
                   "JJ NNP", "NNP NNP NN", "JJ NNP NNP", "NNP NN NN", "JJ NNP NN", "NN NN NNS", "VBG NNS", "RB NNP",
                   "CD NNP", "NN NNS", "RB VB", "CD NN NN", ]
    for phrase_len in range(2, 4):
        n_grams_list = []
        n_grams = []
        for sent in range(len(word_lists)):
            if len(word_lists[sent]) < phrase_len:
                pass
            else:
                for i in range(0, len(word_lists[sent])-phrase_len+1):
                    phrase = " ".join(word_lists[sent][i:i+phrase_len])
                    POS_of_phrase[phrase] = " ".join(POS_lists[sent][i:i+phrase_len])
                    n_grams.append(phrase)
        for n_gram in Counter(n_grams).items():
            if n_gram[1] > 1:
                n_grams_list.append(n_gram)
        all_n_grams_list.append(n_grams_list)
#   for n_gram_list in all_n_grams_list:
#     for i in n_gram_list:
#            print i, POS_of_phrase[i[0]]
    for n_gram_list in all_n_grams_list:
        for i in n_gram_list:
            if POS_of_phrase[i[0]] in POS_pattern:
                phrase_set.add(i[0])
#   for i in phrase_set:
#       print "phrase:", i
    return phrase_set
