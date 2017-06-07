from flask import Flask, request, make_response
from flask_script import Manager

app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent') 
    response = make_response('You\'re browser is <p>{}</p>'.format(user_agent))
    response.set_cookie('answer', '42')
    return response

if __name__ == '__main__':
    manager.run() 
