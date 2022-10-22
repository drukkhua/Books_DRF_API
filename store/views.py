from django.db.models import F
from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        owner_name=F('owner__username')) \
        .prefetch_related('readers')
    # select_related('owner') - выберет связанный 1 объект по ForeignKey
    # prefetch_related('reders') - работает по связям manytomany
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    # http://127.0.0.1:8000/book/?price=1000
    filterset_fields = ['price']

    # http://127.0.0.1:8000/book/?search Author
    search_fields = ['name', 'author_name']

    # http://127.0.0.1:8000/book/?ordering=price or -price
    ordering_fields = ['price', 'author_name']

    # Прилинковка создателя(юзера) к книге при создании
    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin,
                           GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                              book_id=self.kwargs['book'])
        return obj


def auth(request):
    return render(request, 'oauth.html')
