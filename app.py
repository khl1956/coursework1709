from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, current_user, login_required, roles_accepted, RoleMixin, UserMixin \
    , Security
from datetime import datetime
from forms.person_form import PersonForm
from forms.group_form import GroupForm
from forms.post_form import PostForm
from forms.hashtag_form import HashtagForm

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

import plotly
import plotly.graph_objs as go
import json
from math import exp
# from neupy import algorithms
from flask_security.utils import hash_password

# from forms.function_form import FunctionForm
# from forms.tectcase_form import TestCaseForm
# from forms.ban import BanForm
# from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security, UserMixin, login_required, current_user

# from flask_security.decorators import roles_accepted, roles_accepted
# import plotly
# import json
# import plotly.graph_objs as go
# from random import randint
# import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import StandardScaler
# import numpy as np
# from math import exp
# from random import uniform

# from neupy import algorithms

app = Flask(__name__)
app.secret_key = 'key'

app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['USER_EMAIL_SENDER_EMAIL'] = "noreply@example.com"

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:01200120@localhost/Anna'
else:
    app.debug = False
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgres://bgyzqnxijhefuh:f051436962728e3da6be944f2c62351b8977eee822399fae8179aaac123a8ca1@ec2-75-101-128-10.compute-1.amazonaws.com:5432/d9mhc45m37qtpa'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Input_L:
    def activation(self, x):
        self.y = x * 1
        return self.y


class Image_L:
    def __init__(self, w):
        self.w = w

    def activation(self, x):
        sum = 0
        for i in range(len(self.w)):
            sum += exp(-(self.w[i] - x[i]) ** 2 / 0.3 ** 2)
        return sum


class Add_L:
    def activation(self, x):
        sum = 0
        for i in x:
            sum += i
        res = sum / len(x)
        return res


class Output_L:
    def activation(self, x):
        clas = "A"
        val = x[clas]
        for i in x.items():
            if i[1] > val:
                clas = i[0]
        return clas


person_have_role = db.Table('person_have_role',
                            db.Column("person_id", db.Integer(), db.ForeignKey('orm_person.id')),
                            db.Column("role_id", db.Integer(), db.ForeignKey('orm_role.id'))
                            )

person_own_group = db.Table('person_own_group',
                            db.Column("person_id", db.Integer(), db.ForeignKey('orm_person.id')),
                            db.Column("group_id", db.Integer(), db.ForeignKey('orm_group.group_id'))
                            )

post_have_person = db.Table('post_have_person',
                            db.Column("person_id", db.Integer(), db.ForeignKey('orm_person.id')),
                            db.Column("post_id", db.Integer(), db.ForeignKey('orm_post.post_id'))
                            )

group_have_post = db.Table('group_have_post',
                           db.Column("group_id", db.Integer(), db.ForeignKey('orm_group.group_id')),
                           db.Column("post_id", db.Integer(), db.ForeignKey('orm_post.post_id'))
                           )

post_have_hashtage = db.Table('post_have_hashtage',
                              db.Column("post_id", db.Integer(), db.ForeignKey('orm_post.post_id')),
                              db.Column("hashtag_name", db.String(100), db.ForeignKey('orm_hashtags.hashtag_name'))
                              )


class ormPersons(db.Model, UserMixin):
    __tablename__ = 'orm_person'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=True)

    roles = db.relationship("ormRole", secondary=person_have_role, backref=db.backref('person', lazy='dynamic'))
    group = db.relationship("ormGroup", secondary=person_own_group, backref=db.backref('owner', lazy='dynamic'))


class ormRole(db.Model, RoleMixin):
    __tablename__ = 'orm_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)


class ormGroup(db.Model):
    __tablename__ = 'orm_group'

    group_id = db.Column(db.Integer, db.Sequence('group_id_seq', start=1, increment=1), primary_key=True)
    group_name = db.Column(db.String(200), nullable=False)
    group_description = db.Column(db.String(500), nullable=False)

    posts = db.relationship("ormPost", secondary=group_have_post, backref=db.backref('group', lazy='dynamic'))


