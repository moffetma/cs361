from flask import render_template, flash, redirect, url_for, request
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ProjectForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Project
from werkzeug.urls import url_parse

@app.route('/login', methods =['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
    	user = User.query.filter_by(username=form.username.data).first()
    	if user is None or not user.check_password(form.password.data):
    		flash('Wrong username or password')
    		return redirect(url_for('login'))
    	login_user(user, remember=form.remember_me.data)
    	next_page = request.args.get('next')
    	if not next_page or url_parse(next_page).netloc != '':
    		next_page = url_for('index')
    	return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Max'}

    posts = [

    {	'author': {'username': 'Lonnie'},
    	'body': 'Looks good, we just need one more team member'

    },

    {
    	'author': {'username': 'Keane'},
    	'body': 'Agree, we can stick them with the registration page :)'
    }
    ]

    return render_template('index.html', title='Home', posts=posts)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
	{'author': user, 'body': 'Post #1'},
	{'author': user, 'body': 'Post #2'}
	]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data 
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.project_title.data, body=form.project.data, owner=current_user)
        db.session.add(project)
        db.session.commit()
        flash('Your project has been created')
        return redirect(url_for('index'))
    return render_template('create_project.html', title='Create Project', form=form)

@app.route('/list_projects')
@login_required 
def list_projects():
    projects = Project.query.all()
    return render_template('list_projects.html', title='Projects', projects=projects)

@app.route('/project_details/<proj>')
@login_required
def project_details(proj):
    project = Project.query.get(proj)
    user = User.query.get(project.user_id)
    return render_template('project_details.html', title='Project Details', project=project, user=user)