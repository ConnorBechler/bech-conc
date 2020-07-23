"""
This module implements a range of corpus related functions and classes 
using the NLTK and spaCy libraries

https://www.nltk.org/book/ch03.html
https://www.nltk.org/_modules/nltk/collocations.html


@author: Connor Bechler
@date: Spring, 2020
"""

import nltk
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder, TrigramAssocMeasures, TrigramCollocationFinder
import spacy

#Initialize general lemmatizing/parsing tools
nlp = spacy.load("en_core_web_sm")
lem = spacy.load("en_core_web_sm", disable = ['parser'])

def clean_corpus(text):
    """Function for removing extra lines from a given text and returning it as a string"""
    punc = '.?!" \''
    newlines = []
    newtext = ""
    lines = text.split("\n")

    for line in lines:
        if line != "":
            if line[-1] not in punc:
                line += "."
            line += "\n"
            newlines.append(line)
    for line in newlines:
        newtext += line
    return newtext

def lemmatize_corpus(text):
    """Function producing a lemmatized version of a given text"""
    #Tokenize for processing
    text_tokens = nltk.word_tokenize(text)
    token_num = len(text_tokens)
    #Chunk texts to permit spacy parsing
    token_limit = 10000
    chunks = []
    chunk_num = token_num // token_limit
    for i in range(1, chunk_num):
        txt = ' '.join(text_tokens[token_limit*(i-1):token_limit*i])
        chunks.append(txt)
    txt = ' '.join(text_tokens[token_limit*(chunk_num):token_num])
    chunks.append(txt)
    #lemmatize chunks
    lemmas = []
    print('Chunks:', chunk_num)
    cur = 1
    for chunk in chunks:
        doc = lem(chunk)
        for token in doc:
            try:
                lemmas.append(token.lemma_)
            except:
                lemmas.append(token.text)
        print('Chunk', cur, 'of', chunk_num, 'processed')
        cur += 1
    newtext = " ".join(lemmas)
    
    return newtext