class ormPost(db.Model):
    __tablename__ = 'orm_post'

    post_id = db.Column(db.Integer, db.Sequence('post_id_seq', start=1, increment=1), primary_key=True)
    post_title = db.Column(db.String(100), nullable=False)
    post_text = db.Column(db.String(1000), nullable=False)
    post_date = db.Column(db.Date, nullable=False)

    person = db.relationship("ormPersons", secondary=post_have_person, backref=db.backref('post', lazy='dynamic'))
    hashtage = db.relationship("ormHashtags", secondary=post_have_hashtage, backref=db.backref('post', lazy='dynamic'))


class ormHashtags(db.Model):
    __tablename__ = 'orm_hashtags'

    hashtag_name = db.Column(db.String(100), primary_key=True)
    hashtag_views = db.Column(db.Integer, nullable=False)


user_datastore = SQLAlchemyUserDatastore(db, ormPersons, ormRole)
security = Security(app, user_datastore)


@app.route('/new', methods=['GET', 'POST'])
def new():
    db.create_all()

    # db.session.delete(person_have_role)
    # db.session.delete(person_own_group)
    # db.session.delete(post_have_person)
    # db.session.delete(post_have_hashtage)
    # db.session.delete(group_have_post)
    # db.session.flush()
    # db.session.query(ormRole).delete()
    # db.session.query(ormHashtags).delete()
    # db.session.query(ormPost).delete()
    # db.session.query(ormGroup).delete()
    # db.session.query(ormPersons).delete()

    Dima = user_datastore.create_user(username="Dima",
                                      password="0000",
                                      name="Dima",
                                      surname="Koltsov",
                                      email="dima_2010@ukr.net")

    Vlad = user_datastore.create_user(username="Vlad",
                                      password="0000",
                                      name="Vlad",
                                      surname="Kanevckyi",
                                      email="vladkaneve@gmail.com")

    Anna = user_datastore.create_user(username="Anna",
                                      password="0000",
                                      name="Anna",
                                      surname="Trishyna",
                                      email="trish@gmail.com")

    Admin = user_datastore.create_role(name="Admin")

    User = user_datastore.create_role(name="User")

    Dima.roles.append(User)
    Vlad.roles.append(User)
    Anna.roles.append(Admin)

    Traveling = ormGroup(group_name="Trip my dream",
                         group_description="traveling")

    Nails = ormGroup(group_name="Good nails",
                     group_description="nails")

    Books = ormGroup(group_name="harry Potter",
                     group_description="books")

    Dima.group.append(Books)
    Vlad.group.append(Traveling)
    Anna.group.append(Nails)

    Sale = ormPost(
        post_title="Sale",
        post_text="Big sale",
        post_date="2020-01-12")

    Black_friday = ormPost(
        post_title="Black friday",
        post_text="Black friday",
        post_date="2020-01-10")

    New_book = ormPost(
        post_title="New book",
        post_text="J. K. Rowling wrote new books about harry potter",
        post_date="2020-01-13")

    Traveling.posts.append(Sale)
    Nails.posts.append(Black_friday)
    Books.posts.append(New_book)

    Harry = ormHashtags(hashtag_name="harryPotter",
                        hashtag_views=0)
    Nail = ormHashtags(hashtag_name="longNail",
                       hashtag_views=0)
    Rome = ormHashtags(hashtag_name="Rome",
                       hashtag_views=0)

    Sale.person.append(Vlad)
    Black_friday.person.append(Anna)
    New_book.person.append(Dima)

    Sale.hashtage.append(Rome)
    Black_friday.hashtage.append(Nail)
    New_book.hashtage.append(Harry)

    db.session.add_all(
        [Dima, Vlad, Anna, Sale, Black_friday, New_book, Traveling, Nails, Books, Harry, Nail, Rome])

    db.session.commit()

    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


@app.route('/person', methods=['GET'])
@login_required
@roles_accepted('Admin', 'User')
def person():
    if current_user.has_role('Admin'):
        result = db.session.query(ormPersons).all()
    else:
        result = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).all()

    # result = db.session.query(ormPersons).all()
    return render_template('person.html', persons=result)


@app.route('/new_person', methods=['GET', 'POST'])
def new_person():
    form = PersonForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('person_form.html', form=form, form_name="New person", action="new_person")
        else:
            new_person = user_datastore.create_user(
                username=form.username.data,
                password=form.password.data,
                name=form.name.data,
                surname=form.surname.data,
                email=form.email.data)

            role = db.session.query(ormRole).filter(ormRole.name == "User").one()

            new_person.roles.append(role)

            db.session.add(new_person)
            db.session.commit()

            return redirect(url_for('person'))

    return render_template('person_form.html', form=form, form_name="New person", action="new_person")


