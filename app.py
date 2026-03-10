import os
import cv2
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

def compare_faces(img1_path, img2_path):
    # फोटो लोड करणे
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    # फोटोंचा आकार समान करणे
    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))
    
    # Gray scale मध्ये रूपांतर
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Similarity स्कोअर काढणे (Template matching/Histogram)
    res = cv2.absdiff(gray1, gray2)
    percentage = 100 - (np.mean(res) / 255 * 100)
    
    return round(percentage, 2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    try:
        id_file = request.files["id_image"]
        selfie_file = request.files["selfie_image"]
        
        id_path = os.path.join(app.config['UPLOAD_FOLDER'], id_file.filename)
        selfie_path = os.path.join(app.config['UPLOAD_FOLDER'], selfie_file.filename)
        
        id_file.save(id_path)
        selfie_file.save(selfie_path)

        # फेस कंपॅरिझन लॉजिक
        score = compare_faces(id_path, selfie_path)
        
        result = "VERIFIED" if score > 70 else "FAILED"
        color = "green" if result == "VERIFIED" else "red"

        return f"""
        <div style="font-family:sans-serif; text-align:center; padding:50px;">
            <h1 style="color:{color};">{result}</h1>
            <p>Match Score: {score}%</p>
            <p>Offline Verification Completed Successfully ✅</p>
            <a href="/">Back</a>
        </div>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)