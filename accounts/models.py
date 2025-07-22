# myapp/models.py
from django.db import models
from django.core.exceptions import ValidationError

class Medicine(models.Model):
    TYPE_CHOICES = (
        ('1', '树脂'),
        ('2', '溶剂'),
        ('3', '粉末'),
        ('4', '固化剂'),
        ('5', '添加剂'),
        ('6', '其他'),
    )

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)

    def clean(self):
        if Medicine.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': '该药品名称已存在'})
        if Medicine.objects.filter(code=self.code).exclude(pk=self.pk).exists():
            raise ValidationError({'code': '该药品编号已存在'})

    def __str__(self):
        return f"{self.name} - {self.code}"
