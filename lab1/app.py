from flask import Flask, render_template, request, redirect, url_for
from uuid import uuid4
import lab1lib as lab1

app = Flask(__name__)

'''
Chat Interface Application
--------------------------
This module provides a Flask-based web interface for interacting with 
the lab1lib chat processing library.
'''

# home route
@app.route("/")
def index():
    '''
    Renders the main chat interface.
    
    If no chat_id is provided in the URL parameters, generates a new 
    UUID and redirects to initialize a fresh session.
    '''
    chat_id = request.args.get("chat_id")
    temp = request.args.get("temperature")
    top_p = request.args.get("top_p")
    max_tokens = request.args.get("max_tokens")
    if chat_id is None:
        return redirect(url_for("index", chat_id=uuid4()))
    return render_template('form.html', chat_id=chat_id, temperature=temp, top_p=top_p, max_tokens=max_tokens, results=lab1.get_chat_html(chat_id))


@app.route("/submit", methods=["POST"])
def submit():
    # retrieve form data for chat_id and user
    chat_id = request.form.get("chat_id")
    user_message = request.form.get("user")
    temp = request.form.get("temperature")
    top_p = request.form.get("top_p")
    max_tokens = request.form.get("max_tokens")
    
    # retrieve LLM parameters, cast to float and create dictionary
    config = {}
    for key, value in request.form.items():
        if key in [ 'temperature', 'top_p', 'max_tokens' ] and value:
            config[key] = float(value)
    # debugging output
    print(f"Received message: {user_message}")
    print(f"Recieved config: {config}")
    
    # pass chat to lab1lib for processing
    lab1.chat(chat_id, user_message, config)
    return redirect(url_for('index', chat_id=chat_id, temperature=temp, top_p=top_p, max_tokens=max_tokens, status='success'))

if __name__ == "__main__":
    app.run(debug=True)