import html
from flask import Flask, request, make_response, redirect, render_template, Response, jsonify
from database import user_login
from userClass import User
import mimetypes, hashlib
from postClass import PostHandler
import json

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/javascript', '.js')

app = Flask(__name__, template_folder='public')


# * -------------------------- GET REQUESTS ------------------------------

@app.route("/", methods=["GET"])
@app.route("/public/index.html", methods=["GET"])
def home():
    if "authToken" not in request.cookies:
        return redirect("/authenticate", code=302)
    else:
        token = request.cookies["authToken"].encode()
        h = hashlib.new('sha256')
        h.update(token)
        hashToken = h.hexdigest()

        find_user = user_login.find({"authHash": hashToken})
        if not find_user:
            return redirect("/authenticate", code=302)
        posts = PostHandler()
        posts.db.collection.drop()
        posts.db.id_collection.drop()
        print(posts.get_all_posts_sorted_by_id)
        return Response(render_template("/index.html", posts=posts.get_all_posts_sorted_by_id()), status="200",
                        headers=[("X-Content-Type-Options", "nosniff")])


@app.route("/public/favicon.ico", methods=["GET"])
def icon():
    with open("/public/favicon.ico", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "image/x-icon"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/app.js", methods=["GET"])
def javascriptCode():
    with open("/public/app.js", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "text/javascript"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/authenticate.html", methods=["GET"])
def authenticateHTML():
    with open("/public/authenticate.html", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes,
                          [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/authenticate", methods=["GET"])
def authenticate():
    readBytes = render_template("/authenticate.html", error="")
    return make_response((readBytes,
                          [("Content-Type", "text/html"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/styles.css", methods=["GET"])
def styles():
    with open("/public/styles.css", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, [("Content-Type", "text/css"), ("X-Content-Type-Options", "nosniff")]))


@app.route("/public/image/readme.jpg", methods=["GET"])
def retrieve_image():  # * retrieve images
    with open("/public/image/readme.jpg", "rb") as file:
        readBytes = file.read()
    return make_response((readBytes, [("Content-Type", "image/jpg"), ("X-Content-Type-Options", "nosniff")]))


@app.errorhandler(404)
def page_not_found(error):
    return make_response((b"Can't find page", "HTTP/1.1 404 Not Found",
                          [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")]))


# * -------------------------------- POST REQUESTS ----------------------------------------

@app.route("/register", methods=["POST"])
def handleSignUp():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        passwordCheck = request.form.get('passwordCheck')

        # TODO: placeholder code

        if password != passwordCheck:
            return Response(render_template("/authenticate.html", error="Passwords are not the same").encode(),
                            status=200, headers=[("X-Content-Type-Options", "nosniff")])
        elif not password and not passwordCheck:
            return Response(
                render_template("/authenticate.html", error="Password and repeated password missing").encode(),
                status=200, headers=[("X-Content-Type-Options", "nosniff")])
        elif not password:
            return Response(render_template("/authenticate.html", error="Password missing").encode(), status=200,
                            headers=[("X-Content-Type-Options", "nosniff")])
        elif not passwordCheck:
            return Response(render_template("/authenticate.html", error="Repeated password missing").encode(),
                            status=200, headers=[("X-Content-Type-Options", "nosniff")])
        else:
            user = User()
            user = user.signup(username, password)

            if user == "Error":
                return Response(b"Error during registration", 400,
                                [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
                # response = make_response((redirect("/", code=302), [("X-Content-Type-Options", "nosniff")]))
            else:
                return Response(b"User Registered", "200 OK",
                                [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/login", methods=["POST"])
def handleLogin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # TODO: placeholder code
        authToken = User()
        authToken = authToken.login(username, password)
        if type(authToken) == type(Response):
            # * error occurred
            return Response(b"Invalid username/password", 400,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
        else:

            response = Response(b"", status=302, headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/")])
            response.set_cookie('authToken', authToken, max_age=3600,
                                httponly=True)  # TODO: change "placeholder" to auth token to give user the cookies.

            return response  # * redirect back to homepage
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/logout", methods=["POST"])
def handleLogout():
    if request.method == "POST":
        authToken = request.cookies.get("authToken")
        if authToken:
            user = User()
            user.logout(authToken)

            response = Response(b"", status=302,
                                headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/authenticate")])
            return response

        else:
            return Response(b"Cookie Not Found", 405,
                            [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])
    else:
        return Response(b"Method Not Allowed", 405,
                        [("Content-Type", "text/plain"), ("X-Content-Type-Options", "nosniff")])


@app.route("/", methods=["POST"])
def posts():
    if "authToken" not in request.cookies:
        return redirect("/authenticate", code=302)
    else:
        token = request.cookies["authToken"].encode()
        h = hashlib.new('sha256')
        h.update(token)
        hashToken = h.hexdigest()

        find_user = user_login.find({"authHash": hashToken})
        if not find_user:
            return redirect("/authenticate", code=302)
        else:
            newPost = PostHandler()
            username = user_login.find_one({"authHash": hashToken})
            username = username['username']
            post = html.escape(request.form.get('post'))
            if post != None and post != "":
                newPost.create_post(str(username), str(post))
            return Response(b"", status=302, headers=[("X-Content-Type-Options", "nosniff"), ("Location", "/")])


@app.route("/like", methods=["POST"])
def like_post():
    data = request.json
    postId = data.get('postId')
    username = data.get('username')
    post_handler = PostHandler()
    post = post_handler.collection.find_one({"post_id": postId})
    if post:
        if username in post["likes"]:
            post_handler.unlike_post(postId, username)
            liked = False
        else:
            post_handler.like_post(postId, username)
            liked = True
    else:
        liked = False
    updated_like_count = post_handler.get_likes(postId)
    response_data = {
        "liked": liked,
        "likeCount": updated_like_count
    }
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
