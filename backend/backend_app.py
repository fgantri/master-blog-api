from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

def get_id():
    """
    Generates a unique identifier for a new blog post.

    The function calculates the next available ID by finding the
    maximum existing ID among all blog posts in the POSTS list
    and adding 1.

    Returns:
        int: The next unique blog post ID.
    """
    try:
        new_id = max(post["id"] for post in POSTS) + 1
    except ValueError:
        new_id = 0
    return new_id


def validate_required_fields(request_body, required_fields):
    """
    Validates the presence of required fields in a request body.

    Iterates through a list of required fields and checks if each field
    is present in the provided request body. If any required field is missing,
    it returns an error response with a 400 status code.

    Args:
        request_body (dict): The body of the request to validate.
        required_fields (list): A list of field names that are required.

    Returns:
        tuple: A JSON response with an error message and a 400 status code
               if a required field is missing, or None if all fields are present.
    """
    missing_fields = []
    for field in required_fields:
        if field not in request_body:
            missing_fields.append(field)
    n = len(missing_fields)
    if n > 0:
        error_msg = f"{', '.join(missing_fields)} fields are required!"
        if n == 1:
            error_msg = f"{missing_fields[0]} is required!"
        return jsonify({"error": error_msg}), 400
    return None


@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    """
    Handles HTTP requests for managing blog posts.

    This route supports both GET and POST methods:

    - **GET**: Returns a list of all blog posts.
    - **POST**: Adds a new blog post. The request body must include
      "title" and "content" fields. If any required field is missing,
      an error response is returned with a 400 status code. If the post
      is successfully created, it is added to the `POSTS` list, and a
      JSON response with the newly created post and a 201 status code
      is returned.

    Returns:
        - For GET: JSON response containing all blog posts.
        - For POST:
          - If successful, a JSON response with the new post and a
            201 status code.
          - If validation fails, a JSON error message with a 400 status code.
    """
    if request.method == 'POST':
        req_body = request.get_json()
        error = validate_required_fields(req_body, ["title", "content"])
        if error:
            return error
        new_post = {
            "id": get_id(),
            "title": req_body["title"],
            "content": req_body["content"]
        }
        POSTS.append(new_post)
        return jsonify(new_post), 201
    return jsonify(POSTS)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def handle_post(post_id):
    """
    Deletes a post by its ID from the global POSTS list.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response:
            - 200 with a success message if the post is deleted.
            - 404 with an error message if the post is not found.
    """
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)
    if post_to_delete:
        POSTS.remove(post_to_delete)
        return jsonify({
            "message": f"Post with id {post_id} has been deleted successfully."
        }), 200
    return jsonify({"error": f"Post with id {post_id} doesn't exist."}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
