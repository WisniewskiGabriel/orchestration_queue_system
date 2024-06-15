from flask import Blueprint, request, jsonify
from models import Queue, Task
from schemas import QueueSchema, TaskSchema
from database import db
from datetime import datetime, timezone

api = Blueprint('api', __name__)

queue_schema = QueueSchema()
queues_schema = QueueSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@api.route('/queues', methods=['POST'])
def create_queue():
    name = request.json.get('name')
    max_retry_count = request.json.get('max_retry_count')
    new_queue = Queue(name=name, max_retry_count=max_retry_count, creation_date=datetime.now(timezone.utc))
    db.session.add(new_queue)
    db.session.commit()
    return jsonify(queue_schema.dump(new_queue)), 201


@api.route('/queues/<int:queue_id>/tasks', methods=['POST'])
def create_task(queue_id):
    reference = request.json.get('reference')
    specific_data = request.json.get('specific_data')
    priority = request.json.get('priority', 'low')
    new_task = Task(queue_id=queue_id, reference=reference, specific_data=specific_data, priority=priority,
                    creation_date=datetime.now(timezone.utc))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(task_schema.dump(new_task)), 201


@api.route('/queues/<int:queue_id>/tasks/next', methods=['GET'])
def get_next_task(queue_id):
    task = Task.query.filter_by(queue_id=queue_id, status='new').order_by(Task.priority.desc(),
                                                                          Task.creation_date).first()
    if task:
        task.status = 'in progress'
        task.start_transaction_date = datetime.now(timezone.utc)
        db.session.commit()
    return jsonify(task_schema.dump(task)) if task else jsonify({"message": "No tasks available"}), 200


@api.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    status = request.json.get('status')
    failure_reason = request.json.get('failure_reason')
    failure_type = request.json.get('failure_type')
    task.status = status
    task.ending_date = datetime.now(timezone.utc)
    if status == 'failed':
        task.failure_reason = failure_reason
        task.failure_type = failure_type
        if failure_type == 'system' and task.retry_count < Queue.query.get(task.queue_id).max_retry_count:
            retry_task = Task(queue_id=task.queue_id, reference=task.reference, specific_data=task.specific_data,
                              priority=task.priority, creation_date=datetime.now(timezone.utc))
            db.session.add(retry_task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 200


@api.route('/queues/<int:queue_id>/tasks', methods=['GET'])
def view_tasks(queue_id):
    tasks = Task.query.filter_by(queue_id=queue_id).all()
    return jsonify(tasks_schema.dump(tasks)), 200


@api.route('/tasks/<int:task_id>/retry', methods=['POST'])
def retry_failed_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == 'failed':
        retry_task = Task(queue_id=task.queue_id, reference=task.reference, specific_data=task.specific_data,
                          priority=task.priority, creation_date=datetime.now(timezone.utc))
        db.session.add(retry_task)
        db.session.commit()
        return jsonify(task_schema.dump(retry_task)), 201
    return jsonify({"message": "Task is not in a failed state"}), 400
