#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_httpauth import HTTPBasicAuth
import jsonpickle

# Object Model
class Task(object):
	def __init__(self, id, title, done):
		self.id = id
		self.title = title
		self.done = done

	def to_json(self, unpicklable):
		return jsonpickle.encode(self, unpicklable=unpicklable)


app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    'jb': 'P@55word'
}

tasks = []


@auth.get_password
def get_password(username):
    if username in users:
        return users.get(username)
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


@app.route('/')
@app.route('/index')
@app.route('/api/v1.0')
def index():
	return 'My api'


@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
	return jsonpickle.encode(tasks, unpicklable=False)


@app.route('/api/v1.0/tasks/<int:id>', methods=['GET'])
def get_task(id):
	task = [task for task in tasks if task.id == id]
	if len(task) == 0:
		abort(404)
	return task[0].to_json(False)


@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    id = tasks[-1]['id'] + 1
    title = request.json['title']
    task = Task(id, title, False)
    tasks.append(task)
    return task.to_json(False), 201


@app.route('/todo/api/v1.0/tasks/<int:id>', methods=['PUT'])
@auth.login_required
def update_task(id):
    task = [task for task in tasks if task.id == id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task.title = request.json.get('title', task[0]['title'])
    task.done = request.json.get('done', task[0]['done'])
    return task.to_json(False)


@app.route('/api/v1.0/tasks/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_task(id):
    task = [task for task in tasks if task.id == id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify( { 'result': True } )


def create_tasks():
	task = Task(1, 'Buy groceries', False)
	tasks.append(task)
	task = Task(2, 'Schedule trip', False)
	tasks.append(task)
	task = Task(3, 'Pickup kids', False)
	tasks.append(task)


def main():
	create_tasks()
	app.run(debug=True)


if __name__ == '__main__':
    main()