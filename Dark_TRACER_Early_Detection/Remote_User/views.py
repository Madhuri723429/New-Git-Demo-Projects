from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import VotingClassifier

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score



# Create your views here.
from Remote_User.models import ClientRegister_Model,detection_type,detection_ratio,detection_accuracy

def login(request):


    if request.method == "POST" and 'submit1' in request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            enter = ClientRegister_Model.objects.get(username=username,password=password)
            request.session["userid"] = enter.id

            return redirect('ViewYourProfile')
        except:
            pass

    return render(request,'RUser/login.html')



def Register1(request):

    if request.method == "POST":
        if request.method == "POST":
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phoneno = request.POST.get('phoneno')
            country = request.POST.get('country')
            state = request.POST.get('state')
            city = request.POST.get('city')
            address = request.POST.get('address')
            gender = request.POST.get('gender')
            ClientRegister_Model.objects.create(username=username, email=email, password=password, phoneno=phoneno,
                                                country=country, state=state, city=city, address=address, gender=gender)
            obj = "Registered Successfully"
            return render(request, 'RUser/Register1.html', {'object': obj})
    else:
        return render(request,'RUser/Register1.html')

def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id= userid)
    return render(request,'RUser/ViewYourProfile.html',{'object':obj})


def Predict_Detection_Type(request):
    if request.method == "POST":

        if request.method == "POST":

            url= request.POST.get('url')
            length_url= request.POST.get('length_url')
            length_hostname= request.POST.get('length_hostname')
            https_token= request.POST.get('https_token')
            page_rank= request.POST.get('page_rank')

            df = pd.read_csv('Malware_Datasets.csv', encoding='latin-1')

            def apply_results(status):
                if (status == "legitimate"):
                    return 0  # legitimate
                elif (status=="malware"):
                    return 1  # malware

            df['Results'] = df['status'].apply(apply_results)

            # cv = CountVectorizer()
            X = df['url']
            y = df['Results']

            cv = CountVectorizer(lowercase=False, strip_accents='unicode', ngram_range=(1, 1))

            X = cv.fit_transform(X)

            models = []
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
            X_train.shape, X_test.shape, y_train.shape

            print("Naive Bayes")
            from sklearn.naive_bayes import MultinomialNB
            NB = MultinomialNB()
            NB.fit(X_train, y_train)
            predict_nb = NB.predict(X_test)
            naivebayes = accuracy_score(y_test, predict_nb) * 100
            print(naivebayes)
            print(confusion_matrix(y_test, predict_nb))
            print(classification_report(y_test, predict_nb))
            models.append(('naive_bayes', NB))
            detection_accuracy.objects.create(names="Naive Bayes", ratio=naivebayes)

            # SVM Model
            print("SVM")
            from sklearn import svm
            lin_clf = svm.LinearSVC()
            lin_clf.fit(X_train, y_train)
            predict_svm = lin_clf.predict(X_test)
            svm_acc = accuracy_score(y_test, predict_svm) * 100
            print(svm_acc)
            print("CLASSIFICATION REPORT")
            print(classification_report(y_test, predict_svm))
            print("CONFUSION MATRIX")
            print(confusion_matrix(y_test, predict_svm))
            models.append(('svm', lin_clf))
            detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

            print("Logistic Regression")
            from sklearn.linear_model import LogisticRegression
            reg = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
            y_pred = reg.predict(X_test)
            print("ACCURACY")
            print(accuracy_score(y_test, y_pred) * 100)
            print("CLASSIFICATION REPORT")
            print(classification_report(y_test, y_pred))
            print("CONFUSION MATRIX")
            print(confusion_matrix(y_test, y_pred))
            models.append(('logistic', reg))

            from sklearn.tree import DecisionTreeClassifier
            print("Decision Tree Classifier")
            dtc = DecisionTreeClassifier()
            dtc.fit(X_train, y_train)
            dtcpredict = dtc.predict(X_test)
            print("ACCURACY")
            print(accuracy_score(y_test, dtcpredict) * 100)
            print("CLASSIFICATION REPORT")
            print(classification_report(y_test, dtcpredict))
            print("CONFUSION MATRIX")
            print(confusion_matrix(y_test, dtcpredict))
            models.append(('DecisionTreeClassifier', dtc))

            print("KNeighborsClassifier")
            from sklearn.neighbors import KNeighborsClassifier
            kn = KNeighborsClassifier()
            kn.fit(X_train, y_train)
            knpredict = kn.predict(X_test)
            print("ACCURACY")
            print(accuracy_score(y_test, knpredict) * 100)
            print("CLASSIFICATION REPORT")
            print(classification_report(y_test, knpredict))
            print("CONFUSION MATRIX")
            print(confusion_matrix(y_test, knpredict))
            models.append(('KNeighborsClassifier', kn))

            classifier = VotingClassifier(models)
            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)

            url1 = [url]
            vector1 = cv.transform(url1).toarray()
            predict_text = classifier.predict(vector1)

            pred = str(predict_text).replace("[", "")
            pred1 = pred.replace("]", "")

            prediction = int(pred1)

            if (prediction== 0):
                val='legitimate'
            elif (prediction== 1):
                val='malware'

            print(val)
            print(prediction)

            detection_type.objects.create(
            url=url,
            length_url=length_url,
            length_hostname=length_hostname,
            https_token=https_token,
            page_rank=page_rank,
            Prediction=val
            )


        return render(request, 'RUser/Predict_Detection_Type.html',{'objs': val})
    return render(request, 'RUser/Predict_Detection_Type.html')



