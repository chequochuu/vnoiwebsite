from django.db import models
from django_bleach.models import BleachField
from forum.models import Forum

class SpojProblemCategory(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __unicode__(self):
        return self.name


class SpojCluster(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class SpojProblemTag(models.Model):
    name = models.CharField(max_length=20, null=True, blank=False)

    def __unicode__(self):
        return self.name


class SpojProblemLanguage(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    lang_id = models.IntegerField(null=False, blank=False)

    def __unicode__(self):
        return self.name


class SpojProblem(models.Model):
    category = models.ForeignKey(SpojProblemCategory, related_name='problems', null=True, blank=True, on_delete=models.SET_NULL)
    problem_id = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=250, null=False, blank=False)
    code = models.CharField(max_length=20, null=False, blank=False)
    accept_count = models.IntegerField(null=False, blank=False, default=0)
    accept_rate = models.FloatField(null=False, blank=False, default=0.0)
    score = models.FloatField(null=False, blank=False, default=2.0)
    statement = BleachField(null=True,
                            allowed_tags=[
                                'p', 'strong', 'em', 'pre', 'code', 'a', 'img', 'ol', 'ul', 'li', 'span', 'i', 'sub',
                                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'sub', 'sup'
                            ],
                            allowed_attributes=['href', 'class', 'alt', 'style', 'src'],
                            strip_tags=False)
    author = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateField(null=True, blank=True, auto_now_add=True)
    # Time limit in second
    time_limit = models.FloatField(null=False, blank=False, default=1)
    # Source code limit in bytes
    source_limit = models.IntegerField(null=False, blank=False, default=50000)
    # Memory limit in MB
    memory_limit = models.IntegerField(null=False, blank=False, default=1536)
    # Allowed languages
    allowed_languages = models.ManyToManyField(SpojProblemLanguage, related_name='+', null=True, blank=True)
    # Problem's tags
    tags = models.ManyToManyField(SpojProblemTag, related_name='problems', null=True, blank=True)
    # Problem's source
    problem_source = models.CharField(max_length=1024, blank=True, null=True)
    # Cluster (doesn't need anymore)
    cluster = models.ForeignKey(SpojCluster, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name


class SpojProblemForum(Forum):
    # Assumption: forum name must be equal to problem code.
    # This is used in get_absolute_url in forum.models.Forum
    problem = models.ForeignKey(SpojProblem, related_name='forum', null=True, blank=True, on_delete=models.SET_NULL)
