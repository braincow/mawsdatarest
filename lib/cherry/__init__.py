import cherrypy
import json
import uuid
from mongoengine import Q
from passlib.hash import pbkdf2_sha256

from lib.rest import rest_response_json
from lib.db.documents import MAWSAPIUser, MAWSAPIAuthRealm

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(rest_response_json(version=1, payload=error))

# helper utility for verifying username + password for a realm from database
def basic_password_helper(rlm, user, passwd):
	realms = MAWSAPIAuthRealm.objects(name=rlm)
	if not realms:
		# no such realm exists
		return False
	realm = realms[0]
	user_objects = MAWSAPIUser.objects(Q(realms__in = [realm]) & Q(username = user))
	if not user_objects:
		# no such user in db or not in such realm so no need to verify pwd
		return False
	user_object = user_objects[0]
	#@NOTE: to hash a new password, use: pbkdf2_sha256.encrypt(password, rounds=cherrypy.config.get("password.rounds"), salt_size=cherrypy.config.get("password.salt_size"))
	return pbkdf2_sha256.verify(passwd, user_object.password)

# eof
