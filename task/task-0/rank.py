import os
import io
import base64
import json
from PIL import Image
import numpy as np

def mse_loss(answer_image, label_image):
    loss = ((answer_image - label_image) ** 2).mean()
    return loss

def get_answer_images():
    answer = []
    with open("example.json", "r") as json_file:
        json_data = json.load(json_file)
        for base64_image in json_data["answer"]:
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            image_ndarray = np.array(image)
            answer.append(image_ndarray)
    return answer

def get_labels_images():
    labels = []
    for image_name in os.listdir("test-labels"):
        image = Image.open(open(f"test-labels/{image_name}", "rb"))
        image_ndarray = np.array(image)
        labels.append(image_ndarray)
    return labels

def cal_score():
    answer_images = get_answer_images()
    labels_images = get_labels_images()
    score = 0.0
    for answer_image, label_image in zip(answer_images, labels_images):
        loss = mse_loss(answer_image, label_image)
        score += loss
    return score

if __name__ == "__main__":
    score = cal_score()
    print(score)