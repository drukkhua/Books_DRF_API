import random

from django.db.models import Avg

from store.models import Book
from store.models import UserBookRelation
from django.contrib.auth.models import User


def set_rating(book: Book):
    rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating = rating
    book.save()


def generate_data(num: int = 100):
    rate_ = (1, 2, 3, 4, 5)
    like_ = (True, False)
    max_users = User.objects.all().count() - 1
    print(f'{max_users=}')
    for n in range(num):
        user = User.objects.create(username=f'User!!!!!__{n}',
                                   first_name=f'User_Name_{n}',
                                   last_name=f'User_Last_Name_{n}')
        print(f'{user=} WAS CREATED')

        book = Book.objects.create(name=f'Test Book {n}',
                                   price=25 * n,
                                   author_name=f'Author {n}',
                                   owner=user)
        print(f'{book=} WAS CREATED')
        max_users += 1

        for z in range(max_users):
            like = random.choice(like_)
            rate = random.choice(rate_)
            try:
                id_like = random.randint(0, max_users)
                user_like = random.choice(User.objects.all())
                UserBookRelation.objects.create(user=user_like, book=book, like=like, rate=rate)
            except:
                print(f'No such user with id {id_like}')