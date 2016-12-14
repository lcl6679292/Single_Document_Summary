# -*- coding: utf-8 -*-
import re
from collections import Counter
from paser.parser import sentences_dealing
from numpy import *
from textrannk3.text_rank_summarizer import get_important_sentences
import math
import time

def remove_redundancy(sentences,similar_T):
    sentences_bag_of_words,sentence_word_num = similar_sentences(sentences)
    dic_extract_cov = remove_redundancy_cov(sentences,similar_T,sentences_bag_of_words,sentence_word_num)
    dic_extract_MMR = remove_redundancy_MMR(sentences,similar_T)
    dic_key = remove_redundancy_capital(sentences)
    dic_already_order = {}
    alpha = 0.7;belta = 0.4;theata = 0.3
    for i in dic_extract_cov:
        dic_already_order[i] = alpha*dic_extract_cov[i]+belta*dic_extract_MMR[i]+theata*dic_key[i]
        # dic_already_order[i] = belta*dic_extract_MMR[i]+theata*dic_key[i]
    dic_already_order = sorted(dic_already_order.iteritems(),key = lambda d:d[1],reverse = True)
#     print dic_already_order
    already_order =[]
    for each in dic_already_order:
        already_order.append(sentences[each[0]][0].strip())
    # print dic_already_order[:int(round(len(already_order)*0.35)+1)]
    # if int(round(len(already_order)*0.35))>=7:
    #     return already_order[:7]
    # elif int(round(len(already_order)*0.35))>=4:
    #     return already_order[:4]
    return already_order[:int(round((len(sentences))*0.5))]
def remove_redundancy_capital(sentences):
    im_word = set()
    for i in sentences:
        words = re.split("\.|,|\s|=|\)|\(|\/", i[0])
        for w in words:
            if sum(1 for c in w if c.isupper()) > 1:
                im_word.add(w)
    # print im_word
    already_order = []
    wait_order = []
    dic_key ={}
    comm1 = im_word    
    for i in range(len(sentences)):
        words = re.split("\.|,|\s|=|\)|\(|\/", sentences[i][0])
        comm = set(words) & im_word
        if len(comm) < len(im_word)*0.3:
            wait_order.append(i)
        else:
            comm1 = comm & comm1
            already_order.append(i)
            im_word=im_word-comm1
    for each in wait_order:
        already_order.append(each)
    # print already_order
    # for each in already_order[:7]:
    #     print sentences[each][0]
    for i in range(len(already_order)):
        dic_key[already_order[i]] = 1.0/(i+1)
    return dic_key

def remove_redundancy_cov(sentences,similar_T,sentences_bag_of_words,sentence_word_num):
    num_sentences = len(sentences)
    E = [0]
    top_words,top_words_rate = get_top_words(sentences_bag_of_words)
    remain_sentences = sentences[:]
    remain_sentences[0] = 0
    alpha = 0.1;belta = 5;theata = 0.5   
    j = 0
    # print sentence_word_num
    # print top_words
    #fE function to get extract sentences
    # start = time.time()
    COV_original = COV(top_words,top_words_rate,sentence_word_num,E,belta)
    REL_original = REL(sentences,E,similar_T,alpha)
    fE_original = COV_original + REL_original
    jump = False
    while j<num_sentences-1 :
        add_E = 0
        max_fE = -10
        if jump:
            break
        for i in range(num_sentences):
            if remain_sentences[i] == 0:
                continue
            else:
                REL_later = REL(sentences,E+[i],similar_T,alpha)
                COV_later = COV(top_words,top_words_rate,sentence_word_num,E+[i],belta)
                if abs(REL_later - REL_original)<0.01:
                    jump = True
                    break
                fE_later = REL_later + COV_later
                fE = (fE_later - fE_original)/float(len(sentences[i][0])**theata)
                if fE>max_fE:
                    max_fE = fE
                    add_E = i
                    fE_original1 = fE_later;REL_original1 = REL_later
        if add_E == 0:
            j+=1
            continue
        fE_original = fE_original1;REL_original = REL_original1
        E.append(add_E)
        remain_sentences[add_E] = 0
        j += 1
        if len(E) > 0.5*num_sentences:
            break
    print 'the number when rel is no use:', j, num_sentences
    while j<num_sentences-1 :
        add_E = 0
        max_fE = -10
        for i in range(num_sentences):
            if remain_sentences[i] == 0:
                continue
            else:
                COV_later = COV(top_words,top_words_rate,sentence_word_num,E+[i],belta)
                fE = (COV_later - COV_original)/float(len(sentences[i][0])**theata)
                if fE>max_fE:
                    max_fE = fE
                    add_E = i
                    COV_original1 = COV_later
        if add_E == 0:
            j+=1
            continue
        COV_original = COV_original1
        E.append(add_E)
        remain_sentences[add_E] = 0
        j += 1
        if len(E) > 0.5*num_sentences:
            break
    dic_sentences = {}
    # print 'COV用时',time.time()-start
    for i in range(len(E)):
        dic_sentences[E[i]] = 1.0/(i+1)
    return dic_sentences

    # already_order = []
    # if len(E)>10:
    #     E = E[:len(E)-4]
    # elif len(E)>=5:
    #     E = E[:len(E)-2]
    # for i in range(len(E)):
    #     already_order.append(sentences[E[i]])
    #     # already_order.append(sentences[E[i]][0].strip())
    # return already_order


