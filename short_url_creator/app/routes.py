from flask import render_template, redirect, url_for, request
from app import app, db, redis
from app.forms import ShortenerForm
import uuid


@app.route('/result', methods=['GET', 'POST'])
def result():
    original_url = request.args.get('original_url')
    short_url_code = uuid.uuid4().hex
    shortened_url = "{}{}".format(request.url_root, short_url_code)
    redis.set(short_url_code, original_url, ex=2592000)

    return render_template('result.html',  title='Result', short_url=shortened_url)


@app.route('/', defaults={'shorl_url_code': None}, methods=['GET', 'POST'])
@app.route('/<short_url_code>', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(short_url_code=None):
    if short_url_code is not None \
            and short_url_code != 'index'\
            and short_url_code != 'favicon.ico':
        link = redis.get(short_url_code)
        if link is not None:
            return redirect(link)

    form = ShortenerForm()
    if form.validate_on_submit():
        return redirect(url_for('result', original_url=form.original_url.data))
    return render_template('index.html',  title='Shortener', form=form)
