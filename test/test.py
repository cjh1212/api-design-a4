import unittest
from unittest.mock import Mock
import sys
sys.path.append("../")

import client.client as client
import src.high_level as high_level

class TestApiFunc(unittest.TestCase):

    
    def test_api_func(self):
        mock_client = Mock(spec=client.RedditClient)
        

        # setting up mock responses
        mock_post_response = client.reddit_pb2.GetPostResponse(
            post=client.reddit_pb2.Post(
                id=1, 
                title="Post Title", 
                body="Post Body", 
                url="http://example.com", 
                score=1, 
                state=0, 
                date="12/02/2023", 
                user_id=1,
                subreddit_id = 1
            )
        )

        # comment that is under the most upvoted comment

        mock_comments_response = client.reddit_pb2.GetMostUpvotedNCommentsResponse(
            comments=[
                client.reddit_pb2.Comment(
                    id=1,
                    body="body1",
                    score=2,
                    state=0,
                    date="12/02/2023",
                    user=client.reddit_pb2.User(id=1, username="user"),
                    post_id=1,
                    parent_id=None
                )
            ]
        )

        mock_expand_response = client.reddit_pb2.ExpandCommentBranchResponse(
            first_level=[
                client.reddit_pb2.Comment(
                    id=2,
                    body="body2",
                    score=1,
                    state=0,
                    date="12/02/2023",
                    user=client.reddit_pb2.User(id=1, username="user"),
                    post_id=1,
                    parent_id=1
                )
            ],
            second_level=[
                client.reddit_pb2.Comment(
                    id=3,
                    body="body3",
                    score=1,
                    state=0,
                    date="12/02/2023",
                    user=client.reddit_pb2.User(id=1, username="user"),
                    post_id=1,
                    parent_id=2
                )
            ]
        )

        # mock return values
        mock_client.get_post.return_value = mock_post_response
        mock_client.get_most_upvoted_comments.return_value = mock_comments_response
        mock_client.expand_comment_branch.return_value = mock_expand_response

        # call the function
        result = high_level.api_func(mock_client, 1)

        # assert the result - check the unique id if it matches expected
        self.assertEqual(result.id, 2)

        # verify methods called
        mock_client.get_post.assert_called_once_with(1)
        mock_client.get_most_upvoted_comments.assert_called_once_with(1, 1)
        mock_client.expand_comment_branch.assert_called_once_with(1, 1)

if __name__ == "__main__":
    unittest.main()