from django import template

register = template.Library()

@register.filter(name='getTimeDiff')
def getTimeDiff(seconds):

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if days > 0:
        return f"{days} days"
    else:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    
@register.filter(name='add')
def add(value, num):

    return f"{value + num}"