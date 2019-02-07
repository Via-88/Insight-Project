from flask import Flask, flash,url_for, redirect, render_template, request, session, abort

import os
#from flask_bootstrap import bootstrap
app = Flask(__name__)
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/send')
def send():
    subject = request.args.get('subject')
    output = 'condition, size, color'
    return render_template(
            'send.html',
            subject = subject,
            output = output)

@app.route('/output')
def output():
    subject = request.args.get('subject')
    return render_template(
            'output.html',
            subject = subject
            )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True)
