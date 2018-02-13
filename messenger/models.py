from django.db import models

# Create your models here.

class Message(models.Model):
    message_text = models.CharField(max_length=2000)
    sent_date = models.DateTimeField('Date Sent')
    # user = models.ForeignKey(User)
    is_sent_by_user = models.BooleanField

    def __str__(self):
        return self.message_text

