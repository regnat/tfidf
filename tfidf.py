#!/ubr/bin/env python

# Simple tf-idf library

import sys
import os.path
import sqlite3
import configparser
import nltk

class tfIdf:
    """
    The tf-idf class
    """

    def __init__(self, database = None, configFile = None):
        if not database:
            self.database = "tfidf.sql"
        else:
            self.database = database

        if not configFile:
            self.configFile = "tfidf.cfg"
        else:
            self.configFile = configFile

        self.db = sqlite3.connect(self.database)
        self.config = configparser.ConfigParser()
        self.defaultFreq = 5

        self.read_config()

    def read_config(self):
        """
        Reads the config file
        """
        if os.path.isfile(self.configFile):
            self.config.read(self.configFile)
        else:
            print("Config file does not exists, creating it", file=sys.stderr)
            self.__create_config()

    def __create_config(self):
        self.config['STATE'] = {'cardCorpus' : 0}

        with open(self.configFile, 'w') as configStream:
            self.config.write(configStream)

    def increase_corpus_cardinal(self):
        """
        Tells that a file has been added to the corpus
        """
        self.config['STATE']['cardCorpus'] = str(int(self.config['STATE']['cardCorpus']) + 1)
        with open(self.configFile, 'w') as configStream:
            self.config.write(configStream)

    def add_to_corpus(self, stream):
        """
        Adds a file to the corpus
        """
        self.increase_corpus_cardinal()
        for line in stream:
            self.parse_line(line)

    def add_string_to_corpus(self, string):
        """
        Adds a string to the corpus
        """
        self.increase_corpus_cardinal()
        self.parse_line(string)

    def parse_line(self, line):
        known_words = {} # The words in the document that are part of the dictionnary
        new_words = {} # The words in the document that have never been met before
        c = self.db.cursor()
        cardCorpus = int(self.config['STATE']['cardCorpus']) 
        tfidfs = {}
        tokens = [word.lower() for word in nltk.word_tokenize(line)]
        searchQuery = "SELECT number_occurences FROM words WHERE word =?"
        for token in tokens:
            if token not in known_words and token not in new_words:
                c.execute(searchQuery, (token,))
                fetch = c.fetchone()
                if fetch:
                    nbOcc, = fetch
                    known_words[token] = {'occurencesInText': 1, 'occurencesInCorpus': int(nbOcc)}
                else:
                    new_words[token] = {'occurencesInText': 1, 'occurencesInCorpus': 0}
            elif token in known_words:
                known_words[token]['occurencesInText'] += 1
            else:
                new_words[token]['occurencesInText'] += 1

        cardTxt = len(known_words) + len(new_words)
        
        for token in known_words:
            tfidfs[token] = (known_words[token]['occurencesInText']/cardTxt) * (cardCorpus/ known_words[token]['occurencesInCorpus'])
        for token in new_words:
            tfidfs[token] = (new_words[token]['occurencesInText']/cardTxt) * self.defaultFreq

        for word in sorted(tfidfs, key =tfidfs.get, reverse=False):
            print(word, tfidfs[word])
        self.add_to_db(c, known_words, new_words)

    def add_to_db(self, c, known_words, new_words):
        updateQuery = "UPDATE words SET number_occurences= number_occurences + 1 WHERE word=:word"
        insertQuery = "INSERT INTO words (word, number_occurences) values (:word, 1)"
        for token, nbOcc in known_words.items():
            c.execute(updateQuery, {"word": token})

        for token, nbOcc in new_words.items():
            c.execute(insertQuery, {"word": token})

        self.db.commit()
