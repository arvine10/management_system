from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, IntegerField, PasswordField)
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3




basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_BINDS'] = {
    'landlord': 'sqlite:///'+os.path.join(basedir, 'landlord.sqlite'),
    'renter': 'sqlite:///'+os.path.join(basedir, 'renter.sqlite')
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MainDB(db.Model):
    '''This is our main database. It stores the information for all pages
    on our site. This includes addresses, repairs, tasks, renters, etc.'''
    __tablename__="MainDB"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String)
    amount_owed = db.Column(db.Integer)
    paid = db.Column(db.Integer)
    phone = db.Column(db.String)
    rent = db.Column(db.Integer)
    repairs = db.Column(db.String)
    task_date = db.Column(db.String)
    tasks = db.Column(db.String)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    renter_phone = db.Column(db.String)
    email = db.Column(db.String)

    def __init__(self, address, amount_owed, paid, phone, rent,
                repairs, task_date, tasks, firstName, lastName,
                renter_phone, email):
        self.address = address
        self.amount_owed = amount_owed
        self.paid = paid
        self.phone = phone
        self.rent = rent
        self.repairs = repairs
        self.task_date = task_date
        self.tasks = tasks
        self.firstName = firstName
        self.lastName = lastName
        self.renter_phone = renter_phone
        self.email = email

class Landlord(db.Model):
    '''This stores the login information for landlords'''
    __bind_key__ = 'landlord'
    __tablename__ = 'landlord'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Renter(db.Model):
    '''This stores the login information for renters'''
    __bind_key__ = 'renter'
    __tablename__ = 'renter'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class LandlordLoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit_landlord = SubmitField('Submit Landlord')

class RenterLoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    submit_renter = SubmitField('Submit Renter')

class InfoForm(FlaskForm):
    address = StringField('Enter the address: ', validators=[DataRequired()])
    amount_owed = IntegerField('Enter the amount owed: ', validators=[DataRequired()])
    paid = IntegerField('Enter the amount paid: ', validators=[DataRequired()])
    phone = StringField('Enter the landlord phone number: ', validators=[DataRequired()])
    rent = IntegerField('Enter rent: ', validators=[DataRequired()])
    repairs = StringField('Enter the repairs: ', validators=[DataRequired()])
    task_date = StringField('Enter the task date: ', validators=[DataRequired()])
    tasks = StringField('Enter the tasks: ', validators=[DataRequired()])
    firstName = StringField('Enter renters first name: ', validators=[DataRequired()])
    lastName = StringField('Enter renters last name: ', validators=[DataRequired()])
    renter_phone = StringField('Enter the renters phone number: ', validators=[DataRequired()])
    email = StringField('Enter renters email: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    id = IntegerField('Enter the ID of propery to delete:', validators=[DataRequired()])
    delete = SubmitField('Delete')

@app.route('/', methods=['GET', 'POST'])
def index():
    landlord_form = LandlordLoginForm(prefix="landlord_form")
    renter_form = RenterLoginForm(prefix="renter_form")

    if landlord_form.submit_landlord.data and landlord_form.validate_on_submit():
        landlord = Landlord.query.filter_by(username=landlord_form.username.data).first()
        if landlord:
            if landlord.password == landlord_form.password.data:
                return redirect(url_for('landlord'))
        flash('Invalid landlord username and/or password. Try again or register.')

    if renter_form.submit_renter.data and renter_form.validate_on_submit():
        renter = Renter.query.filter_by(username=renter_form.username.data).first()
        if renter:
            if renter.password == renter_form.password.data:
                return redirect(url_for('renter'))
        flash('Invalid renter username and/or password. Try again or register.')

    return render_template('index.html', landlord_form=landlord_form, renter_form=renter_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    landlord_form = LandlordLoginForm(prefix="landlord_form")
    renter_form = RenterLoginForm(prefix="renter_form")

    if landlord_form.submit_landlord.data and landlord_form.validate_on_submit():
        new_data = Landlord(landlord_form.username.data, landlord_form.password.data)
        db.session.add(new_data)
        db.session.commit()

    if renter_form.submit_renter.data and renter_form.validate_on_submit():
        new_data = Renter(renter_form.username.data, renter_form.password.data)
        db.session.add(new_data)
        db.session.commit()

    return render_template('register.html', landlord_form=landlord_form, renter_form=renter_form)

@app.route('/landlord')
def landlord():
    return render_template('landlord.html')

@app.route('/renter',methods=['GET', 'POST'])
def renter():
    info_form = InfoForm(prefix="info_form")
    main_data = MainDB.query.all()
    if info_form.submit.data:
        firstName = info_form.firstName.data
        lastName = info_form.lastName.data
        repairInfo = info_form.repairs.data
        for i in range(len(main_data)):
            tenet = MainDB.query.get(i+1)
            f_name = tenet.firstName
            l_name = tenet.lastName
            if f_name == firstName and l_name == lastName:
                tenet.repairs = repairInfo
                
                db.session.commit()
                break
    return render_template('renter.html', info_form=info_form, main_data=main_data)

@app.route('/repairs')
def repairs():
    repair_data = db.session.query(MainDB.address, MainDB.phone, MainDB.repairs)
    return render_template('repairs.html', repair_data=repair_data)

@app.route('/mainDB', methods=['GET', 'POST'])
def mainDB():
        '''
        Because there is more than one form on this page, we must add a prefix and check for the prefix
        so the validate_on_submit function does not submit more than one form at a time.
        '''
        info_form = InfoForm(prefix="info_form")
        delete_form = DeleteForm(prefix="delete_form")
        if info_form.submit.data and info_form.validate_on_submit():
            new_data = MainDB(info_form.address.data, info_form.amount_owed.data, info_form.paid.data, info_form.phone.data,
                              info_form.rent.data, info_form.repairs.data, info_form.task_date.data, info_form.tasks.data,
                              info_form.firstName.data, info_form.lastName.data, info_form.renter_phone.data, info_form.email.data)
            db.session.add(new_data)
            db.session.commit()

        if delete_form.delete.data and delete_form.validate_on_submit():
            delete_maindb_id = MainDB.query.get(delete_form.id.data)
            if delete_maindb_id != None:

                num_list = []
                db.session.delete(delete_maindb_id)
                db.session.commit()
                # Reset id column after deletion
                for i in range(len(MainDB.query.all())):
                    num_list.append(i+1)

                main_data = MainDB.query.all()
                j = 1
                for main in main_data:
                    main.id = j
                    
                    db.session.commit()
                    j += 1
                    print(main.id)

        main_data = MainDB.query.all()
        return render_template('mainDB.html', info_form=info_form, delete_form=delete_form, main_data=main_data)

@app.route('/tasks')
def tasks():
    main_data = db.session.query(MainDB.firstName, MainDB.lastName, MainDB.address, MainDB.tasks, MainDB.task_date)
    return render_template('tasks.html', main_data=main_data)

@app.route('/payments')
def payments():
    return render_template('payments.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
