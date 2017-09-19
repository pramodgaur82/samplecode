import flask
from flask import render_template,flash,redirect, url_for, g, session,request
from app import app, db
from app.models import User, Abstract, Role, Tag
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter,roles_required, current_user
from app.forms import UserInfoForm,EditAbstractForm,AdminUserInfoForm,AdminAbstractForm
from sqlalchemy import and_,not_,desc
import datetime
import pygal
from pygal.style import Style

team_names = ['Elekta','CTF','York Instruments']

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/accommodation')
def accommodation():
    return render_template('accommodation.html')

@app.route('/program')
def program():
    return render_template('program.html')

@app.route('/after_register')
def after_register():
    return render_template('after_register.html')

### TOOLS FOR USER REGISTRATION SELF MANAGEMENT
@app.route('/manage_registration', methods=['GET', 'POST'])
@login_required
def manage_registration():

    # It's a bit ugly to catch 'Other' affiliation here, but this mean not having to overwite
    # any of Flask-User's code for managing users
    # Note - user can ONLY set the temp_custom_affiliation from the register form
    # So this should only happen once
    if current_user.temp_custom_affiliation: 
        current_user.affiliation = current_user.temp_custom_affiliation
        current_user.temp_custom_affiliation = None
        db.session.add(current_user)
        db.session.commit()

    form = UserInfoForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash('Changes saved','success')
        return redirect(url_for('manage_registration'))

    u = User.query.all()
    n_dinner = [x.intends_dinner for x in u].count(True)
    return render_template('manage_registration.html',form=form,n_dinner=n_dinner)

### TOOLS FOR ABSTRACT SELF MANAGEMENT

@app.route('/abstracts', methods=['GET', 'POST'])
@login_required 
def abstracts():

    if request.method == 'POST' and request.form['action'] == 'Add abstract':
        return redirect(url_for('edit_abstract'))

    abstr = Abstract.query.filter(Abstract.author_id == current_user.id).all()

    return render_template('abstracts.html',abstracts=abstr)

@app.route('/edit_abstract', methods=['GET', 'POST'])
@login_required 
def edit_abstract():
    # SCENARIOS
    # - User is starting a new abstract
    # - User is getting an existing abstract
    # - User is submitting an existing abstract
    # - User is submitting a new abstract

    # Make the form
    form = EditAbstractForm()

    # Fetch the abstract, or make a new one
    if request.method == 'POST': # For form submission, abstract ID is in the form
        if form.id.data is None:
            a = Abstract(author_id=current_user.id)
        else:
            a = Abstract.query.filter(Abstract.id==form.id.data).first()
    else: # For direct/initial access, abstract ID is in the GET request
        abstract_id = request.args.get('id')
        if abstract_id is None: # Make a new abstract
            a = Abstract(author_id=current_user.id)
        else:
            a = Abstract.query.filter(Abstract.id==abstract_id).first()
    
    # Now we have an abstract object - either a new one, or an existing one, depending on whether it has an id of its own or not
    if a is None or a.author_id != current_user.id:
        flash('You cannot view or edit an abstract that does not belong to you','danger')
        return redirect(url_for('abstracts'))

    # By this point, we are sure that the Abstract a belongs to the logged in user
    if form.validate_on_submit() or form.delete.data: 

        if form.delete.data: # Delete the abstract if required
            if a.id is not None: # Delete it from the database if it exists
                db.session.delete(a)
                db.session.commit()
            flash('Abstract deleted','danger')
            return redirect(url_for('abstracts'))

        # If the user wants to create an abstract, they aren't allowed to already have one
        if a.id is None: 
            existing_abstracts = Abstract.query.filter(Abstract.author_id==current_user.id).all()
            if existing_abstracts is not None and len(existing_abstracts) >= 1:
                flash('You are only allowed to submit one abstract','danger')
                return render_template('edit_abstract.html',form=form)


        form.populate_obj(a)

        if not a.is_talk:
            a.abstract = ''
        db.session.add(a)
        db.session.commit()
        flash('Changes saved','success')
        return redirect(url_for('abstracts'))

    elif request.method == 'POST':
        # If this block runs, the form was submitted but failed to validate
        return render_template('edit_abstract.html',form=form)
    else:
        # If we are here, the user arrived via a GET request, so just populate the form fields
        form = EditAbstractForm(obj=a)
        return render_template('edit_abstract.html',form=form)


