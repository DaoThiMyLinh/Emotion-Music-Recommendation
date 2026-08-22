from flask import Flask, render_template, Response, jsonify, request
import camera
from camera import VideoCamera

app = Flask(__name__)

headings = ("Name","Album","Artist")
df1 = camera.music_rec()
df1 = df1.head(15)

@app.route('/')
def index():
    return render_template('index.html', headings=headings, data=df1)

def gen(cam):
    while True:
        global df1
        frame, df1 = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/t')
def gen_table():
    genre = request.args.get('genre', 'usuk')
    simulate = request.args.get('simulate', '')
    use_spotify_str = request.args.get('use_spotify', 'false')
    
    camera.current_genre = genre
    camera.use_spotify = True if use_spotify_str == 'true' else False
    
    if simulate and simulate in camera.emotion_dict.values():
        for k, v in camera.emotion_dict.items():
            if v == simulate:
                camera.show_text[0] = k
                break
        curr_emotion = simulate
    else:
        curr_emotion = camera.emotion_dict[camera.show_text[0]]
        
    df = camera.music_rec(genre)
    
    # Đọc và reset cử chỉ nhận được
    gesture = camera.active_gesture
    camera.active_gesture = None
    
    return jsonify({
        "songs": df.to_dict(orient='records'),
        "emotion": curr_emotion,
        "is_group": camera.num_faces_detected > 1,
        "num_faces": camera.num_faces_detected,
        "username": camera.detected_username,
        "gesture": gesture,
        "frozen": camera.frozen
    })

@app.route('/register_face', methods=['POST'])
def register_face():
    name = request.args.get('name', 'User')
    safe_name = "".join([c if c.isalnum() else "_" for c in name])
    camera.register_name = safe_name
    return jsonify({"status": "success", "registering": safe_name})

import os
import cv2
import time
import numpy as np

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    os.makedirs('static/uploads', exist_ok=True)
    filename = 'uploaded_temp.jpg'
    filepath = os.path.join('static/uploads', filename)
    file.save(filepath)
    
    img = cv2.imread(filepath)
    if img is None:
        return jsonify({"error": "Invalid image"}), 400
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Nhập các cấu hình từ camera.py
    from camera import face_cascade, eye_cascade, emotion_model, emotion_dict, music_rec, show_text
    face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    detected_emotions = []
    detected_name = ""
    
    for (x, y, w, h) in face_rects:
        roi_gray_frame = gray[y:y + h, x:x + w]
        shave_y = int(h * 0.1)
        shave_x = int(w * 0.1)
        roi_gray_frame_tight = gray[y + shave_y : y + h - shave_y, x + shave_x : x + w - shave_x]
        
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame_tight, (48, 48)), -1), 0) / 255.0
        prediction = emotion_model.predict(cropped_img)
        # Cân bằng độ nhạy bén giữa các cảm xúc (Tăng mạnh Sad lên 1.9 và giảm Neutral xuống 0.65 để dễ nhận Sad nhất)
        multipliers = [1.1, 1.0, 1.0, 1.2, 0.65, 1.9, 0.7]
        for idx in range(7):
            prediction[0][idx] *= multipliers[idx]

        raw_max = int(np.argmax(prediction))
        if raw_max == 1:
            maxindex = 0
        else:
            maxindex = raw_max

        # Giải quyết sự chồng lấn giữa Sad và Neutral (Mặt buồn thường bị nhận thành Neutral nhưng có điểm Sad tăng nhẹ)
        if maxindex == 4 and prediction[0][5] > 0.14:
            maxindex = 5
            
        # Nhận dạng nhắm mắt để phân biệt: Nếu nhắm mắt thì biến Angry (0) và Neutral (4) thành Sad (5)
        roi_eye_gray = roi_gray_frame[int(h*0.15) : int(h*0.55), int(w*0.15) : int(w*0.85)]
        eyes = eye_cascade.detectMultiScale(roi_eye_gray, 1.15, 3)
        if len(eyes) == 0:
            if maxindex in [0, 4]:
                maxindex = 5
                
        detected_emotions.append(maxindex)
        
        # Nhận diện khuôn mặt đã đăng ký
        matched_name = ""
        best_score = 0
        if os.path.exists("data/registered_faces"):
            face_crop_gray = cv2.resize(roi_gray_frame, (100, 100))
            for reg_file in os.listdir("data/registered_faces"):
                if reg_file.endswith(".png"):
                    template_path = os.path.join("data/registered_faces", reg_file)
                    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                    if template is not None:
                        res = cv2.matchTemplate(face_crop_gray, template, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(res)
                        if max_val > best_score:
                            best_score = max_val
                            if max_val > 0.72:
                                matched_name = reg_file.replace(".png", "").replace("_", " ")
        
        label = emotion_dict[maxindex]
        if matched_name:
            detected_name = matched_name
            label = f"{matched_name} - {label}"
            
        cv2.rectangle(img, (x, y - 50), (x + w, y + h + 10), (0, 255, 0), 2)
        cv2.putText(img, label, (x + 20, y - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
    processed_filename = 'processed_temp.jpg'
    processed_filepath = os.path.join('static/uploads', processed_filename)
    cv2.imwrite(processed_filepath, img)
    
    active_emotion = "Neutral"
    if len(detected_emotions) > 0:
        from collections import Counter
        most_common = Counter(detected_emotions).most_common(1)[0][0]
        show_text[0] = most_common
        active_emotion = emotion_dict[most_common]
        
    genre = request.args.get('genre', 'usuk')
    df = music_rec(genre)
    
    return jsonify({
        "processed_url": f"/static/uploads/{processed_filename}?t={time.time()}",
        "emotion": active_emotion,
        "is_group": len(face_rects) > 1,
        "num_faces": len(face_rects),
        "username": detected_name,
        "songs": df.to_dict(orient='records')
    })

@app.route('/toggle_freeze', methods=['POST'])
def toggle_freeze():
    camera.frozen = not camera.frozen
    return jsonify({"frozen": camera.frozen})

import urllib.request
import urllib.parse
import re

@app.route('/youtube_id')
def get_youtube_id():
    query = request.args.get('query', '')
    try:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode()
        # Fallback to search
        match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if match:
            return jsonify({"video_id": match.group(1)})
        else:
            match_fallback = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
            if match_fallback:
                return jsonify({"video_id": match_fallback[0]})
    except Exception as e:
        pass
    return jsonify({"video_id": None})

if __name__ == '__main__':
    app.debug = True
    app.run(port=5001)
    

