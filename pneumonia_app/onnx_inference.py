from django.conf import settings

from time import time
import cv2 as cv
import numpy as np
import os

import onnxruntime

classes = ('normal', 'pneumonia')
IMAGE_SIZE = 224


# 使用Sigmoid函数进行概率转换
def sigmoid(x):
    return 1 / (1 + np.exp(-np.array(x)))


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


def get_test_transform():
    from torchvision import transforms

    return transforms.Compose([
        transforms.ToTensor(),  # convert image to tensor
        transforms.Resize([IMAGE_SIZE, IMAGE_SIZE]),  # resize image
    ])


def inference_resnet18sam(img, image_size=224):
    model_path = os.path.join(settings.STATICFILES_DIRS[0], 'model_data', 'resnet18-lite.onnx')

    # initialize session
    session = onnxruntime.InferenceSession(model_path)
    session.set_providers(['CPUExecutionProvider'])

    # read image
    src = img

    # pre-process
    resized_img = cv.resize(src, (image_size, image_size))
    img = get_test_transform()(resized_img)
    img = img.unsqueeze_(0)

    # prepare inputs and get prediction
    inputs = {session.get_inputs()[0].name: to_numpy(img)}
    start_time = time()
    outs = session.run(None, inputs)
    end_time = time()

    probabilities = sigmoid(outs)
    print("probabilities:", outs)

    # post-process
    res = classes[np.argmax(outs).item()]

    return 1000. * (end_time - start_time), res, probabilities
