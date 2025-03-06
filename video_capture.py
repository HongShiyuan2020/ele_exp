from ultralytics import YOLO
import cv2

model = YOLO("ckpt/yolov8n_3000.pt")

class VideoCapture:
    def __init__(self, source):
        self.source = source
        self.init_device()

    def init_device(self):
        self.cap = cv2.VideoCapture(self.source)
        self.frame_idx = -1
        self.is_play = False

    def destroy(self):
        self.is_play = False
        self.cap.release()

    def __next__(self):
        ret, frame = self.cap.read()
        if ret and self.is_play:
            self.frame_idx += 1
            return (self.frame_idx ,frame)
        else:
            self.is_play = False
            raise StopIteration
        
    def __iter__(self):
        self.is_play = True
        return self
    
    def stop(self):
        self.is_play = False


if __name__ == "__main__":
    cap = VideoCapture("rtsp://admin:@192.168.4.13")
    res = None

    for idx, frame in cap:
        frame = cv2.resize(frame, [1600, 928])
        if idx % 4 == 0:
            res = model.predict(source=frame)
            res = res[0]
        ann_frame = res.plot(img=frame)
            
        # if idx % 2 == 0:
            # cv2.imwrite(f"labeling-data/COMS/{idx:06d}.jpg", frame)
        cv2.imshow("WND", ann_frame)
        if cv2.waitKey(1) == ord("q"):
            cap.stop()

    cap.destroy()   
    cv2.destroyAllWindows()