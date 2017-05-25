from datetime import *

from django.utils.termcolors import colorize


def log(msg, color="green"):
    print(colorize("[" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "] " + str(msg), fg=color))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
