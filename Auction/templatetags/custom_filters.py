from django import template
from datetime import datetime
from ..utils import getTimestamp

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


@register.filter(name='auctionStatus')
def auctionStatus(startTimestamp, endTimestamp):
    currTime = datetime.strptime(getTimestamp().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
    if startTimestamp > currTime:
        return "Upcoming"
    elif endTimestamp < currTime:
        return "Closed"
    else:
        return "Ongoing"