class Corpus(object):
    """Indexed text class drawn mostly from https://www.nltk.org/book/ch03.html;
       conc_format_lines and concordance are a decomposed form of their original concordance function,
       which conc_collocate is strongly modeled after.
    """
    
    def __init__(self, stemmer, raw):
        """Initializes indexed text with index of stemmed words as tokens"""
        self._raw = raw 
        self._tokens = nltk.word_tokenize(raw)
        self._text = self._tokens
        #Kind of legacy, but here just in case I end up re-implementing stemming
        self._stemmer = stemmer
        self._index = nltk.Index((word, i) for (i, word) in enumerate(self._text))
        self._sents = nltk.sent_tokenize(self._raw)

    def conc_format_line(self, ind, width=50):
        """Method to return or print a specified concordance line"""
        wc= int(width/4)
        lcontext = ' '.join(self._text[ind-wc:ind])
        rcontext = ' '.join(self._text[ind:ind+wc])
        ldisplay = '{:>{width}}'.format(lcontext[-width:], width=width)
        rdisplay = '{:{width}}'.format(rcontext[:width], width=width)
        return str(ind) + " " + ldisplay + " " + rdisplay + "\n"
    
    def concordance(self, word, width=50):
        """LEGACY Prints all concordance lines for a given word within a given word-span
        NO LONGER IN USE, REPLACED BY conc_mult"""
        key = word #self._stem(word)
        output = ""
        for i in self._index[key]:
            output += self.conc_format_line(i, width) 
        return output

    def conc_collocate(self, word, coll, width=50):
        """LEGACY Modified concordance function to pull lines based on presence of collocate
        NO LONGER IN USE REPLACED BY conc_mult"""
        key = word #self._stem(word)
        key2 = coll
        wc = int(width/4)
        output = ""
        for i in self._index[key]:
            context = ' '.join(self._text[i-wc:i+wc])
            mid = context.find(self._text[i])
            context = context[mid-width-1:mid+width]
            if key2 in context:
                output += self.conc_format_line(i, width)
        return output

    def conc_mult(self, word, width=50):
        """Method which prints all concordance lines for a given sequence of words within a given character-span"""
        keys = nltk.word_tokenize(word)
        wc = int(width/4)
        output = ""
        #Get concordance lines with first (or only) key
        for i in self._index[keys[0]]:
            #Check if more than one key
            if len(keys) > 1:
                context = ' '.join(self._text[i-wc:i+wc])
                mid = context.find(self._text[i])
                context = context[mid-width-1:mid+width]
                #If more than one key, check if each key is in context or not
                for j in range(len(keys)):
                    if (' ' + keys[j] + ' ') in context:
                        #If final key in context, add line to output
                        if j+1 >= len(keys):
                            output += self.conc_format_line(i, width)
                    else :
                        break
            #If only key, add line to output
            else :
               output += self.conc_format_line(i, width) 
        return output

    def _stem(self, word):
        """LEGACY Method which lowercases and stems a given word"""
        return self._stemmer.stem(word).lower()
    
    def sentence_search(self, key):
        """Method which pulls sentences with specific keywords from corpus and returns them as a string
        TODO: Make function not bound to two keys"""
        output = []
        keys = nltk.word_tokenize(key)
        if len(keys) == 1:
            for sent in self._sents:
                if key in sent:
                    output.append(sent)
        elif len(keys) == 2 :
            for sent in self._sents:
                if (keys[0] in sent) and (keys[1] in sent):
                    output.append(sent)
        return output
    
    def sentence_parse(self, key1=None, key2=None, sent_list = []):
        """UNUTILIZED: Need to perfect grammar dependency comparison
        Method which parses the grammatical relationships between two words in every sentence they co-occur"""
        if sent_list == []:
            sent_list = self.sentence_search(key1 + " " +key2)
        output = ""
        for sent in sent_list:
            doc = nlp(sent)
            output += sent + "\n"
            for token in doc:
                if key1 !=None and key2 !=None:
                    if nlp(key1)[0].lemma == token.lemma:
                        output += "(" + token.text + ", " + token.head.text + ") "
                    if nlp(key2)[0].lemma == token.lemma:
                        output += "(" + token.text + ", " + str([child for child in token.children]) + ") "
                        if (child for child in token.children) == nlp(key1)[0].lemma:
                            output += "key2 depedent on key 1"
                else:
                    output += "(" + token.text + ", " + token.dep_ + ") "
            output += "\n"
        return output

    def find_collocates(self, key, win=5, min_freq=1, min_score=0):
        """Method to give all collocations for a given score
        http://www.nltk.org/howto/collocations.html
        """
        collocates = []
        keys = nltk.word_tokenize(key)
        if len(keys) == 1:
            #Initialize ngram list of bigrams
            bgrm_msr = BigramAssocMeasures()
            finder = BigramCollocationFinder.from_words(self._text, window_size=win)
            finder.apply_freq_filter(min_freq)
            ngram_list = finder.score_ngrams(bgrm_msr.pmi)
            #Find bigrams with key
            for x in range(len(ngram_list)):
                if ngram_list[x][1] >= min_score:
                    #Check if the non-key part of bigram is to the right of key1
                    if (key in ngram_list[x][0][0]):    
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][1], ngram_list[x][1], 'R', freq))
                    #... or to the left of key 1
                    elif (key in ngram_list[x][0][1]):
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][0], ngram_list[x][1], 'L', freq))
        elif len(keys) == 2:
            #Initialize ngram list of trigrams
            tgram_msr = TrigramAssocMeasures()
            finder = TrigramCollocationFinder.from_words(self._text, window_size=win)
            finder.apply_freq_filter(min_freq)
            ngram_list = finder.score_ngrams(tgram_msr.pmi)
            #Find trigrams with keys
            for x in range(len(ngram_list)):
                if ngram_list[x][1] >= min_score:
                    #Check if the non-key part of trigram is to the right of key1 and key2
                    if (keys[0] in ngram_list[x][0][0]) and (keys[1] in ngram_list[x][0][1]):    
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][2], ngram_list[x][1], '1 2 X', freq))
                    #... or to the left of key 1 and key 2
                    elif (keys[0] in ngram_list[x][0][1]) and (keys[1] in ngram_list[x][0][2]):
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][0], ngram_list[x][1], 'X 1 2', freq))
                    #... or between key 1 and key 2
                    elif (keys[0] in ngram_list[x][0][0]) and (keys[1] in ngram_list[x][0][2]):
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][1], ngram_list[x][1], '1 X 2', freq))
                    #... or between key 2 and key 1
                    elif (keys[0] in ngram_list[x][0][2]) and (keys[1] in ngram_list[x][0][0]):
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][1], ngram_list[x][1], '1 X 2', freq))
                    #... or to the right of key 2 and key 1
                    elif (keys[0] in ngram_list[x][0][1]) and (keys[1] in ngram_list[x][0][0]):    
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][2], ngram_list[x][1], '2 1 X', freq))
                    #... or to the left of key 2 and key 1
                    elif (keys[0] in ngram_list[x][0][2]) and (keys[1] in ngram_list[x][0][1]):
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][0], ngram_list[x][1], 'X 2 1', freq))
        else:
            raise ValueError('Can only handle bigrams and trigrams')
        return collocates

    def alt_find_collocates(self, key, win=5, min_freq=1, min_score=0):
        """Method to give all collocations for a given score
        http://www.nltk.org/howto/collocations.html
        """
        collocates = []
        keys = nltk.word_tokenize(key)
        if len(keys) == 1:
            #Initialize ngram list of bigrams
            bgrm_msr = BigramAssocMeasures()
            finder = BigramCollocationFinder.from_words(self._text, window_size=win)
            finder.apply_freq_filter(min_freq)
            ngram_list = finder.score_ngrams(bgrm_msr.pmi)
            #Find bigrams with key
            for x in range(len(ngram_list)):
                if ngram_list[x][1] >= min_score:
                    if (key in ngram_list[x][0]):    
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][0] + ' ' + ngram_list[x][0][1], freq, ngram_list[x][1]))
        elif len(keys) == 2:
            #Initialize ngram list of trigrams
            tgram_msr = TrigramAssocMeasures()
            finder = TrigramCollocationFinder.from_words(self._text, window_size=win)
            finder.apply_freq_filter(min_freq)
            ngram_list = finder.score_ngrams(tgram_msr.pmi)
            #Find trigrams with keys
            for x in range(len(ngram_list)):
                if ngram_list[x][1] >= min_score:
                    if (keys[0] in ngram_list[x][0]) and (keys[1] in ngram_list[x][0]):    
                        freq = finder.ngram_fd[ngram_list[x][0]]
                        collocates.append((ngram_list[x][0][0] + ' ' + ngram_list[x][0][1] + ' ' + ngram_list[x][0][2], freq, ngram_list[x][1]))
        else:
            raise ValueError('Can only handle bigrams and trigrams')
        return collocates

    def format_collocates(self, colls, pr=False):
        """Method to properly format or print a given list of collocates"""
        output = '     Collocate\t     Location\t     Frequency\t     Score\n'
        format_string = '{rank:<5}{collocate:<16}{loc:<16}{freq:<16}{score:<6}'
        for i in range(len(colls)):
            output += format_string.format(rank=i+1, collocate=colls[i][0], loc=colls[i][2], freq=colls[i][3], score=round(colls[i][1], 4)) + '\n'
        if pr :
            print(output)
        else :
            return output

    def alt_format_collocates(self, colls, pr=False):
        """Method to properly format or print a given list of collocates"""
        output = '     Collocation\t     \t     Frequency\t     Score\n'
        format_string = '{rank:<5}{collocation:<40}{freq:<16}{score:<6}'
        for i in range(len(colls)):
            output += format_string.format(rank=i+1, collocation=colls[i][0], freq=colls[i][1], score=round(colls[i][2], 4)) + '\n'
        if pr :
            print(output)
        else :
            return output

#Test cases
if __name__ == '__main__':
    
    try:
        porter = nltk.PorterStemmer()
        text = ' '.join(nltk.corpus.webtext.words('grail.txt'))
        corpus = Corpus(porter, text)
        print("Tokens in test corpora:", len(corpus._text))
        print(corpus._index)
        print(type(corpus._index))
        print(len(corpus._index))
        print(len(corpus._index['Arthur']))
        """
        print(corpus.format_collocates(corpus.find_collocates('FRENCH GUARDS', 10, 1, 15)))
        print(corpus.concordance('coconut'))
        print(corpus.conc_format_line(4000))
        print(corpus.conc_collocate('knight', 'grail'))
        print(corpus.sentence_parse("coconut", "swollow"))
        print(corpus.conc_mult('ROBIN bravely', 50))
        print("Tests passed!")
        """
    except Exception as e:
        print("Tests failed due to:", e)