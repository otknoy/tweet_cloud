#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MeCab
import unicodedata
import re
import math
import numpy as np
import sys

# hiragana, katakana, ascii symbol
STOPWORDS = [unichr(i) for i in xrange(12353, 12353+86)] + \
    [unichr(i) for i in xrange(12449, 12449+90)] + \
    [chr(i) for i in range(33, 127)] + \
    [u'これ', u'あれ', u'それ', u'どれ', u'よう', u'とき', u'こと', u'もの', u'そこ', u'ー',
     u'やつ', u'そう', u'なん', u'なに', u'わけ', u'どこ', u'ほう', u'ため', u'さん', u'くん',
     u'もん', u'みたい', u'いつ', u'ところ',
     u'人', u'自分', u'久しぶり',
     u'月', u'とこ',
     u'部屋', u'目', u'話', u'気', u'頭', u'あと', u'こいつ', u'', 
     'http', '://', 'pdf', 'jp', 'com', '...', 'www',u'html', 'txt',
     'ac', '!!', ');', 'value', 'ne', '.(', 'in', 'of', 'for', '=>', '`)', '):', 'index', 'or',
     'the', 'org', 'To', u')、', '?(', 'to', '!(', '?)', '!!!', 'and', 'co', u')。', ':::', 'ppt',
     '),', ').'
     
     ]
    # [chr(i) for i in range(33, 48)+range(58, 65)+range(91, 97)+range(123, 127)] + \


class Term:
    def __init__(self, surface, basic_form, posid, features):
        self.surface = surface
        self.basic_form = basic_form
        self.posid = posid
        self.features = features

    def __str__(self):
        return u"%s, %s" % (self.surface, u', '.join(self.features))

    def __len__(self):
        return len(self.basic_form)

    def is_noun(self):
        noun_id_list = range(36, 67+1)
        return self.posid in noun_id_list

    def is_adjective(self):
        adjective_id_list = range(10, 12+1)
        return self.posid in adjective_id_list

    def is_verb(self):
        verb_id_list = range(31, 33+1)
        return self.posid in verb_id_list

    def is_suffix(self):
        suffix_id_list = [11, 32] + range(50, 58+1)
        return self.posid in suffix_id_list

    def is_pronoun(self):
        pronoun_id_list = [59, 60]
        return self.posid in pronoun_id_list

    def is_temporal_noun(self):
        temporal_noun_id_list = [58, 66, 67]
        return self.posid in temporal_noun_id_list

    def is_not_independent(self):
        not_independent_id_list = [12, 33, 61] + range(63, 66+1)
        return self.posid in not_independent_id_list

    def is_numeric(self):
        return self.posid == 48 or re.match('[0-9]+', self.surface)

    def is_symbol(self):
        regexp = re.compile(r'^[!"#\$\%\&\'\(\)\*\+,\-\./:;\<\=\>\?\@\[\\\]\^\_\`\{\}\~\|]+$')
        if regexp.search(self.surface) != None:
            return True
        else:
            return False

        
def term_frequency(terms, normalize=False):
    tf = {}
    for t in terms:
        if not tf.has_key(t):
            tf[t] = 0
        tf[t] += 1
    if normalize:
        for t, f in tf.items():
            tf[t] /= float(len(terms))
    return tf

def document_frequency(docs):
    df = {}
    for terms in docs:
        for t in list(set(terms)):
            if not df.has_key(t):
                df[t] = 0
            df[t] += 1
    return df

def tf_idf(docs, normalize=False):
    tfidf_list = []
    df = document_frequency(docs)
    n = len(docs)
    for terms in docs:
        tf = term_frequency(terms, normalize=normalize)
        tfidf = {}
        for t in df.keys():
            if tf.has_key(t):
                tfidf[t] = tf[t] * math.log(float(n)/df[t])
            else:
                tfidf[t] = 0.0
        tfidf_list.append(tfidf)
    return tfidf_list


def tokenizer(s):
    uni = s.encode('utf-8')
    tagger = MeCab.Tagger("-Ochasen")
    node = tagger.parseToNode(uni)

    terms = []
    while node:
        surface = node.surface.decode('utf-8')
        features = node.feature.decode('utf-8').split(u',')
        basic_form = features[6]
        if basic_form == u'*':
            basic_form = surface
        posid = node.posid
        term = Term(surface, basic_form, posid, features)
        terms.append(term)
        node = node.next
    return terms[1:-1]

def normalize(text):
    return unicodedata.normalize('NFKC', text)

def merge_nouns(terms):
    ret = []
    i = 0
    while i < len(terms)-1:
        if not terms[i].is_noun() or terms[i].is_symbol():
            ret.append(terms[i])
            i += 1
            continue
        merged = terms[i]
        j = 0
        while i+j+1 < len(terms):
            if not terms[i+j+1].is_noun():
                break
            surface = merged.surface + terms[i+j+1].surface
            basic_form = merged.basic_form + terms[i+j+1].basic_form
            posid = merged.posid
            features = merged.features
            merged = Term(surface, basic_form, posid, features)
            j += 1
        ret.append(merged)
        i += j+1
    return ret

def extract_noun(terms):
    return [t for t in terms if t.is_noun()]

def remove_stopword(terms, stopwords=STOPWORDS):
    terms = [t for t in terms if not t.is_pronoun()]
    terms = [t for t in terms if not t.is_temporal_noun()]
    terms = [t for t in terms if not t.is_not_independent()]
    terms = [t for t in terms if not t.is_suffix()]
    terms = [t for t in terms if not t.is_numeric()]
    return [t for t in terms if not t.basic_form in stopwords]


if __name__ == '__main__':
    texts = [u'山下さんは山下くんと東京特許許可局へ行った。',
             u'山下さんは山下くんと北海道へ行った。',
             u'山下さんは下山くんと New York へ行った。',
             u'山上さんは山下くんと東京特許許可局へ行った。',]             

    docs = []
    for text in texts:
        terms = tokenizer(text)
        terms = merge_nouns(terms)
        terms = remove_stopword(terms)
        terms = [t.basic_form for t in terms]
        docs.append(terms)

        
    # tf
    print
    print "term frequency"
    for terms in docs:
        tf = term_frequency(terms)
        print " | ".join(["%s, %0.2f" % (t, f) for t, f in tf.items()])

        
    # df
    print
    print "document frequency"        
    df = document_frequency(docs)
    print " | ".join(["%s, %d" % (t, f) for t, f in df.items()])

    
    # tfidf
    print
    print "term frequency * inverse document frequency"        
    tfidf_list = tf_idf(docs)
    for tfidf in tfidf_list:
        print " | ".join(["%s, %0.2f" % (t, f) for t, f in tfidf.items()])
