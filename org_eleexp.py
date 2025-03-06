import numpy as np
import cv2 as cv

from det import comdet_one_img, select_coms

org_area = [0.51, 0.0, 1, 0.37]


def dec(img: np.ndarray):
    
    h, w, c = img.shape
    org_tl = (int(w*org_area[0]), int(h*org_area[1]))
    org_br = (int(w*org_area[2]), int(h*org_area[3]))
    img = cv.rectangle(img, org_tl, org_br, (0, 255, 0))


    _, res = comdet_one_img(img)
    coms = select_coms(res)

    for c in coms:
        fcx = (c["xyxy"][0] + c["xyxy"][2])/2
        fcy = (c["xyxy"][1] + c["xyxy"][3])/2

        cent = (int(w*fcx), int(h*fcy))

        img = cv.circle(img, cent, 3, (0, 0, 255), 2)

    cv.imshow("aa", img)
    cv.waitKey(0)

    pass

if __name__ == "__main__":
    im = cv.imread("labeling-data/01_1_5/images/01_20250110_100325-00:01:06.jpg")
    im = cv.resize(im, [640, 384])
    dec(im)