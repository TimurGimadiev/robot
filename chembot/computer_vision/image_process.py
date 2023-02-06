import torch
from os import system
from time import time
from loguru import logger

model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')
def predict(device=3, skip=3):
    command = f"fswebcam -d /dev/video{device} -r 1920x1080 -S {skip} --no-banner " \
              f"/tmp/robot_image_for_analysis.jpg"
    #command = ["fswebcam", "-d", "/dev/video2", "-D", "1", "-r", "1920x1080", "-S", "2", "--no-banner", "/home/robot/code/yolov5/images/image1.jpg"]
    start = time()
    try:
        while True:
            err = system(command)
            if not err:
                break
            if time() - start > 15 :
                raise ValueError("timeout waiting camera")
    except ValueError:
        return None
    print("photo captured")
    results = model("/tmp/robot_image_for_analysis.jpg")
    res = []
    for result in results.xyxyn[0].tolist():
        res.append((((result[0] + result[2])/ 2 - 0.5)*1080, ((result[1] + result[3])/ 2 - 0.5)*1920))
    return res