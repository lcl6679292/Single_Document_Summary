#!/usr/bin/env python
# -*- coding: utf-8 -*-
from textrannk3.parser import sentences_dealing
from six.moves import xrange
from collections import Counter
from preprocess import *
import numpy as np
import math
from math import fabs
from numpy import *
import re
import nltk


def get_important_sentences(a_list, percent):
    sentences_list = []
    score_list = []
    process_sentences, original_sentences, sentence_cleaned = sentences_dealing(a_list)   #句子清洗
    #   print process_sentences
    if len(original_sentences) == 0:
        return None

    if len(process_sentences) == 0:
        return None
#    print "共有句子：" + str(len(original_sentences))
#    print "需取句子：" + str(len(original_sentences)*0.2)
    phrase_list = get_phrase_list(original_sentences)
    keywords = get_keywords(original_sentences)
    bag_of_sentences = []
    for sentence in process_sentences:
        bag_of_sentences.append(get_bag_of_words(sentence, phrase_list))
    words_score = get_words_score(bag_of_sentences, keywords, phrase_list)
    sentence_list = sentence_representation(bag_of_sentences, words_score)
    sentence_key = [tuple(sentence) for sentence in sentence_list]
    sentences_by_corpus = dict(zip(sentence_key, original_sentences))

    # 使用BM25算法*******************
    sentences_bag_of_words = [Counter(words_list).most_common() for words_list in sentence_cleaned]  # 句子词袋表示
    #     for i in sentences_bag_of_words:
    #      print i
    if len(sentences_bag_of_words) == 0:
        return None
    sentence_cleaned_key = [tuple(words_list) for words_list in sentences_bag_of_words]
    #使用BM25算法*********************

#    for i in range(len(original_sentences)):
#        print str(i+1)+" original sentences: " + original_sentences[i]
#        print str(i+1)+" process_sentences_key" + str(process_sentences_key[i])
    sentences_scores_result,sentence_similarity_list = sentences_cleaned_importance_score(sentence_list, sentence_cleaned_key)      #句子重要性计算
#     k=0

    for i in sentences_scores_result:
#         k=k+1
#         print  'A',sentences_by_corpus[tuple(i[0])],i[1]
        sentences_list.append(sentences_by_corpus[tuple(i[0])])
        score_list.append(i[1]) 
#     print '------',len(sentences_scores_result) * percent 
#     print len(sentences_list[:int(len(sentences_scores_result) * percent)])    
    return score_list[:int(len(sentences_scores_result) * percent)],sentences_list[:int(len(sentences_scores_result) * percent)],sentence_similarity_list


def sentences_cleaned_importance_score(sentence_list, sentence_cleaned):
    sentences_scores_dic = {}
    sentence_similarity_TFIDF_list = get_similarity_of_sentences(sentence_list)
    sentence_similarity_BM25_list = get_BM25_sentence_similarity(sentence_cleaned)
    sentence_similarity_list = []
    sentence_num = len(sentence_similarity_BM25_list)
    integration_weight = 0.9
    for i in range(sentence_num):
        each_sentence_similarity = []
        for j in range(sentence_num):
#           print sentence_similarity_TFIDF_list[i][j], sentence_similarity_BM25_list[i][j], "||",
            each_sentence_similarity.append(sentence_similarity_TFIDF_list[i][j]*integration_weight + sentence_similarity_BM25_list[i][j]*(1-integration_weight))
        sentence_similarity_list.append(each_sentence_similarity)
#       print
#       print each_sentence_similarity
    k = 0
    for i in xrange(0, sentence_num):
        for j in xrange(0, sentence_num):
            if sentence_similarity_list[i][j] < 0.001 :
                k += 1
                sentence_similarity_list[i][j] = 0
    if k == sentence_num * sentence_num:
        for i in xrange(0, sentence_num):
            for j in xrange(sentence_num):
                if i != j:
                    sentence_similarity_list[i][j] = 1
#     print a
    each_sentence_similarity = [sum(i) for i in sentence_similarity_list]
#     for i in xrange(len(a)):
#         for j in xrange(len(a)):
#             if(each_sentence_similarity[j] !=0):
#                 a[i][j]= float(a[i][j])/float(each_sentence_similarity[j])
#     for i in a:
#         print i
    sentence_importance_result = sentence_importance_computing(sentence_list, sentence_similarity_list, each_sentence_similarity, damping=0.85)
#     print b
    sentence_key = [tuple(sentence) for sentence in sentence_list]
    for i, j in zip(sentence_key, sentence_importance_result):
        sentences_scores_dic[i] = j
    sentences_scores_rank_list = sorted(sentences_scores_dic.items(), key=lambda x:x[1],reverse=True)
    return sentences_scores_rank_list,sentence_similarity_list


def get_similarity_of_sentences(sentence_list):
    similarity_of_sentences = []
    for sentence1 in sentence_list:
        each_sentence_similarity = []
        sentence1_norm = get_product_of_2_sentences(sentence1, sentence1)
        for sentence2 in sentence_list:
            sentence2_norm = get_product_of_2_sentences(sentence2, sentence2)
            each_sentence_similarity.append((get_product_of_2_sentences(sentence1, sentence2)/sqrt(sentence1_norm)/sqrt(sentence2_norm)))
        similarity_of_sentences.append(each_sentence_similarity)
    return similarity_of_sentences


