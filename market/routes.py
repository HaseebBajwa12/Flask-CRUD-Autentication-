from flask_login import login_user, logout_user, login_required

from market import app
from flask import Flask, render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm
from market import db


# @app.route('/')
# def hello_world():
#     return 'hellow world'


#
# @app.route('/about')
# def about_pages():
#     return "<h1>this is about page</h1>"
#
#
# @app.route('/about/<username>')
# def about_page(username):
#     return f"<h1> this is about page of  {username}</h1>"


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        # flash(f'Account created successfully.Now you are logged in as a{user_to_create.username}', category='success')
        return redirect(url_for('login_page'))
    if form.errors != {}:  # If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    if request.method == 'GET':
        users = User.query.all()

    return render_template('market.html', items=items, users=users)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('you have been logged out', category='info')
    return redirect(url_for('home_page'))


@app.route('/insert', methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        barcode = request.form['barcode']
        description = request.form['description']
        owner = request.form.get('owner')
        my_items = Item(name=name, price=price, barcode=barcode, description=description, owner=owner)
        db.session.add(my_items)
        db.session.commit()
        return redirect(url_for('market_page'))


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('market_page'))


@app.route('/update/', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        item = Item.query.get(request.form.get('id'))
        item.name = request.form['name']
        item.price = request.form['price']
        item.barcode = request.form['barcode']
        item.description = request.form['description']
        db.session.commit()
        return redirect(url_for('market_page'))
