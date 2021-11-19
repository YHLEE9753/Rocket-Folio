from django.shortcuts import redirect, render
from .models import Account


def login(request):
    return render(request, "login.html")

def register1(request):
    django_user = request.user
    if django_user:
        try: # 로켓폴리오 계정이 있을 경우
            account = Account.objects.get(user = django_user)
        except Account.DoesNotExist:
            account = 0
        if account: # google 회원가입 정보가 있고, Account도 있는 경우
            return redirect('myportfolio')
        # 로켓폴리오 계정이 없을 경우
        else:
            if request.method == "POST":
                nickname = request.POST.get('nickname')
                email = request.POST.get('email')
                new_account = Account()
                new_account.user = request.user
                new_account.user.email = email
                new_account.nickname = nickname
                new_account.save()
                return redirect('myportfolio')
            return render(request,"register1.html")
    else:
        return render(request,"register1.html")