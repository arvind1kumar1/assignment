from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import BankUsers,Transactions
from datetime import datetime
from django.utils import timezone

from email.message import EmailMessage

import smtplib
from email.mime.multipart import MIMEMultipart
import pytz
import os

import pandas as pd

from myapp import sendExcelFile

# Create your views here.
@api_view(['POST','GET'])
def createuser(request):
    email = request.data["email"]
    password = request.data["password"]
    userType = request.data["userType"]
    #fix amount for each user 5000
    amount = request.data["amount"]
    output = BankUsers.objects.filter(email=email).first()
    if output is None:
        result = BankUsers.objects.create(email=email,password=password,userType=userType,amount=amount)
        if result.pk:
            return JsonResponse({"status":True,"message":"user created successfully"})
    else:
        return JsonResponse({"status":False,"message":"user alredy exist "+email})
    

@api_view(['POST','GET'])
def transaction(request):
    debiter = request.data["debiterEmail"]
    amount = request.data["amount"]
    receiver = request.data["receiverEmail"]
    # import ipdb
    # ipdb.set_trace()
    # date = datetime.now(tz=timezone.utc).replace(microsecond=0)

    # date = datetime.now(tz=pytz.UTC).replace(microsecond=0)
    # date = datetime.now(tz=pytz.timezone("Asia/Kolkata")).replace(microsecond=0)
    # tzinfo=pytz.timezone("Asia/Kolkata")
    
    date = datetime.now().replace(microsecond=0)
    debiterUser = BankUsers.objects.filter(email=debiter).first()
    receiverUser = BankUsers.objects.filter(email=receiver).first()
    if debiterUser is not None and debiterUser.amount < amount:
        return JsonResponse({"status":True,"message":"you does not have sufficient amount"})
    elif debiterUser is not None and receiverUser is not None and debiterUser.amount >= amount:
        result = Transactions.objects.create(amount=amount,email= receiver,transactionType = "debit",date=date,bankUsers=debiterUser)
        debiterUser.amount -= amount
        debiterUser.save()
        result = Transactions.objects.create(amount=amount,email= debiter,transactionType = "credit",date=date,bankUsers=receiverUser)
        receiverUser.amount += amount
        receiverUser.save()  

        output = sendExcelFile.sendMailOnTransaction(amount,debiterUser,receiverUser,debiter,receiver)
        print("output ",output)        
        return JsonResponse({"status":True,"message":"transaction executed successfully"}) 
    else:
        return JsonResponse({"status":True,"message":"some data is missing when make transaction"})    
    

@api_view(['POST','GET'])
def enquiry(request):
    email = request.data["email"]    
    user = BankUsers.objects.filter(email=email).first()
    if user:
        return JsonResponse({"status":True,"balance":user.amount})    
    else:
        return JsonResponse({"status":True,"message":"user does not exist"}) 

