from os import system, remove, path
from time import time
from loguru import logger
from .detector import Detector

class ImageProcessor(Detector):

    def __init__(self, model_path, tmp_file = "/tmp/robot_image_for_analysis.jpg"):
        super().__init__(model_path=model_path)
        #model = Detector('./Segf16.tflite')
        self.tmp_file = tmp_file

    def predict(self, device=0, skip=3):
        if path.exists(self.tmp_file):
            remove(self.tmp_file)
            logger.info("previous photo removed")
        command = f"fswebcam -d /dev/video{device} -r 1920x1080 -S {skip} --no-banner " \
                f"{self.tmp_file}"
        #command = ["fswebcam", "-d", "/dev/video2", "-D", "1", "-r", "1920x1080", "-S", "2", "--no-banner", "/home/robot/code/yolov5/images/image1.jpg"]
        start = time()
        try:
            while True:
                err = system(command)
                if not err:
                    break
                if time() - start > 15:
                    raise ValueError("timeout waiting camera")
        except ValueError:
            return None
        logger.info("photo captured")
        result = self.detect_closest_object(self.tmp_file)[4]
        return result[0], result[1]
        #return ((result[0] + result[2])/ 2 - 0.5)*1080, ((result[1] + result[3])/ 2 - 0.5)*1920
