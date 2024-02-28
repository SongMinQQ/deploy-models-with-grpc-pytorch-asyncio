## Getting Started

Let's start by setup our environment using virtual env

**Tested with python 3.9**

``
conda create -n grpc python=3.9
source ~/opt/anaconda3/bin/activate grpc
pip install -r requirements.txt

```


Then, let's install all the required packages, `grpcio`, `grpcio-tools`, `torch`, `torchvision` and `Pillow`

```

pip install grpcio grpcio-tools torch torchvision Pillow==9.3.0

````

All set!
## Server

The next step is to create the actual gRPC server. First, we describe the message and the service in the `.proto` file.

A list of all types of messages can be found [here](https://learn.microsoft.com/en-us/dotnet/architecture/grpc-for-wcf-developers/protocol-buffers) and the official python tutorial for gRPC [here](https://grpc.io/docs/languages/python/basics/)

### Proto

We will start by defining our `inference + Merkle tree service` service

```proto
// infer_merkle.proto

syntax = "proto3";

service InferMerkle {
  // Sends a inference reply
  rpc inference (InferenceRequest) returns (InferenceReply) {}
  rpc build_mt(MT_Request) returns (MT_Response);
}


### Build the server and client

Now, we need to generate the client and server code using `grpcio-tools` (we install it at the beginning).

```bash
cd src && python -m grpc_tools.protoc -I . --python_out=. --pyi_out=. --grpc_python_out=. infer_merkle.proto
````

This will generate the following files

```
└── src
    ├── infer_merkle_pb2_grpc.py
    ├── infer_merkle_pb2.py
    ├── infer_merkle_pb2.pyi
    ...
```

- `infer_merkle_pb2_grpc` contains our gRPC's server definition
- `infer_merkle_pb2` contains our gRPC's messages definition
- `infer_merkle_pb2` contains our gRPC's messages types definition

We now have to code our service,

```python
# server.py
# we will use asyncio to run our service
import asyncio
...
# from the generated grpc server definition, import the required stuff
from infer_merkle_pb2_grpc import InferMerkleServicer, add_InferMerkleServicer_to_server
# import the requests and reply types
from infer_merkle_pb2 import InferenceRequest, InferenceReply
from infer_merkle_pb2 import MT_Response, MT_Request
...
```

To create the gRPC server we need to import `InferMerkleServicer` and `add_InferMerkleServicer_to_server` from the generated `infer_merkle_pb2_grpc`. Our logic will go inside a subclass of `InferMerkleServicer` in the `inference` function, the one we defined in the `.proto` file.

```python
# server.py
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

```

Notice we subclass `InferMerkleService`, we add our logic inside `inference` and we label it as an `async` function, this is because we will lunch our service using [asyncio](https://docs.python.org/3/library/asyncio.html).

We now need to tell gRPC how to start our service.

```python
# server.py
...
from infer_merkle_pb2_grpc import InferMerkleServicer, add_InferMerkleServicer_to_server

import logging

logging.basicConfig(level=logging.INFO)

async def serve():
    server = grpc.aio.server()
    add_InferMerkleServicer_to_server(InferMerkleService(), server)
    # using ip v6
    adddress = "[::]:50052"
    server.add_insecure_port(adddress)
    logging.info(f"[📡] Starting server on {adddress}")
    await server.start()
    await server.wait_for_termination()
```

Line by line, we create a grpc asyncio server using `grpc.aio.server()`, we add our service by passing it to `add_InferMerkleServicer_to_server` then we listed on a custom port using ipv6 by calling the `.add_insecure_port` method and finally we await the `.start` server method

Finally,

```python
# server.py
if __name__ == "__main__":
    asyncio.run(serve())
```

If you know run the file

```bash
python src/server.py
```

You'll see

```
INFO:root:[📡] Starting server on [::]:50052
```

Sweet 🎉! We have our gRPC running with asyncio. We now need to define our **client**.

## Client

Creating a client is straightforward, similar to before we need the definitions that were generated in the previous step.

let's run it!

```bash
python src/infer_client.py
python src/mt_client.py

uvicorn app:app --reload
```
