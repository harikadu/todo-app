from flask import Flask ,render_template, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://harikaduyu@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    def ___repr__(self):
        return f'<Todo {self.id} {self.description}'

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False)
    todos = db.relationship('Todo', backref= 'list', lazy = True)

#db.create_all()

@app.route('/')
def index():
    return render_template('index.html', data = Todo.query.order_by('id').all() )

@app.route('/todos/create', methods=['POST'])
def create():
    error = False
    body = {}
    try:
        text = request.get_json()['description']
        new_todo = Todo(description = text)
        db.session.add(new_todo)
        body['description'] = new_todo.description
        db.session.commit()
        body['id'] = new_todo.id
        body['completed'] = new_todo.completed
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo_item(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

    