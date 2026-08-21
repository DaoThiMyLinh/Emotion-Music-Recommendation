import os, glob, numpy as np, cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense

emotion_dict = {0:"Angry", 1:"Disgusted", 2:"Fearful", 3:"Happy", 4:"Neutral", 5:"Sad", 6:"Surprised"}

def load_legacy():
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), activation="relu", input_shape=(48,48,1)))
    model.add(Conv2D(64, kernel_size=(3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(128, kernel_size=(3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(128, kernel_size=(3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(7, activation="softmax"))
    model.load_weights("model.h5")
    return model

def prep(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return None, None
    img = cv2.resize(img, (48,48))
    raw = img.astype(np.float32)
    norm = raw / 255.0
    return raw[None, ..., None], norm[None, ..., None]

def top1(p):
    p = p.reshape(-1)
    i = int(np.argmax(p))
    return emotion_dict[i], float(p[i])

if __name__ == "__main__":
    model = load_legacy()
    base = os.path.join("data", "test")
    folders = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    for folder in folders:
        paths = glob.glob(os.path.join(base, folder, "*"))
        paths = [px for px in paths if os.path.isfile(px)][:1]
        if not paths:
            print(f"{folder} NO FILES")
            continue
        print(f"=== {folder} ===")
        for p in paths:
            xr, xn = prep(p)
            if xr is None: continue
            pr = model.predict(xr, verbose=0)
            pn = model.predict(xn, verbose=0)
            print(f"{os.path.basename(p)} raw: {top1(pr)} norm: {top1(pn)}")
