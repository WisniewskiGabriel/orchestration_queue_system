from datetime import datetime, timezone
from database import db


class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    max_retry_count = db.Column(db.Integer, nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'), nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    start_transaction_date = db.Column(db.DateTime)
    ending_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='new')  # 'new', 'in progress', 'success', 'failed'
    specific_data = db.Column(db.JSON)
    failure_reason = db.Column(db.String(255))
    priority = db.Column(db.String(20), nullable=False, default='low')  # 'low', 'medium', 'high', 'critical'
    retry_count = db.Column(db.Integer, default=0)
    failure_type = db.Column(db.String(20))  # 'system', 'business'
