from flask_marshmallow import Marshmallow
from models import Queue, Task

ma = Marshmallow()


class QueueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Queue


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
