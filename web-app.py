from flask import Flask, flash,url_for, redirect, render_template, request, session, abort

import os
#from flask_bootstrap import bootstrap
app = Flask(__name__, static_folder='static', template_folder='templates')
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/head.html')
def head_html():
    subject = request.args.get('subject')
    return render_template('head.html', subject=subject)

@app.route('/pricemap.html')
def pricemap_html():
    return render_template('pricemap.html')

@app.route('/adspool.html')
def adspool_html():
    return render_template('adspool.html')

@app.route('/newoutput')
def newoutput():
    return render_template('newoutput.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True)
