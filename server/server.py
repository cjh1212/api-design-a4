import sys
sys.path.append("../")

from concurrent import futures

import grpc
import reddit_pb2 as reddit_pb2
import reddit_pb2_grpc as reddit_pb2_grpc
import src.endpoint as endpoint

def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reddit_pb2_grpc.add_RedditServicer_to_server(endpoint.Reddit(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    port = input("Enter port: ")
    serve(port)