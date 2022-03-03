from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate , login,logout
from django.contrib.auth.forms import UserCreationForm 
from django.db.models import Q
from .models import Room ,Topic , Message
from django.contrib.auth.models import User
from .forms import RoomForm


'''
rooms=[
    {'id':1,'name':'pythonlearning'},
    {'id':2,'name':'phplearning'},
    {'id':3,'name':'javascriptlearning'}
    ]
'''

# Create your views here.

def loginPage(request):


    if request.user.is_authenticated:
        return redirect('home')

    page='login'
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(username=username)

        except:  
            messages.error(request,'user does not exist')  

        user=authenticate(request,username=username,password=password)    
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'username or password is not correct') 
    
    return render(request,'base/login-register.html',{'page':page})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'an error occurred')


    return render(request,'base/login-register.html',{'form':form})
def home(request):
    q= request.GET.get('q') if request.GET.get('q') !=None else ''
    #__icontains =means that the word has those chars
    rooms=Room.objects.filter(Q(topic__name__icontains=q)| Q(name__icontains=q)| Q(description__icontains=q))
    topics=Topic.objects.all()
    rooms_count=rooms.count()
    context={'rooms':rooms,'topics':topics,'rooms_count':rooms_count}
    return render(request,'base/index.html',context)

def room(request,pk):
    '''
    room=None
    for i in rooms:
        if i['id']==int(pk):
            room=i
            '''
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('created')
    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
            )
        return redirect('room',pk=room.id)
    context={'room':room,'room_messages':room_messages}
    return render(request,'base/room.html',context)

@login_required(login_url='login')
def createRoom(request):
    form= RoomForm()
    context={'form':form}
    if request.method=='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return  render(request,'base/room_form.html',context)  

def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)

    if request.user != room.host:
        return  HttpResponse('you are not allowed here')



    if request.method == 'POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context={'form':form}
    return  render(request,'base/room_form.html',context) 
@login_required(login_url='login')
def deleteRoom(request, pk):
    room=Room.objects.get(id=pk)
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})