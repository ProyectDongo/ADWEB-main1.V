from django.apps import AppConfig
from flask import Flask, redirect, url_for, session



class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WEB'
app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for(''))

if __name__ == '__main__':
    app.run(debug=True)