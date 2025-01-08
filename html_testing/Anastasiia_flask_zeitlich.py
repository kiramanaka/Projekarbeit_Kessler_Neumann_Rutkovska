from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.datetime.now()
    if now.hour >= 6 and now.hour < 12:
        greeting = 'Guten Morgen'
    elif now.hour >= 12 and now.hour < 18:
        greeting = 'Guten Tag'
    elif now.hour >= 18 and now.hour < 24:
        greeting = 'Guten Abend'
    else: 'Guten Nacht'
    return render_template('index.html', greeting=greeting)

if __name__ == '__main__':
    app.run(debug=True)