@app.route('/edit_person', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "User")
def edit_person():
    form = PersonForm()

    if request.method == 'GET':

        person_login = request.args.get('person_login')
        person = db.session.query(ormPersons).filter(ormPersons.username == person_login).one()

        # fill form and send to user
        form.username.data = person.username
        form.password.data = person.password
        form.name.data = person.name
        form.surname.data = person.surname
        form.email.data = person.email

        return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")


    else:

        if not form.validate():
            return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")
        else:
            # find user
            person = db.session.query(ormPersons).filter(ormPersons.username == form.username.data).one()

            # update fields from form data
            person.username = form.username.data
            person.password = form.password.data
            person.name = form.name.data
            person.surname = form.surname.data
            person.email = form.email.data

            db.session.commit()

            return redirect(url_for('person'))


@app.route('/delete_person', methods=['POST'])
@login_required
@roles_accepted('Admin')
def delete_person():
    person_login = request.form['person_login']

    result = db.session.query(ormPersons).filter(ormPersons.username == person_login).one()

    db.session.delete(result)
    db.session.commit()

    return person_login


@app.route('/group', methods=['GET'])
# @login_required
# @roles_accepted('Admin', 'User')
def group():
    result = db.session.query(ormGroup).all()
    edit_result = []
    viev_result = []
    if current_user.has_role('Admin'):
        edit_result = result
    elif current_user.has_role('User'):
        person = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).one()
        for i in result:
            if person.group[0] == i:
                edit_result.append(i)
            else:
                viev_result.append(i)
    else:
        viev_result = result
    # result = db.session.query(ormGroup).all()
    return render_template('group.html', groups=edit_result, groups_1=viev_result)


@app.route('/new_group', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', 'User')
def new_group():
    form = GroupForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('group_form.html', form=form, form_name="New group", action="new_group")
        else:
            new_group = ormGroup(
                group_name=form.group_name.data,
                group_description=form.group_name.data)

            person = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).one()

            person.group.append(new_group)

            # Dima.group.append(Books)
            db.session.add(person)
            db.session.commit()

            return redirect(url_for('group'))

    return render_template('group_form.html', form=form, form_name="New group", action="new_group")


@app.route('/edit_group', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "User")
def edit_group():
    form = GroupForm()

    if request.method == 'GET':

        group_id = request.args.get('group_id')
        group = db.session.query(ormGroup).filter(ormGroup.group_id == group_id).one()

        # fill form and send to user
        form.group_id.data = group.group_id
        form.group_name.data = group.group_name
        form.group_description.data = group.group_description

        return render_template('group_form.html', form=form, form_name="Edit group", action="edit_group")

    else:

        if not form.validate():
            return render_template('group_form.html', form=form, form_name="Edit group", action="edit_group")
        else:
            # find user
            group = db.session.query(ormGroup).filter(ormGroup.group_id == form.group_id.data).one()

            # update fields from form data
            group.group_name = form.group_name.data
            group.group_description = form.group_description.data

            db.session.commit()

            return redirect(url_for('group'))


@app.route('/delete_group', methods=['POST'])
@login_required
@roles_accepted('Admin', "User")
def delete_group():
    group_id = request.form['group_id']

    result = db.session.query(ormGroup).filter(ormGroup.group_id == group_id).one()

    db.session.delete(result)
    db.session.commit()

    return group_id


@app.route('/post', methods=['GET'])
@app.route('/post/<hashtag_name>', methods=['GET'])
def post(hashtag_name=None):
    if hashtag_name == None:
        result = db.session.query(ormPost).all()
    else:
        # result = db.session.query(ormPost).filter_by(ormPost.hashtage.contains(hashtag_name)).all()
        result = db.session.query(ormPost).filter(ormPost.hashtage.any(hashtag_name=hashtag_name)).all()
        incriment = db.session.query(ormHashtags).filter(ormHashtags.hashtag_name == hashtag_name).one()
        incriment.hashtag_views = incriment.hashtag_views + 1
        db.session.commit()
    edit_result = []
    viev_result = []
    if current_user.has_role('Admin'):
        edit_result = result
    elif current_user.has_role('User'):
        person = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).one()
        for i in result:
            if i.person[0] == person:
                edit_result.append(i)
            else:
                viev_result.append(i)
    else:
        viev_result = result
    # result = db.session.query(ormGroup).all()
    # return render_template('group.html', posts=edit_result, posts_1=viev_result)

    # return redirect(url_for('post', posts=edit_result, posts_1=viev_result))
    return render_template('post.html', posts=edit_result, posts_1=viev_result)


