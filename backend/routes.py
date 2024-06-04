from flask import jsonify, request

from database import db
from models import Task

from sqlalchemy.exc import SQLAlchemyError


def init_routes(app):

    @app.route('/api/get_tasks')
    def get_tasks():
        tasks = Task.query.all()
        return jsonify([task.to_dict() for task in tasks])

    @app.route('/api/post_task', methods=['POST'])
    def post_task():
        task = Task()
        task.title = request.json['title']
        task.description = request.json['description']
        task.done = False
        db.session.add(task)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({'code': 500, 'message': 'Database error occurred'})
        print(f'Task created: {task}')
        return jsonify({'code': 200, 'message': 'Task created successfully'})

    @app.route('/api/delete_task/<int:ident>', methods=['POST'])
    def delete_task(ident):
        task = Task.query.get(ident)
        if task is None:
            return jsonify({'code': 404, 'message': 'Task not found'})
        db.session.delete(task)
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({'code': 500, 'message': 'Database error occurred'})
        print(f'Task deleted: {task}')
        return jsonify({'code': 200, 'message': 'Task deleted successfully'})

