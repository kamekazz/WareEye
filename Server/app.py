from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World from Flask!'


@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json(force=True, silent=True) or {}
    print(f"Received payload: {data}")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
