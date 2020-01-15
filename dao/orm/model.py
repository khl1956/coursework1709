from app import db
from app import app
from flask_security import RoleMixin, UserMixin
from flask_security import SQLAlchemyUserDatastore, Security

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

user_datastore = SQLAlchemyUserDatastore(db, ormPersons, ormRole)
security = Security(app, user_datastore)