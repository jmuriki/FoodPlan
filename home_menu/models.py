from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Dish(models.Model):
    title = models.CharField('Название', max_length=50)
    description = models.TextField('Описание')
    image = models.ImageField('Изображение')
    category = models.ForeignKey('Category', verbose_name='Категория', on_delete=models.CASCADE)
    product = models.ManyToManyField('Product', verbose_name='Состав')

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
    weight = models.IntegerField('Количество грамм')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title


class Allergy(models.Model):
    title = models.CharField('Название', max_length=50)

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'

    def __str__(self):
        return self.title


class Customer(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    promo_code = models.ManyToManyField('PromotionalCode', verbose_name='Промо-код', blank=True)
    image = models.ImageField('Фото')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.user.username


class PromotionalCode(models.Model):
    title = models.CharField('Название', max_length=50, unique=True)
    valid_until = models.DateTimeField('Годен до', blank=True, null=True)

    class Meta:
        verbose_name = 'Промо-код'
        verbose_name_plural = 'Промо-коды'

    def __str__(self):
        return self.title


class Subscription(models.Model):
    customer = models.ForeignKey('Customer', verbose_name='Клиент', related_name='subscriptions', on_delete=models.CASCADE)
    title = models.CharField('Название', max_length=50)
    description = models.TextField('Описание')
    persons = models.PositiveIntegerField('Количество персон', validators=[MaxValueValidator(6)])
    allergy = models.ManyToManyField('Allergy', verbose_name='Аллергия', blank=True)
    calories = models.IntegerField('Калории')
    number_meals = models.PositiveIntegerField('Количество приемов пищи', validators=[MaxValueValidator(4)])
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2, db_index=True, validators=[MinValueValidator(0)])
    type_dish = models.ForeignKey('Category', verbose_name='Тип блюда', on_delete=models.CASCADE)
    promo_code = models.ManyToManyField('PromotionalCode', verbose_name='Промо-код', blank=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.title
