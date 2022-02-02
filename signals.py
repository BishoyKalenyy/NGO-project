from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import NGO, profile

from django.core.mail import send_mail
from django.conf import settings




#@receiver(post_save, sender=profile)
#def create_profile(sender, instance, created, **kwargs):
    #if created:
       #profile.objects.create(user=instance)
    #instance.profile.save
#@receiver(post_save, sender=User)
#def create_profile(sender, instance, created, **kwargs):
   # if created:
       # NGO.objects.create(user=instance)
   # instance.NGO.save

#@receiver(post_save, sender=User)
#def save_NGO(sender, instance, **kwargs):
    #instance.NGO.save()
def createNGO(sender, instance, created, **kwargs):
    if created:
        user = instance
        ngo = NGO.objects.create(
            user=user,
        )

post_save.connect(createNGO, sender=User)