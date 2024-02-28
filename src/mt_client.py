import grpc

import hashlib
import infer_merkle_pb2
import infer_merkle_pb2_grpc
import time

PORT = 50052


def build_mtree_with_grpc(hash):
    with grpc.insecure_channel(f"localhost:{PORT}") as channel:
        stub = infer_merkle_pb2_grpc.InferMerkleStub(
            channel
        )  # Use the correct stub class
        request = infer_merkle_pb2.MT_Request(
            fingerprint=hash
        )  # Create the request message
        response = stub.build_mt(request)  # Send the request message
        return response.root


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


start_time = time.time()

# features consists of features of image
# feature is a piece of information about the content of an image
features = "a,b,c,d,e,f,k"
fingerprint = generate_fingerprint(features)

# fingerprint = "a,b,c,d,e,f,k"
root = build_mtree_with_grpc(fingerprint)

if root:
    print(f"Sending {root} using gRPC speed:{time.time() - start_time}")
else:
    print(f"Failed to send hash")
