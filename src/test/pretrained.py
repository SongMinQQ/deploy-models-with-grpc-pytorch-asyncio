# Add the path to torchvision - change as needed
import sys

# sys.path.insert(0, '/home/mircea/python-envs/env/lib/python3.6/site-packages/vision')

# Choose an image to pass through the model
test_image = "images/dog.jpg"

# Imports
import torch, json
import numpy as np
from torchvision import datasets, models, transforms
from PIL import Image
import time

# Import matplotlib and configure it for pretty inline plots
import matplotlib.pyplot as plt

# %matplotlib inline
#  %config InlineBackend.figure_format = 'retina'

# Prepare the labels
with open("../imagenet-simple-labels.json") as f:
    labels = json.load(f)

# First prepare the transformations: resize the image to what the model was trained on and convert it to a tensor
data_transform = transforms.Compose(
    [transforms.Resize((224, 224)), transforms.ToTensor()]
)
# Load the image
image = Image.open(test_image)
plt.imshow(image), plt.xticks([]), plt.yticks([])

# Now apply the transformation, expand the batch dimension, and send the image to the GPU
# image = data_transform(image).unsqueeze(0).cuda()
image = data_transform(image).unsqueeze(0)


# Download the model if it's not there already. It will take a bit on the first run, after that it's fast
model = models.resnet50(pretrained=True)
# Send the model to the GPU
# model.cuda()
# Set layers such as dropout and batchnorm in evaluation mode
model.eval()

fps = np.zeros(200)

# Get the 1000-dimensional model output
for i in range(200):
    t0 = time.time()
    out = model(image)
    fps[i] = 1 / (time.time() - t0)
    # Find the predicted class
    print("Predicted class is: {}".format(labels[out.argmax()]))

fig, ax = plt.subplots()
# the semicolon silences the irrelevant output
ax.plot(fps)
ax.set_xlabel("Iteration")
ax.set_ylabel("FPS")
