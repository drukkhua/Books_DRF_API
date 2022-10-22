from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    name = models.CharField(max_length=255,
                            verbose_name='Название книги')
    price = models.DecimalField(max_digits=7,
                                decimal_places=2,
                                verbose_name='Цена')
    author_name = models.CharField(max_length=255,
                                   verbose_name='Имя автора')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation',
                                     related_name='books')

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'ID: {self.id}; {self.name}; Price:{self.price}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}: Price:{self.book.name}, RATE: {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating

        creating = not self.pk
        old_rating = None
        if not creating:
            old_rating = UserBookRelation.objects.get(id=self.id).rate

        super().save(*args, **kwargs)

        new_rating = self.rate
        if new_rating != old_rating:
            set_rating(self.book)
