from django import template

register = template.Library()

@register.filter(name='getTimeDiff')  # You can also just use @register.filter
def getTimeDiff(value):

    days = value.days

    if days > 0:
        return f"{days} days"
    else:
        values = str(value).split()
        return f"{values[-1]}"