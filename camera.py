import numpy as np
import cv2
import os
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image
import datetime
from threading import Thread
# from Spotipy import *  
import time
import pandas as pd
face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
ds_factor=0.6

import tensorflow as tf
emotion_model = tf.keras.models.load_model('model.keras')


cv2.ocl.setUseOpenCL(False)

emotion_dict = {0:"Angry",1:"Disgusted",2:"Fearful",3:"Happy",4:"Neutral",5:"Sad",6:"Surprised"}
music_dist={0:"songs/angry.csv",1:"songs/disgusted.csv",2:"songs/fearful.csv",3:"songs/happy.csv",4:"songs/neutral.csv",5:"songs/sad.csv",6:"songs/surprised.csv"}
global last_frame1                                    
last_frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
global cap1 
cap1 = None
global frozen
frozen = False
global current_genre
current_genre = 'usuk'
show_text=[0]
global num_faces_detected
num_faces_detected = 0
global register_name
register_name = None
global detected_username
detected_username = ""
global motion_history_x
motion_history_x = []
global active_gesture
active_gesture = None
global emotion_history_queue
emotion_history_queue = []

vpop_music = {
    0: [
        {"Name": "Thật Bất Ngờ", "Album": "Single", "Artist": "Trúc Nhân"},
        {"Name": "Em Không Sai Chúng Ta Sai", "Album": "Single", "Artist": "ERIK"},
        {"Name": "Gạt Đi Nước Mắt", "Album": "Single", "Artist": "Noo Phước Thịnh"},
        {"Name": "Chạm Đáy Nỗi Đau", "Album": "Single", "Artist": "ERIK"},
        {"Name": "Bạc Phận", "Album": "Single", "Artist": "K-ICM x Jack"}
    ],
    1: [
        {"Name": "Bắt Cóc Con Tim", "Album": "Single", "Artist": "Lou Hoàng"},
        {"Name": "Buông Đôi Tay Nhau Ra", "Album": "Single", "Artist": "Sơn Tùng M-TP"},
        {"Name": "Ai Mang Cô Đơn Đi", "Album": "Single", "Artist": "K-ICM x APJ"},
        {"Name": "Nơi Này Có Anh (Remix)", "Album": "Single", "Artist": "Sơn Tùng M-TP"},
        {"Name": "Có Chắc Yêu Là Đây", "Album": "Single", "Artist": "Sơn Tùng M-TP"}
    ],
    2: [
        {"Name": "Chạy Ngay Đi", "Album": "Single", "Artist": "Sơn Tùng M-TP"},
        {"Name": "Cứu Vãn Kịp Không", "Album": "Single", "Artist": "Vương Anh Tú"},
        {"Name": "Bông Hoa Đẹp Nhất", "Album": "Single", "Artist": "Quân A.P"},
        {"Name": "Hết Thương Cạn Nhớ", "Album": "Single", "Artist": "Đức Phúc"},
        {"Name": "Lạc Trôi", "Album": "Single", "Artist": "Sơn Tùng M-TP"}
    ],
    3: [
        {"Name": "Yêu Đời", "Album": "Single", "Artist": "Da LAB"},
        {"Name": "Đi Về Nhà", "Album": "Single", "Artist": "Đen Vâu x JustaTee"},
        {"Name": "Tình Bạn Diệu Kỳ", "Album": "Single", "Artist": "Amee x Ricky Star"},
        {"Name": "Ngày Đầu Tiên", "Album": "Single", "Artist": "Đức Phúc"},
        {"Name": "Yêu Là Cưới", "Album": "Single", "Artist": "Phát Hồ"}
    ],
    4: [
        {"Name": "Lối Nhỏ", "Album": "Single", "Artist": "Đen Vâu"},
        {"Name": "Tháng Tư Là Lời Nói Dối Của Em", "Album": "Single", "Artist": "Hà Anh Tuấn"},
        {"Name": "Mắt Biếc", "Album": "Single", "Artist": "Phan Mạnh Quỳnh"},
        {"Name": "Nước Mắt Em Lau Bằng Tình Yêu Mới", "Album": "Single", "Artist": "Tóc Tiên x Da LAB"},
        {"Name": "Ngày Mai Em Đi", "Album": "Single", "Artist": "Touliver x Lê Hiếu x Soobin"}
    ],
    5: [
        {"Name": "Sau Tất Cả", "Album": "Single", "Artist": "ERIK"},
        {"Name": "Anh Đang Ở Đâu Đấy Anh", "Album": "Single", "Artist": "Hương Giang"},
        {"Name": "Gặp Nhưng Không Ở Lại", "Album": "Single", "Artist": "Hiền Hồ"},
        {"Name": "Thay Tôi Yêu Cô Ấy", "Album": "Single", "Artist": "Thanh Hưng"},
        {"Name": "Phía Sau Một Cô Gái", "Album": "Single", "Artist": "Soobin Hoàng Sơn"}
    ],
    6: [
        {"Name": "Để Mị Nói Cho Mà Nghe", "Album": "Single", "Artist": "Hoàng Thùy Linh"},
        {"Name": "Gieo Quẻ", "Album": "Single", "Artist": "Hoàng Thùy Linh"},
        {"Name": "Kẻ Cắp Gặp Bà Già", "Album": "Single", "Artist": "Hoàng Thùy Linh x Binz"},
        {"Name": "See Tình", "Album": "Single", "Artist": "Hoàng Thùy Linh"},
        {"Name": "Hai Phút Hơn", "Album": "Single", "Artist": "Pháo"}
    ]
}

