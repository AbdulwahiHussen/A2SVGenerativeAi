from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from  quiz_app.api import api_caller
from bardapi import Bard
from .models import CustomUser, Message
from quiz_app.file_processor import file_reader, file_summerizer, file_chunk
from .generator import get_question
import urllib.parse

import json
#import api_request
# Create your views here.

def handle_upload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        num_of_questions = request.POST.get('qnumber')
        difficulty = request.POST.get('difficulty')
        spage = int(request.POST.get('spage'))
        epage = int(request.POST.get('epage'))
        generator = get_question(file, num_of_questions, difficulty, spage, epage)
        



def user_register(request):
    if request.method == "POST":
        full_name = request.POST.get("fullname")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        carrier = request.POST.get("profession")
        gender = request.POST.get("gender")
        
        try:
            existing_user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            existing_user = None
        
        if password1 == password2 and not existing_user:
            user = CustomUser.objects.create(username=email, password=password2, email=email, carrier=carrier, gender=gender, first_name=full_name)
            user.save()
            return redirect('quiz')
        elif existing_user:
            return render(request, 'registeration.html', {'error': 'A user with this email is already registered.'})
        else:
            return render(request, 'registeration.html', {'error': 'Passwords did not match.'})
        
    return render(request, 'registeration.html')


@login_required(login_url='login')
def home(request):
    user = request.user
    if request.method == "POST":
        uploaded_file = request.FILES['file']
        num_of_questions = request.POST.get('qnumber')
        difficulty = request.POST.get('difficulty')
        spage = int(request.POST.get('spage'))
        epage = int(request.POST.get('epage'))
        file_handle = file_reader.FileHandler(uploaded_file)
        file_handle.read_file(spage, epage)
        
        summerised = file_handle.summerized()
        #make Apicall
        question = bard_api.generate_question(summerised, num_of_questions, difficulty, user.id)
        parsed = bard_api.process_response(question)

        if parsed:
            return JsonResponse(parsed)
        else:
            return JsonResponse({'error2':'error genrating a response'})
    if user.is_authenticated:   
        return render(request, 'home.html', {"auth":True})
    return render(request, 'home.html', {"auth":False})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('test')
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials.'})
    
    return render(request, 'login.html')


def test(request):
    return render(request, 'quiz2.html')

def ask_bard(query):
    bard = Bard(token="awiOMPQoafvrVEaYBvowM9Sp4MhBCaAFzKk_5WO11Wf0XwWsJEXQu3mHG623uNSMhhms5g.")
    answer = bard.get_answer(query)
    return answer

def get_chat(request):
    user_query = request.GET.get('query')
    user = request.user
    chats = Message.objects.all().filter(user=user).order_by('-sent_date')[:6]
    last_3_chats= chats
    response = 'this is response'#bard_api.gpt_chat_session(last_3_chats, user_query)
    #print('sddddddddddddddddddddddddddddddddddddddddddddddddd'+user_query)
    #ask_bard(user_query)
    # Process the user_query and generate the chat response
    #chat_response = process_chat_query(user_query)
    message1  = Message.objects.create(user=user, text=user_query, is_recieved = False)
    message1.save()
    message2  = Message.objects.create(user=user, text=response, is_recieved = True)
    message2.save()
    res = {}
    res['answer'] = response
    return JsonResponse(res)


@login_required(login_url='login')
def chat(request, query):
    user = request.user
    chats = Message.objects.all().filter(user=user).order_by('-sent_date')[:10]
    #answer = ask_bard(query)
    last_3_chats = chats
    if len(last_3_chats) > 6:
        last_3_chats = last_3_chats[:6]     
    response = 'this is response' #bard_api.gpt_chat_session(last_3_chats, query)
    
    if response:
        message1  = Message.objects.create(user=user, text=query, is_recieved = False)
        message1.save()
        message2  = Message.objects.create(user=user, text=response, is_recieved = True)
        message2.save()
       
    return render(request, 'chat.html', {'prev_chats':chats, 'response':response})


def user_logout(request):
    logout(request)
    return redirect('login')


# # example usage for group_text.py (import HttpResponse from django.http and convert_to_pdf_group from api and zipfile)
# def convert_text_to_pdf_groups(request):
#     if request.method == 'POST':
#         text = request.POST.get('text')
#         pdf_groups = convert_to_pdf_groups(text)

#         response = HttpResponse(content_type='application/zip')
#         response['Content-Disposition'] = 'attachment; filename="pdf_groups.zip"'

#         with zipfile.ZipFile(response, 'w') as zipf:
#             for pdf_path in pdf_groups:
#                 zipf.write(pdf_path)

#         return response

def acccess(request):
    return render(request, 'quiz3.html')

def home(request):
    return render(request, 'home2.html')

def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        num_of_questions = request.POST.get('qnumber')
        difficulty = request.POST.get('difficulty')
        spage = int(request.POST.get('spage'))
        epage = int(request.POST.get('epage'))
        comment = request.POST.get('additional_comment')
        
        questions = get_question(uploaded_file, 5, difficulty, spage, epage, 'multiple_choice', 'chatgpt')
        print(questions)
        #redirect_url = 'quiz/?questions={}'.format(questions['questions'])
        return render(request, 'quiz3.html', {'questions':questions['questions']})
    
    return render(request, 'upload.html')



def quiz(request):
    questions = urllib.parse.unquote(request.GET.get('questions'))
    return render(request, 'quiz3.html', {'questions':questions})


def chat(request):
    return render(request, 'chat2.html')