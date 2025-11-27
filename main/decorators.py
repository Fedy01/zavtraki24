from django.contrib.auth.decorators import user_passes_test

def manager_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name="manager").exists())(view_func)

def courier_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name="courier").exists())(view_func)

def kitchen_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name="kitchen").exists())(view_func)