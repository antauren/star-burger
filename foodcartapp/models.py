import datetime as dt

from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import DecimalField, F, Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        db_index=True,
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
        db_index=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects.filter(availability=True).values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        db_index=True,
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        db_index=True,
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def get_total_amount(self):
        return self.annotate(
            total_amount=Sum(
                F('items__price') * F('items__quantity'),
                output_field=DecimalField(max_digits=8, decimal_places=2)
            )
        )


class Order(models.Model):
    STATUS_CHOICES = (
        ('unprocessed', 'Необработанный'),
        ('processed', 'Обработанный'),
    )

    PAYMENT_CHOICES = (
        ('cash', 'Наличностью'),
        ('card', 'Электронно'),
        ('not_selected', 'Не выбран'),
    )
    address = models.CharField('Адрес', max_length=100)
    firstname = models.CharField('Имя', max_length=20)
    lastname = models.CharField('Фамилия', max_length=20)
    phonenumber = PhoneNumberField('Телефон')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='unprocessed')
    comment = models.TextField('Комментарий', blank=True)
    registered_at = models.DateTimeField('Время заказа', auto_now=True)
    called_at = models.DateTimeField('Время звонка', )
    delivered_at = models.DateTimeField('Время доставки', )
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES, default='not_selected')

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return '{} {} {}'.format(self.firstname[:10], self.lastname[:10], self.address[:10])

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='Товар')
    quantity = models.PositiveSmallIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Содержимое заказа'
        unique_together = [
            ['order', 'product']
        ]
