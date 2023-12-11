import sys
sys.path.append("../")

import grpc
import reddit_pb2 as reddit_pb2
import reddit_pb2_grpc as reddit_pb2_grpc

class RedditClient:

    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = reddit_pb2_grpc.RedditStub(self.channel)
    
    def create_post(self, title, body, url, score, state, date, user_id):
        response = self.stub.CreatePost(reddit_pb2.CreatePostRequest(title=title, body=body, url=url, score=score, state=state, date=date, user_id=user_id))
        return response
    
    # upvote = 1, downvote = -1
    def vote_post(self, id, score):
        response = self.stub.VotePost(reddit_pb2.VotePostRequest(id=id, score=score))
        return response

    def get_post(self, id):
        response = self.stub.GetPost(reddit_pb2.GetPostRequest(id=id))
        return response
    
    def create_comment(self, body, score, state, date, user_id, post_id):
        response = self.stub.CreateComment(reddit_pb2.CreateCommentRequest(body=body, score=score, state=state, date=date, user_id=user_id, post_id=post_id))
        return response
    
    def vote_comment(self, id, score):
        response = self.stub.VoteComment(reddit_pb2.VoteCommentRequest(id=id, score=score))
        return response

    def get_most_upvoted_comments(self, post_id, n):
        response = self.stub.GetMostUpvotedNComments(reddit_pb2.GetMostUpvotedNCommentsRequest(post_id=post_id, n=n))
        return response

    def expand_comment_branch(self, comment_id, n):
        response = self.stub.ExpandCommentBranch(reddit_pb2.ExpandCommentBranchRequest(comment_id=comment_id, n=n))
        return response


    # Extra credit - monitor updates
    def monitor_updates(self, post_id, comment_ids):
        
        def request_iterator():
            yield reddit_pb2.MonitorUpdatesRequest(post_id=post_id)

            yield reddit_pb2.MonitorUpdatesRequest(comment_ids=comment_ids)
            
        response = self.stub.MonitorUpdates(request_iterator())

        for update in response:
            print(update)
            


if __name__ == "__main__":
    client = RedditClient("localhost", 50051)
    print(client.monitor_updates(1, [1, 2, 3]))
