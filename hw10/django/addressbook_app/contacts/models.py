from django.db import models
from django.urls import reverse


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class Contact(models.Model):

    first_name = models.CharField(
        max_length=255,
    )
    last_name = models.CharField(
        max_length=255,

    )

    email = models.EmailField()

    def get_absolute_url(self):
        return reverse('contacts-view', kwargs={'pk': self.id})

    def __str__(self):

        return ' '.join([
            self.first_name,
            self.last_name,
        ])


class Address(models.Model):

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    address_type = models.CharField(
        max_length=10,
    )

    address = models.CharField(
        max_length=255,
    )
    city = models.CharField(
        max_length=255,
    )
    state = models.CharField(
        max_length=2,
    )
    postal_code = models.CharField(
        max_length=20,
    )

    class Meta:
        unique_together = ('contact', 'address_type',)
