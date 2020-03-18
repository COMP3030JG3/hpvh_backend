import os
from core import app
from flask import Flask, send_file, jsonify

@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, 'index.html')
    
    return send_file(index_path)

# Route React App
@app.route('/<path:path>')
def route_frontend(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        return send_file(index_path)
