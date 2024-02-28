from fastapi import FastAPI, File, UploadFile

from pydantic import BaseModel

# CORS 처리
from fastapi.middleware.cors import CORSMiddleware

import grpc
from infer_merkle_pb2 import InferenceRequest, InferenceReply
from infer_merkle_pb2 import MT_Response, MT_Request


import hashlib
import infer_merkle_pb2_grpc
import time
import json

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Feature(BaseModel):
    value: str


with open("imagenet-simple-labels.json") as f:
    labels = json.load(f)


def main(file_content):
    with grpc.insecure_channel("[::]:50052 ") as channel:
        stub = infer_merkle_pb2_grpc.InferMerkleStub(channel)

        res: InferenceReply = stub.inference(
            InferenceRequest(image=[file_content, file_content, file_content])
        )
        print(res.pred)
    return res.pred[0]
    # return labels[res.pred[0]]


@app.get("/pred/{img_id}")
async def pred_img(img_id):
    success = main()
    return {"img_id": img_id}


@app.post("/predict_img")
async def upload_file_grpc(file: UploadFile = File(...)):
    content = await file.read()
    start_time = time.time()
    success = main(content)
    if success:
        print(f"Sending file using gRPC speed: {time.time() - start_time}")
        # return {"message": f"({success}) :File {file.filename} has been uploaded."}
        result = {"class": f"{success}"}
        print(result)
        return result

    else:
        return {"message": "Failed to upload the file."}


def generate_fingerprint(features):
    feature_set = []
    for f in features.split(","):
        feature_set.append(hashlib.sha256(f.encode("utf-8")).hexdigest())

    # fingerprint is used for building a node  of Merkle tree
    fingerprint = ""
    for fg in feature_set:
        fingerprint = fingerprint + fg
        fingerprint = fingerprint + ","

    return fingerprint


def build_mtree_with_grpc(hash):
    with grpc.insecure_channel(f"[::]:50052 ") as channel:
        stub = infer_merkle_pb2_grpc.InferMerkleStub(
            channel
        )  # Use the correct stub class
        request = MT_Request(fingerprint=hash)  # Create the request message
        response = stub.build_mt(request)  # Send the request message
        return response.root


@app.post("/build_mt")
async def build_mt_grpc(feature: Feature):
    start_time = time.time()
    print(feature)
    f = feature.value

    finger_print = generate_fingerprint(f)
    root = build_mtree_with_grpc(finger_print)

    if root:
        print(f"Sending {root} using gRPC speed:{time.time() - start_time}")
        return {"root": root}
    else:
        return {"message": f"Failed to build mt"}
