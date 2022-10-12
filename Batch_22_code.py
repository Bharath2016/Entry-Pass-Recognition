from flask import *
import os
import cv2
import imutils
import numpy as np
import pytesseract
from flask_uploads import UploadSet, configure_uploads, IMAGES
try:
    from PIL import Image
except:
    import Image


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

peoject_dir = os.path.dirname(os.path.abspath(__file__))



app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

photos = UploadSet('photos', IMAGES)

app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = 'images'

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return 'There is no photo in form'
        name = request.form['img-name'] + '.jpg'
        print(name)
        photo = request.files['photo']
        print(photo)
        path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        photo.save(path)

        img = cv2.imread('images/'+name,cv2.IMREAD_COLOR)
        img = cv2.resize(img, (600,400) )

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 13, 15, 15)

        edged = cv2.Canny(gray, 30, 200)
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
        screenCnt = None

        for c in contours:

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)

            if len(approx) == 4:
                screenCnt = approx
                break

        if screenCnt is None:
            detected = 0
            print ("No contour detected")
        else:
            detected = 1

        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

            mask = np.zeros(gray.shape,np.uint8)
            new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
            new_image = cv2.bitwise_and(img,img,mask=mask)

            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx:bottomx+1, topy:bottomy+1]

            text = pytesseract.image_to_string(Cropped, config='--psm 11')
            print("Detected license plate Number is:",text)
            img = cv2.resize(img,(500,300))
            Cropped = cv2.resize(Cropped,(400,200))
        else:
            text = pytesseract.image_to_string(Image.open('images/' + name))
        
        att={"EDM18B017":'Nikhil',"EDM18B023":'Karthik',"ESD181009":'Bharath'}
        new=text[0:len(text)-2]
        if  new in att:
            text="Allow "+att[new]
        else:
            text="Dont allow"
        print(len(text))
        if len(text) <= 1:

            text = 'Image not clear. Please try with clearimage'

        return render_template('result.html', text = text)


    return render_template('index.html')

if __name__ == '__main__':
    app.run()