@app.route('/game', methods=['GET'])
@roles_required('admin')  
@login_required 
def game():
    # Is the game active? If tags have not been added, exit gracefully by redirecting to the home page
    if current_user.link is None:
        return redirect(url_for('index'))

    web_link = request.args.get('u')
    if web_link is not None: # If a link was provided
        target_user = User.query.filter(User.link == web_link).first()
        if target_user is None:
            flash('Invalid code','danger')
        else:
            # Find the tag
            this_tag = Tag.query.filter(and_(Tag.source == current_user.id, Tag.destination == target_user.id)).first()
            if this_tag is None:
                flash('Not one of your targets','danger')
            else:
                if this_tag.time is None:
                    this_tag.time = datetime.datetime.now()
                    db.session.add(this_tag)
                    db.session.commit()
                flash('Scan successful','success')

    # Get the team scores
    team_data = []
    for team in [0,1,2]:
        users_on_team = User.query.filter(User.team == team).all()
        team_tags = Tag.query.filter(Tag.source.in_([x.id for x in users_on_team])).all()
        team_score = float(len([x for x in team_tags if x.time is not None]))/len(team_tags)
        team_data.append((team_names[team],team_score))

    chart_style = Style(background='transparent', plot_background='transparent', opacity='.6', opacity_hover='.9', transition='400ms ease-in') 
    bar_chart = pygal.HorizontalStackedBar(range=(0, 100),style=chart_style,height=200,show_legend=False)
    bar_chart.title = "Scoreboard"
    bar_chart.x_title = "Scan completion (%)"
    bar_chart.x_labels = [x[0] for x in team_data]
    bar_chart.add('Scores', [100*x[1] for x in team_data])
    chart = bar_chart.render().decode('utf-8')

    user_team = team_names[current_user.team]

    # Get the user's tags
    user_tags = Tag.query.filter(Tag.source == current_user.id).order_by(desc(Tag.destination)).all()
    user_targets = User.query.filter(User.id.in_([x.destination for x in user_tags])).order_by(desc(User.id)).all()
    tag_data = zip(user_targets,user_tags)

    return render_template('game.html',chart=chart,user_team=user_team,tag_data=tag_data)

            
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 404

### ADMIN TOOLS

@app.route('/admin_user_list')
@roles_required('admin')  
@login_required 
def admin_user_list():
    u = User.query.filter(and_(User.confirmed_at,User.is_attending)).all()
    
    n_attending = [x.is_attending for x in u].count(True)
    n_posters = [x.intends_poster for x in u].count(True)
    n_talks = [x.intends_talk for x in u].count(True)
    n_workshop = [x.intends_workshop for x in u].count(True)
    n_dinner = [x.intends_dinner for x in u].count(True)
    n_no_reqs = [x.dietary_requirements=='No special requirements' for x in u if x.intends_dinner].count(True)
    
    veg_people = [x for x in u if x.dietary_requirements=='Vegetarian' and x.intends_dinner]
    gf_people = [x for x in u if x.dietary_requirements=='Gluten free' and x.intends_dinner]
    df_people = [x for x in u if x.dietary_requirements=='Dairy free' and x.intends_dinner]
    halal_people = [x for x in u if x.dietary_requirements=='Halal' and x.intends_dinner]
    
    lunch_veg_people = [x for x in u if x.dietary_requirements=='Vegetarian' and not x.intends_dinner]
    lunch_gf_people = [x for x in u if x.dietary_requirements=='Gluten free' and not x.intends_dinner]
    lunch_df_people = [x for x in u if x.dietary_requirements=='Dairy free' and not x.intends_dinner]
    lunch_halal_people = [x for x in u if x.dietary_requirements=='Halal' and not x.intends_dinner]

    num_people = [('Number attending',n_attending),('Number of intended posters',n_posters),('Number of intended talks',n_talks),('Number for workshop',n_workshop),('Number for dinner',n_dinner),('Number of regular meals',n_no_reqs),('Number of vegetarian meals',len(veg_people)),('Number of gluten free meals',len(gf_people)),('Number of dairy free meals',len(df_people)),('Number of halal meals',len(halal_people))]

    mlist = ';'.join([x.email for x in u])

    u_not_attending = User.query.filter(and_(User.confirmed_at,not_(User.is_attending))).all();
    u_unvalidated = User.query.filter(User.confirmed_at == None).all();
    return render_template('_user_list.html',lunch_veg_people=lunch_veg_people,lunch_gf_people=lunch_gf_people,lunch_df_people=lunch_df_people,lunch_halal_people=lunch_halal_people,veg_people=veg_people,gf_people=gf_people,df_people=df_people,halal_people=halal_people, not_attending_users=u_not_attending,unvalidated_users = u_unvalidated,mailing_list=mlist,users=u,num_people=num_people)

