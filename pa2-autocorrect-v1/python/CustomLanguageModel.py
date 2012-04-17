import math, collections

class CustomLanguageModel:

    def __init__(self, corpus):
      self.unigramCounts = collections.defaultdict(lambda: 0)
      self.bigramCounts = collections.defaultdict(lambda: 0)
      self.bigramStartingWithCount = collections.defaultdict(lambda: 0)
      self.bigramEndingWithCount = collections.defaultdict(lambda: 0)
      self.total = 0
      self.train(corpus)
      self.delta = self.findDelta()
      
    def findDelta(self):
        n1 = 0
        n2 = 0
        for bigram in self.bigramCounts:
              if (self.bigramCounts[bigram] == 1):
                  n1 += 1
              elif (self.bigramCounts[bigram] == 2):
                  n2 += 1
        return float(n1)/(n1 + 2*n2)           

    def train(self, corpus):
      """Takes a HolbrookCorpus corpus, does whatever training is needed."""
      for sentence in corpus.corpus:
        previous_token = ''  
        for datum in sentence.data:  
          token = datum.word
          self.unigramCounts[token] = self.unigramCounts[token] + 1
          self.total += 1
          if (previous_token):
              bigram = previous_token + '|' + token
              if not self.bigramCounts[bigram]:
                  self.bigramStartingWithCount[previous_token] = self.bigramStartingWithCount[previous_token] + 1
                  self.bigramEndingWithCount[token] = self.bigramEndingWithCount[token] + 1
              self.bigramCounts[bigram] = self.bigramCounts[bigram] + 1
              
          previous_token = token
          
    def bigramScore(self, previous_token, token):
        bigram = previous_token + '|' + token
        numerator = max(self.bigramCounts[bigram] - self.delta, 0)
        denominator = self.unigramCounts[previous_token]
        return numerator/float(denominator)
    
    def normalizingConstant(self, previous_token):
        denominator = self.unigramCounts[previous_token]
        return self.delta* self.bigramStartingWithCount[previous_token]  / \
         float(denominator)
        
    def continuationP(self, token):
        return self.bigramEndingWithCount[token]/float(len(self.bigramCounts))           
          
    def kn_score(self, previous_token, token):
        bigram = previous_token + '|' + token
        if self.unigramCounts[previous_token]:
            return self.bigramScore(previous_token, token) + \
                self.normalizingConstant(previous_token)*self.continuationP(token)
        else:
            return self.delta*0.1*self.continuationP(token)
          
    def score(self, sentence):
      """Takes a list of strings, returns a score of that sentence."""
      score = 0.0
      previous_token = '' 
      for token in sentence:
        if (previous_token):
            score += math.log(self.kn_score(previous_token, token)+1.0e-15)
        else:
            pass
        previous_token = token    
      return score
