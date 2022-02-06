
from cv2 import _OutputArray_DEPTH_MASK_16F
import face_recognition
import pickle
import cv2


def detectFace(img_name):
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    img = cv2.imread(img_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #detect the face
    res = cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    if(len(res) == 1):
        return True
    
    return False

def copy_array(array, array2):
    for obj in array:
        array2.append(obj)

    return array2


#aopening the data.pkl file and saving the data over there

def check_and_add(namee, img_loc):
    img = cv2.imread(img_loc)
    enc = face_recognition.face_encodings(img)[0]

    dati = open("data.pkl", "rb")
    out = pickle.load(dati)

    #check in the out list if the encogind exits
    c=0
    print(len(out))
    for obj in out:
        print(obj['name'])
        x = obj['encoding']
        if(c==0):
            x = obj['encoding'][0]

        res = face_recognition.compare_faces([x], enc)
        print(res)
        if(res[0] == True):
            return True
        c+=1

    dic = {
        "name": namee,
        "encoding":enc
    }

    
    lista = []
    lista = copy_array(out, lista)
    lista.append(dic)

    dati = open("data.pkl", "wb")
    pickle.dump(lista, dati)
    dati.close()

    return False

#checking if the data exists in the data.pkl file

def check_and_pass(name, img_loc):
    img = cv2.imread(img_loc)
    enc = face_recognition.face_encodings(img)[0]

    file = open("data.pkl","rb")
    out = pickle.load(file)
    
    c=0
    print(len(out))
    for obj in out:
        x = obj['encoding']
        if(c==0):
            x = obj['encoding'][0]
        res = face_recognition.compare_faces([x] ,enc)
        print(res)
        print('--------------')
        if(res[0] == True and obj['name'] == name):
            return True
        c+=1
        
    return False


print(check_and_add("Hj", "static/unknown/aaf.jpeg"))