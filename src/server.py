import asyncio
from time import perf_counter

import grpc
from PIL import Image
from io import BytesIO
from inference import inference
import logging
from infer_merkle_pb2_grpc import InferMerkleServicer, add_InferMerkleServicer_to_server
from infer_merkle_pb2 import InferenceRequest, InferenceReply
from infer_merkle_pb2 import MT_Response, MT_Request

from buildmtree import buildTree

logging.basicConfig(level=logging.INFO)


class InferMerkleService(InferMerkleServicer):
    def open_image(self, image: bytes) -> Image.Image:
        image = Image.open(BytesIO(image))
        return image

    async def inference(self, request: InferenceRequest, context) -> InferenceReply:
        logging.info(f"[🦾] Received request")
        start = perf_counter()
        images = list(map(self.open_image, request.image))
        preds = inference(images)
        logging.info(f"[✅] Done in {(perf_counter() - start) * 1000:.2f}ms")
        return InferenceReply(pred=preds)

    async def build_mt(self, request: MT_Request, context):
        print(request)
        f = open("merkle.tree", "w")
        leaves = request.fingerprint.split(",")
        root = buildTree(leaves, f)
        print(root.hashValue)
        f.close()
        return MT_Response(root=root.hashValue)


async def serve():
    server = grpc.aio.server()
    add_InferMerkleServicer_to_server(InferMerkleService(), server)
    # using ip v6
    adddress = "[::]:50052"
    server.add_insecure_port(adddress)
    logging.info(f"[📡] Starting server on {adddress}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