#MMR
def remove_redundancy_MMR(sentences,similar_T):
    num_sentences = len(sentences)
    E = [0]
    remain_sentences = sentences[:]
    remain_sentences[0] = 0
    score = [0]*num_sentences
    i=0;theata=1.5;alpha=0.5
    while i<num_sentences:
        max_score = -10
        add_E = 0
        for j in range(num_sentences):
            if remain_sentences[j]==0:
                continue
            sum_similarity = 0
            for k in E:
                sum_similarity+=similar_T[j][k]
            sum_similarity = sum_similarity/(float(len(E))**alpha)
            score[j] = sentences[j][1]-theata*sum_similarity
            # print sentences[j][1],sum_similarity,score[j]
            if score[j]>max_score:
                max_score =sentences[j][1]
                add_E = j
        if add_E==0:
            i+=1
            continue
        E.append(add_E)
        remain_sentences[add_E] = 0
        i+=1
    # print E
    dic_sentences = {}
    for i in range(len(E)):
        dic_sentences[E[i]] = 1.0/(i+1)
    # dic_sentences = sorted(dic_sentences.iteritems(),key = lambda d:d[1],reverse = True)
    # print dic_sentences
    return dic_sentences
    # already_order = []
    # if len(E)>10:
    #     E = E[:len(E)-4]
    # elif len(E)>=5:
    #     E = E[:len(E)-2]
    # for i in range(len(E)):
    #     # already_order.append(sentences[E[i]])
    #     already_order.append(sentences[E[i]][0].strip())
    # return already_order

def get_top_words(sentences_bag_of_words):
    limit_times = 3
    num_words = 0
    top_words = []
    for i in range(len(sentences_bag_of_words[0])):
        num_words += sentences_bag_of_words[0][i][1]
        if sentences_bag_of_words[0][i][1] >= limit_times:
            tmp = []
            tmp.append(sentences_bag_of_words[0][i][0])
            tmp.append(sentences_bag_of_words[0][i][1])
            top_words.append(tmp)
        else:
            continue
    # print len(top_words)
    top_words = top_words[:25]
    top_words_rate = [a[1]/float(num_words) for a in top_words]
    # print top_words_rate
    return top_words,top_words_rate

def REL(sentences,E,similar_T,alpha):
    if len(E) == 0:
        return 0
    length_sentences = len(sentences)
    length_E = len(E)
    result = 0
    REL = 0
    for i in range(length_sentences):
        sum_E = 0
        for j in range(length_E):
            sum_E += similar_T[i][E[j]]
        sum_V = alpha*sum(similar_T[i])
        if sum_E > sum_V:
            REL += sum_V
            # print 1
        else:
            # print 2
            REL += sum_E
    return REL

def COV(top_words,top_words_rate,sentence_word_num,E,belta):
    num_top_words = len(top_words)
    COV = 0
    for i in range(len(top_words)):
        sum_word_times = 0
        for j in range(len(E)):
            for k in range(len(sentence_word_num[E[j]])):
                if sentence_word_num[E[j]][k][0] == top_words[i][0]:
                    sum_word_times += sentence_word_num[E[j]][k][1]
                    break
        COV += top_words_rate[i]*sqrt(sum_word_times)
    COV *= belta
    return COV

def similar_sentences(sentences):
    text=''
    sentence_bag_of_words = []
    word_num = 0

    for i in range(len(sentences)):
        text += sentences[i][0]
    process_sentences,original_sentences = sentences_dealing(text)
    for i in range(1,len(process_sentences)):
        process_sentences[0].extend(process_sentences[i])
    process_sentences = [process_sentences[0]]
    
    for i in range(len(sentences)):
        sentence_bag_of_words.append(sentences_dealing(sentences[i][0])[0])
    sentence_word_num =  [Counter(words_list[0]).most_common() for words_list in sentence_bag_of_words]
    sentences_bag_of_words = [Counter(words_list).most_common() for words_list in process_sentences]
    
    return sentences_bag_of_words,sentence_word_num

def multip(x,y):
    return x*y