import math, collections

class StupidBackoffLanguageModel:

    def __init__(self, corpus):
      self.unigramCounts = collections.defaultdict(lambda: 0)
      self.bigramCounts = collections.defaultdict(lambda: 0)
      self.total = 0
      self.train(corpus)

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
              self.bigramCounts[bigram] = self.bigramCounts[bigram] + 1
          previous_token = token

    def score(self, sentence):
      """Takes a list of strings, returns a score of that sentence."""
      score = 0.0
      previous_token = '' 
      for token in sentence:
        if (previous_token):
            bigram = previous_token + '|' + token
            if (self.bigramCounts[bigram]):
                score += math.log(self.bigramCounts[bigram]) - math.log(self.unigramCounts[previous_token])
            else:
                score += math.log(self.unigramCounts[token]+1) + math.log(0.4)
                score -= math.log(self.total+len(self.unigramCounts))
        else:
            pass
        previous_token = token    
      return score
