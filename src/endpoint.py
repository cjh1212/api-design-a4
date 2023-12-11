import sys
sys.path.append("../")

import reddit_pb2 as reddit_pb2
import reddit_pb2_grpc as reddit_pb2_grpc
import sqlite3

class Reddit(reddit_pb2_grpc.RedditServicer):

    # counter for post ids
    post_id = 1

    # Connecting to the database
    def connect_db(self):
        db = sqlite3.connect('reddit.sqlite')
        return db
    
    # querying database
    def query_db(self, query, args=(), one=False):
        with self.connect_db() as db:
            cur = db.execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return rv[0] if rv else None
    
    # query multiple rows
    def query_multiple(self, query, args=(), one=False):
        with self.connect_db() as db:
            cur = db.execute(query, args)
            rv = cur.fetchall()
            cur.close()
            return rv if rv else None

    def CreatePost(self, request, context):
        title = request.title
        body = request.body
        url = request.url
        score = request.score
        state = request.state
        date = request.date
        user_id = request.user_id
        subreddit_id = request.subreddit_id

        # insert into database
        try:
            self.query_db("INSERT INTO posts (title, body, url, score, state, date, user_id, subreddit_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, body, url, score, state, date, user_id, subreddit_id))

            response = self.query_db("SELECT * FROM posts ORDER BY id DESC LIMIT 1;")

            return reddit_pb2.CreatePostResponse(id=response[0])
        except Exception as e:
            print(f"Error creating post: {e}")
            return reddit_pb2.CreatePostResponse(id=0)
    
    def VotePost(self, request, context):
        id = request.id
        score = request.score
        
        # update score in database
        try:
            self.query_db("UPDATE posts SET score = score + ? WHERE id = ?", (score, id))
            updated_score = self.query_db("SELECT score FROM posts WHERE id = ?", (id,))
            return reddit_pb2.VotePostResponse(success=True, score=updated_score[0])
        except Exception as e:
            print(f"Error voting post: {e}")
            return reddit_pb2.VotePostResponse(success=False)
    
    # Retrieve a post content
    def GetPost(self, request, context):
        id = request.id
        try:
            response = self.query_db("SELECT * FROM posts WHERE id = ?", (id,))
            comment_response = self.query_multiple("SELECT * FROM comments WHERE post_id = ?", (id,))
            comments = []
            for comment in comment_response:
                user = self.query_db("SELECT * FROM users WHERE id = ?", (comment[5],))
                user1 = reddit_pb2.User(id=user[0], username=user[1])
                c = reddit_pb2.Comment(
                    id=int(comment[0]),
                    body=comment[1],
                    score=int(comment[2]),
                    state=int(comment[3]),
                    date=comment[4],
                    user=user1,
                    post_id=int(comment[6]),
                    parent_id=comment[7]
                )
                comments.append(c)

            post = reddit_pb2.Post(
                id=int(response[0]), 
                title=response[1], 
                body=response[2], 
                url=response[3], 
                score=response[4], 
                state=response[5], 
                date=response[6], 
                user_id=int(response[7]),
                comments=comments,
                subreddit_id=int(response[8])
            )

            return reddit_pb2.GetPostResponse(post=post)
        except Exception as e:
            print(f"Error retrieving post: {e}")
            result = reddit_pb2.GetPostResponse(post=None)
            # result.post.append(reddit_pb2.Post(id=0, title="", body="", url="", score=0, state=0, date="", user_id=0))
            return result
    
    # Create a comment
    # TODO - handle parent comment
    def CreateComment(self, request, context):
        body = request.body
        score = request.score
        state = request.state
        date = request.date
        user_id = request.user_id
        post_id = request.post_id
        parent_id = request.parent_id

        # insert into database
        try:
            self.query_db("INSERT INTO comments (body, score, state, date, user_id, post_id, parent_comment_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (body, score, state, date, user_id, post_id, parent_id))
            response = self.query_db("SELECT * FROM comments ORDER BY id DESC LIMIT 1;")
            return reddit_pb2.CreateCommentResponse(success=True, id=int(response[0]))
        except Exception as e:
            print(f"Error creating comment: {e}")
            return reddit_pb2.CreateCommentResponse(success=False)
    
    # Vote a comment
    def VoteComment(self, request, context):
        id = request.id
        score = request.score

        # update score in database
        try:
            self.query_db("UPDATE comments SET score = score + ? WHERE id = ?", (score, id))
            updated_score = self.query_db("SELECT score FROM comments WHERE id = ?", (id,))
            return reddit_pb2.VoteCommentResponse(success=True, score=updated_score[0])
        except Exception as e:
            print(f"Error voting comment: {e}")
            return reddit_pb2.VoteCommentResponse(success=False)
    
    # Retrieve a list of N most upvoted comments under a post
    def GetMostUpvotedNComments(self, request, context):
        post_id = request.post_id
        n = request.n

        try:
            # query database
            response = self.query_multiple("SELECT * FROM comments WHERE post_id = ? ORDER BY score DESC LIMIT ?", (post_id, n))
            result = reddit_pb2.GetMostUpvotedNCommentsResponse()
            for row in response:
                user = self.query_db("SELECT * FROM users WHERE id = ?", (row[5],))
                user1 = reddit_pb2.User(id=user[0], username=user[1])
                comment = reddit_pb2.Comment(
                    id=int(row[0]),
                    body=row[1],
                    score=int(row[2]),
                    state=int(row[3]),
                    date=row[4],
                    user=user1,
                    post_id=int(row[6]),
                    parent_id=row[7]
                )
                result.comments.append(comment)
            return result
        except Exception as e:
            print(f"Error retrieving comments: {e}")
            return reddit_pb2.GetMostUpvotedNCommentsResponse()
    
    #Expand a comment branch
    def ExpandCommentBranch(self, request, context):
        comment_id = request.comment_id
        n = request.n

        try:
            # Need to handle exception

            query = """
            SELECT * FROM comments WHERE parent_comment_id = ?
            ORDER BY score DESC LIMIT ?;
            """
            response = reddit_pb2.ExpandCommentBranchResponse()
            depth_one = self.query_multiple(query, (comment_id, n))
            for row in depth_one:
                query = """
                SELECT * FROM comments WHERE parent_comment_id = ?
                ORDER BY score DESC LIMIT ?;
                """
                temp = self.query_multiple(query, (row[0], n))
                for row1 in temp:
                    user = self.query_db("SELECT * FROM users WHERE id = ?", (row1[5],))
                    user1 = reddit_pb2.User(id=user[0], username=user[1])
                    c = reddit_pb2.Comment(
                        id=int(row1[0]),
                        body=row1[1],
                        score=int(row1[2]),
                        state=int(row1[3]),
                        date=row1[4],
                        user=user1,
                        post_id=int(row1[6]),
                        parent_id=row1[7],
                        # comments=None
                    )
                    response.second_level.append(c)
            
            
            for row in depth_one:
                user = self.query_db("SELECT * FROM users WHERE id = ?", (row[5],))
                user1 = reddit_pb2.User(id=user[0], username=user[1])
                comment = reddit_pb2.Comment(
                    id=int(row[0]),
                    body=row[1],
                    score=int(row[2]),
                    state=int(row[3]),
                    date=row[4],
                    user=user1,
                    post_id=int(row[6]),
                    parent_id=row[7],
                    # comments=depth_two[row[0]]
                )
                response.first_level.append(comment)
            return response
        except Exception as e:
            print(f"Error expanding comment branch: {e}")
            return reddit_pb2.ExpandCommentBranchResponse()
    
    ## Extra Credit
    # Monitor updates - client initiates the call with a post, with ability to add comment IDs later in a stream.
    def MonitorUpdates(self, request_iterator, context):
        for request in request_iterator:
            if request.post_id:
                post_id = request.post_id
                post_score = self.fetch_post_score(post_id)
                yield reddit_pb2.MonitorUpdatesResponse(id=post_id, score=post_score)
            if request.comment_ids:
                comment_ids = request.comment_ids
                for comment_id in comment_ids:
                    comment_score = self.fetch_comment_score(comment_id)
                    yield reddit_pb2.MonitorUpdatesResponse(id=comment_id, score=comment_score)

    def fetch_post_score(self, post_id):
        try:
            score = self.query_db("SELECT score FROM posts WHERE id = ?", (post_id,))
            return score[0]
        except Exception as e:
            print(f"Error retrieving post score: {e}")
            return 0
    
    def fetch_comment_score(self, id):
        try:
            score = self.query_db("SELECT score FROM comments WHERE id = ?", (id,))
            return score[0]
        except Exception as e:
            print(f"Error retrieving comment scores: {e}")
            return 0
