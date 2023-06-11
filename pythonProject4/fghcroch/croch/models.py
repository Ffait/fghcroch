import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from croch.utils import unique_slugify
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField


class Products(models.Model):
    name = models.CharField('Название', max_length=100)
    content = models.TextField('Описание', blank=True, null=True)
    structure = models.CharField('Состав', blank=True, null=True, max_length=100)
    thickness = models.FloatField('Толщина инструмента', blank=True, null=True)
    tr_length = models.FloatField('Длина нити', blank=True, null=True)
    material = models.CharField('Материал', blank=True, null=True, max_length=100)
    size = models.FloatField('Размер', blank=True, null=True)
    color = models.CharField('Цвет', blank=True, null=True, max_length=100)
    photo = models.ImageField('Фото', upload_to='product/', blank=True)
    price = models.FloatField('Цена', max_length=10, null=True)
    cat = models.ForeignKey('Category', verbose_name="Категория", on_delete=models.PROTECT)
    slug = models.SlugField('URL', max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Category(models.Model):
    name = models.CharField('Категория', max_length=50)
    slug = models.SlugField('URL', max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatar/',
        default='woman.jpg',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    class Meta:
        db_table = 'app_profiles'
        ordering = ('user',)
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'profile_detail': self.slug})

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Feedback(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    email = models.EmailField(max_length=255, verbose_name='E-mail')
    content = models.TextField(verbose_name='Содержимое письма')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    ip_address = models.GenericIPAddressField(verbose_name='IP отправителя',  blank=True, null=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-time_create']
        db_table = 'app_feedback'

    def __str__(self):
        return f'Письмо от {self.email}'


class Comment(MPTTModel):

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Продукт', related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE, related_name='comments_author')
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class MTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-time_create', 'time_update', 'status', 'parent'])]
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}:{self.content}'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f'{self.user}'

    def total_items_by_product_type(self):
         return len(self.cartitem_set.all())

    @receiver(post_save, sender=User)
    def create_user_cart(sender, instance, created, **kwargs):
        if created:
            Cart.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_cart(sender, instance, **kwargs):
        instance.cart.save()


class Cartitem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    cover = models.ImageField(upload_to='product/')
    prod_id = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f'{self.name} + {self.id}'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=settings.PAYMENT_METHODS, verbose_name='Метод оплаты', default='Банковская карта')
    delivery_method = models.CharField(max_length=50, choices=settings.DELIVERY_METHODS, verbose_name='Доставка',  default='Самовывоз')
    status = models.CharField(max_length=50, choices=settings.DELIVERY_STATUSES, default='Заказ подтвержден')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    cover = models.ImageField(upload_to='product/')
    price = models.FloatField()


class Payment(models.Model):
    cc_number = CardNumberField('Номер карты')
    cc_expiry = CardExpiryField('Срок действия')
    cc_code = SecurityCodeField('CVV/CVC')
    order = models.ForeignKey("Order", verbose_name="Заказ", on_delete=models.CASCADE, null=True, blank=True)




