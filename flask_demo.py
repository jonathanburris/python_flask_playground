from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'Hello World'

def main():
    app.run(debug=true)

if __name__ == '__main__':
    main()