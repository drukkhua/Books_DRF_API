import json

from django.db.models import Count, Case, When, Avg
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from django.db.models import F

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_user', first_name='U1_F', last_name='U1_L')
        self.user2 = User.objects.create(username='test_user2', first_name='U2_F', last_name='U2_L')
        self.user_stuff = User.objects.create(username='test_suff_user',
                                              is_staff=True)
        self.book_1 = Book.objects.create(name='Test Book 1',
                                          price=25, author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Test Book 2',
                                          price=55, author_name='Author 5',
                                          owner=self.user)
        self.book_3 = Book.objects.create(name='Test Book Author 1',
                                          price=55, author_name='Author 2',
                                          owner=self.user)
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True,
                                        rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            owner_name=F('owner__username')) \
            .prefetch_related('readers')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print(*serializer_data, sep='\n')
        # print('==========')
        # print(*response, sep='\n')
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_by_id(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        books = Book.objects.filter(id=self.book_1.id).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            owner_name=F('owner__username')) \
            .prefetch_related('readers')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data[-1], response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55})
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            owner_name=F('owner__username')) \
            .prefetch_related('readers')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            owner_name=F('owner__username')) \
            .prefetch_related('readers')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
            owner_name=F('owner__username')) \
            .prefetch_related('readers').order_by('-price')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {"name": "Programming in Python 2",
                "price": 200,
                "author_name": "Mark Summerfield"}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        book_post = Book.objects.last()
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(data["name"], book_post.name)
        self.assertEqual(data["price"], book_post.price)
        self.assertEqual(data["author_name"], book_post.author_name)
        self.assertEqual(self.user, book_post.owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 200,
                "author_name": self.book_1.author_name}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(data["name"], self.book_1.name)
        self.assertEqual(data["price"], self.book_1.price)
        self.assertEqual(data["author_name"], self.book_1.author_name)

    def test_update_not_owner(self):
        '''not update for not owner of the book'''
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 300,
                "author_name": self.book_1.author_name}
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        '''Update for not owner but for stuff'''
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": 'Test for Changes',
                "price": 200,
                "author_name": 'Test for one mo changes'}
        json_data = json.dumps(data)
        self.client.force_login(self.user_stuff)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(data["name"], self.book_1.name)
        self.assertEqual(data["price"], self.book_1.price)
        self.assertEqual(data["author_name"], self.book_1.author_name)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        count_id = Book.objects.filter(pk=self.book_1.id).count()
        self.assertEqual(0, count_id)

    def test_delete_not_owner(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        count_id = Book.objects.filter(pk=self.book_1.id).count()
        self.assertEqual(1, count_id)


class BookRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_user')
        self.user2 = User.objects.create(username='test_user2')
        self.user_stuff = User.objects.create(username='test_suff_user',
                                              is_staff=True)
        self.book_1 = Book.objects.create(name='Test Book 1',
                                          price=25, author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Test Book 2',
                                          price=55, author_name='Author 5',
                                          owner=self.user)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {"like": True,
                "in_bookmarks": True}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json'
                                     )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {"rate": 4}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json'
                                     )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(4, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {"rate": 6}
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json'
                                     )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
