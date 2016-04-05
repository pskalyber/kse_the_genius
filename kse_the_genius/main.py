# -*- coding: utf-8 -*-
"""
    KSE THE GENIUS
    ~~~~~~~~

    A KSE Quiz application written with Flask and sqlite3.

    :copyright: (c) 2016 by Sangkeun Park.
    :license: KAIST, see LICENSE for more details.
"""

from __future__ import with_statement
import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash
import collections

# configuration -> app.config[] 로 활용 가능. 어떤 원리지?
DATABASE = 'minitwit.db'
PER_PAGE = 10
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = g.db.execute('select user_id from user where username = ?',
                       [username]).fetchone()
    return rv[0] if rv else None

def get_last_post_id():
    """Convenience method to look up the id for a last post."""
    rv = g.db.execute('SELECT post_id FROM post ORDER BY post_id DESC LIMIT 1').fetchone()
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), 
         size)


@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/mypost')
def mypost():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_request'))
    return render_template('timeline.html', posts=query_db('''
        select post.*, user.* from post, user
        where post.author_id = user.user_id and (
            user.user_id = ? )
        order by post.publish_date desc limit ?''',
        [session['user_id'], PER_PAGE]))

@app.route('/test')
def public_request(post_id=None):
    """Displays the latest post of all users."""
    posts = query_db('''
        select post.*, user.* from post, user
        where post.author_id = user.user_id
        order by post.publish_date desc limit ?''', [PER_PAGE])
    
    if post_id:
        selected_post = query_db('''
            select post.*, user.* from post, user
            where post_id = ?
            order by post.publish_date desc limit ?''', [post_id, PER_PAGE], one=True)
        print selected_post
        return render_template('timeline.html', posts=posts, selected_post=selected_post)
    else:
        return render_template('timeline.html', posts=posts)

@app.route('/course')
def course():
    """Displays the course list"""
    return render_template('course.html')

@app.route('/')
@app.route('/ranking')
def ranking(post_id=None):
    """Displays the latest post of all users."""
    
    total_score = collections.OrderedDict()
    print "Lv1=============="
    total_score['genius'] = getUserList(80, 100)
    print "Lv2=============="
    total_score['nerd'] = getUserList(60, 80)
    print "Lv3=============="
    total_score['smarty-pants'] = getUserList(40, 60)
    print "Lv4=============="
    total_score['eager_beaver'] = getUserList(20, 40)
    print "Lv5=============="
    total_score['Newbie'] = getUserList(0, 20)
    return render_template('ranking.html', total_score = total_score)

#과목별 만점
MUNYI_MAX_POINT = ("munyi_point", 100.0)
WCYOON_MAX_POINT = ("wcyoon_point", 100.0)
UCLEE_MAX_POINT = ("uclee_point", 100.0)
JAEGIL_MAX_POINT = ("jaegil_point", 100.0)
AVIV_MAX_POINT = ("aviv_point", 100.0)
KSE_MAX_POINT = ("kse_point", 100.0)
TOTAL_MAX_POINT = ("total_point", 100.0)
def getUserList(range_min, range_max):
    """get user list for each course"""
    
    score = collections.OrderedDict()
    score['munyi_point']=[]
    score['wcyoon_point']=[]
    score['uclee_point']=[]
    score['jaegil_point']=[]
    score['aviv_point']=[]
    score['kse_point']=[]
    score['total_point']=[]       

    for PROF_POINT, MAX_POINT in (MUNYI_MAX_POINT, WCYOON_MAX_POINT, UCLEE_MAX_POINT, JAEGIL_MAX_POINT, AVIV_MAX_POINT, KSE_MAX_POINT, TOTAL_MAX_POINT):
        print PROF_POINT, MAX_POINT, "----------"
        users = query_db("SELECT username, " + PROF_POINT + " FROM user WHERE (" + PROF_POINT + " / ? * 100.0) > ? AND (" + PROF_POINT + " / ? * 100.0) <= ?", [MAX_POINT, range_min, MAX_POINT, range_max])
        for user in users:
            print user['username'], user[PROF_POINT] 
            score[PROF_POINT].append(user)
        # 여기서 왜 SQL에 직접 PROF_POINT 라고 넣어야 되고, ?를 대체하는 값으로 넣으면 안되지? 개빡치네!!!
    
    return score
        
@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.publish_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)

@app.route('/quiz')
def quiz():
    """Displaying quiz for the selected Prof"""
    
    prof = request.args.get('prof')
    error = request.args.get('error')
    
    user_info = query_db('''SELECT * FROM user WHERE
            user.user_id = ?''',
            [session['user_id']],
            one=True)

    numOfQuiz = query_db('''SELECT count(*) FROM quiz WHERE
            professor_id = ? ''',
            [prof],
            one=True)

    quiz = query_db('''SELECT * FROM quiz WHERE
            professor_id = ? AND quiz_id = ?''',
            [prof, user_info[prof + "_last_quiz"]+1],
            one=True)

    return render_template('quiz.html', prof=prof, quiz=quiz, error=error)

@app.route('/quiz_processing', methods=['POST'])
def quiz_processing():
    """Registers a new post"""
    if 'user_id' not in session:
        abort(401)
    error = None
    if request.method == 'POST':
        prof = request.form['prof']
        my_answer = "".join(request.form.getlist("answers"))
        quiz_value = request.form['quiz_value']
        
        user_info = query_db('''SELECT * FROM user WHERE
            user.user_id = ?''',
            [session['user_id']],
            one=True)

        quiz = query_db('''SELECT * FROM quiz WHERE
            professor_id = ? AND quiz_id = ?''',
            [prof, user_info[prof + "_last_quiz"]+1],
            one=True)
        
        #Check whether the answer is correct or not
        if my_answer == unicode(quiz['correct_answer']):
            g.db.execute("UPDATE user SET " + prof + "_last_quiz = " \
                + prof + "_last_quiz+1 WHERE user_id =?", 
                [session['user_id']])
            g.db.execute("UPDATE user SET " + prof + "_point = " \
                + prof + "_point + " + quiz_value + " WHERE user_id =?", 
                [session['user_id']])
        else:
            error = 'Wrong answer. You got -1 point!'
            g.db.execute("UPDATE user SET " + prof + "_point = " \
                + prof + "_point-1 WHERE user_id =?", 
                [session['user_id']])
        
        g.db.execute('''UPDATE user SET total_point = 
                munyi_point + 
                wcyoon_point + 
                uclee_point + 
                jaegil_point + 
                aviv_point + 
                kse_point 
                WHERE user_id =?''', 
                [session['user_id']])
        
        g.db.commit()
    
    return redirect(url_for('quiz', prof=prof, error=error))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('course'))
    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('course'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('course'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            g.db.execute('''insert into user (
                username, email, pw_hash) values (?, ?, ?)''',
                [request.form['username'], request.form['email'],
                 generate_password_hash(request.form['password'])])
            g.db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_request'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    init_db()

    app.run(host="0.0.0.0", port=80, debug=True)
    
