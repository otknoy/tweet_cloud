#!/usr/bin/env python
import nlp
import csv
import re

def load_tweets_from_csv(filename):
    ret = csv.reader(open(filename))
    tweets = [nlp.normalize(r[5].decode('utf-8')) for r in ret]
    tweets = [t for t in tweets if not u'@' in t]
    return tweets

def remove_uri(terms):
    return [t for t in terms if re.match('^https?.+?', t.basic_form) == None]


if __name__ == '__main__':
    filename = 'tweets.csv'

    tweets = load_tweets_from_csv(filename)

    terms = []
    for t in tweets:
        temp = nlp.tokenizer(t)
        temp = nlp.merge_nouns(temp)

        temp = nlp.extract_noun(temp)
        temp = nlp.remove_stopword(temp)
        
        temp = remove_uri(temp)
        terms += [t.basic_form for t in temp]

    tf = nlp.term_frequency(terms)
    print "word,count"
    for t, f in sorted(tf.items(), key=lambda x:-x[1]):
        print "%s,%d" % (t.encode('utf-8'), f)
        
