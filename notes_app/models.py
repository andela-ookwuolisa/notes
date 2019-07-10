from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
    )

    def __repr__(self):
        return self.title

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in self.__dict__.keys()
            if k != '_state'
        }
