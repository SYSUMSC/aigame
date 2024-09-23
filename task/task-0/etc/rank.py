import os
import io
import base64
from PIL import Image
import numpy as np

from typing import Dict

def mse_loss(answer_image, label_image):
    loss = ((answer_image - label_image) ** 2).mean()
    return loss

def get_answer_images(answer_json:Dict):
    answer = []
    for base64_image in answer_json["answer"]:
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        image_ndarray = np.array(image).reshape(321, 481, 3)
        answer.append(image_ndarray)
    return answer

def get_labels_images():
    labels = []
    for image_name in os.listdir("test-labels"):
        image = Image.open(open(f"test-labels/{image_name}", "rb"))
        image_ndarray = np.array(image)
        labels.append(image_ndarray)
    return labels

def cal_score(answer_json:Dict) -> float:
    answer_images = get_answer_images(answer_json)
    labels_images = get_labels_images()
    score = 0.0
    for answer_image, label_image in zip(answer_images, labels_images):
        loss = mse_loss(answer_image, label_image)
        score += loss
    return score