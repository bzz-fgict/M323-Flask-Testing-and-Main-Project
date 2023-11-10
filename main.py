from flask import Flask, render_template, request, redirect, url_for
from data.access import user_dao, post_dao
from flask_login import LoginManager

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def Home():
    return 'Base Page'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = user_dao.get_user_by_username(data['username'])
    if user and user.password == data['password']:
        login_user(user)
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True}), 200



if __name__ == '__main__':
    app.run(debug=True)