lofi_music = {
    0: [
        {"Name": "Calm Down Lofi", "Album": "Lofi Chill", "Artist": "Lofi Fruit"},
        {"Name": "Chill Angry Beats", "Album": "Rest", "Artist": "Lofi Sleep"},
        {"Name": "Patience", "Album": "Vibe", "Artist": "Lofi Beats"},
        {"Name": "Deep Breath", "Album": "Relax", "Artist": "Lofi Garden"},
        {"Name": "Soothing Guitar", "Album": "Acoustic", "Artist": "Lofi Boy"}
    ],
    1: [
        {"Name": "Soothe Your Soul", "Album": "Chill Study", "Artist": "Lofi Generator"},
        {"Name": "Clean Slate", "Album": "Fresh", "Artist": "Lofi Boy"},
        {"Name": "Peaceful Mind", "Album": "Calm", "Artist": "Lofi Network"},
        {"Name": "Reset", "Album": "Relax", "Artist": "Lofi Sleep"},
        {"Name": "New Dawn", "Album": "Vibe", "Artist": "Lofi Garden"}
    ],
    2: [
        {"Name": "Safe Space", "Album": "Chill Vibes", "Artist": "Lofi Beats"},
        {"Name": "No Fear", "Album": "Relax", "Artist": "Lofi Land"},
        {"Name": "Comforting Sound", "Album": "Acoustic", "Artist": "Lofi Cafe"},
        {"Name": "Warm Hug", "Album": "Cozy", "Artist": "Lofi Sleep"},
        {"Name": "Under the Stars", "Album": "Night Chill", "Artist": "Lofi Network"}
    ],
    3: [
        {"Name": "Morning Coffee", "Album": "Happy Lofi", "Artist": "Lofi Café"},
        {"Name": "Sunny Day Beats", "Album": "Chill Out", "Artist": "Lofi Garden"},
        {"Name": "Happy Walk", "Album": "Joy", "Artist": "Lofi Beats"},
        {"Name": "Sunday Vibes", "Album": "Relax", "Artist": "Lofi Boy"},
        {"Name": "Smiling Face", "Album": "Happiness", "Artist": "Lofi Network"}
    ],
    4: [
        {"Name": "Rainy Night in Tokyo", "Album": "Chill Beats", "Artist": "Lofi Rain"},
        {"Name": "Study Session", "Album": "Focus Lofi", "Artist": "Lofi Study"},
        {"Name": "Late Night Drive", "Album": "Vibe Beats", "Artist": "Lofi Network"},
        {"Name": "Coffee Shop Ambient", "Album": "Relax", "Artist": "Lofi Cafe"},
        {"Name": "Walking Alone", "Album": "Midnight", "Artist": "Lofi Boy"}
    ],
    5: [
        {"Name": "Lonely Heart", "Album": "Sad Lofi", "Artist": "Lofi Sad"},
        {"Name": "Missing You", "Album": "Tears", "Artist": "Lofi Vibe"},
        {"Name": "Rain on Window", "Album": "Sleep Lofi", "Artist": "Lofi Rain"},
        {"Name": "Sad Autumn", "Album": "Melancholy", "Artist": "Lofi Boy"},
        {"Name": "Lost in Thought", "Album": "Empty Room", "Artist": "Lofi Sleep"}
    ],
    6: [
        {"Name": "Unexpected Journey", "Album": "Surprise Lofi", "Artist": "Lofi Beats"},
        {"Name": "Magic Night", "Album": "Chill", "Artist": "Lofi Land"},
        {"Name": "Wonderland", "Album": "Dreamy", "Artist": "Lofi Boy"},
        {"Name": "Aha Moment", "Album": "Vibe", "Artist": "Lofi Network"},
        {"Name": "Curiosity", "Album": "Focus", "Artist": "Lofi Study"}
    ]
}


