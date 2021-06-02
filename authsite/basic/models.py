import os
# import pickle
import face_recognition as fr
from uuid import uuid4
from PIL import UnidentifiedImageError
from django.db import models
from django.core.files import File
from django.conf import settings
from django.dispatch import receiver
# Create your models here.


class Voter(models.Model):
    pid = models.CharField('ID Number', max_length=9, unique=True)
    birth = models.DateField('Birth Date')
    image = models.FileField('Face Image')
    voted = models.BooleanField(default=False)
    session = models.CharField(max_length=32, null=True)


@receiver(models.signals.post_delete, sender=Voter)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Voter)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if instance.pk:
        old_file = Voter.objects.get(pk=instance.pk).image
        new_file = instance.image
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)


@receiver(models.signals.post_save, sender=Voter)
def auto_generate_face_encoding(sender, instance, **kwargs):
    try:
        im = fr.load_image_file(instance.image)
        loc = fr.face_locations(im)
        enc = fr.face_encodings(im, loc)[0]
        del im
        del loc
        temp_path = os.path.join(settings.MEDIA_ROOT, str(uuid4()))
        enc.tofile(temp_path, " ")
        models.signals.post_save.disconnect(auto_generate_face_encoding, sender=Voter)
        instance.image.save(str(uuid4()), File(open(temp_path)), save=True)
        models.signals.post_save.connect(auto_generate_face_encoding, sender=Voter)
        os.remove(temp_path)
    except UnidentifiedImageError:
        pass
    finally:
        pass
