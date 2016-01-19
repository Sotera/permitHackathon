#Random forest model developed to predict tags based on the free text of building permit data.
import json
import cPickle as pickle
import tables
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier


def mlTrainModel(X,y):

    #remove nulls
    X = [element if element is not None else ' ' for element in X] #put spaces for nulls
    y = [element if element is not None else ' ' for element in y] #put spaces for nulls

    #set up a count vectorizer
    cv = CountVectorizer(min_df=0, max_features=500)
    ct = cv.fit(X)
    cTrain = cv.transform(X)  #transform the text into a one hot matrix

    #create a random forest classifier
    randomForest = RandomForestClassifier(random_state=123,n_estimators=10)
    rfc = randomForest.fit(cTrain,y)
    return cv, rfc

def mlPredict(cTrain, rfc, inputList):
    cPredict = cTrain.transform(inputList)  #run inputList through the count vectorizer
    clf_probs = rfc.predict_proba(cPredict)   #predict

    predictionLabels = rfc.classes_        #extract prediction labels from classifier
    indices = np.argmax(clf_probs,axis=1)   #get indices of max probabilities

    predictions = predictionLabels[indices] #map indices back to terms
    return predictions  


def main():
    #procedures specific to our particular data set
    #import sys
    #sys.path.append('../mlPredictionWorkType/')

    #import data
    JSONFile = '../data/seattle.json'

    with open(JSONFile,'r') as fp:
        data = json.load(fp)

    #put the data into a dataframe
    df = pd.DataFrame(data['data'])


    text = df[11]  #choose the column which contains the freeText
    tag = df[13]   #choose the column which contains the tag
    print len(tag)
    text = [element if element is not None else ' ' for element in text] #put spaces for nulls


    #define the training data and the testing data
    #this is free text which has labels
    textTrain = []
    tagTrain  = []
    textTest  = []
    tagTest   = []
    recordIndex = []
    for kk,element in enumerate(tag):
        if element is not None:
            textTrain.append(text[kk])
            tagTrain.append(tag[kk])
        else:
            textTest.append(text[kk])
            tagTest.append(tag[kk])
            recordIndex.append(kk)

    # place ' ' in the absence of elements
    textTrain = [element if element is not None else ' ' for element in textTrain]
    tagTrain = [element if element is not None else ' ' for element in tagTrain]
    textTest = [element if element is not None else ' ' for element in textTest]
    tagTest =  [element if element is not None else ' ' for element in tagTest]

    #verify the training data
    print textTrain[0]
    print tagTrain[0]

    #train the model
    cv, rfc = mlTrainModel(textTrain,tagTrain)

    #make perdictions
    tagTest = mlPredict(cv,rfc,textTest)

    #verify the length of the predictions
    print len(tagTest)
    print tagTest[0]

    #check the first several predictions
    print '--Predictions for previously empty tags--'
    for i in range(5):
        print tagTest[i] + '-' +textTest[i]
        print

if __name__ == "__main__":
    main()