@api_view(['POST','GET'])
def transaction_history(request):
    email = request.data["email"]        
    userEmail = request.data["userEmail"] 
    print("dgdgdg ",isinstance(userEmail,str))
    fileName = ""
    # startTime = datetime.strptime(request.data["startTime"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
    # endTime = datetime.strptime(request.data["endTime"],"%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
    startTime = datetime.strptime(request.data["startTime"],"%Y-%m-%d %H:%M:%S")
    endTime = datetime.strptime(request.data["endTime"],"%Y-%m-%d %H:%M:%S")
    manager = BankUsers.objects.filter(email=email).first()
    # user = BankUsers.objects.filter(email=userEmail).first()
    if manager.userType != "manager":
        return JsonResponse({"status":True,"message":"Sorry you are not manager"})    
    else:
        if isinstance(userEmail,str) and userEmail.lower() == "all": #it for all users
            obj = {}
            i = 1
            dataForExcelSheet = []
            transaction = Transactions.objects.filter(date__gte=startTime,date__lte=endTime)
            for data in transaction:
                obj[i]={
                    "amount":data.amount,
                    "type":data.transactionType,
                    "date":data.date.replace(tzinfo=None)                       
                }
                if data.transactionType == "debit":
                    obj[i]["receiverEmail"] = data.email
                    obj[i]["debiterEmail"] = data.bankUsers.email
                if data.transactionType == "credit":
                    obj[i]["debiterEmail"] = data.email
                    obj[i]["receiverEmail"] = data.bankUsers.email
                dataForExcelSheet.append(obj[i])
                i += 1
            # import ipdb
            # ipdb.set_trace()
            df = pd.DataFrame(dataForExcelSheet)
            currentDateTime = (datetime.now().strftime('%d-%m-%Y %H-%M-%S'))[0:23]
            local_path = os.path.abspath(os.path.curdir)
            fileName = "allUserTransaction" + currentDateTime + ".xlsx"
            filepath = local_path + "\\sendExcel\\" + fileName
            # writer = pd.ExcelWriter('persDetail.xlsx', engine='xlsxwriter')
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            # if fileName != "":
            #     sendExcelFile.sendExcelToManager(fileName,email)
            return JsonResponse({"status":True,"message":obj}) 

        elif isinstance(userEmail,list):             
            obj = {}
            i = 1

            dataForExcelSheet = []
            for email in userEmail:
                user = BankUsers.objects.filter(email=email).first()
                transaction = Transactions.objects.filter(date__gte=startTime,date__lte=endTime,bankUsers=user)
                for data in transaction:                    
                    obj[i]={
                        "amount":data.amount,
                        "type":data.transactionType,
                        "date":data.date.replace(tzinfo=None)                         
                    }
                    if data.transactionType == "debit":
                        obj[i]["receiverEmail"] = data.email
                        obj[i]["debiterEmail"] = data.bankUsers.email
                    if data.transactionType == "credit":
                        obj[i]["debiterEmail"] = data.email
                        obj[i]["receiverEmail"] = data.bankUsers.email
                    dataForExcelSheet.append(obj[i])
                    i += 1
            # import ipdb
            # ipdb.set_trace()
            df = pd.DataFrame(dataForExcelSheet)
            currentDateTime = (datetime.now().strftime('%d-%m-%Y %H-%M-%S'))[0:23]
            local_path = os.path.abspath(os.path.curdir)
            fileName = "allUserTransaction" + currentDateTime + ".xlsx"
            filepath = local_path + "\\sendExcel\\" + fileName
            # writer = pd.ExcelWriter('persDetail.xlsx', engine='xlsxwriter')
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            # if fileName != "":
            #     sendExcelFile.sendExcelToManager(fileName,email)
            return JsonResponse({"status":True,"message":obj}) 

        else:
            obj = {}
            i = 1
            dataForExcelSheet = []
            user = BankUsers.objects.filter(email=userEmail).first()
            transaction = Transactions.objects.filter(date__gte=startTime,date__lte=endTime,bankUsers=user)
            # import ipdb
            # ipdb.set_trace()
            for data in transaction:
                obj[i]={
                    "amount":data.amount,
                    "type":data.transactionType,
                    "date":data.date.replace(tzinfo=None)                  
                }
                if data.transactionType == "debit":
                    obj[i]["receiverEmail"] = data.email
                    obj[i]["debiterEmail"] = data.bankUsers.email
                if data.transactionType == "credit":
                    obj[i]["debiterEmail"] = data.email
                    obj[i]["receiverEmail"] = data.bankUsers.email
                dataForExcelSheet.append(obj[i])
                i += 1
            
            df = pd.DataFrame(dataForExcelSheet)
            currentDateTime = (datetime.now().strftime('%d-%m-%Y %H-%M-%S'))[0:23]
            local_path = os.path.abspath(os.path.curdir)
            fileName = "allUserTransaction" + currentDateTime + ".xlsx"
            filepath = local_path + "\\sendExcel\\" + fileName
            # writer = pd.ExcelWriter('persDetail.xlsx', engine='xlsxwriter')
            writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            # if fileName != "":
            #     sendExcelFile.sendExcelToManager(fileName,email)
            return JsonResponse({"status":True,"message":obj}) 
    
    