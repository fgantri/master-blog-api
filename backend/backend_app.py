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
      Optional query parameters:
        - sort: Field to sort by ('title' or 'content')
        - direction: Sort direction ('asc' or 'desc')
    - **POST**: Adds a new blog post. The request body must include
      "title" and "content" fields. If any required field is missing,
      an error response is returned with a 400 status code. If the post
      is successfully created, it is added to the `POSTS` list, and a
      JSON response with the newly created post and a 201 status code
      is returned.

    Returns:
        - For GET: 
          - JSON response containing all blog posts, optionally sorted.
          - 400 if invalid sort parameters are provided.
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
    
    # GET method
    # Get sorting parameters from query string
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction')
    
    # Validate parameters if provided
    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400
    
    if sort_direction and sort_direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid sort direction. Must be 'asc' or 'desc'."}), 400
    
    # If sort parameters are valid, sort the posts
    if sort_field:
        # Create a copy of POSTS to sort
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_field], reverse=(sort_direction == 'desc'))
        return jsonify(sorted_posts)
    
    # If no sorting is requested, return posts in original order
    return jsonify(POSTS)


@app.route('/api/posts/<int:post_id>', methods=['PUT', 'DELETE'])
def handle_post(post_id):
    """
    Handles updating or deleting a post by its ID.

    Depending on the HTTP method, this function either updates the fields
    of an existing post (`PUT`) or deletes the post (`DELETE`) from the
    global POSTS list.

    Args:
        post_id (int): The ID of the post to update or delete.

    Returns:
        Response:
            - `PUT`:
                - 200 with the updated post if successful.
                - 404 if the post is not found.
            - `DELETE`:
                - 200 with a success message if the post is deleted.
                - 404 if the post is not found.
    """
    global POSTS
    selected_post = next((post for post in POSTS if post["id"] == post_id), None)
    if selected_post:
        if request.method == 'PUT':
            valid_updated_fields = {}
            for key in request.get_json():
                if key in ["title", "content"]:
                    valid_updated_fields[key] = request.get_json()[key]
            selected_post.update(valid_updated_fields)
            return jsonify(selected_post), 200
        POSTS.remove(selected_post)
        return jsonify({
            "message": f"Post with id {post_id} has been deleted successfully."
        }), 200
    return jsonify({"error": f"Post with id {post_id} doesn't exist."}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search posts based on title and content query parameters.

    This endpoint allows searching through posts by matching case-insensitive
    substrings in either the title or content fields. If both title and content
    parameters are provided, posts matching either condition will be returned.

    Args:
        title (str, optional): Substring to search for in post titles
        content (str, optional): Substring to search for in post content

    Returns:
        json: List of post dictionaries that match the search criteria. Each post
              contains 'title' and 'content' fields. Returns empty list if no
              matches are found.
    """
    title = request.args.get('title')
    content = request.args.get('content')

    results = []
    for post in POSTS:
        if (title is not None and title.lower() in post['title'].lower() or
                content is not None and content.lower() in post['content'].lower()):
            results.append(post)
    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
