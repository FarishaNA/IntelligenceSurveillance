from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.hashers import check_password

# Create your views here.


def index(request):
    return render(request, "index.html")


def login(request):
    if request.method == "POST":
        email = request.POST['name']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user is not None:
            request.session['email'] = email
            if user.is_active:
                if user.is_superuser:
                    return redirect("/adminHome")
                else:
                    sf = Users.objects.get(email=email)
                    request.session['id'] = sf.id
                    return redirect("/sfHome")
            else:
                msg = "Account is not Active..."
                return render(request, "login.html", {"msg": msg})
        elif user is None and User.objects.filter(username=email).exists() and check_password(password, User.objects.get(username=email).password):
            msg = "Blocked by admin..."
        elif user is None and User.objects.filter(username=email).exists():
            msg = "Invalid password..."
        else:
            msg = "User dosent exists..."
        return render(request, "login.html", {"msg": msg})
    else:
        return render(request, "login.html")


def sfReg(request):
    flag = 0
    msg = ""
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        img = request.FILES["file"]

        if User.objects.filter(username=email).exists():
            msg = "Email already exists..."

        else:
            user = User.objects.create_user(
                username=email, password=password, is_active=1)
            user.save()
            
            sf = Users.objects.create(
                name=name, email=email, phone=phone, address=address, document=img, user=user)
            sf.save()
            msg = "Registration Successful..."
            flag = 1

    return render(request, "sfReg.html", {"msg": msg, "flag": flag})


def adminHome(request):
    return render(request, "adminHome.html")


def adminStartUp(request):
    data = Users.objects.filter(user__is_active=0)
    dataActive = Users.objects.filter(user__is_active=1)
    return render(request, "adminStartup.html", {"data": data, "dataActive": dataActive})


def approveStartUp(request):
    id = request.GET['id']
    status = request.GET['status']
    sf = User.objects.get(id=id)
    sf.is_active = status
    sf.save()
    return redirect("/adminStartUp")


def adminViewFeedback(request):

    data = Feedback.objects.all()
    return render(request, "adminViewFeedback.html", {"data": data})


def adminViewDetections(request):

    data = Detection.objects.all()
    return render(request, "adminViewDetections.html", {"data": data})


def adminViewChatDetections(request):
    data = ChatDetection.objects.all()
    users = Users.objects.all()
    return render(request, "adminViewChatDetections.html", {"data": data, "users": users})

def adminViewCommentDetections(request):
    data = CommentDetection.objects.all()
    return render(request, "adminViewCommentDetections.html", {"data": data})

def adminViewReportedComment(request):
    data = CommentReport.objects.all()
    return render(request, "adminViewReportedComment.html", {"data": data})

def adminDeleteReportedComment(request):
    id = request.GET['id']
    data = Comments.objects.get(id=id)
    data.delete()
    return redirect("/adminViewReportedComment")

def adminIgnoreReportedComment(request):
    id = request.GET['id']
    data = CommentReport.objects.get(id=id)
    data.delete()
    return redirect("/adminViewReportedComment")

def adminViewReportedPost(request):
    data = PostReport.objects.all()
    return render(request, "adminViewReportedPost.html", {"data": data})

def adminIgnoreReportedPost(request):
    id = request.GET['id']
    data = PostReport.objects.get(id=id)
    data.delete()
    return redirect("/adminViewReportedPost")