''' Class for calculating FPS while streaming. Used this to check performance of using another thread for video streaming '''
class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0
	def start(self):
		# start the timer
		self._start = datetime.datetime.now()
		return self
	def stop(self):
		# stop the timer
		self._end = datetime.datetime.now()
	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1
	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()
	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()


''' Class for using another thread for video streaming to boost performance '''
class WebcamVideoStream:
    	
		def __init__(self, src=0):
			self.stream = cv2.VideoCapture(src)
			(self.grabbed, self.frame) = self.stream.read()
			self.stopped = False

		def start(self):
				# start the thread to read frames from the video stream
			Thread(target=self.update, args=()).start()
			return self
			
		def update(self):
			# keep looping infinitely until the thread is stopped
			while True:
				# if the thread indicator variable is set, stop the thread
				if self.stopped:
					return
				# otherwise, read the next frame from the stream
				(self.grabbed, self.frame) = self.stream.read()

		def read(self):
			# return the frame most recently read
			return self.frame
		def stop(self):
			# indicate that the thread should be stopped
			self.stopped = True

''' Class for reading video stream, generating prediction and recommendations '''
class VideoCamera(object):
	
	def get_frame(self):
		global cap1
		global df1
		global last_frame1
		global frozen
		global current_genre
		global num_faces_detected
		global register_name
		global detected_username
		global motion_history_x
		global active_gesture

		if frozen:
			ret, jpeg = cv2.imencode('.jpg', last_frame1)
			return jpeg.tobytes(), df1

		if cap1 is None:
			cap1 = WebcamVideoStream(src=0).start()
		image = cap1.read()
		if image is not None:
			image = cv2.flip(image, 1)
			h, w = image.shape[:2]
			target_h = 480
			target_w = int(w * (target_h / h))
			image = cv2.resize(image, (target_w, target_h))
		else:
			image = last_frame1
		gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
		face_rects=face_cascade.detectMultiScale(gray,1.3,5)
		
		# Reset name detected in this frame 
		detected_username = ""
		num_faces_detected = len(face_rects)
		detected_emotions = []
		
		df1 = music_rec(current_genre)
		for (x,y,w,h) in face_rects:
			roi_gray_frame = gray[y:y + h, x:x + w]
			
			# Logic Đăng ký khuôn mặt mới
			if register_name is not None:
				os.makedirs("data/registered_faces", exist_ok=True)
				face_crop = cv2.resize(roi_gray_frame, (100, 100))
				cv2.imwrite(f"data/registered_faces/{register_name}.png", face_crop)
				register_name = None  # Reset lại trigger
			# Cắt tỉa bớt 10% viền ngoài của khung khuôn mặt để loại bỏ tóc, tai và nền nhiễu
			shave_y = int(h * 0.1)
			shave_x = int(w * 0.1)
			roi_gray_frame_tight = gray[y + shave_y : y + h - shave_y, x + shave_x : x + w - shave_x]
			
			# Phân tích cảm xúc
			cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame_tight, (48, 48)), -1), 0) / 255.0
			prediction = emotion_model.predict(cropped_img)
			# Cân bằng độ nhạy bén giữa các cảm xúc (Tăng mạnh Sad lên 1.9 và giảm Neutral xuống 0.65 để dễ nhận Sad nhất)
			multipliers = [1.1, 1.0, 1.0, 1.2, 0.65, 1.9, 0.7]
			for idx in range(7):
				prediction[0][idx] *= multipliers[idx]

			# Giải quyết sự chồng lấn giữa Sad và Neutral (Mặt buồn thường bị nhận thành Neutral nhưng có điểm Sad tăng nhẹ)
			# Gộp Chán ghét (Disgusted) vào Tức giận (Angry) làm mặc định ban đầu
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
				
			print(f"DEBUG - Raw Max: {raw_max}, Final Maxindex: {maxindex}, Eyes: {len(eyes)}, Probs: {[round(float(v), 3) for v in prediction[0]]}")
			detected_emotions.append(maxindex)
			
			# Logic Nhận diện danh tính khuôn mặt
			matched_name = ""
			best_score = 0
			if os.path.exists("data/registered_faces"):
				face_crop_gray = cv2.resize(roi_gray_frame, (100, 100))
				for file in os.listdir("data/registered_faces"):
					if file.endswith(".png"):
						template_path = os.path.join("data/registered_faces", file)
						template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
						if template is not None:
							res = cv2.matchTemplate(face_crop_gray, template, cv2.TM_CCOEFF_NORMED)
							_, max_val, _, _ = cv2.minMaxLoc(res)
							if max_val > best_score:
								best_score = max_val
								if max_val > 0.72:  # Ngưỡng khớp khuôn mặt
									matched_name = file.replace(".png", "").replace("_", " ")
			
			if matched_name:
				detected_username = matched_name
				display_label = f"{matched_name} - {emotion_dict[maxindex]}"
			else:
				display_label = emotion_dict[maxindex]

			# Vẽ khung và nhãn tên + cảm xúc lên ảnh
			cv2.rectangle(image,(x,y-50),(x+w,y+h+10),(0,255,0),2)
			cv2.putText(image, display_label, (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
			
			# Theo dõi cử chỉ đầu (tâm X)
			cx = x + w // 2
			motion_history_x.append((time.time(), cx))
			
		# Lọc hàng đợi cử chỉ giữ lại 1.2 giây
		now = time.time()
		motion_history_x = [pos for pos in motion_history_x if now - pos[0] < 1.2]
		
		# Nhận diện cử chỉ lắc đầu trái/phải nhanh
		if len(motion_history_x) >= 6:
			times = [pos[0] for pos in motion_history_x]
			xs = [pos[1] for pos in motion_history_x]
			dx = xs[-1] - xs[0]
			dt = times[-1] - times[0]
			
			if abs(dx) > 100 and dt < 0.8:
				if dx > 0:
					active_gesture = "swipe_right"
				else:
					active_gesture = "swipe_left"
				motion_history_x = []  # Reset
				
		if len(detected_emotions) > 0:
			global emotion_history_queue
			from collections import Counter
			current_dominant = Counter(detected_emotions).most_common(1)[0][0]
			emotion_history_queue.append(current_dominant)
			
			# Giữ lại lịch sử của 7 khung hình gần nhất để làm mịn (tương đương ~0.3-0.5 giây)
			if len(emotion_history_queue) > 7:
				emotion_history_queue.pop(0)
				
			# Chọn cảm xúc xuất hiện nhiều nhất trong hàng đợi làm cảm xúc đại diện chính thức
			smoothed_emotion = Counter(emotion_history_queue).most_common(1)[0][0]
			show_text[0] = smoothed_emotion
			df1 = music_rec(current_genre)
			
		last_frame1 = image.copy()
		pic = cv2.cvtColor(last_frame1, cv2.COLOR_BGR2RGB)     
		img = Image.fromarray(last_frame1)
		img = np.array(img)
		ret, jpeg = cv2.imencode('.jpg', img)
		return jpeg.tobytes(), df1

def music_rec(genre='usuk'):
	emotion_idx = show_text[0]
	if genre == 'vpop':
		return pd.DataFrame(vpop_music.get(emotion_idx, []), columns=['Name', 'Album', 'Artist'])
	elif genre == 'lofi':
		return pd.DataFrame(lofi_music.get(emotion_idx, []), columns=['Name', 'Album', 'Artist'])
	else:
		df = pd.read_csv(music_dist[emotion_idx])
		df = df[['Name', 'Album', 'Artist']]
		df = df.head(15)
		return df
