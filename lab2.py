from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)
api = Api(app)

# In-memory database for tasks
task_db = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]

# Parser for task input
parser = reqparse.RequestParser()
parser.add_argument('task_title', type=str, required=True, help="Task title cannot be blank")
parser.add_argument('task_desc', type=str, required=True, help="Task description cannot be blank")
parser.add_argument('is_finished', type=bool)

# Resource for Task
class Task(Resource):
    def get(self, task_id):
        """Get a task by its ID
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: The ID of the task
        responses:
          200:
            description: A task object
          404:
            description: Task not found
        """
        task = next((task for task in task_db if task["task_id"] == task_id), None)
        if task:
            return task, 200
        return {"error": "Task not found"}, 404

    def patch(self, task_id):
        """Update a task by its ID
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: The ID of the task
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_title:
                  type: string
                task_desc:
                  type: string
                is_finished:
                  type: boolean
        responses:
          200:
            description: Task updated
          404:
            description: Task not found
        """
        task = next((task for task in task_db if task["task_id"] == task_id), None)
        if not task:
            return {"error": "Task not found"}, 404

        args = parser.parse_args()
        task["task_title"] = args["task_title"] if args["task_title"] is not None else task["task_title"]
        task["task_desc"] = args["task_desc"] if args["task_desc"] is not None else task["task_desc"]
        task["is_finished"] = args["is_finished"] if args["is_finished"] is not None else task["is_finished"]

        return {"status": "ok", "task": task}, 200

    def delete(self, task_id):
        """Delete a task by its ID
        ---
        parameters:
          - name: task_id
            in: path
            type: integer
            required: true
            description: The ID of the task
        responses:
          200:
            description: Task deleted
          404:
            description: Task not found
        """
        global task_db
        task = next((task for task in task_db if task["task_id"] == task_id), None)
        if not task:
            return {"error": "Task not found"}, 404

        task_db = [t for t in task_db if t["task_id"] != task_id]
        return {"status": "ok"}, 200

class TaskList(Resource):
    def get(self):
        """Get the list of tasks
        ---
        responses:
          200:
            description: A list of tasks
        """
        return task_db, 200

    def post(self):
        """Create a new task
        ---
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                task_title:
                  type: string
                task_desc:
                  type: string
        responses:
          201:
            description: Task created
        """
        args = parser.parse_args()
        new_task_id = max(task["task_id"] for task in task_db) + 1 if task_db else 1
        new_task = {
            "task_id": new_task_id,
            "task_title": args["task_title"],
            "task_desc": args["task_desc"],
            "is_finished": False
        }
        task_db.append(new_task)
        return {"status": "ok", "task": new_task}, 201

# Setting up routes
api.add_resource(TaskList, '/tasks')
api.add_resource(Task, '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)
