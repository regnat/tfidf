#!/ubr/bin/env python

# Simple tf-idf library

import sqlite3
import nltk


class tfIdf:
    """
    The tf-idf class
    """

    def __init__(self, database=None):
        if not database:
            self.database = "tfidf.sql"
        else:
            self.database = database

        self.defaultFreq = 5

        self.init_database()

    def init_database(self):
        """
        Fetches the state from the database, creating it if needed
        """
        db = sqlite3.connect(self.database)
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS state (state_variable char(64),"
                  "state_value int)")
        c.execute("CREATE TABLE IF NOT EXISTS words (word char(50), "
                  "number_occurences int)")
        c.execute("SELECT state_value FROM state WHERE state_variable ="
                  "\"cardCorpus\"")
        qRes = c.fetchone()
        if (qRes):
            self.cardCorpus, = qRes
        else:
            self.cardCorpus = 0
            c.execute("INSERT INTO state (state_variable, state_value)"
                      "values (\"cardCorpus\", 0)")

        db.commit()
        db.close()

    def increase_corpus_cardinal(self):
        """
        Tells that a file has been added to the corpus
        """
        self.cardCorpus += 1
        db = sqlite3.connect(self.database)
        c = db.cursor()
        c.execute("UPDATE state SET state_value = " + str(self.cardCorpus) +
                  " WHERE state_variable = \"cardCorpus\"")
        db.commit()
        db.close()

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
        known_words = {}
        # The words in the document that are part of the dictionnary
        new_words = {}
        # The words in the document that have never been met before
        cardCorpus = int(self.cardCorpus)
        # Number of documents in the corpus
        db = sqlite3.connect(self.database)
        c = db.cursor()
        tfidfs = {}
        tokens = [word.lower() for word in nltk.word_tokenize(line)]
        searchQuery = "SELECT number_occurences FROM words WHERE word =?"

        for token in tokens:
            if token not in known_words and token not in new_words:
                c.execute(searchQuery, (token,))
                fetch = c.fetchone()
                if fetch:
                    nbOcc, = fetch
                    known_words[token] = {'occurencesInText': 1,
                                          'occurencesInCorpus': int(nbOcc)}
                else:
                    new_words[token] = {'occurencesInText': 1,
                                        'occurencesInCorpus': 0}
            elif token in known_words:
                known_words[token]['occurencesInText'] += 1
            else:
                new_words[token]['occurencesInText'] += 1

        cardTxt = len(known_words) + len(new_words)
        for token in known_words:
            tfidfs[token] = ((known_words[token]['occurencesInText']/cardTxt) *
                             (cardCorpus /
                              known_words[token]['occurencesInCorpus']))
        for token in new_words:
            tfidfs[token] = ((new_words[token]['occurencesInText']/cardTxt) *
                             self.defaultFreq)
        db.close()

        for word in sorted(tfidfs, key=tfidfs.get, reverse=False):
            print(word, tfidfs[word])

        self.add_to_db(known_words, new_words)

    def add_to_db(self, known_words, new_words):
        updateQuery = ("UPDATE words SET number_occurences="
                       "number_occurences + 1 WHERE word=:word")
        insertQuery = ("INSERT INTO words (word, number_occurences)"
                       "values (:word, 1)")
        db = sqlite3.connect(self.database)
        c = db.cursor()
        for token, nbOcc in known_words.items():
            c.execute(updateQuery, {"word": token})

        for token, nbOcc in new_words.items():
            c.execute(insertQuery, {"word": token})

        db.commit()
        db.close()
