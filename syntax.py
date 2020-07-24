"""
This module implements a simple set of grammar/syntax functions
using the NLTK and spaCy libraries

@author: Connor Bechler
@date: Summer, 2020
"""

import spacy
from spacy import displacy
import nltk

nlp = spacy.load("en_core_web_sm")

sent1 = "Protesters threw rocks at police"
sent2 = "Police beat protesters"
sent3 = "Police and protesters clashed"


#class SyntaxFinder:
    #"""Object which analyzes syntactical relationships within a sentence"""

    #def __init__(self):
        
        #self.tg_parse(sent1)
        #self.tg_parse(sent2)
        #self.tg_parse(sent3)

#test = SyntaxFinder()
        
def agency_parse(sents):
    """Command for collecting all of the subjects, processes, direct objects, and propositional objects into a dictionary"""
    agency_list = []
    for sent in sents:
        agency_out = {"sent": [], "subj": [], "process": [], "dobj": [], "propj": []}
        #output = sent + "\n"
        parsed = nlp(sent)
        for token in parsed:
            agency_out["sent"].append(token.text)
            if token.dep_ == "nsubj":
                agency_out["subj"].append(token.text)
            elif token.dep_ == "ROOT":
                agency_out["process"].append(token.text)
            elif token.dep_ == "dobj":
                agency_out["dobj"].append(token.text)
            elif token.dep_ == "propj":
                agency_out["propj"].append(token.text)
        agency_list.append(agency_out)
    return agency_list

        #displacy.serve(nlp(sent), style="dep")

def analyze_agency(agency_list, keys):
    """Command for parsing lists of agency dictionaries"""
    output = ""
    key_count = []
    agents = nltk.word_tokenize(keys)
    for x in range(len(agents)):
        key_count.append([0, 0, 0])
    for entry in agency_list:
        for x in range(len(agents)):
            for word in entry["sent"]: 
                if word.lower() == agents[x]:
                    key_count[x][0] += 1
            for word in entry["subj"]:
                if word.lower() == agents[x]:
                    key_count[x][1] += 1
            for word in entry["dobj"]:
                if word.lower() == agents[x]:
                    key_count[x][2] += 1
            for word in entry["propj"]:
                if word.lower() == agents[x]:
                    key_count[x][2] += 1
    
    for x in range(len(agents)):
        output += (agents[x] + " occured " + str(key_count[x][0]) + " times, was the subject " + str(key_count[x][1]) +
                " times, and the object " + str(key_count[x][2]) + " times." + "\n")
    
    return output
    
    


"""
TODO: Make analyze agency more interesting or introduce a new function

"""
