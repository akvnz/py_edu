from flask import render_template, redirect, url_for, request
from app import app, db
from app.forms import ShortenerForm
from app.models import Link
import short_url


@app.route('/result', methods=['GET', 'POST'])
def result():
    original_url = request.args.get('original_url')
    link = Link(original_url=original_url)
    db.session.add(link)
    db.session.commit()
    param = short_url.encode_url(link.id)
    shortened_url = "{}{}".format(
        request.url_root,
        param
    )

    link.short_url = shortened_url
    db.session.commit()

    return render_template('result.html',  title='Result', short_url=shortened_url)


@app.route('/', defaults={'shorl_url_code': None}, methods=['GET', 'POST'])
@app.route('/<shorl_url_code>', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(shorl_url_code=None):
    if shorl_url_code is not None:
        link = Link.query.get(str(short_url.decode_url(shorl_url_code)))
        if link is not None:
            return redirect(link.original_url)

    form = ShortenerForm()
    if form.validate_on_submit():
        return redirect(url_for('result', original_url=form.original_url.data))
    return render_template('index.html',  title='Shortener', form=form)
