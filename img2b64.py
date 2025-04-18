import cv2 as cv
import base64


def img2b64(img_path):
    img = cv.imread(img_path)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    img = cv.resize(img, [1600, 928])
    b64 = base64.b64encode(img.tobytes()).decode("utf-8")
    
    print(b64)
    
    with open("b64.txt", mode="w", encoding="utf-8") as fout:
        fout.write(b64)


img2b64(r"labeling-data\total\images\01_20250121_02-00_05_11.jpg")