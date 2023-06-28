import cv2
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite
import statistics
import os
from loguru import logger
from memory_profiler import profile
# import tensorflow as tf

# https://bestprogrammer.ru/programmirovanie-i-razrabotka/python-opencv-markirovka-i-analiz-podklyuchennyh-komponentov
class Detector:

    def __init__(self, model_path):
        self.model = tflite.Interpreter(model_path=model_path)
        self.size = 512
        self.dict_classes = {(158, 26, 107): 'cap', (51, 91, 102): 'hole', (0, 0, 0): 'background', (125, 5, 10): '0',
                             (209, 35, 69): '1', (53, 13, 234): '2', (71, 159, 254): '3',
                             (74, 100, 159): '4', (71, 129, 68): '5', (87, 35, 107): '6',
                             (28, 221, 165): '7', (226, 188, 110): '8', (240, 103, 219): '9'}
        self.new_img = False

        # self.model = tf.lite.Interpreter(model_path=model_path)

    def detect_closest_object(self, image_path, save=False, memory=False):
        if memory:
            temp = profile(self.__detect_objects)
            return temp(image_path, save)[0]
        else:
            return self.__detect_objects(image_path, save)[0]

    def detect_all_object(self, image_path, save=False, memory=False):
        if memory:
            temp = profile(self.__detect_objects)
            return temp(image_path, save)
        else:
            return self.__detect_objects(image_path, save)

    def __save_image(self, filename):
        cv2.imwrite(filename, self.new_img)

    def __detect_objects(self, image_path, save=False):
        list_objects = []
        list_digits = []

        # Load the image
        img = Image.open(image_path).convert('RGB')

        # Convert image to np.array with resize
        img = np.array(img.resize((self.size, self.size), resample=Image.LANCZOS)).astype(np.float32)
        # Perform inference using the TFLite model
        self.model.allocate_tensors()
        input_details = self.model.get_input_details()
        output_details = self.model.get_output_details()
        self.model.set_tensor(input_details[0]['index'], np.array([img]))
        self.model.invoke()
        ans = self.model.get_tensor(output_details[0]['index'])


        # Convert and processing predict to np.array with size as size original image
        img = Detector.np_array_to_image(ans)


        # preprocess the image
        gray_img = cv2.cvtColor(img,
                                cv2.COLOR_BGR2GRAY)
        # Applying 7x7 Gaussian Blur
        blurred = cv2.GaussianBlur(gray_img, (7, 7), 0)
        # Applying threshold
        threshold = cv2.threshold(blurred, 0, 255,
                                  cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # Apply the Component analysis function
        analysis = cv2.connectedComponentsWithStats(threshold,
                                                    4,
                                                    cv2.CV_32S)
        (totalLabels, label_ids, values, centroid) = analysis
        self.new_img = img.copy()
        self.new_img = cv2.cvtColor(self.new_img, cv2.COLOR_BGR2RGB)
        for i in range(1, totalLabels):

            # Area of the component
            area = values[i, cv2.CC_STAT_AREA]

            # If area of object more than 125000 pixel
            if (area > 6000):
                object = []
                digit = []

                # Now extract the coordinate points
                x1 = values[i, cv2.CC_STAT_LEFT]
                y1 = values[i, cv2.CC_STAT_TOP]
                w = values[i, cv2.CC_STAT_WIDTH]
                h = values[i, cv2.CC_STAT_HEIGHT]

                # Coordinate of the bounding box
                pt1 = (x1, y1)
                pt2 = (x1 + w, y1 + h)
                # Center of the object
                (X, Y) = centroid[i]
                # Manhattan distance from the center of the image to the object
                distance = abs(int(X) - 960) + abs(int(Y) - 540)
                motion_vector = (int(X) - 960, int(Y) - 540)
                center = (int(X), int(Y))
                fully_in_frame = 'YES'
                # The object class definition
                classes = []
                for k in range(round(X) - round(w / 2.3), round(X) + round(w / 2.3), round(w / 10)):
                    for j in range(round(Y) - round(h / 2.3), round(Y) + round(h / 2.3), round(h / 10)):
                        # if need to see points
                        # cv2.circle(self.new_img, (round(k), round(j)), 0, (0, 128, 0), 10)
                        temp = tuple(img[round(j), round(k)])
                        classes.append(self.dict_classes.get(temp, 'background'))
                classes = [i for i in classes if i != 'background']
                try:
                    class_object = statistics.mode(classes)
                except statistics.StatisticsError:
                    raise ValueError('Ошибка в определении класса объекта')

                # If the object pretty small in the image, therefore it is not fully in the image
                if class_object == 'cap' and area < 350000:
                    fully_in_frame = 'NO'
                elif class_object == 'hole' and area < 150000:
                    fully_in_frame = 'NO'

                # Bounding boxes for each component
                cv2.rectangle(self.new_img, pt1, pt2,
                              (0, 255, 0), 3)
                cv2.circle(self.new_img, (int(X),
                                          int(Y)),
                           4, (0, 0, 255), -1)
                cv2.arrowedLine(self.new_img, (960, 540), (int(X), int(Y)),
                                (0, 0, 255), 1)

                if class_object in ('cap', 'hole'):
                    object.append(class_object)  # class
                    object.append(fully_in_frame)  # fully in frame
                    object.append(distance)  # distance
                    object.append(center)  # center coordinates
                    object.append(motion_vector)  # motion vector from the center
                    list_objects.append(object)

                # Class is digit
                else:
                    distance_from_right_edge = 1920 - int(X)
                    digit.append(class_object)  # class
                    digit.append(center)  # center coordinates
                    digit.append(distance_from_right_edge)  # distance from right edge
                    list_digits.append(digit)

                if save == True:
                    self.__save_image(os.path.basename(image_path)[:-4]+'.png')

        list_objects.sort(key=lambda object: object[2])  # sort to use distance from the center
        list_digits.sort(key=lambda digit: digit[2])  # sort to use distance from right edge
        list_numbers = []
        list_objects_copy = list_objects.copy()
        used_number = False
        for i in range(len(list_digits)):
            if i == len(list_digits) - 1 and not used_number:  # the last digit need correct
                list_numbers.append(list_digits[i])
                break
            elif used_number:
                used_number = False
                continue
            elif list_digits[i+1][2] - list_digits[i][2] <= 300:  # concatenation of digits into the number
                new_number = []
                new_number.append(list_digits[i][0] + list_digits[i+1][0])  # class
                center = tuple(map(lambda x, y: (x + y) // 2, list_digits[i][1], list_digits[i+1][1]))
                # center = (list_digits[i][2] + list_digits[i + 1][2]) // 2)
                new_number.append(center)  # center coordinates
                new_number.append(list_digits[i][2] + list_digits[i+1][2])  # distance from right edge
                list_numbers.append(new_number)
                used_number = True
                if i + 1 == len(list_digits):
                    break
            else:
                list_numbers.append(list_digits[i])

        # Matching numbers and cells
        for j in list_numbers:
            for i in range(len(list_objects_copy)):
                if len(list_objects[i]) == 6:
                    continue
                else:
                    temp = list(map(lambda x, y: x - y, list_objects_copy[i][3], j[1]))
                    # print(f'object {list_objects_copy[i][3]}')
                    # print(f'digit {j[1]}')
                    # print(sum(temp))
                    # if abs(sum(temp) >= 1000) and list_objects_copy[i][3] < j[1]:
                    #     list_objects[i].append(j[0])  # add intel about a cell
                    #     break
                    # elif abs(sum(temp) <= 900) and list_objects_copy[i][3] < j[1]:
                    #     list_objects[i].append('out_of_frame')  # if part of the number is out of frame
                    #     break
                    if list_objects_copy[i][3] < j[1]:
                        list_objects[i].append(j[0])  # add intel about a cell
                        break
                    else:
                        list_objects[i].append('unknown')  # if there is no number in the frame
                        break

        logger.info(f"Количество найденных крышек: {len([i for i in list_objects if i[0] =='cap'])}")
        logger.info(f"Количество найденных дырок: {len([i for i in list_objects if i[0] =='hole'])}")
        return list_objects

    @staticmethod
    def np_array_to_image(arr, height=1080, width=1920, SIZE=512):
        class_colors = ((125, 5, 10), (209, 35, 69), (53, 13, 234), (71, 159, 254), (74, 100, 159), (71, 129, 68),
                        (87, 35, 107), (28, 221, 165), (226, 188, 110), (240, 103, 219), (158, 26, 107), (51, 91, 102))

        # Convert one-hot encoded array to class label array
        y = np.squeeze(arr)
        y = np.argmax(y, axis=-1)
        num_classes = len(class_colors)

        # Convert class label array to RGB image
        x = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
        for i in range(num_classes):
            color = class_colors[i]
            mask = y == i + 1
            x[mask] = color

        # Resize image to original size
        img = Image.fromarray(x)
        img = img.resize((width, height), resample=Image.LANCZOS)  # resize image back to original size
        return np.array(img)

