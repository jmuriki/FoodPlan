from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Dish(models.Model):
    title = models.CharField('Название', max_length=50)
    description = models.TextField('Описание')
    image = models.ImageField('Изображение')
    category = models.ForeignKey('Category', verbose_name='Категория', on_delete=models.CASCADE)
    product = models.ManyToManyField('Product', verbose_name='Состав')
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2, db_index=True, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'

    def __str__(self):
        return self.title



class Category(models.Model):	
    title = models.CharField('Название', max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField('Название', max_length=50)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title


class Subscription(models.Model):
    class ChoicesAllergy(models.TextChoices):
        No = 'Нет', 'Нет'
        Seafood = 'Рыба и морепродукты', 'Рыба и морепродукты'
        Cereals = 'Мясо', 'Мясо'
        Beekeeping = 'Зерновые', 'Зерновые'
        Nuts = 'Продукты пчеловодства', 'Продукты пчеловодства'
        Meat = 'Орехи и бобовые', 'Орехи и бобовые'
        Dairy = 'Молочные продукты', 'Молочные продукты'

    title = models.CharField('Название', max_length=50)
    description = models.TextField('Описание')
    persons = models.PositiveIntegerField('Количество персон', validators=[MaxValueValidator(6)])
    allergy = models.CharField('Аллергии', max_length=50, choices=ChoicesAllergy.choices)
    calories = models.IntegerField('Калории')
    number_meals = models.PositiveIntegerField('Количество приемов пищи', validators=[MaxValueValidator(4)])
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2, db_index=True, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.title
