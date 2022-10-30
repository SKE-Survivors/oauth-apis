from flask import Blueprint, request
from flask_cors import CORS, cross_origin
from handler import DatabaseHandler
from utils import build_response, encode_pwd

user_endpoint = Blueprint('user', __name__)
CORS(user_endpoint)

dbh = DatabaseHandler()

# todo: check login session (aka call /auth/check before)


@user_endpoint.route('/')
def index():
    return 'user ok!'


@user_endpoint.route("/profile", methods=['GET', 'PUT', 'DELETE'])
@cross_origin()
def user():
    mail = request.args.get("mail")
    if not mail:
        body = {'STATUS': 'FAILED', 'MESSAGE': 'Missing argument'}
        return build_response(status_code=400, body=body)

    if not dbh.find_user(mail):
        body = {"STATUS": "FAILED", "MESSAGE": f"User does not exist"}
        return build_response(status_code=400, body=body)

    if request.method == "GET":
        user = dbh.find_user(mail=mail)
        email = user.email
        username = user.username
        lesson = user.unlocked_lesson
        story = user.unlocked_story
        bag = user.bag
        body = {
            "STATUS":
            "SUCCESS",
            "userInfo": [{
                "mail": email,
                "username": username,
                "unlocked_lesson": lesson,
                "unlocked_story": story,
                "bag": bag
            }],
        }

    # todo: add confirm-password field
    if request.method == "PUT":
        data = request.json
        if not data:
            body = {'STATUS': 'FAILED', 'MESSAGE': 'Missing body'}
            return build_response(status_code=400, body=body)

        for key in data:
            if key != "username" and key != "password":
                return build_response(
                    status_code=400,
                    body={
                        'STATUS': 'FAILED',
                        'MESSAGE': 'INCORRECT BODY'
                    },
                )
            if key == "password":
                data[key] = encode_pwd(data[key])

        dbh.update_profile(mail, **data)
        body = {"STATUS": "SUCCESS", "MESSAGE": f"UPDATE USER {mail}"}

    if request.method == "DELETE":
        dbh.delete_user(mail=mail)
        body = {"STATUS": "SUCCESS", "MESSAGE": f"DELETE USER {mail}"}

    return build_response(status_code=201, body=body)