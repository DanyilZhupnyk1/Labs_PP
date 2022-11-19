from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World 7'

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=50100, threads=1, url_prefix="/api/v1/hello-world-7")