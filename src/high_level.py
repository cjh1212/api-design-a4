# example high level function
import sys
sys.path.append("../")

import client.client as client

def api_func(client, id):

    # retrieve post using post id
    post = client.get_post(id)
    post_id = post.post.id

    # retrieve most upvoted comment under the post -- using 1 as n because we only want the most upvoted comment
    comments = client.get_most_upvoted_comments(post_id, 1)
    
    # expand the most upvoted comment
    most_upvoted_comment_id = comments.comments[0].id
    expanded_comments = client.expand_comment_branch(most_upvoted_comment_id, 1)

    # get most upvoted comment under the most upvoted comment, or none if no comments under the most upvoted comment
    if len(expanded_comments.first_level) > 0:
        result = expanded_comments.first_level[0]
        return result
    else:
        return None


if __name__ == "__main__":
    reddit_client = client.RedditClient("localhost", 50051)
    print(api_func(reddit_client, 1))