def get_product_of_2_sentences(sentence1, sentence2):
    product = 0
    for word1 in sentence1:
        for word2 in sentence2:
            if word1[0] == word2[0]:
                product += (word1[1] * word2[1])
                break;
    return product


def sentence_importance_computing(sentence_list, similarity_values, each_sentence_similarity, damping=0.85):
    dic = {}
    sentences_num = len(sentence_list)
    default_importance_values = [1.0 / sentences_num] * sentences_num
    for number in xrange(50):
        importance_values = []
#         stop_computing_num = 0
        for index, similarity_value in enumerate(similarity_values):
            rank = 1 - damping
            for i, j, k in zip(similarity_value,default_importance_values,each_sentence_similarity):
                if k == 0:
                    k += 0.0001
                rank += damping * i * j/k
            importance_values.append(rank)
         
        tag = 0
        for i, j in zip(default_importance_values, importance_values):      #页面排序终止条件
            if fabs(i-j) <= 0.0001:
                tag += 1
#         print tag
        if tag == len(default_importance_values):
            break
        else:
            default_importance_values = importance_values
#             if abs(j - rank) <= 0.0001:
#                 stop_computing_num += 1
# #             defalut_importance_values[index] = rank
#         defalut_importance_values=importance_values
#         print 'modify',defalut_importance_values
#         if stop_computing_num == len(similarity_values):
#             break
#     for i,j in zip(sentences_cleaned,defalut_importance_values):
#         print i
#         print j
#         dic[tuple(i)]=j
#     dict=sorted(dic.items(),key=lambda x:x[1],reverse=True)
#     for i in dict:
#         print i[0]
#    print 'modify', defalut_importance_values
    return default_importance_values


def get_bag_of_words(sentence, phrase_list):  # 得到句子关于词和短语的词袋模型
    semi_sentences = re.split("[.,;?!\"\"\'\']", sentence)
    word_list = []
    phrase_process_list = []
    for phrase in phrase_list:
        phrase_process = ' '.join(nltk.stem.SnowballStemmer('english').stem(word) for word in phrase.split())
        phrase_process_list.append(phrase_process)
    for semi_sentence in semi_sentences:
        for phrase in phrase_process_list:
            if phrase in semi_sentence:
                word_list.append(phrase)
                phrase = re.sub("[+]", "\\+", phrase)
                phrase = re.sub("[*]", "\\*", phrase)
                semi_sentence = re.sub(" ?" + phrase, "", semi_sentence)
        for word in semi_sentence.split():
            if (len(word) > 3)or (re.search("\d",word) != None):
                word_list.append(word)
    return word_list


def sentence_representation(bag_of_sentences, words_score):  # 获取句子的TFIDF表示
    sentence_list = []
    for bag_of_sentence in bag_of_sentences:
#        print "bag_of_sentence:", bag_of_sentence
        TFIDF = {}
        sentence = Counter(bag_of_sentence)
#        print "counter:", sentence
        for (word, number) in sentence.items():
#           print "words_score[" + word + "]", words_score[word],
            TFIDF[word] = number * words_score[word]
#        print ""
#        print "sentence:", TFIDF.items()
        sentence_list.append(TFIDF.items())
    return sentence_list


def get_BM25_sentence_similarity(sentences_cleaned):
    words_weight_dic = {}
    total_sentences = ()
    sentences_similarity_scores = []

    sentences_num = len(sentences_cleaned)
    average_sentence_lenth = sum([float(len(i)) for i in sentences_cleaned]) / sentences_num
    words_num_in_each_sentence = [Counter(sentence) for sentence in sentences_cleaned]

    for sentence in sentences_cleaned:
        total_sentences = total_sentences + sentence
    words_num_in_total_sentence = Counter(total_sentences)

    for word, freq in words_num_in_total_sentence.items():
        words_weight_dic[word] = math.log(sentences_num - freq + 0.5) - math.log(freq + 0.5)
    average_weight = sum(words_weight_dic.values()) / len(words_weight_dic.keys())

    for sentence in sentences_cleaned:
        scores = []
        for index in xrange(sentences_num):
            score1 = 0
            #             score = 0
            for word in sentence:
                if word not in words_num_in_each_sentence[index]:
                    continue

                if words_weight_dic[word] >= 0:
                    word_weight = words_weight_dic[word]
                else:
                    word_weight = 0.25 * average_weight

                K = 1.5 * (0.25 + 0.75 * sentences_num / average_sentence_lenth)
                f = words_num_in_each_sentence[index][word]
                score1 += word_weight * f * 2.5 / (f + 1.5 * K)
            # score += (word_weight*words_num_in_each_sentence[index][word]*2.5/(words_num_in_each_sentence[index][word] + 1.5*(0.25+0.75*sentences_num / average_sentence_lenth)))
            #             print score,score1
            scores.append(score1)
        # print 'scores',scores
        sentences_similarity_scores.append(scores)
    # for i in weights:
    #         print i
    return sentences_similarity_scores