@app.route('/admin_abstract_list')
@roles_required('admin')
@login_required   
def admin_abstract_list():
    # When the admin views an abstract, they can see whether it is for posters (all abstracts) or just talks
    display_talks = request.args.get('talk') == u'True'

    abstract_list = []
    maccept = []

    if display_talks:
        # abstract_list = [todo,accept,reject]
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.is_talk == True).filter(Abstract.session_talk == 0).all()) 
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.is_talk == True).filter(Abstract.session_talk == 1).all())
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.is_talk == True).filter(Abstract.session_talk == -1).all())
        maccept.append(','.join([x[0].email for x in abstract_list[1]]))
        mreject = ','.join([x[0].email for x in abstract_list[2]])
    else:
        # abstract_list = [todo,s1,s2,reject]
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.session_poster == 0).all())
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.session_poster == 1).all())
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.session_poster == 2).all())
        abstract_list.append(db.session.query(User,Abstract).filter(User.id == Abstract.author_id).filter(Abstract.session_poster == -1).all())
        maccept.append(','.join([x[0].email for x in abstract_list[1]]))
        maccept.append(','.join([x[0].email for x in abstract_list[2]]))
        mreject = ','.join([x[0].email for x in abstract_list[3]])

    return render_template('_abstract_list.html',abstract_list=abstract_list,is_talks=display_talks,mailing_list_accepted=maccept, mailing_list_rejected = mreject)

@app.route('/admin_abstract_review', methods=['GET', 'POST'])
@roles_required('admin')
@login_required   
def admin_abstract_review():
    if request.method == 'GET': # Visiting the page
        abstract_id = request.args.get('id')
        a = Abstract.query.filter(Abstract.id == abstract_id).first();
        if a is None:
            flash('Abstract not found','danger')
            return redirect(url_for('admin_abstract_list',talk=False))

        u = User.query.filter(User.id==a.author_id).first()
        form = AdminAbstractForm(obj=a)

        try:
            return_to_talk = request.referrer.split('=')[-1] == 'True'
        except:
            return_to_talk = False

        form.return_to_talk.data = return_to_talk
        return render_template('_abstract_review.html',user=u,abstract=a,form=form)

    form = AdminAbstractForm()
    a = Abstract.query.filter(Abstract.id == form.id.data).first()
    u = User.query.filter(User.id==a.author_id).first()

    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(a)
            db.session.commit()
            flash('Abstract deleted','danger')
            return redirect(url_for('admin_abstract_list',talk=form.return_to_talk.data))

        # Save the new object 
        form.populate_obj(a)
        db.session.add(a)
        db.session.commit()
        flash('Changes saved','success')
        return redirect(url_for('admin_abstract_list',talk=form.return_to_talk.data))
    else:
        return render_template('_abstract_review.html',user=u,abstract=a,form=form)

@app.route('/admin_manage_registration', methods=['GET', 'POST'])
@roles_required('admin')
@login_required
def admin_manage_registration():

    if request.method == 'GET':
        user_id = request.args.get('id')
        u = User.query.filter(User.id==user_id).first()
        # If visiting the user's registration page BEFORE the user does, 
        # then copy the affliation over now. In the user list, it may appear once
        # with 'Other' as the affiliation, but it will be synced as soon as anyone
        # tries to view it
        if u.temp_custom_affiliation:
            u.affiliation = u.temp_custom_affiliation
            u.temp_custom_affiliation = None
            db.session.add(u)
            db.session.commit()
        form = AdminUserInfoForm(obj=u)
        is_confirmed = u.confirmed_at is not None
    else:
        form = AdminUserInfoForm()
        u = User.query.filter(User.id == form.id.data).first()
        is_confirmed = u.confirmed_at is not None

    if form.validate_on_submit():

        if form.delete.data:
            abstracts = Abstract.query.filter(Abstract.author_id == u.id).all()
            for a in abstracts:
                db.session.delete(a)
            db.session.delete(u)
            db.session.commit()
            flash('User deleted','danger')
            return redirect(url_for('admin_user_list'))

        if form.activate.data:
            u.confirmed_at=datetime.datetime.now()
            db.session.add(u)
            db.session.commit()
            flash('User has been activated','success')
            return redirect(url_for('admin_manage_registration',id=u.id))

        form.populate_obj(u)

        u.roles = []
        if u.is_admin:
            admin_role = Role.query.filter(Role.name=='admin').first()
            u.roles = [admin_role]

        db.session.add(u)
        db.session.commit()
        flash('Changes saved','success')
        return redirect(url_for('admin_manage_registration',id=u.id))

    return render_template('_user_review.html',form=form,is_confirmed=is_confirmed)