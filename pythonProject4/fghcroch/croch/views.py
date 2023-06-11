from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import *
from django.urls import reverse_lazy
from django.views.generic import *

from .email import send_contact_email_message
from .forms import *
from .models import *


class CrochHome(ListView):
    model = Products
    context_object_name = 'products'
    template_name = 'croch/index.html'
    extra_context = {'title': 'Главная страница'}
    paginate_by = 9


def about(request):
    context = {'title': 'Контакты'}
    return render(request, 'croch/contacts.html', context=context)


class ShowProducts(DetailView):
    model = Products
    template_name = 'croch/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'
    extra_context = {'title': 'Продукт'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.object.name
        context['form'] = CommentCreateForm
        return context


def product_detail(request, product_id):
    product = Products.objects.get(id=product_id)
    user_cart = Cart.objects.get(user=request.user)
    form = CartItemForm()
    context = {'product': product, 'form': form, 'cart': user_cart}
    return render(request, 'croch/cart.html', context)


def cart_add(request, product_id):
    product = Products.objects.get(id=product_id)
    form = CartItemForm(data=request.POST)

    # if form.is_valid():
    Cart.objects.get_or_create(user=request.user)
    user_cart = Cart.objects.get(user=request.user)
    # try:
    #     item = Cartitem.objects.filter(cart=user_cart).get(prod_id=int(product.pk))
    #     print("1")
    # except Cartitem.DoesNotExist:
    print("2")
    new_item = form.save(commit=False)
    new_item.name = product.name
    new_item.price = product.price
    new_item.cart = user_cart
    new_item.cover = product.photo
    new_item.product_id = product.id
    new_item.save()
    # else:
        # add_num = form.save(commit=False)
        # item.quantity += add_num.quantity
        # item.save()
    return redirect('cart')



def cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = Cartitem.objects.filter(cart=cart)
    form = CartItemForm(instance=Cartitem)
    context = {'cart': cart, 'cart_items': cart_items, 'form': form}
    context['title'] = 'Корзина'
    return render(request, 'croch/cart.html', context)


def item_update(request, item_id):
    item = Cartitem.objects.get(id=item_id)
    form = CartItemForm(data=request.POST)
    new_num = form.save(commit=False)
    item.save()
    return redirect('cart')


def item_delete(request, item_id):
    item = Cartitem.objects.get(id=item_id)
    item.delete()
    return redirect('cart')


def create_order(request):
    user_cart = Cart.objects.get(user=request.user)
    cart_items_list = Cartitem.objects.filter(cart=user_cart)
    if request.method != 'POST':
        form = OrderForm()
    else:
        form = OrderForm(data=request.POST)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.user = request.user
            new_order.status = str('To be confirmed')
            new_order.save()
            for item in cart_items_list:
                # item_quantity = item.quantity
                item_cover = item.cover
                item_name = item.name
                item_price = item.price
                OrderItem(order=new_order, name=item_name, cover=item_cover, price=item_price).save()
                item.delete()
            return redirect('home')
    context = {'cart_items': cart_items_list, 'form': form}
    context['title'] = 'Заказ'
    return render(request, 'croch/order.html', context)


class ProdCategory(ListView):
    model = Products
    template_name = 'croch/index.html'
    context_object_name = 'products'
    extra_context = {'title': 'Товары'}
    paginate_by = 3

    def get_queryset(self):
        return Products.objects.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')


class AddProd(CreateView):
    form_class = AddProdForm
    template_name = 'croch/add_prod.html'
    extra_context = {'title': 'Добавление товара'}


class UpdateProd (UpdateView):
    form_class = AddProdForm
    model = Products
    template_name = "croch/update_prod.html"
    slug_url_kwarg = "product_slug"
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Редактирование товара'}


class DeleteProd (DeleteView):
    model = Products
    slug_url_kwarg = "product_slug"
    template_name = "croch/delete_prod.html"
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Удаление продукта'}



class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'croch/register.html'
    success_url = reverse_lazy('login')
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'croch/login.html'
    extra_context = {'title': 'Войти'}


def logout_user(request):
    logout(request)
    return redirect('login')


class ProfileDetailView(DetailView):
    model = Profile
    context_object_name = 'profile'
    slug_url_kwarg = 'profile_detail'
    template_name = 'croch/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Страница пользователя: {self.object.user.username}'
        return context


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    slug_url_kwarg = 'profile_detail'
    template_name = 'croch/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'profile_detail': self.object.slug})


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'croch/user_password_change.html'
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение пароля'
        return context

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'profile_detail': self.request.user.profile.slug})


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = ContactForm
    template_name = 'croch/support.html'
    extra_context = {'title': 'Контактная форма'}
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if form.is_valid():
            feedback = form.save(commit=False)
            if self.request.user.is_authenticated:
                feedback.user = self.request.user
            send_contact_email_message(feedback.subject, feedback.email, feedback.content, feedback.user_id)
        return super().form_valid(form)


class CommentCreateView (LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.product_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.product.get_absolute_url())

class PaymentView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'croch/payment.html'
    extra_context = {'title': 'Оплата'}
    success_url = reverse_lazy('home')


class Cheque(DetailView):
    model = Order
    template_name = 'croch/cheque.html'
    extra_context = {'title': 'Чек об оплате'}
    success_url = reverse_lazy('home')
