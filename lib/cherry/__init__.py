import cherrypy
import json
import uuid
import hashlib
from mongoengine import Q

from lib.rest import rest_response_json
from lib.db.documents import MAWSAPIUser, MAWSAPIAuthRealm

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(rest_response_json(version=1, payload=error))

def _hash_password(password, salt=None):
	# uuid is used to generate a random number
	if not salt:
		salt = uuid.uuid4().hex
	return dict(hash=hashlib.sha256(salt.encode('utf8') + password.encode('utf8')).hexdigest(), salt=salt)

def _verify_user_password(user, password):
	# user object should hold internal_user mongoengine document
	verify_hash = _hash_password(password, user.salt)["hash"]
	stored_hash = user.password
	if stored_hash == verify_hash:
		return True
	return False

# helper utility for fetching username + password combinations for a realm from database
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
	return _verify_user_password(user_object, passwd)

# eof
