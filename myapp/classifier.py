from textblob.classifiers import NaiveBayesClassifier
import pandas
def check(res):

    var = "static\spamham.csv"

    pd = pandas.read_csv(var)

    x = pd.values[:1000, :]

    train = []

    for i in x:
        train.append((i[1], i[0]))

    a = NaiveBayesClassifier(train)

    s = a.classify(res)

    print(s)
    return s
# check("call 09061209465 now! C Suprman V, Matrix3, StarWars3, etc all 4 FREE! bx420-ip4-5we. 150pm. Dont miss out!")