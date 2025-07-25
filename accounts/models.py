from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User


class Medicine(models.Model):
    TYPE_CHOICES = (
        ('1', '树脂'),
        ('2', '溶剂'),
        ('3', '粉末'),
        ('4', '固化剂'),
        ('5', '添加剂'),
        ('6', '其他'),
    )

    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='标签编号',
        error_messages={
            'unique': '该编号已存在，请输入不同的编号。'
        }
    )
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    cas_number = models.CharField(max_length=50, verbose_name="CAS号", blank=True, null=True)
    specification = models.CharField(max_length=100, verbose_name="规格", blank=True, null=True)
    unit = models.CharField(max_length=50, verbose_name="单位", blank=True, null=True)
    quantity = models.FloatField(default=0.0, verbose_name="数量", blank=True, null=True)
    manufacturer = models.CharField(max_length=100, verbose_name="生产厂家", blank=True, null=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'cas_number', 'manufacturer'],
                name='unique_name_cas_manufacturer'
            ),
        ]

    def clean(self):
        # 如果某些字段为空，不进行唯一性校验
        if all([self.name, self.cas_number, self.manufacturer]):
            if Medicine.objects.filter(
                name=self.name,
                cas_number=self.cas_number,
                manufacturer=self.manufacturer
            ).exclude(pk=self.pk).exists():
                raise ValidationError({'name': '该药品名称 + CAS号 + 生产厂家的组合已存在'})

    def __str__(self):
        return f"{self.name} - {self.code}"


class Recipe(models.Model):
    name = models.CharField(max_length=255, verbose_name="配方名称")
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    def __str__(self):
        return self.name

class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255, verbose_name="药品名称")
    manufacturer = models.CharField(max_length=255, null=True, blank=True, verbose_name="厂商")
    cas = models.CharField(max_length=255, null=True, blank=True, verbose_name="CAS")
    amount = models.FloatField(default=0, verbose_name="克数")
