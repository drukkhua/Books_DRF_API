from django.test import TestCase
from django.contrib.auth.models import User

from store.logic import set_rating
from store.models import UserBookRelation, Book


class SetRatingTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create(username='User1', first_name='U_N1', last_name='U_L1')
        self.user2 = User.objects.create(username='User2', first_name='U_N2', last_name='U_L2')
        self.user3 = User.objects.create(username='User3', first_name='U_N3', last_name='U_L3')

        self.book_1 = Book.objects.create(name='Test Book 1',
                                          price=25, author_name='Author 1',
                                          owner=self.user1)
        self.book_2 = Book.objects.create(name='Test Book 2',
                                          price=55, author_name='Author 1',
                                          owner=self.user1)

        # self.book_1.readers.add(self.user1)
        # self.book_1.readers.add(self.user2)
        UserBookRelation.objects.create(user=self.user1, book=self.book_1, like=True,
                                        rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book_1, like=True,
                                        rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book_1, like=True,
                                        rate=4)

        UserBookRelation.objects.create(user=self.user1, book=self.book_2, like=True,
                                        rate=3)
        UserBookRelation.objects.create(user=self.user2, book=self.book_2, like=True,
                                        rate=4)
        UserBookRelation.objects.create(user=self.user3, book=self.book_2, like=False)
    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()

        set_rating(self.book_2)
        self.book_2.refresh_from_db()

        self.assertEqual('4.67', str(self.book_1.rating))
        self.assertEqual('3.50', str(self.book_2.rating))