@app.route('/new_post/<group_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "User")
def new_post(group_id):
    form = PostForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('post_form.html', form=form, form_name="New post", action="new_post")
        else:
            new_post = ormPost(
                post_title=form.post_title.data,
                post_text=form.post_text.data,
                post_date=datetime.now().strftime("%Y-%m-%d"))

            group = db.session.query(ormGroup).filter(ormGroup.group_id == group_id).one()
            person = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).one()

            group.posts.append(new_post)
            new_post.person.append(person)

            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('post'))

    return render_template('post_form.html', form=form, form_name="New post", action="new_post/" + group_id)


@app.route('/edit_post', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "User")
def edit_post():
    form = PostForm()

    if request.method == 'GET':

        post_id = request.args.get('post_id')
        post = db.session.query(ormPost).filter(ormPost.post_id == post_id).one()

        # fill form and send to user
        form.post_id.data = post.post_id
        form.post_title.data = post.post_title
        form.post_text.data = post.post_text
        # form.post_date.data = post.post_date.strftime("%Y-%m-%d")

        return render_template('post_form.html', form=form, form_name="Edit post", action="edit_post")

    else:

        if not form.validate():
            return render_template('post_form.html', form=form, form_name="Edit post", action="edit_post")
        else:
            # find user
            post = db.session.query(ormPost).filter(ormPost.post_id == form.post_id.data).one()

            # update fields from form data
            post.post_title = form.post_title.data
            post.post_text = form.post_text.data

            db.session.commit()

            return redirect(url_for('post'))


@app.route('/delete_post', methods=['POST'])
@login_required
@roles_accepted('Admin', "User")
def delete_post():
    post_id = request.form['post_id']

    result = db.session.query(ormPost).filter(ormPost.post_id == post_id).one()

    db.session.delete(result)
    db.session.commit()

    return post_id


@app.route('/hashtag', methods=['GET'])
@app.route('/hashtag/<post_id>', methods=['GET'])
@login_required
@roles_accepted('Admin', 'User')
def hashtag(post_id=None):
    # if current_user.has_role('Admin'):
    #     result = db.session.query(ormPersons).all()
    # else:
    #     result = db.session.query(ormPersons).filter(ormPersons.id == current_user.id).all()

    if post_id == None:
        result = db.session.query(ormHashtags).all()
    else:
        result = db.session.query(ormPost).filter(ormPost.post_id == post_id).one()
        result = result.hashtage

    return render_template('hashtag.html', hashtags=result)


@app.route('/new_hashtag/<post_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Admin', "User")
def new_hashtag(post_id):
    form = HashtagForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('hashtag_form.html', form=form, form_name="New hashtag", action="new_hashtag")
        else:

            new_hashtag = db.session.query(ormHashtags).filter(
                ormHashtags.hashtag_name == form.hashtag_name.data).one_or_none()

            if new_hashtag == None:
                new_hashtag = ormHashtags(
                    hashtag_name=form.hashtag_name.data,
                    hashtag_views=0)

            post = db.session.query(ormPost).filter(ormPost.post_id == post_id).one()

            post.hashtage.append(new_hashtag)

            # z = post_have_hashtage(post_id=3, hashtag_name="Rome")

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('hashtag'))

    return render_template('hashtag_form.html', form=form, form_name="New hashtag", action="new_hashtag/" + post_id)


