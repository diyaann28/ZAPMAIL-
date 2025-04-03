from textblob.classifiers import NaiveBayesClassifier
import pandas
def check(res):
 
     var = "static/spamham.csv"
 
     pd = pandas.read_csv(var)
 
     x = pd.values[:1000, :]
 
     train = []
 
     for i in x:
         train.append((i[1], i[0]))
 
     a = NaiveBayesClassifier(train)
 
     s = a.classify(res)
 
     print(s)
     return s
 