from typing import List

import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.models import ResNet34_Weights, resnet34

preprocess = T.Compose(
    [
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


model = torch.hub.load("pytorch/vision:v0.10.0", "resnet18", pretrained=True)
model.eval()


@torch.no_grad()
def inference(images: List[Image.Image]) -> List[int]:
    input_batch = torch.stack([preprocess(image) for image in images])
    # input_tensor = preprocess(image)
    # input_batch = input_tensor.unsqueeze(
    #    0
    # )  # create a mini-batch as expected by the model
    if torch.cuda.is_available():
        input_batch = input_batch.to("cuda")
        model.to("cuda")

    with torch.no_grad():
        output = model(input_batch)

    # print(output[0])
    # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    # print(probabilities)

    top5_prob, top5_catid = torch.topk(probabilities, 5)

    print(top5_prob[0].item())
    return [int(top5_catid[0])]


if __name__ == "__main__":
    image = Image.open("./examples/cat.jpg")
    print(inference([image]))