@app.route('/correlation/<hashtag_name>', methods=['GET', 'POST'])
@login_required
@roles_accepted("User", "Admin")
def correlation(hashtag_name):
    result_1 = db.session.query(ormPost.post_id).filter(ormPost.hashtage.any(hashtag_name=hashtag_name)).all()
    result_2 = db.session.query(ormHashtags.hashtag_views).filter(ormHashtags.hashtag_name == hashtag_name).one()

    liste = []
    for i in range(len(result_1)):
        liste.append([])
        liste[i].append(result_1[i][0])
        liste[i].append(result_2[0])
    print(liste)

    matrix_data = np.matrix(liste)  # .transpose()

    df = pd.DataFrame(matrix_data, columns=('par1', 'result'))

    print(df)

    scaler = StandardScaler()
    scaler.fit(df[['par1']])
    train_X = scaler.transform(df[['par1']])
    # print(train_X, df[["count_files"]])
    reg = LinearRegression().fit(train_X, df[["result"]])

    test_array = [[liste[-1][0]]]
    test = scaler.transform(test_array)
    result = reg.predict(test)

    return render_template('regretion.html', row=int(round(result[0, 0])), test_data=test_array[0],
                           coef=reg.coef_[0],
                           coef1=reg.intercept_)


@app.route('/clustering', methods=['GET', 'POST'])
@app.route('/clustering', methods=['GET', 'POST'])
@login_required
@roles_accepted("User", "Admin")
def claster():
    #     if id == None:
    #         id = db.session.query(ormTestCase.testcase_id).filter(
    #         ormTestCase.function_name_fk == function_name).all()[-1][0]
    #
    res1 = db.session.query(ormHashtags).all()

    liste = []
    normal = []
    for i in range(len(res1)):
        normal.append(i)

    for i in range(len(res1)):
        liste.append([])
        liste[i].append(normal[i])
        liste[i].append(res1[i].hashtag_views)
    matrix_data = np.matrix(liste)
    df = pd.DataFrame(matrix_data, columns=('par1', 'result'))
    print(df)
    X = df
    print(X)
    count_clasters = 2
    print(count_clasters)
    kmeans = KMeans(n_clusters=count_clasters, random_state=0).fit(X)
    # print(kmeans)
    count_columns = len(X.columns)
    # test_list = [0] * count_columns
    # test_list[0] = 1
    # test_list[1] = 1
    # test_list[2] = 1
    # print(test_list)
    iter = 0
    count_elements = [0, 0]
    for i in matrix_data:
        if kmeans.predict(i)[0] == 0:
            count_elements[0] += 1
        else:
            count_elements[1] += 1
        iter += 1
    # print(kmeans.labels_)
    # print(kmeans.predict(np.array([test_list])))

    pie = go.Pie(
        values=np.array(count_elements),
        labels=np.array(['unpopular', 'popular'])
    )
    data = {
        "pie": [pie]
    }
    graphsJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('clasteresation.html', count_claster=count_clasters, graphsJSON=graphsJSON)


@app.route('/neural_network/<hashtag_name>', methods=['GET', 'POST'])
@login_required
@roles_accepted("User", "Admin")
def neural_network(hashtag_name):
    result_1 = db.session.query(ormHashtags).all()
    # res = db.session.query(ormHashtags.hashtag_views).all()

    input_data = []
    for i in range(len(result_1)):
        input_data.append(result_1[i].hashtag_views)

    # # input_w = [[1, 1, 2], [1, 2, 1], [2, 2, 1], [5, 5, 5]]
    # input_data = [hashtag_name]

    input_list = []
    input_w = []
    for i in range(1):
        input_list.append(Input_L)

    image_list = []
    for i in range(len(input_w)):
        image_list.append(Image_L(input_w[i]))

    class_A = Add_L()
    class_B = Add_L()

    res = Output_L()

    y_input = []
    y_image = []
    y_add = {}

    for i in range(len(input_data)):
        y_input.append(input_list[i].activation(input_list[i], input_data[i]))

    y_image.append([])
    y_image.append([])
    for i in range(len(q)):
        if q[i][41] == "normal":
            y_image[0].append(image_list[i].activation(y_input))
        else:
            y_image[1].append(image_list[i].activation(y_input))

    y_add.update({"normal": class_A.activation(y_image[0])})
    y_add.update({type: class_B.activation(y_image[1])})

    res = res.activation(y_add)

    print("Класс", res)

    return render_template('regretion.html', row=int(round(result[0, 0])), test_data=test_array[0],
                           coef=reg.coef_[0],
                           coef1=reg.intercept_)



if __name__ == "__main__":
    app.debug = True
    app.run()
