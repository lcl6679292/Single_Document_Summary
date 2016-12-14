# -*- coding: utf-8 -*-
import nltk
import os
from numpy import average
from textrannk3.text_rank_summarizer import get_important_sentences
from scorerank.score_summarizer import *
import os
import re
from remove_redundancy_2 import *
import sys
import time
import string
reload(sys)
sys.setdefaultencoding('utf-8')

def generate_summary(text,answer,ideal_len):
    star=time.time()
    pagerank_dit={}
    scorerank_dic={}
    ratio=1
    return_ratio = 0.8
    sentences_list=get_important_sentences(text, ratio)[1]
    sentence_similarity_list = get_important_sentences(text,ratio)[2]
    for i,sentence in enumerate (sentences_list):
        pagerank_dit[sentence]=(1.0/(i+2))
    sr = ScoreRank()
    result_score,result_sentence=sr.get_important_sentence_by_score_rank(text,ideal_len, ratio)
    for i,sentence in enumerate(result_sentence):
        if pagerank_dit.has_key(sentence.strip()):
            scorerank_dic[sentence]=(1.0/(i+2))*0.2+pagerank_dit[sentence.strip()]*0.8
        else:
            print '图模型中不存在的句子：',sentence.strip()
    all_merge_result= sorted(scorerank_dic.iteritems(), key=lambda d:d[1], reverse = True)
    print 'pagerank与scorerank用时：',time.time()-star
    star=time.time()
    print 'the number of sentences：',len(all_merge_result)
    already_order = remove_redundancy(all_merge_result[:int(len(all_merge_result)*return_ratio)+1],sentence_similarity_list)
    print '去冗余用时：',time.time()-star
    print '\nAnswer',answer
    for i,j in enumerate(already_order):
        print i+1,j
    return already_order
        
def summary(text_name): 
    content=open(text_name).readlines()
    store_list=[]
    for i in content:
        if(i.strip() != '' ):
            store_list.append(i.strip('\n').strip()+' ')
            store_list.append(i.strip('\n').strip()+' ')
    ideal_len=average([len(i) for i in store_list])
#     extract_sentences = generate_summary(text=''.join(store_list),text1=store_list,answer=text_name,ideal_len=ideal_len)
    extract_sentences = generate_summary(text=store_list,answer=text_name,ideal_len=ideal_len)
    return extract_sentences

def summary_description(text_name): 
    store_list=[]
    tokenizer = nltk.data.load('file:' + os.path.dirname(os.path.abspath(__file__)) + '/punkt/english.pickle')
    descripsition_content=open(text_name).readlines()
    for i in descripsition_content:
        if 'FIGS. ' in  i:
            i=i.replace('FIGS. ', 'FIGS.') 
        if 'FIG. ' in  i:
            i=i.replace('FIG. ', 'FIG.')             
        if len(i.strip()) > 65:
            i=re.sub(r"(\([^\)]+\))+", " ", i.strip())
            store_list.extend([(i.strip('\n')+' ')  for i in tokenizer.tokenize(i.strip()) if len(i) > 50])
    ideal_len=average([len(i) for i in store_list])
    extract_sentences = generate_summary(text=store_list,answer=text_name,ideal_len=ideal_len)
    return extract_sentences


if __name__ == "__main__":
    # summary_description('description/'+'Machine translation using global lexical selection and sentence reconstruction_description.txt') 
    # start=time.time()
    # for filenames in os.walk('claim'): 
    #     for filename in filenames[2]:
    #         summary('claim/'+filename)
    # print 'claim用时：',time.time()-start
    start=time.time()
    for filenames in os.walk('description'): 
        for filename in filenames[2]:
            summary_description('description/'+filename)
    print 'description用时：',time.time()-start
