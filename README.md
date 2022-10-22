# Books_DRF_API
Django DRF API project with annotate, AVG, select_related, prefetch_related, F, calculating with SQL &amp; in model.

- <a href="https://github.com/drukkhua/Books_DRF_API/tree/model_calculate"><h2>Branch: model_calculate:</h2></a> Rate field of the book, calculating when changed UserBookRelation table.

        class UserBookRelation(models.Model):
        ...
        
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

- <a href="https://github.com/drukkhua/Books_DRF_API/tree/sql_calculate"><h2>Branch: sql_calculate:</h2></a> Rate field of the book calculating in the table:

        queryset = Book.objects.all().annotate(
                   annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                   rating=Avg('userbookrelation__rate'),
                   owner_name=F('owner__username'))
                   .prefetch_related('readers')
