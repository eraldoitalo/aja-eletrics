def interface(request):
    user = request.user
    administrative = user.is_authenticated and user.is_administrative
    commercial = user.is_authenticated and (administrative or user.role == 'seller')
    return {'administrative': administrative, 'commercial': commercial,
        'theme': 'dark' if request.COOKIES.get('aja_theme') == 'dark' else 'light'}