def adminDeleteReportedPost(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    data.delete()
    return redirect("/adminViewReportedPost")


def sfHome(request):
    id = request.session['id']

    data = Users.objects.get(id=id)
    post = Post.objects.exclude(user=id).order_by("-id")
    if request.method == "POST":
        search = request.POST['search']
        post = Post.objects.filter(idea__contains=search).exclude(
            user=id).order_by("-id")
    return render(request, "sfHome.html", {"data": data, "post": post})


def sfProfile(request):
    id = request.session['id']

    data = Users.objects.get(id=id)
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        password = request.POST['password']
        proUp = Users.objects.get(id=id)
        proUp.name = name
        proUp.email = email
        proUp.phone = phone
        proUp.address = address
        proUp.save()
        logUp = User.objects.get(username=data.user)
        logUp.set_password(password)
        logUp.username = email
        logUp.save()
        return redirect("/sfHome")
    return render(request, "sfProfile.html", {"data": data})


def sfChangeImage(request):
    id = request.session['id']
    data = Users.objects.get(id=id)
    if request.method == "POST":
        img = request.FILES["file"]

        data.document = img
        data.save()
        return redirect("/sfHome")
    return render(request, "sfChangeImage.html", {"data": data})


def sfPost(request):
    id = request.session['id']
    user = Users.objects.get(id=id)
    msg = ''
    if request.method == "POST":
        idea = request.POST['idea']
        description = request.POST['description']
        img = request.FILES['img']
        from bad_word_detector import main as check
        resultTitle = check(idea)
        resultDesc = check(description)
        if resultDesc == 'Good' and resultTitle == 'Good':
            db = Post.objects.create(
                idea=idea, desc=description, user=user, img=img)
            db.save()
        else:
            det = Detection.objects.create(
                user=user, title=idea, desc=description)
            det.save()
            msg = "Offensive language used. Cant post the content"

    return render(request, "sfPost.html", {"msg": msg})


def sfViewSelfPost(request):
    id = request.session['id']

    data = Post.objects.filter(user=id).order_by("-id")
    return render(request, "sfViewSelfPost.html", {"data": data})


def sfUpdateIdea(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    if request.method == "POST":
        idea = request.POST['idea']
        description = request.POST['description']
        data.idea = idea
        data.desc = description
        data.save()
        return redirect("/sfViewSelfPost")
    return render(request, "sfUpdateIdea.html", {"data": data})


def sfDeleteIdea(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    data.delete()

    return redirect("/sfViewSelfPost")


def sfViewIdea(request):
    id = request.GET['post']
    sfid = request.session['id']
    msg = ''
    data = Post.objects.get(id=id)
    if request.method == "POST":
        comment = request.POST['comment']
        from bad_word_detector import main as check
        result = check(comment)
        user = Users.objects.get(id=sfid)
        if result == 'Good':
            db = Comments.objects.create(comment=comment, idea=data, user=user)
            db.save()
        else:
            det = CommentDetection.objects.create(user=user, post=data, comment=comment)
            det.save()
            msg = "Offensive language used. Cant post the comment"
    comments = Comments.objects.filter(idea=id)
    commentReports = CommentReport.objects.all()
    cmtReports = []
    for i in commentReports:
        cmtReports.append(i.comment.id)
    postsReps = PostReport.objects.all()
    posReps = []
    for i in postsReps:
        posReps.append(i.post.id)
    return render(request, "sfViewIdea.html", {"data": data, "comments": comments, "msg":msg, "commentReports": cmtReports, "postsReps": posReps})



def sfViewSf(request):
    id = request.GET['sfid']
    user = Users.objects.get(id=id)

    post = Post.objects.filter(user=id)
    return render(request, "sfViewSf.html", {"user": user, "post": post})


def sfAddFeedBack(request):
    id = request.session['id']
    if request.method == "POST":
        feedback = request.POST['feedback']
        user = Users.objects.get(id=id)

        db = Feedback.objects.create(feedback=feedback, user=user)
        db.save()
    data = Feedback.objects.filter(user=id)
    return render(request, "sfAddFeedBack.html", {"data": data})


def sfChat(request):
    sender = request.session["email"]
    data = Chat.objects.filter(
        Q(sender=sender) | Q(receiver=sender)).distinct()
    emails = []
    for i in data:
        emails.append(i.receiver)
        emails.append(i.sender)
    emails = set(emails)
    emails = list(emails)
    data = emails
    users = Users.objects.all()
    return render(request, "sfChat.html", {"data": data, "user": sender, "users":users})


def sfChatPer(request):
    sender = request.session['email']
    receiver = request.GET['email']
    sen = Users.objects.get(email=sender)
    if request.method == "POST":
        msg = request.POST['msg']
        from bad_word_detector import main as check
        result = check(msg)
        if result == 'Good':
            db = Chat.objects.create(
                sender=sender, receiver=receiver, message=msg)
            db.save()
        else:
            det = ChatDetection.objects.create(
                user=sen, receiver=receiver, message=msg)
            det.save()
    messages = Chat.objects.filter(
        Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender))
    return render(request, "sfChatPer.html", {"messages": messages, "user": sender,"receiver": receiver})


def sfReportComment(request):
    id = request.GET['id']
    data = Comments.objects.get(id=id)
    user = Users.objects.get(id=request.session['id'])
    det = CommentReport.objects.create(user=user, comment=data)
    det.save()
    return redirect("/sfViewIdea?post="+str(data.idea.id))

def sfReportPost(request):
    id = request.GET['id']
    data = Post.objects.get(id=id)
    user = Users.objects.get(id=request.session['id'])
    det = PostReport.objects.create(user=user, post=data)
    det.save()
    return redirect("/sfViewIdea?post="+str(data.id))

def block_user(request):
    sender = request.session['email']
    receiver = request.GET.get('email')
    
    # Block logic: Set canChat = False and blockedBy = sender
    Chat.objects.filter(
        Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
    ).update(canChat=False, blockedBy=sender)

    return redirect(f'/sfChatPer?email={receiver}')

def unblock_user(request):
    sender = request.session['email']
    receiver = request.GET.get('email')
    
    # Unblock logic: Reset canChat and blockedBy
    Chat.objects.filter(
        Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender),
        blockedBy=sender
    ).update(canChat=True, blockedBy=None)

    return redirect(f'/sfChatPer?email={receiver}')