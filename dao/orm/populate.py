from dao.orm.model import *
from app import user_datastore

db.create_all()

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

Harry = ormHashtags(hashtag_name="harryPotter")
Nail = ormHashtags(hashtag_name="longNail")
Rome = ormHashtags(hashtag_name="Rome")

Sale.person.append(Vlad)
Black_friday.person.append(Anna)
New_book.person.append(Dima)

Sale.hashtage.append(Rome)
Black_friday.hashtage.append(Nail)
New_book.hashtage.append(Harry)

db.session.add_all([Dima, Vlad, Anna, Admin, User, Sale, Black_friday, New_book, Traveling, Nails, Books, Harry, Nail, Rome])

db.session.commit()
