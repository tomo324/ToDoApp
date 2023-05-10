from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)
# LoginManagerをインスタンス化
login_manager = LoginManager()
# Flaskアプリと紐づけ
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

@app.route('/index', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        user = current_user
        username = user.username
        #現在ログインしているユーザーが投稿したポストをすべて取得し、日付順に並び替える
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.due).all()
        return render_template('index.html', posts=posts, today=date.today(), username=username)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('create.html')
    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')
        due = datetime.strptime(due, '%Y-%m-%d')
        user_id = current_user.id
        new_post = Post(title=title, detail=detail, due=due, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/index')

@app.route('/detail/<int:id>')
@login_required
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        #アクセスされたらそのページを返す
        return render_template('update.html', post=post)
    else:
        # 変更内容を反映する
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')
        
        # 反映した内容をdbに渡す
        db.session.commit()
        return redirect('/index')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/index')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            # Userのインスタンスを生成
            user = User(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return "<script>alert('This user name is already in use');window.location.href='/signup'</script>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            # Userテーブルからusernameに一致するユーザーを取得
            user = User.query.filter_by(username=username).first()
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/index')
            else:
                return "<script>alert('Incorrect user name or password');window.location.href='/login'</script>"
        except:
            return "<script>alert('Incorrect user name or password');window.location.href='/login'</script>"

@app.route('/', methods=['GET'])
def top():
    if request.method == 'GET':
        return render_template('top.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



if __name__ == "__main__":
    app.run()