#!/ubr/bin/env python

# Simple tf-idf library

import sqlite3
import collections


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

        self.initDatabase()

    def initDatabase(self):
        """
        Fetches the state from the database, creating it if needed
        """
        db = sqlite3.connect(self.database)
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS state ("
                  "id INTEGER PRIMARY KEY,"
                  "stateVariable char(64) UNIQUE,"
                  "stateValue int)"
                  )
        c.execute("CREATE TABLE IF NOT EXISTS words ("
                  "id INTEGER PRIMARY KEY,"
                  "word char(50) UNIQUE,"
                  "numberOccurences int)")
        c.execute("SELECT stateValue FROM state WHERE stateVariable ="
                  "\"cardCorpus\"")
        qRes = c.fetchone()
        if (qRes):
            self.cardCorpus, = qRes
        else:
            self.cardCorpus = 0
            c.execute("INSERT INTO state (stateVariable, stateValue)"
                      "values (\"cardCorpus\", 0)")

        db.commit()
        db.close()

    def increaseCorpusCardinal(self):
        """
        Tells that a file has been added to the corpus
        """
        self.cardCorpus += 1
        db = sqlite3.connect(self.database)
        c = db.cursor()
        c.execute("UPDATE state SET stateValue = " + str(self.cardCorpus) +
                  " WHERE stateVariable = \"cardCorpus\"")
        db.commit()
        db.close()

    def addStreamToCorpus(self, stream):
        """
        Adds a file to the corpus
        """
        self.increaseCorpusCardinal()
        tfIdfs = self.parseStream(stream)
        self.addToDb(tfIdfs)

    def addStringToCorpus(self, string):
        """
        Adds a string to the corpus
        """
        self.increaseCorpusCardinal()
        tfIdfs = self.parseString(string)
        self.addToDb(tfIdfs)

    def parseStream(self, stream):
        """
        Parse a stream and returns the tfidfs of the words in it
        """
        words = self.countWordsInStream(stream)
        return self.calculateTfIdf(words)

    def parseString(self, string):
        """
        Parse a string and returns the tfidfs of the words in it
        """
        words = self.countWordsInString(string)
        return self.calculateTfIdf(words)

    def countWordsInStream(self, stream):
        self.increaseCorpusCardinal()
        wordCounts = collections.Counter()
        for line in stream:
            wordCounts += self.countWordsInString(line)
        return wordCounts

    def countWordsInString(self, line):
        tokens = [word.lower() for word in line.split()]
        wordCounts = collections.Counter()
        for token in tokens:
            if token in wordCounts:
                wordCounts[token] += 1
            else:
                wordCounts[token] = 1
        return wordCounts

    def calculateIdf(self, cursor, word, defaultIdf=1.5):
        searchQuery = "SELECT numberOccurences FROM words WHERE word =?"
        cursor.execute(searchQuery, (word,))
        fetch = cursor.fetchone()
        if fetch:
            nbOcc, = fetch
            idf = self.cardCorpus / nbOcc
        else:
            idf = defaultIdf
        return idf

    def calculateTf(self, count, cardTxt):
        return count/cardTxt

    def calculateTfIdf(self, wordCounts, defaultIdf=1.5):
        frequencies = {}
        db = sqlite3.connect(self.database)
        c = db.cursor()
        cardTxt = len(wordCounts)
        for word, count in wordCounts.items():
            frequencies[word] = (self.calculateTf(count, cardTxt) /
                                 self.calculateIdf(c, word, defaultIdf))

        return frequencies

    def addToDb(self, words):
        query = ("INSERT OR REPLACE INTO words (word, numberOccurences) "
                 "VALUES (:word, "
                 "coalesce((select numberOccurences + 1 from words "
                 "WHERE word =:word), 1))")
        db = sqlite3.connect(self.database)
        c = db.cursor()
        for token, occurences in words.items():
            c.execute(query, {'word': token})

        db.commit()
        db.close()
