"""
This module implements a command line interface for the corpus module, 
using the colorama module to print results in c o l o r

TODO: Fix collocation coloring, which is currently a mess

@author: Connor Bechler
@date: Spring, 2020
"""

import nltk
from colorama import init, Fore, Back, Style
from corpus import clean_corpus, lemmatize_corpus, Corpus
from syntax import agency_parse, analyze_agency

#Porter function for stemming, although this is now legacy
porter = nltk.PorterStemmer()
#Initialize colorama
init(autoreset=True)
 
class corpus_loop():
    """Main corpus application loop"""

    def __init__(self):
        """Initialize loop"""
        self.comm = ""
        #Initialize text and corpus lists
        self.text_list = []
        self.corpus_list = []
        #Define quit keywords and help text
        self.QUIT = ['Quit','quit','Exit','exit']
        self.help_text = (
"""This is the corpus program BecConc, designed by Connor Bechler.
                
Possible commands are listed below. [square brackets] are command names, 
|straight brackets| are necessary arguments, and (parentheses) are optional arguments.

Commands:  
    *[conc]ordance |word OR index| (additional words) (character span width)
    *[coll]ocation |word| (second word) (window) (min ngram frequency) (min collocation score)
    *[parse] |word| (second word)
    *[switch] corpora
    *[list] corpora
    *[settings]
    *[save] last output as text file in current directory""")
        #Default concordance and collocation settings
        self.conc_width = 50
        self.coll_win = 5
        self.coll_min_freq = 20
        self.coll_min_score = 0
        self.last_out = ''

        #Test/Research default loading of the National Media Protest Corpora (Commented out)
        #self.preload('C:/Users/cbech/Desktop/NLP/BechConc/new_us_corpora.txt')
        #self.preload('C:/Users/cbech/Desktop/NLP/BechConc/new_zh_corpora.txt')

        #Run main loop
        self.load_loop()
        self.io_loop()
    

    def load_loop(self):
        """A function for fetching corpora from the user"""
        while (self.corpus_list == []) and (self.comm not in self.QUIT):
            #Import or load text file into text list or lemmatize a given text
            self.comm = ''
            self.comm = input("[clean] new text, [load] pre-cleaned text, or [lemmatize] a cleaned text? ")
            try:
                if self.comm.lower() == "clean": 
                    #Clean uncleaned text of extra whitespace
                    text_file = input("Filename: ")
                    with open(text_file, encoding='utf8', errors='replace') as f:
                        unclean = f.read()
                        clean = clean_corpus(unclean)
                    #Prompt the user to load the cleaned text for processing or export it
                    while True:
                        choice = input("[load] or [export]? ")
                        if choice.lower() == "load":
                            self.text_list.append((text_file, (clean)))
                            break
                        elif choice.lower() == "export":
                            export_file = 'clean_' + text_file 
                            with open(export_file, 'w') as f:
                                f.write(clean)
                            break
                        else :
                            print("Input not recognized, try again")
                elif self.comm.lower() == "load":
                    #Load cleaned text
                    corp_file = input("Filename: ")
                    with open(corp_file, encoding='utf8', errors='replace') as f:
                        self.text_list.append((corp_file, f.read()))   
                elif self.comm.lower() == "lemmatize":
                    #Lemmatize cleaned text
                    corp_file = input("Filename: ")
                    print("Lemmatizing...")
                    with open(corp_file, encoding='utf8', errors='replace') as f:
                        text = f.read()
                        newtext = lemmatize_corpus(text)
                    new_corp_file = 'lemma_' + corp_file 
                    with open(new_corp_file, mode='w', encoding='utf8', errors='replace') as f:
                        f.write(newtext)
                    print("Lemmatized version written to " + new_corp_file + "!")
                elif (self.comm not in self.QUIT):
                    raise ValueError("Error: Invalid input")
                else :
                    #Break if input is exit command
                    break
                print("Number of texts loaded:", len(self.text_list))
            except Exception as e:
                print(e)
            #Check if finished
            self.comm = input("Load texts as corpora? Y/N: ")
            try:
                if self.comm.lower() == "y":
                    if self.text_list != []:
                        print("Loading corpora...")
                        for txt in self.text_list:
                            self.corpus_list.append((txt[0], (Corpus(porter, txt[1]))))
                            print(txt[0], "loaded!")
                        print("Number of corpora loaded:", len(self.corpus_list))
                    else :
                        self.comm="exit"
            except Exception as e:
                print(e)
    

    def io_loop(self):
        """Main I/O loop"""
        if (self.comm not in self.QUIT):
            #Default to last loaded corpus
            corp_ind = len(self.corpus_list)-1
            self.corpus = self.corpus_list[corp_ind][1]
            print("Corpus Selected:", self.corpus_list[corp_ind][0], "| Tokens in corpus:", len(self.corpus._text))
            #Actual loop
            while (self.comm not in self.QUIT):
                self.comm = input("->")
                parsed = self.comm.split(' ')
                #Check number of commands
                if "conc" in parsed[0]:
                    self.conc_comm(parsed)
                elif "coll" in parsed[0]:
                    self.coll_comm(parsed)
                elif "parse" in parsed[0]:
                    self.parse_agency_comm(parsed)
                elif "list" in parsed[0]:
                    self.list_corpora()
                elif "save" in parsed[0]:
                    self.save_output()
                elif parsed[0].lower() == "settings" : 
                    self.settings()
                elif parsed[0].lower() == "help" : 
                    print(self.help_text)
                elif parsed[0].lower() == "switch" :
                    if corp_ind < len(self.corpus_list)-1:
                        corp_ind +=1
                    else :
                        corp_ind = 0
                    self.corpus = self.corpus_list[corp_ind][1]
                    print("Corpus Selected:", self.corpus_list[corp_ind][0], "| Tokens in corpus:", len(self.corpus._text))


    def list_corpora(self):
        for c in self.corpus_list:
            print(c[0], "| Tokens:", len(c[1]._text))


    def coll_comm(self, inpt):
        """Method for calling and processing collocation commands from parsed input"""
        key = None
        win = self.coll_win
        minfreq = self.coll_min_freq
        minscore = self.coll_min_score
        #Parse command
        try:
            if len(inpt) >=2:
                key = inpt[1]
            else: 
                print("[coll] command requires at least a key")
                return None
            if len(inpt) >= 3 and inpt[2].isalpha:
                key += ' ' + inpt[2]
                inpt.pop(2)
            if len(inpt) >= 3:
                if inpt[2].isalpha():
                    raise ValueError('Collocation takes at most two words, more than two words were given')
                win = int(inpt[2])
            if len(inpt) >= 4:
                minfreq = int(inpt[3])
            if len(inpt) == 5:
                minscore = int(inpt[4])
            elif len(inpt) > 5 : 
                print("Collocation attempted, but too many arguments were given")
            print('Finding collocates of', key + '... ')
            self.last_out = self.corpus.alt_format_collocates(self.corpus.alt_find_collocates(key, win, minfreq, minscore))
            print(self.coll_colorize(self.last_out, key))
        except Exception as e:
            print(e)

    def coll_colorize(self, text, key):
        """Method for colorizing collocate output"""
        text = self.conc_colorize(text, key)
        lines = text.split('\n')
        color1 = Style.BRIGHT + Fore.BLACK
        color2 = Fore.WHITE
        color = color1
        for x in range(len(lines)-1):
            lines[x+1] = color + lines[x+1][:60] + color + lines[x+1][60:]
            if color == color1:
                color = color2
            else :
                color = color1
        output = '\n'.join(lines)
        return output
            
    def conc_comm(self, inpt):
        """Method for calling and processing concordance commands from parsed input"""
        key = None
        width = self.conc_width
        try:
            if len(inpt) >= 2:
                key = inpt[1]
                #Index concordance search
                if inpt[1].isdigit():    
                    key = int(inpt[1])
                    if len(inpt) == 3:
                        width = int(inpt[2])
                    elif len(inpt) > 3:
                        raise ValueError("Index concordance attempted, but too many arguments were given")
                    self.last_out = self.corpus.conc_format_line(key, width)
                    print(self.last_out)
                #Regular concordance search
                else : 
                    #Add additional keys to key string and remove them from inpt
                    while len(inpt) >= 3 and not inpt[2].isdigit():
                        key += ' ' + inpt[2]
                        inpt.pop(2)
                    #Allow for user control of width from inpt
                    if len(inpt) == 3:
                        if inpt[2].isdigit():
                            width = int(inpt[2])
                    elif len(inpt) > 3:
                        raise ValueError('Concordance attempted, but too many arguments were given')
                    self.last_out = self.corpus.conc_mult(key, width)
                    print(self.conc_colorize(self.last_out, key))
        except Exception as e:
            print(e)

    def conc_colorize(self, text, key):
        """Method for colorizing a given string of keys within a text (modeled specifically for concordances)"""
        keys = key.split(' ')
        tokens = text.split(' ')
        uncolor = '\033[0m'
        colors_available = 5
        #Iterate through tokenized text
        for x in range(len(tokens)):
            #Reserve red and consistently color first key in key string with it
            if (' ' + tokens[x] + ' ') in (' ' + keys[0] + ' '):
                tokens[x] = Fore.RED + tokens[x] + uncolor
            #Otherwise, assuming their are more keys, cycle through colors
            elif len(keys) > 1: 
                for y in range(len(keys)-1):
                    if (' ' + keys[y+1] + ' ') in (' ' + tokens[x] + ' '):
                        tokens[x] = '\033[' + str(32+(y % colors_available)) + 'm' + tokens[x] + uncolor
        text = ' '.join(tokens)
        return text

    def old_parse_comm(self, inpt):
        """LEGACY Method for calling and processing dependency parsing commands from parsed input"""
        try:
            if len(inpt) >= 2:
                key1 = inpt[1]
                if len(inpt) > 2:
                    key2 = inpt[2]
                    self.last_out = self.corpus.sentence_parse(key1, key2)
                    print(self.last_out)
                else :
                    print("Finding and printing all sentences including key")
                    self.last_out = self.corpus.sentence_parse(key1)
                    print(self.last_out)
        except Exception as e:
            print(e)
    
    def parse_agency_comm(self, inpt):
        """Method for calling and processing dependency parsing commands from parsed input"""
        try:
            if len(inpt) > 1:
                if len(inpt) >=2:
                    key = inpt[1]
                else: 
                    print("[parse] command requires at least a key")
                    return None
                while len(inpt) >= 3:
                    key += ' ' + str(inpt[2])
                    inpt.pop(2)
                sents = self.corpus.sentence_search(key)
                agency_list = agency_parse(sents)
                print(analyze_agency(agency_list, key))
            else :
                raise ValueError("The parse agency command requires keys to be input")
        except Exception as e:
            print(e)

    def settings(self):
        """Method for displaying settings and getting changes"""
        comm = ''
        while comm.lower() != 'back':
            print("—Concordance Settings—\n[span]:", self.conc_width)
            print("—Collocation Settings—\n[win]dow:", self.coll_win, "| minimum [freq]uency:", 
                self.coll_min_freq, "| minimum [score]:", self.coll_min_score)
            comm = input('\\_>')
            parsed = comm.split(' ')
            try:
                if (len(parsed) == 2) and parsed[1].isdigit():
                    if 'span' in parsed[0]:
                        self.conc_width = int(parsed[1])
                    if 'win' in parsed[0]:
                        self.coll_win = int(parsed[1])
                    if 'freq' in parsed[0]:
                        self.coll_min_freq = int(parsed[1])
                    if 'score' in parsed[0]:
                        self.coll_min_score = int(parsed[1])
                    print()
                elif comm.lower() != 'back':
                    print('Please enter a setting and a new integer value, or go [back]')
                else :
                    print()
            except Exception as e:
                print(e)

    def save_output(self):
        """Method for saving output to an external file"""
        filename = input("Saved output filename: ")
        try:
            with open(filename, 'w') as f:
                f.write(self.last_out)
            print()
        except Exception as e:
            print(e)
                
    def preload(self, text_file):
        """Method which loads corpus directly from a program specific filename"""
        print("Loading", text_file)
        with open(text_file, encoding='utf8', errors='replace') as f:
                text = f.read()
        self.corpus_list.append((text_file, Corpus(porter, text)))
        print(text_file, "loaded!")
    
    def preimport(self, text_file):
        """Method which imports, cleans, and loads corpus from a specific filename """
        print("Loading", text_file)
        with open(text_file, encoding='utf8', errors='replace') as f:
                unclean = f.read()
                text = clean_corpus(unclean)
        self.corpus_list.append((text_file, Corpus(porter, text)))
        print(text_file, "loaded!")


if __name__ == "__main__":

    App = corpus_loop()

