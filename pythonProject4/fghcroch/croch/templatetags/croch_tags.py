from django import template
from croch.models import *

register = template.Library()

@register.simple_tag(name='getcats')
def get_categories():
    return Category.objects.all()

@register.inclusion_tag('croch/list_categories.html')
def show_categories():
    cats = Category.objects.all()
    return {"cats": cats}