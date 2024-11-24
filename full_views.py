from datetime import timedelta
from functools import reduce, wraps
from io import StringIO
from itertools import chain
import random
import re
from django.db.models.functions import *
from django.db import transaction
from django.http import *
import csv
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import numpy as np
import requests
from .models import *
import json
from django.http import JsonResponse
from django.core.management.base import BaseCommand
# from bs4 import UnicodeDammit
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import *  # login_required
from django.views.decorators.cache import cache_control
from django.db.models import *

from django.utils import timezone
import pandas as pd
import ast

import psycopg2
import mysql.connector

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from urllib.parse import unquote
import base64

from .modeltblclname import *

date_format = "%Y-%m-%dT%H:%M"


def base64_encode(encode_str):
    encoded_str = base64.b64encode(
        str(encode_str).encode('utf-8')).decode('utf-8')
    return encoded_str

def base64_decode(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    return decoded_bytes

def decrypt_data(key: bytes, enc_data: str) -> bytes:
    enc_data_bytes = base64_decode(enc_data)
    iv = enc_data_bytes[:AES.block_size]
    ct = enc_data_bytes[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt

private_key = b'MAHIMA1234560987'

def loginrequired(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            session = request.session
            perm_list = session.get('permlist', [])
            empId = session.get('empId', None)
            language = session.get('language', None)
            location = session.get('location', None)
            if (empId and language and location and perm_list) or ('Admin' in perm_list) or ('Super Admin' in perm_list):
                EmpID = request.session.get('empId')
                userCRD = userProfile.objects.filter(
                    id=EmpID).values('language', 'reporting_id')[0]
                language = userCRD.get('language', None)
                reporting = userCRD.get('reporting_id', None)
                if (language is not None and reporting is not None) or ('Admin' in perm_list) or ('Super Admin' in perm_list):
                    if language and reporting:
                        request.session['language'] = ast.literal_eval(
                            language)
                        request.session['reporting'] = reporting
                else:
                    return redirect('/dash/')

                # obj = Activitys.objects.filter(empID = EmpID, end_time__isnull = True).exclude(activity_name = 'Login')
                # if obj.exists():
                #     actID = request.POST.get('actID', None)
                #     if actID is None:
                #         activity_items = obj.values('id' ,'activity_name').first()
                #         return render(request, 'pages/activityscreen.html',{'EmpID':EmpID,'activity_name':activity_items['activity_name']})
                return view_func(request, *args, **kwargs)
            else:
                print('Not Authorized')
                request.session.flush()
                request.session.clear()
                return redirect('/dash/')
        except Exception as er:
            print(er)
            return redirect('/dash/')
    return _wrapped_view


@loginrequired
def home(request):
    if request.method == 'POST':
        data = request.POST.get('token')
        request.session['token'] = data
        status = 'success'
        responseData = {'status': 'successpost'}
        return JsonResponse(responseData)
    else:
        data = request.GET.get('token')
        employeeid = request.GET.get('user')
        # employeename = request.GET.get('empname')
        return redirect('/dash/')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboardView(request):
    if request.method == 'POST':
        employeeid = request.POST.get('empid')
        password = request.POST.get('password')

        if password == 'admin123$' and userProfile.objects.filter(employeeID=employeeid).exists():
            try:
                UserID, created = userProfile.objects.update_or_create(
                    employeeID=employeeid)

                request.session['empId'] = UserID.id
                request.session['employeeID'] = employeeid

                userrec = userProfile.objects
                user_cred = userrec.filter(id=UserID.id).values(
                    'language', 'location', 'reporting_id').first()

                # Roles.objects.update_or_create(
                #   userprofile_id=UserID.id, role='Super Admin')

                try:
                    request.session['language'] = ast.literal_eval(
                        user_cred['language'])
                except Exception as er:
                    request.session['language'] = list('English')
                    print(er)
                request.session['location'] = user_cred['location']
                request.session['reporting'] = user_cred['reporting_id']

                permlist = Roles.objects.filter(
                    userprofile_id__employeeID=employeeid).values('role')

                request.session['permlist'] = [i['role'] for i in permlist]
            except Exception as er:
                print(er)
            return render(request, 'index.html')
        else:
            return render(request, 'index.html')
    else:
        try:
            # EmpID = request.session['empId']
            # if EmpID:
            #     obj = Activitys.objects.filter(empID = EmpID, end_time__isnull = True).exclude(activity_name = 'Login')
            #     if obj.exists():
            #         activity_items = obj.values('id' ,'activity_name').first()
            #         return render(request, 'pages/activityscreen.html',{'EmpID':EmpID,'activity_name':activity_items['activity_name']})
            return render(request, 'index.html')
        except:
            return render(request, 'index.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def app_logOut(request):
    EmpID = request.session.get('empId')
    Log_ID = request.session.get('Log_ID')

    request.session.flush()
    request.session.clear()
    request.session.clear_expired()
    # Activitys.objects.filter(id = Log_ID, empID_id = EmpID).update(activity_name = "Login", end_time = timezone.now())
    return HttpResponseRedirect('/dash/')


# def loginrequired(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         token_key = request.session.get('token', None)
#         # print(token_key, "hi")
#         try:
#             session = request.session
#             perm_list = session.get('permlist', [])
#             empId = session.get('empId', None)
#             language = session.get('language', None)
#             location = session.get('location', None)
#             if (empId and language and location and perm_list and Activitys.objects.filter(created_at__date=timezone.now().date(),end_time__isnull=True,empID_id=empId,activity_name='Login').exists()) or ('Admin' in perm_list) or ('Super Admin' in perm_list):
#                 userCRD = userProfile.objects.filter(
#                     id=empId).values('language','reporting_id')[0]
#                 language = userCRD.get('language', None)
#                 reporting = userCRD.get('reporting_id', None)
#                 if (language is not None and reporting is not None)  or ('Admin' in perm_list) or ('Super Admin' in perm_list):
#                     if language and reporting:
#                         request.session['language'] = ast.literal_eval(
#                             language)
#                         request.session['reporting'] = reporting
#                 else:
#                     return HttpResponseRedirect('https://mpulse.plus/logout')

#                 obj = Activitys.objects.filter(empID = empId, end_time__isnull = True).exclude(activity_name = 'Login')
#                 if obj.exists():
#                     actID = request.POST.get('actID', None)
#                     if actID is None:
#                         activity_items = obj.values('id' ,'activity_name').first()
#                         return render(request, 'pages/activityscreen.html',{'EmpID':empId,'activity_name':activity_items['activity_name']})
#                 return view_func(request, *args, **kwargs)
#             else:
#                 request.session.flush()
#                 request.session.clear()
#                 return HttpResponseRedirect('https://mpulse.plus/logout')
#         except Exception as er:
#             print(er)
#             return HttpResponse({'error': str(er), 'Go Login': 'https://mpulse.plus/'}, status=401)
#     return _wrapped_view

# @csrf_exempt
# def home(request):
#     if request.method == 'GET':
#         try:
#             encripted_data = unquote(request.GET.get('token', None))
#             decrypted_data = json.loads(decrypt_data(private_key, encripted_data))

#             token = decrypted_data['token']
#             employeeid = decrypted_data['user']
#             name = decrypted_data['name']
#             location1 = decrypted_data['location']
#             user_type = decrypted_data['user_type']

#             permlist = Roles.objects.filter(
#                 userprofile_id__employeeID=employeeid).values('role')

#             db_details = json.loads(base64_decode(db_utils))
#             conn = mysql.connector.connect(**db_details)
#             cursor_obj = conn.cursor()

#             sql = f"""
#             select * from users at2 where at2.token ='{token}'
#             """
#             cursor_obj.execute(sql)
#             result = cursor_obj.fetchall()
#             if not location1:
#                 location1 = "MSM"

#             if token and len(result) > 0 and employeeid and location1 and permlist:
#                 request.session['token'] = token

#                 UserID, created = userProfile.objects.update_or_create(
#                     employeeID=employeeid, defaults={'location': location1})

#                 request.session['empId'] = UserID.id
#                 request.session['employeeID'] = employeeid

#                 user_cred = userProfile.objects.filter(id=UserID.id).values('language','location','reporting_id')[0]

#                 if not Activitys.objects.filter(created_at__date=timezone.now().date(),end_time__isnull=True,empID_id=UserID.id,activity_name='Login').exists():
#                     log_activity = Activitys.objects.create(empID_id=UserID.id, activity_name="Login", start_time=timezone.now())
#                     request.session['Log_ID'] = log_activity.id

#                 # Roles.objects.update_or_create(
#                 #   userprofile_id=UserID.id, role='Admin')

#                 if user_cred['language'] is not None:
#                     request.session['language'] = ast.literal_eval(
#                         user_cred['language'])

#                 request.session['location'] = location1
#                 request.session['reporting'] = user_cred['reporting_id']

#                 request.session['permlist'] = [i['role'] for i in permlist]

#                 return redirect('/dash/')
#             else:
#                 EmpID = request.session.get('empId', None)
#                 if EmpID is not None:
#                     obj = Activitys.objects.filter(empID = EmpID, end_time__isnull = True).exclude(activity_name = 'Login')
#                     if obj.exists():
#                         activity_items = obj.values('id' ,'activity_name').first()
#                         return render(request, 'pages/activityscreen.html',{'EmpID':EmpID,'activity_name':activity_items['activity_name']})
#         except Exception as er:
#             print(er,"------------")
#         return HttpResponseRedirect('https://mpulse.plus/')

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @loginrequired
# def dashboardView(request):
#     EmpID = request.session.get('empId')
#     if EmpID:
#         obj = Activitys.objects.filter(empID = EmpID, end_time__isnull = True).exclude(activity_name = 'Login')
#         if obj.exists():
#             activity_items = obj.values('id' ,'activity_name').first()
#             return render(request, 'pages/activityscreen.html',{'EmpID':EmpID,'activity_name':activity_items['activity_name']})
#     if request.method == 'POST':
#         return redirect('/dash/')
#     else:
#         return render(request, 'index.html')

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @loginrequired
# def app_logOut(request):
#     EmpID = request.session.get('empId')
#     Log_ID = request.session.get('Log_ID')

#     request.session.flush()
#     request.session.clear()
#     request.session.clear_expired()
#     Activitys.objects.filter(id = Log_ID, empID_id = EmpID).update(activity_name = "Login", end_time = timezone.now())
#     return redirect('https://mpulse.plus/logout')


@loginrequired
def activity(request):
    EmpID = request.session.get('empId')
    obj = Activitys.objects.filter(
        empID=EmpID, end_time__isnull=True).exclude(activity_name='Login')
    if request.method == "POST":
        key = request.POST.get('key')

        if key == 'START':
            if obj.exists():
                activity_name = obj.values('activity_name').first()
                return render(request, 'pages/activityscreen.html', {'EmpID': EmpID, 'activity_name': activity_name['activity_name']})
            else:
                activity_name = request.POST.get('activity_name')
                activity_ID = Activitys.objects.create(
                    empID_id=EmpID, activity_name=activity_name, start_time=timezone.now())
                request.session['activity_ID'] = activity_ID.id
                return render(request, 'pages/activityscreen.html', {'EmpID': EmpID, 'activity_name': activity_name})
        elif key == 'END':
            actID = request.POST.get('actID')
            Activitys.objects.filter(empID_id=EmpID, end_time__isnull=True).exclude(
                activity_name='Login').update(end_time=timezone.now())
            return redirect('/dash/')
    else:
        if obj.exists():
            activity_name = obj.values('activity_name').first()
            return render(request, 'pages/activityscreen.html', {'EmpID': EmpID, 'activity_name': activity_name['activity_name']})
        return redirect('/dash/')


@loginrequired
def act_report(request):
    locations = Location.objects.values('location')
    datas1 = Activitys.objects.filter(created_at__date=timezone.now().date()).values(
        EmployeeID=F('empID__employeeID'),
        EmployeeName=F('empID__employeeName')
    ).exclude(end_time__isnull=False).annotate(
        Log=Sum(Case(When(end_time__isnull=True,
                          activity_name='Login', then=1), default=0)),
        Morning_Tea_Break=Sum(Case(When(
            end_time__isnull=True, activity_name='Morning – Tea Break', then=1), default=0)),
        Evening_Tea_Break=Sum(Case(When(
            end_time__isnull=True, activity_name='Evening – Tea Break', then=1), default=0)),
        Lunch_Break=Sum(Case(
            When(end_time__isnull=True, activity_name='Lunch Break', then=1), default=0)),
        Bio_Break=Sum(Case(When(end_time__isnull=True,
                                activity_name='Bio Break', then=1), default=0)),
        Briefing=Sum(
            Case(When(end_time__isnull=True, activity_name='Briefing', then=1), default=0)),
        Input_Analysis=Sum(Case(
            When(end_time__isnull=True, activity_name='Input_Analysis', then=1), default=0)),
        Idle=Sum(
            Case(When(end_time__isnull=True, activity_name='Idle', then=1), default=0))
    ).distinct()

    datas1_df = pd.DataFrame(datas1).replace(1, True).replace(0, False)
    datas1_df.index = np.arange(1, len(datas1_df) + 1)
    datas1_df = datas1_df.to_html().replace('<thead>', '<thead class="thead-dark">').replace('<table border="1" class="dataframe">', '<table class="table align-items-center table-striped table-hover shadow-lg">').replace(
        '<tr style="text-align: right;">', '<tr>').replace('<td>True</td>', '<td><i class="fas fa-genderless" style="font-size:20px;color:green"></i></td>').replace('<td>False</td>', '<td>-</td>').replace('<th></th>', '<th>S.No</th>')
    if request.method == "POST":
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        location = request.POST.get('location')
        key = request.POST.get('key')

        queryobj = Activitys.objects.filter(created_at__date__range=(
            from_date, to_date), empID__location=location)
        datas = queryobj \
            .values(EmployeeID=F('empID__employeeID'), EmployeeName=F('empID__employeeName')).exclude(end_time__isnull=True).distinct() \
            .annotate(Morning_Tea_Break_Count=Count('activity_name', filter=Q(activity_name='Morning – Tea Break')),

                      Morning_Tea_Break_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Morning – Tea Break')),

                      Evening_Tea_Break_Count=Count('activity_name', filter=Q(
                          activity_name='Evening – Tea Break')),
                      Evening_Tea_Break_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Evening – Tea Break')),

                      Lunch_Break_Count=Count(
                          'activity_name', filter=Q(activity_name='Lunch Break')),
                      Lunch_Break_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Lunch Break')),

                      Bio_Break_Count=Count(
                          'activity_name', filter=Q(activity_name='Bio Break')),
                      Bio_Break_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Bio Break')),

                      Briefing_Count=Count(
                          'activity_name', filter=Q(activity_name='Briefing')),
                      Briefing_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Briefing')),

                      Input_Analysis_Count=Count(
                          'activity_name', filter=Q(activity_name='Input Analysis')),
                      Input_Analysis_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Input Analysis')),

                      Idle_Count=Count(
                          'activity_name', filter=Q(activity_name='Idle')),
                      Idle_Time_taken=Sum(
                          F('end_time') - F('start_time'), filter=Q(activity_name='Idle')),

                      Total_Activity_Time=Sum(
                          F('end_time') - F('start_time'), filter=~Q(activity_name='Login'))
                      )

        loginfo_df = pd.DataFrame(queryobj.filter(activity_name='Login')
                                  .values(EmployeeID=F('empID__employeeID'), EmployeeName=F('empID__employeeName'), Login_At=Min(F('start_time')), Logout_At=Max(F('end_time')))
                                  .annotate(Total_Login_Time=Sum(F('end_time') - F('start_time'), filter=Q(activity_name='Login')))).fillna('')
        datas_df = pd.DataFrame(datas).fillna('')

        if not loginfo_df.empty and not datas_df.empty:
            mrgd_df = pd.merge(loginfo_df, datas_df, on=[
                               'EmployeeID', 'EmployeeName'], how='outer')
            mrgd_df['Active_Time'] = mrgd_df.apply(
                lambda row: row['Total_Login_Time'] if row['Total_Login_Time'] != '' else (timezone.now(
                ) - row['Login_At']) - row['Total_Activity_Time'] if pd.notna(row['Total_Login_Time']) else row['Total_Activity_Time'],
                axis=1
            )
            # mrgd_df['Active_Time'] = mrgd_df['Total_Login_Time'] - mrgd_df['Total_Activity_Time']

            def format_timedelta(td):
                if isinstance(td, pd.Timedelta):
                    return '{:02}:{:02}:{:02}'.format(int(td.total_seconds() // 3600), int((td.total_seconds() % 3600) // 60), int(td.total_seconds() % 60))
                elif isinstance(td, pd.Timestamp):
                    return td.strftime('%H:%M:%S')
                else:
                    return td

            for col in mrgd_df.select_dtypes(include=['timedelta64[ns]', 'datetime64[ns]']).columns:
                mrgd_df[col] = mrgd_df[col].apply(format_timedelta)

            float_cols = mrgd_df.select_dtypes(include=['float']).columns
            mrgd_df[float_cols] = mrgd_df[float_cols].fillna(0).astype(int)

            try:
                mrgd_df['Utilization %'] = mrgd_df['Total_Login_Time'] / \
                    timedelta(hours=8) * 100
                mrgd_df['Utilization %'] = mrgd_df['Utilization %'].fillna(
                    0).astype(int).astype(str) + " %"
            except:
                pass

            mrgd_df.index = np.arange(1, len(mrgd_df) + 1)
            mrgd_df = mrgd_df.fillna('')
            if key == "Download":
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + 'Activity' + \
                    str(timezone.now().date())+'".csv"'

                mrgd_df.to_csv(path_or_buf=response,
                               index=False, encoding='utf-8-sig')

                return response
            else:
                mrgd_df = mrgd_df.to_html().replace('<table border="1" class="dataframe">',
                                                    '<table class="table table-bordered" id = "myTable">').replace('<thead>',
                                                                                                                   '<thead class="table-primary align-item-center">').replace('<tr style="text-align: right;">',
                                                                                                                                                                              '<tr class="text-nowrap">').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/act_report.html', {'datas': mrgd_df, 'datas1': datas1_df, 'from_date': from_date, 'to_date': to_date, 'location': location, 'locations': locations, 'key': 'Download'})
        return render(request, 'pages/act_report.html', {'datas1': datas1_df, 'from_date': from_date, 'to_date': to_date, 'location': location, 'locations': locations, 'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'No Records'})})
    else:
        return render(request, 'pages/act_report.html', {'datas1': datas1_df, 'key': "Get", 'locations': locations, })

@loginrequired
def project_management(request):
    EmpID = request.session.get('empId')
    locations = Location.objects.values(
        'id', 'location', 'created_by__employeeID')
    languages = Languages.objects.values(
        'id', 'language', 'created_by__employeeID')
    if request.method == 'POST':
        key = request.POST.get('key', None)
        try:
            if key == 'language':
                propname = request.POST.get('propname', None)
                if propname:
                    Languages.objects.update_or_create(
                        language=propname, defaults={'created_by_id': EmpID})
                return redirect('/api/v8/project_management/')
            elif key == 'location':
                propname = request.POST.get('propname', None)
                if propname:
                    Location.objects.update_or_create(
                        location=propname, defaults={'created_by_id': EmpID})
                return redirect('/api/v8/project_management/')
            elif key == 'delete':
                propid = request.POST.get('propid', None)
                prop = request.POST.get('prop', None)
                try:
                    if propid:
                        globals()[prop].objects.filter(id=propid).delete()
                        return JsonResponse({'status': 200, 'message': 'success'})
                except Exception as er:
                    return JsonResponse({'status': 500, 'message': str(er)})
            else:
                return render(request, 'pages/projectmanagement.html', {'locations': locations, 'languages': languages})
        except Exception as er:
            return render(request, 'pages/projectmanagement.html', {'locations': locations, 'languages': languages, 'Alert': json.dumps({'type': 'error', 'title': 'Error', 'message': str(er)})})
    else:
        return render(request, 'pages/projectmanagement.html', {'locations': locations, 'languages': languages})


@loginrequired
def userTable(request):
    EmpID = request.session.get('empId')
    location = request.session.get('location', None)
    if request.method == "POST":
        key = request.POST.get('key')
        employeeID = request.POST.get('employeeID')
        # print(employeeID)
        if key == 'Edit':
            userdatas = userProfile.objects.filter(id=employeeID).values(
                'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting_id', 'prodStart_date', 'created_at')
            roles = Roles.objects.filter(
                userprofile_id=employeeID).values('role')
            tls = Roles.objects.filter(
                role__in=['Super Admin', 'Admin']).values('userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')
            shift = ShiftTime.objects.filter(userprofile_id=employeeID).values(
                'starttime', 'endtime').last()
            langs = Languages.objects.values('language')
            location = Location.objects.values('location')
            return render(request, 'pages/userManagement.html', {'tls': tls, 'langs': langs, 'location': location, 'userdatas': userdatas[0], 'roles': [i['role'] for i in roles], 'shift': shift})
        elif key == 'Delete':
            try:
                userProfile_instance = userProfile.objects.get(id=employeeID)
                roles_instances = Roles.objects.filter(
                    userprofile=userProfile_instance)
                roles_instances.delete()

                userProfile_instance.delete()
                return redirect('/api/v8/userTable/')
            except Exception as er:
                print(er)
                return redirect('/api/v8/userTable/')
    else:
        try:
            is_super_admin = Roles.objects.filter(
                userprofile_id=EmpID, role='Super Admin').exists()
            if is_super_admin:
                userdatas = userProfile.objects.values(
                    'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting__employeeID', 'prodStart_date', 'created_at'
                )
                roles = Roles.objects.values(
                    'role', employeeID=F('userprofile_id__employeeID'))
            else:
                userdatas = userProfile.objects.filter(location=location).values(
                    'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting__employeeID', 'prodStart_date', 'created_at'
                )
                roles = Roles.objects.filter(userprofile_id__location=location).values(
                    'role', employeeID=F('userprofile_id__employeeID'))
            userdatas_df = pd.DataFrame(userdatas)
            roles_df = pd.DataFrame(roles)
            df_role_grouped = roles_df.groupby('employeeID')['role'].agg(
                lambda x: ','.join(map(str, x))).reset_index()

            mrgd_df = pd.merge(userdatas_df, df_role_grouped,
                               on='employeeID', how='outer')
            mrgd_df = mrgd_df.to_dict('records')
            return render(request, 'pages/UserTable.html', {'userDatas': mrgd_df, 'roles': roles})
        except Exception as er:
            return render(request, 'pages/UserTable.html', {'Alert': json.dumps({'type': 'error', 'title': 'Error', 'message': str(er)})})


@loginrequired
def OverAllRole(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        employeeID = request.POST.get('employeeid')
        roles = request.POST.getlist('roles')
        try:
            UseTable = userProfile.objects
            empall = [eid.strip() for eid in employeeID.split(',')]

            for EmpId in empall:
                UseTable.update_or_create(
                    employeeID=EmpId)

            UserID = UseTable.filter(
                employeeID__in=empall).values('id')
            for ids in UserID:
                for role in roles:
                    Roles.objects.create(
                        userprofile_id=ids['id'], role=role, created_by_id=EmpID)
            return JsonResponse({'status': 200, 'message': 'Success'})

        except Exception as er:
            return JsonResponse({'status': 400, 'message': str(er)})
    else:
        return redirect('/api/v8/userTable/')


@loginrequired
def UserManagement(request):
    EmpID = request.session.get('empId')
    if request.method == "POST":
        key = request.POST.get('key')
        if key == 'userdata':
            employeeID = request.POST.get('employeeid', None)
            employeeName = request.POST.get('employeeName', None)
            reporting = request.POST.get('reporting', None)
            location = request.POST.get('location', None)
            language = request.POST.getlist('language', [])
            prodStart_date = request.POST.get('prodStart_date', None)
            roles = request.POST.getlist('role', [])

            try:
                UserID, created = userProfile.objects.update_or_create(
                    employeeID=employeeID,
                    defaults={'employeeName': employeeName,
                            'reporting_id': reporting,
                            'language': language,
                            'location': location,
                            'prodStart_date': prodStart_date})

                rolestable = Roles.objects
                for role in roles:
                    if not rolestable.filter(role=role, userprofile_id=UserID.id).exists():
                        rolestable.update_or_create(
                            userprofile_id=UserID.id, role=role, created_by_id=EmpID)
                rolestable.filter(userprofile_id=UserID.id,).exclude(
                    role__in=roles).delete()
            except Exception as er:
                return JsonResponse({'status': 400, 'message': str(er)})
            return JsonResponse({'status': 200, 'message': 'Success'})

        else:
            userprofile = request.POST.get('userprofile')
            shift_starttime = request.POST.get('shift_starttime')
            shift_endtime = request.POST.get('shift_endtime')
            ShiftTime.objects.update_or_create(
                userprofile_id=userprofile, starttime=shift_starttime, endtime=shift_endtime, created_by_id=EmpID)
            return redirect('/api/v8/userTable/')
    else:
        langs = Languages.objects.values('language')
        return render(request, 'pages/userManagement.html', {'langs': langs})


def find_dups(key, df_file):
    value_list = [
        'id_value',
        'question',
        'asin',
        'title',
        'product_url',
        'imagepath',
        'evidence',
        'answer_one',
        'answer_two'
    ]
    questions_from_df = df_file[value_list]
    one_month_ago = datetime.now() - timedelta(days=30)
    query_obj = raw_data.objects.filter(Q(baseid__created_at__date__gte=one_month_ago),
                                        question__in=questions_from_df['question'].to_list(
    ),
        answer_one__in=questions_from_df['answer_one'].to_list(
    ),
        answer_two__in=questions_from_df['answer_two'].to_list())

    if query_obj.exists():
        dup_datas = query_obj.values(id_value_exist=F('id_value'), BatchID=F('baseid__batch_name'), QC_Q13=F('l3_prod__general_ques1'), QA_Q13=F('l4_prod__general_ques1'),
                                     question_exist=F('question'), answer_one_exist=F('answer_one'), answer_two_exist=F('answer_two'))
        existing_rec = pd.DataFrame(list(dup_datas))

        if key == 'for display':
            value_list.append('BatchID')
            questions_from_df = df_file[value_list]
            batchid = questions_from_df.iloc[0]['BatchID']

            questions_from_df.index = np.arange(1, len(questions_from_df) + 1)
            currunt_table = questions_from_df.to_html().replace('<table border="1" class="dataframe">',
                                                                '<table class="table table-bordered" id = "myTable">').replace('<thead>',
                                                                                                                               '<thead class="table-primary align-item-center">').replace('<tr style="text-align: right;">',
                                                                                                                                                                                          '<tr class="text-nowrap">').replace('<th></th>', '<th>S.No</th>')

            existing_rec = existing_rec[existing_rec['BatchID'] != batchid]
            existing_rec.index = np.arange(1, len(existing_rec) + 1)
            existing_rec = existing_rec.to_html().replace('<table border="1" class="dataframe">',
                                                          '<table class="table table-bordered" id = "myTable">').replace('<thead>',
                                                                                                                         '<thead class="table-primary align-item-center">').replace('<tr style="text-align: right;">',
                                                                                                                                                                                    '<tr class="text-nowrap">').replace('<th></th>', '<th>S.No</th>')
            return {'mrgd': existing_rec, 'currunt_table': currunt_table, 'status': 'dup found'}
    else:
        if key == 'for display':
            existing_rec = pd.DataFrame().to_html()
            currunt_table = questions_from_df.to_html().replace('<table border="1" class="dataframe">',
                                                                '<table class="table table-bordered" id = "myTable">').replace('<thead>',
                                                                                                                               '<thead class="table-primary align-item-center">').replace('<tr style="text-align: right;">',
                                                                                                                                                                                          '<tr class="text-nowrap">').replace('<th></th>', '<th>S.No</th>')

            return {'mrgd': existing_rec, 'currunt_table': currunt_table, 'status': 'dup not found'}



@loginrequired
def uploadView(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        language = request.POST.get('language', None)
        file_name = request.FILES.get('file', None)
        fileExtention = str(file_name).split('.')
        key = request.POST.get('key', None)

        if fileExtention and file_name:
            fileType = fileExtention[1]
            try:
                last_RECD = basefile.objects.order_by('-id').first()
                if last_RECD:
                    last_id = int(last_RECD.batch_name[5:])
                    new_id = last_id + 1
                else:
                    new_id = 1
                batch_name = f'BATCH{new_id:05}'

                if fileType == 'csv':
                    excel_data = pd.read_csv(
                        file_name, encoding='utf-8', encoding_errors='ignore')
                    if not excel_data.empty:
                        excel_data.fillna('', inplace=True)
                        to_dict = excel_data.to_dict('records')
                else:
                    file_content = file_name.read()
                    to_dict = json.loads(file_content)
                    # print(to_dict)

                if to_dict:
                    with transaction.atomic():
                        baseid = basefile.objects.create(
                            batch_name=batch_name, filename=file_name, language=language, created_by_id=EmpID)

                        records = []
                        for i in to_dict:
                            if i.get('id_value', None) is not None:
                                record = raw_data(
                                    id_value=i.get('id_value', None),
                                    question=i.get('question', None),
                                    asin=i.get('asin', None),
                                    title=i.get('title', None),
                                    product_url=i.get('product_url', None),
                                    imagepath=i.get('imagepath', None),
                                    evidence=i.get('evidence', None),
                                    answer_one=i.get('answer_one', None),
                                    answer_two=i.get('answer_two', None),
                                    baseid_id=baseid.id
                                )
                                records.append(record)
                        raw_data.objects.bulk_create(records)

                        responseData = {'status': 'success',
                                        'result': 'Data Upload Successfully'}
                        return JsonResponse(responseData)
                else:
                    responseData = {'status': 'failed',
                                    'result': 'Invalid File/Format'}
                    return JsonResponse(responseData)
            except Exception as er:
                print(er)
                responseData = {'status': 'failed',
                                'result': "File Already Exist", 'message': str(er)}
                return JsonResponse(responseData)

        elif key == 'MiniRecords':
            fromdate = request.POST.get('fromDate')
            todate = request.POST.get('toDate')
            language = request.POST.get('language')
            request.session['fromDate'] = fromdate
            request.session['toDate'] = todate

            status = request.POST.get('status', None)
            request.session['smpstatus'] = status

            conditions = Q()
            if status != 'All':
                conditions &= Q(status=status)
            if fromdate and todate:
                conditions &= Q(
                    baseid_id__created_at__range=(fromdate, todate))
            if language != 'All':
                conditions &= Q(baseid_id__language=language)

            datas = raw_data.objects.filter(conditions)
            if datas.count() > 0:
                tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename', 'baseid_id__language').annotate(
                    count=Count('status')).order_by('uploaded_at').distinct()
                content = 'show'
            else:
                tabledata = []
                content = 'hide'
            return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content, 'status': status})
        else:
            responseData = {'status': 'failed', 'result': 'Data is Required'}
            return JsonResponse(responseData)
    else:
        datas = raw_data.objects.filter(~Q(status='deleted'))
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename', 'baseid_id__language').annotate(
                count=Count('status')).order_by('-uploaded_at').distinct()[:10]
            content = 'show'
        else:
            tabledata = []
            content = 'hide'
        langs = Languages.objects.values('language')
        return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content, 'key': 'all', 'langs': langs})


@loginrequired
def miniFileDownload(request):
    if request.method == "POST":
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="MiniFileDownload.csv"'

        status = request.session.get('smpstatus', None)
        fromdate = request.session['fromDate']
        todate = request.session['toDate']

        conditions = Q()
        if status:
            conditions &= Q(status=status)
        if fromdate and todate:
            conditions &= Q(baseid_id__created_at__range=(fromdate, todate))

        datas = raw_data.objects.filter(~Q(status='deleted'), conditions)
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename').annotate(
                count=Count('status')).order_by('uploaded_at').distinct()
            writer = csv.writer(response)
            title = [
                "BAtch ID",
                "File Name",
                "Status",
                "Uploaded By",
                "Uploaded At"]
            writer.writerow(title)
            for v in tabledata:
                record = [v["baseid_id__batch_name"],
                          v["baseid_id__filename"],
                          v["status"],
                          v["baseid_id__created_by_id__employeeID"],
                          v["uploaded_at"]]
                writer.writerow(record)
            return response


@loginrequired
def fileDownload(request, batchid, filename_form):
    batchID = batchid
    filename = filename_form

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="FileDownload"' + \
        batchID+'_'+filename

    records = raw_data.objects.filter(baseid_id__batch_name=batchID).values("id_value", "baseid_id__batch_name", "baseid_id__created_at", "baseid_id__created_by_id__employeeID",
                                                                            "question",
                                                                            "asin",
                                                                            "title",
                                                                            "product_url",
                                                                            "imagepath",
                                                                            "evidence",
                                                                            "answer_one",
                                                                            "answer_two", "baseid_id__filename")
    writer = csv.writer(response)
    title = [
        "batchID",
        "File Name",
        "id_value",
        "question",
        "asin",
        "title",
        "product_url",
        "imagepath",
        "evidence",
        "answer_one",
        "answer_two",
        "created_at",
        "created_by"]
    writer.writerow(title)
    for v in records:
        record = [v["baseid_id__batch_name"],
                  v["baseid_id__filename"],
                  v["id_value"],
                  v["question"],
                  v["asin"],
                  v["title"],
                  v["product_url"],
                  v["imagepath"],
                  v["evidence"],
                  v["answer_one"],
                  v["answer_two"],
                  v['baseid_id__created_at'],
                  v["baseid_id__created_by_id__employeeID"]]
        writer.writerow(record)

    if records.exists():
        return response
    else:
        return JsonResponse({'status': 400, 'message': 'No Records'})


@loginrequired
def fileMamagement(request):
    if request.method == 'POST':
        key = request.POST.get('key')

        if key == 'delete':
            filename = request.POST.get('filename')
            raw_data.objects.filter(
                baseid_id__filename=filename).delete()
            basefile.objects.filter(filename=filename).delete()

            # raw_data.objects.filter(
            #     baseid_id__filename=filename).update(status='deleted')
            # basefile.objects.filter(filename=filename).update(
            #     filename=str(filename)+'Deleted')
        elif key == 'processing':  # Hold records when it is processing
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL':
                raw_data.objects.filter(
                    baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA1':
                raw_data.objects.filter(Q(l1_status__isnull=True) | ~Q(
                    l1_status='completed'), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA2':
                raw_data.objects.filter(Q(l2_status__isnull=True) | ~Q(
                    l2_status='completed'), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QC':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l3_status__isnull=True) | ~Q(l3_status='picked')), baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QA':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l4_status__isnull=True) | ~Q(l4_status='picked')), baseid_id__batch_name=batch_name).update(status='hold')

        elif key == 'hold':  # Unhold Records when it is Hold
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL':
                raw_data.objects.filter(
                    baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA1':
                raw_data.objects.filter(Q(l1_status__isnull=True) | ~Q(
                    l1_status='completed'), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA2':
                raw_data.objects.filter(Q(l2_status__isnull=True) | ~Q(
                    l2_status='completed'), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QC':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l3_status__isnull=True) | ~Q(l3_status='picked')), baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QA':
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status='completed')) & (Q(l2_status__isnull=True) | Q(l2_status='completed')) & (
                    Q(l4_status__isnull=True) | ~Q(l4_status='picked')), baseid_id__batch_name=batch_name).update(status='processing')

        return JsonResponse({'status': 'Success'})
    # return render(request, 'pages/upload.html')


@loginrequired
def remove_binary_and_newlines(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, bytes):
                del data[key]  # Remove binary value
            else:
                data[key] = remove_binary_and_newlines(value)
    elif isinstance(data, list):
        data = [remove_binary_and_newlines(item) for item in data]
    elif isinstance(data, str):
        data = data.replace('\n', '')

    return data


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def SampleFileDownloadView(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="evaluate.csv"'
    csv_writer = csv.writer(response)
    header = ["id_value", "question", "asin", "title", "product_url",
              "imagepath", "evidence", "answer_one", "answer_two"]
    csv_writer.writerow(header)
    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def loneproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    reporting = request.session.get('reporting')

    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)

    if request.method == 'GET':
        filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
            status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
        l1_count = raw_data.objects.filter(Q(l1_prod_id__end_time__date=timezone.now().date()), Q(
            l1_status='completed') & Q(l1_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l1_count is not None:
            l1_count = l1_count
        else:
            l1_count = 0

        BaseID = request.GET.get('baseid', None)
        if BaseID != None and BaseID != "":
            request.session['BaseID'] = BaseID
        else:
            BaseID = request.session.get('BaseID', None)

        batcQueue = raw_data.objects.filter(baseid_id=BaseID).exclude(
            status__in=['hold', 'deleted']).exists()
        if batcQueue:
            try:
                with transaction.atomic():
                    reporting_list = userProfile.objects.filter(
                        reporting_id=reporting).values_list('id', flat=True)

                    comn_query = Q()
                    if language:
                        comn_query &= Q(baseid_id__language__in=language)
                    comn_query &= (Q(l2_emp_id__isnull=True) |
                                   Q(l2_emp_id__in=reporting_list))

                    instance = raw_data.objects.select_for_update(skip_locked=True).filter(Q(baseid_id=BaseID) &
                                                                                           comn_query & (Q(reporting_by_id=reporting) | Q(reporting_by_id__isnull=True)) &
                                                                                           (
                        (Q(l1_status='picked') & Q(l1_emp_id=EmpID)) | (
                            Q(l1_status='not_picked') & Q(l1_emp_id__isnull=True) & Q(l1_loc__isnull=True))
                    ) & (
                        Q(l2_loc__isnull=True) | Q(
                            l2_loc=location)
                    )
                    ).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l1_emp_id', 'baseid__batch_name').exclude(status__in=['hold', 'deleted']).exclude(l2_emp_id=EmpID).order_by('baseid_id', 'id', '-l1_status').first()

                    if instance:
                        from_weeks = timezone.now() - timedelta(weeks=2)
                        que_count = raw_data.objects.filter(
                            baseid__created_at__date__gte=from_weeks, question=instance['question']).count()

                        ###################################
                        dup_count = raw_data.objects.filter(
                            question=instance['question']).exclude(status__in=['hold']) .count()
                        if dup_count > 1:
                            raw_data.objects.filter(baseid_id=BaseID, question=instance['question'], reporting_by__isnull=True).update(
                                reporting_by=reporting)

                        # user_ids = list(reporting_list.filter(role='DA1').values_list('userprofile_id', flat=True))
                        # user_id = list(Activitys.objects.filter(created_at__date=timezone.now().date(),end_time__isnull=True,empID__in=user_ids,activity_name='Login').values_list('empID_id',flat=True))

                        # dup_count = raw_data.objects.filter(question=instance['question']).exclude(l1_status__in=['picked', 'completed']) .count()
                        # if dup_count > 1:
                        #     dup_ids = raw_data.objects.filter(baseid_id=BaseID,question=instance['question']).values_list('id', flat=True).exclude(l2_emp_id=EmpID)
                        #     if dup_ids:
                        #         for id in dup_ids:
                        #             rand_id = random.choice(user_id)
                        #             raw_data.objects.filter(id=id,baseid_id=BaseID) \
                        #                             .exclude(l1_status__in=['picked', 'completed']).exclude(l2_emp_id=EmpID) \
                        #                             .update(l1_emp_id=rand_id,l1_status='picked',l1_loc=location)
                    #################################################

                        l1prod = l1_production.objects
                        if l1prod.filter(qid_id=instance['id']).exists():
                            l1_production.objects.filter(qid_id=instance['id']).update(
                                start_time=timezone.now())
                            raw_data.objects.filter(id=instance['id']).update(reporting_by=reporting,
                                l1_status='picked', l1_emp_id=EmpID, l1_loc=location)
                        else:
                            prodid = l1_production.objects.create(
                                qid_id=instance['id'], start_time=timezone.now())
                            raw_data.objects.filter(id=instance['id']).update(reporting_by=reporting,
                                l1_status='picked', l1_emp_id=EmpID, l1_loc=location, l1_prod_id=prodid.id)
                    else:
                        request.session['BaseID'] = None
                        que_count = 0
                    return render(request, 'pages/l1_production.html', {'filenames': filenames, 'que_count': que_count, 'result': instance, 'l1_count': l1_count, 'start_time': timezone.now()})
            except Exception as er:
                print(er)
        instance = []
        que_count = 0
        return render(request, 'pages/l1_production.html', {'filenames': filenames, 'que_count': que_count, 'result': instance, 'l1_count': l1_count, 'start_time': timezone.now()})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        q0 = request.POST.get('q0', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)

        q4_1 = request.POST.get('q4_1', None)
        q4_11 = request.POST.getlist('q4_11', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)

        q4_2 = request.POST.get('q4_2', None)
        q4_22 = request.POST.getlist('q4_22', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)

        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        annot_commant = request.POST.get('annot_commant', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                    l1prod_values = l1prod.values_list('id', flat=True)

                    link_objects = [
                        l1_production_link(
                            production_id=l1prod_values, link=value, linkfor='q7_1')
                        for value in q7_other_1 if value
                    ] + [
                        l1_production_link(
                            production_id=l1prod_values, link=value, linkfor='q7_2')
                        for value in q7_other_2 if value
                    ]

                    with transaction.atomic():
                        l1_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l1prod_values = l1prod.values_list('id', flat=True)
                link_objects = [
                    l1_production_link(
                        production_id=l1prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l1_production_link(
                        production_id=l1prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]

                with transaction.atomic():
                    l1_production_link.objects.bulk_create(link_objects)
                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='hold', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def ltwoproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    reporting = request.session.get('reporting')

    if request.method == 'GET':
        filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
            status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()

        BaseID = request.GET.get('baseid', None)
        if BaseID != None and BaseID != "":
            request.session['BaseID'] = BaseID
        else:
            BaseID = request.session.get('BaseID', None)

        l2_count = raw_data.objects.filter(Q(l2_prod_id__end_time__date=timezone.now().date()), Q(
            l2_status='completed') & Q(l2_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l2_count is not None:
            l2_count = l2_count
        else:
            l2_count = 0

        batcQueue = raw_data.objects.filter(baseid_id=BaseID).exclude(
            status__in=['hold', 'deleted']).exists()
        if batcQueue:
            try:
                with transaction.atomic():
                    reporting_list = userProfile.objects.filter(
                        reporting_id=reporting).values_list('id', flat=True)

                    comn_query = Q()
                    if language:
                        comn_query &= Q(baseid_id__language__in=language)
                    comn_query &= (Q(l1_emp_id__isnull=True) |
                                   Q(l1_emp_id__in=reporting_list))

                    instance = raw_data.objects.select_for_update(skip_locked=True).filter(Q(baseid_id=BaseID) &
                                                                                           comn_query & (Q(reporting_by_id=reporting) | Q(reporting_by_id__isnull=True)) &
                                                                                           (
                        (Q(l2_status='picked') & Q(l2_emp_id=EmpID)) | (
                            Q(l2_status='not_picked') & Q(l2_emp_id__isnull=True) & Q(l2_loc__isnull=True))
                    ) & (
                        Q(l1_loc__isnull=True) | Q(
                            l1_loc=location)
                    )
                    ).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l2_emp_id', 'baseid__batch_name').exclude(status__in=['hold', 'deleted']).exclude(l1_emp_id=EmpID).order_by('baseid_id', 'id', '-l2_status').first()

                    if instance:
                        from_weeks = timezone.now() - timedelta(weeks=2)
                        que_count = raw_data.objects.filter(
                            baseid__created_at__date__gte=from_weeks, question=instance['question']).count()

                        ###################################
                        dup_count = raw_data.objects.filter(
                            question=instance['question']).exclude(status__in=['hold']) .count()
                        if dup_count > 1:
                            raw_data.objects.filter(baseid_id=BaseID, question=instance['question'], reporting_by__isnull=True).update(
                                reporting_by=reporting)

                        # user_ids = list(reporting_list.filter(role='DA2').values_list('userprofile_id', flat=True))
                        # user_id = list(Activitys.objects.filter(created_at__date=timezone.now().date(),end_time__isnull=True,empID__in=user_ids,activity_name='Login').values_list('empID_id',flat=True))

                        # dup_count = raw_data.objects.filter(question=instance['question']).exclude(l2_status__in=['picked', 'completed']) .count()
                        # if dup_count > 1:
                        #     dup_ids = raw_data.objects.filter(baseid_id=BaseID,question=instance['question']).values_list('id', flat=True).exclude(l1_emp_id=EmpID)
                        #     if dup_ids:
                        #         for id in dup_ids:
                        #             rand_id = random.choice(user_id)
                        #             raw_data.objects.filter(id=id,baseid_id=BaseID) \
                        #                             .exclude(l2_status__in=['picked', 'completed']).exclude(l1_emp_id=EmpID) \
                        #                             .update(l2_emp_id=rand_id,l2_status='picked',l2_loc=location)
                        #################################################

                        l2prod = l2_production.objects
                        if l2prod.filter(qid_id=instance['id']).exists():
                            l2_production.objects.filter(qid_id=instance['id']).update(
                                start_time=timezone.now())
                            raw_data.objects.filter(id=instance['id']).update(reporting_by=reporting,
                                l2_status='picked', l2_emp_id=EmpID, l2_loc=location)
                        else:
                            prodid = l2_production.objects.create(
                                qid_id=instance['id'], start_time=timezone.now())
                            raw_data.objects.filter(id=instance['id']).update(reporting_by=reporting,
                                l2_status='picked', l2_emp_id=EmpID, l2_loc=location, l2_prod_id=prodid.id)
                    else:
                        request.session['BaseID'] = None
                        que_count = 0
                    return render(request, 'pages/l2_production.html', {'filenames': filenames, 'que_count': que_count, 'result': instance, "l2_count": l2_count, 'start_time': timezone.now()})
            except Exception as er:
                print(er)
        instance = []
        que_count = 0
        return render(request, 'pages/l2_production.html', {'filenames': filenames, 'que_count': que_count, 'result': instance, "l2_count": l2_count, 'start_time': timezone.now()})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        q0 = request.POST.get('q0', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)

        q4_1 = request.POST.get('q4_1', None)
        q4_11 = request.POST.getlist('q4_11', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)

        q4_2 = request.POST.get('q4_2', None)
        q4_22 = request.POST.getlist('q4_22', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)

        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        annot_commant = request.POST.get('annot_commant', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l2prod_values = l2prod.values_list('id', flat=True)
                link_objects = [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]

                with transaction.atomic():
                    l2_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                           l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l2prod_values = l2prod.values_list('id', flat=True)
                link_objects = [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    l2_production_link.objects.bulk_create(link_objects)

                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                           l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod_values,
                                                           l2_status='hold', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)


def queue():
    rawData = raw_data.objects.filter(Q(l1_status='completed') & Q(
        l2_status='completed') & Q(l1_l2_accuracy__isnull=True)).values('id')
    for i in rawData:
        fromqueue = l1_l2Comparison(i['id'])
        queue = fromqueue['result']
        if 'Not Matched' in queue['Comparison'].values:
            l1_l2_accuracy = 'fail'
        else:
            l1_l2_accuracy = 'pass'
        raw_data.objects.filter(id=i['id']).update(
            l1_l2_accuracy=l1_l2_accuracy)
    return


def l1_l2Comparison(id):
    l1_prod = l1_production.objects.filter(qid_id=id).values('id', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1',
                                                             'que7_ans1', 'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 'que7_ans2',
                                                             'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2', 'general_ques1')
    l2_prod = l2_production.objects.filter(qid_id=id).values('id', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1',
                                                             'que7_ans1', 'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 'que7_ans2',
                                                             'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2', 'general_ques1')

    df1 = pd.DataFrame(l1_prod).fillna('null')
    df2 = pd.DataFrame(l2_prod).fillna('null')

    if not df1.empty and not df2.empty:

        l1id = int(df1['id'].item())
        l2id = int(df2['id'].item())

        if l1id:
            l1_prod_link = l1_production_link.objects.filter(
                production_id=l1id).values('linkfor', 'link')
        else:
            l1_prod_link = []
        if l2id:
            l2_prod_link = l2_production_link.objects.filter(
                production_id=l2id).values('linkfor', 'link')
        else:
            l2_prod_link = []

        result_list = []
        for field in fields_to_compare:
            # print(df1[field],"===========", df2[field])
            comparison_result = 'Matched' if (
                df1[field] == df2[field]).all() else 'Not Matched'
            result_list.append(
                {'Field': field, 'Comparison': comparison_result, 'DA2ans': str(df2[field].item())})

        result_df = pd.DataFrame(result_list)

        l2_generalcommndas = l2_production.objects.filter(
            qid_id=id).values('general_ques2', 'annotation_comment')[0]

        datas = {'result': result_df, 'l1_prod_link': l1_prod_link,
                 'l2_prod_link': l2_prod_link, 'l2gencomds': l2_generalcommndas}
        return datas
    else:
        return False


@loginrequired
def lthreeproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    reporting = request.session.get('reporting')

    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        q0 = request.POST.get('q0', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)

        q4_1 = request.POST.get('q4_1', None)
        q4_11 = request.POST.getlist('q4_11', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)

        q4_2 = request.POST.get('q4_2', None)
        q4_22 = request.POST.getlist('q4_22', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)

        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        annot_commant = request.POST.get('annot_commant', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)
                    l3prod_values = l3prod.values_list('id', flat=True)

                    link_objects = [
                        QcQa_production_link(
                            l3production_id=l3prod_values, link=value, linkfor='q7_1', prodtype='QC')
                        for value in q7_other_1 if value
                    ] + [
                        QcQa_production_link(
                            l3production_id=l3prod_values, link=value, linkfor='q7_2', prodtype='QC')
                        for value in q7_other_2 if value
                    ]
                    with transaction.atomic():
                        QcQa_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                           l3_status='completed', l3_emp_id=EmpID)
                    error_checker(eid)
            except Exception as er:
                print(er)
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)

                    l3prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l3prod_values = l3prod.values_list('id', flat=True)

                link_objects = [
                    QcQa_production_link(
                        l3production_id=l3prod_values, link=value, linkfor='q7_1', prodtype='QC')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l3production_id=l3prod_values, link=value, linkfor='q7_2', prodtype='QC')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                           l3_status='completed', l3_emp_id=EmpID)
                    error_checker(eid)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod_values,
                                                           l3_status='hold', l3_emp_id=EmpID)
                    # error_checker(eid)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        l3_count = raw_data.objects.filter(Q(l3_prod_id__end_time__date=timezone.now().date()), Q(
            l3_status='completed') & Q(l3_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l3_count is not None:
            l3_count = l3_count
        else:
            l3_count = 0
        try:
            reporting_list = userProfile.objects.filter(
                reporting_id=reporting).values_list('id', flat=True)

            query = Q()
            if language:
                query = Q(baseid_id__language__in=language) & Q(
                    l1_emp_id__in=reporting_list) & Q(l2_emp_id__in=reporting_list)

            def loop():
                with transaction.atomic():
                    rawData = raw_data.objects.select_for_update(skip_locked=True).filter(
                        Q(l1_status='completed') & Q(l2_status='completed') & query &
                        (
                            (Q(l3_status='not_moved') & Q(l3_emp_id__isnull=True)) | (
                                Q(l3_status='picked') & Q(l3_emp_id=EmpID))
                        ) & (
                            Q(l1_l2_accuracy__isnull=True) | Q(
                                l1_l2_accuracy='fail')
                        )
                    ).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two','baseid__batch_name').exclude(status__in=['hold', 'deleted']).exclude(l1_l2_accuracy='pass').exclude(l1_emp_id=EmpID).exclude(l2_emp_id=EmpID).order_by('baseid_id', 'id', '-l3_status').first()

                    if rawData and rawData is not None:
                        from_weeks = timezone.now() - timedelta(weeks=2)
                        que_count = raw_data.objects.filter(
                            baseid__created_at__date__gte=from_weeks, question=rawData['question']).count()

                        l3comp = l1_l2Comparison(rawData['id'])
                        if l3comp:
                            l3input = l3comp['result']
                            l3link = l3comp
                            if 'Not Matched' in l3input['Comparison'].values:
                                l1_l2_accuracy = 'fail'

                                if l3_production.objects.filter(qid_id=rawData['id']).exists():
                                    l3_production.objects.filter(qid_id=rawData['id']).update(
                                        start_time=timezone.now())
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l3_status='picked', l3_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy)
                                else:
                                    prodid = l3_production.objects.create(
                                        qid_id=rawData['id'], start_time=timezone.now(), created_by_id=EmpID)
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l3_status='picked', l3_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy, l3_prod_id=prodid.id)

                                l3dict = json.dumps(
                                    l3input.to_dict(orient='records'))
                                return {'que_count': que_count, 'start_time': timezone.now(), 'l3_count': l3_count, 'result': rawData, 'status': l3dict, 'l1_prod_link': l3link['l1_prod_link'], 'l2_prod_link': l3link['l2_prod_link'], 'gencomds': l3comp['l2gencomds']}
                            else:
                                l1_l2_accuracy = 'pass'
                                raw_data.objects.filter(id=rawData['id']).update(
                                    l1_l2_accuracy=l1_l2_accuracy)
                                return loop()
                        return None
                    return None

            loop_result = loop()
            if loop_result:
                return render(request, 'pages/l3_production.html', loop_result)
            else:
                queue()
                return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': []})
        except Exception as er:
            print(er)
            # , 'l3count':l3count l3count = raw_data.objects.filter(Q(l3_status='completed', l3_emp_id=EmpID)).values('baseid__batch_name').annotate(l3count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
            rawData = []
        return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': rawData})


@loginrequired
def lfourproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    reporting = request.session.get('reporting')

    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        q0 = request.POST.get('q0', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)

        q4_1 = request.POST.get('q4_1', None)
        q4_11 = request.POST.getlist('q4_11', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)

        q4_2 = request.POST.get('q4_2', None)
        q4_22 = request.POST.getlist('q4_22', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)

        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        annot_commant = request.POST.get('annot_commant', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l4prod_values = l4prod.values_list('id', flat=True)
                link_objects = [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_1', prodtype='QA')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_2', prodtype='QA')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                           l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l4prod_values = l4prod.values_list('id', flat=True)
                link_objects = [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_1', prodtype='QA')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_2', prodtype='QA')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                           l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod_values,
                                                           l4_status='hold', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
            status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
        l4_count = raw_data.objects.filter(Q(l4_prod_id__end_time__date=timezone.now().date()), Q(
            l4_status='completed') & Q(l4_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l4_count is not None:
            l4_count = l4_count
        else:
            l4_count = 0

        BaseID = request.GET.get('baseid', None)
        if BaseID != None and BaseID != "":
            request.session['BaseID'] = BaseID
        else:
            BaseID = request.session.get('BaseID')

        batcQueue = raw_data.objects.filter(baseid_id=BaseID).exists()
        if batcQueue:
            try:
                reporting_list = userProfile.objects.filter(
                    reporting_id=reporting).values_list('id', flat=True)

                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language) & Q(
                        l1_emp_id__in=reporting_list) & Q(l2_emp_id__in=reporting_list)

                filecount = raw_data.objects.filter(l1_l2_accuracy='pass', baseid_id=BaseID).exclude(status__in=['hold', 'deleted']).aggregate(comp_count=Count(
                    'l4_status', Q(l4_status='completed')), cur_count=Count('l4_status', Q(l4_status='not_picked')), total_count=Count('l1_l2_accuracy', Q(l1_l2_accuracy='pass')))
                getdata_for_target = QA_queue.objects.filter(queue_batch_id=BaseID).aggregate(
                    queue=Sum(Cast('queue_percentage', models.IntegerField())))
                target_percentage = int(getdata_for_target['queue'])

                queue = int(target_percentage / 100 *
                            int(filecount['total_count']))

                print("Total :", int(filecount['total_count']), "Queue :", queue,
                      "Competed :", filecount['comp_count'], "Target % :", getdata_for_target)
                # print(filecount['comp_count'] <= queue)
                if filecount['comp_count'] < queue and int(filecount['cur_count']) >= 0 and int(queue) >= 0:
                    with transaction.atomic():
                        rawData = raw_data.objects.select_for_update(skip_locked=True).filter(Q(l1_status='completed') & Q(l2_status='completed') & query &
                                                                                              (
                            Q(l4_status='not_picked') & Q(l4_emp_id__isnull=True) | Q(
                                l4_status='picked') & Q(l4_emp_id=EmpID)
                        ) &
                            (
                            Q(l1_l2_accuracy__isnull=True) | Q(
                                l1_l2_accuracy='pass')
                        ) & Q(baseid_id=BaseID)
                        ).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two').exclude(status__in=['hold', 'deleted']).exclude(l1_l2_accuracy='fail').exclude(l1_emp_id=EmpID).exclude(l2_emp_id=EmpID).order_by('baseid_id', 'id', '-l4_status').first()

                        if rawData:
                            from_weeks = timezone.now() - timedelta(weeks=2)
                            que_count = raw_data.objects.filter(
                                baseid__created_at__date__gte=from_weeks, question=rawData['question']).count()

                            l4comp = l1_l2Comparison(rawData['id'])
                            if l4comp:
                                l4input = l4comp['result']

                                if 'Not Matched' in l4input['Comparison'].values:
                                    l1_l2_accuracy = 'fail'
                                    raw_data.objects.filter(id=rawData['id']).update(
                                        l1_l2_accuracy=l1_l2_accuracy)
                                    return redirect('/api/v8/productionl4/')
                                else:
                                    l1_l2_accuracy = 'pass'

                                    l4prod = l4_production.objects
                                    if l4prod.filter(qid_id=rawData['id']).exists():
                                        l4_production.objects.filter(qid_id=rawData['id']).update(
                                            start_time=timezone.now())
                                        raw_data.objects.filter(id=rawData['id']).update(
                                            l4_status='picked', l4_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy)
                                    else:
                                        prodid = l4_production.objects.create(
                                            qid_id=rawData['id'], start_time=timezone.now())

                                        raw_data.objects.filter(id=rawData['id']).update(
                                            l4_status='picked', l4_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy, l4_prod_id=prodid.id)
                                    l4dict = json.dumps(
                                        l4input.to_dict(orient='records'))
                                    return render(request, 'pages/l4_production.html', {'que_count': que_count, 'start_time': timezone.now(), 'l4_count': l4_count, 'result': rawData, 'status': l4dict, 'l1_prod_link': l4comp['l1_prod_link'], 'l2_prod_link': l4comp['l2_prod_link'], 'gencomds': l4comp['l2gencomds']})
                return render(request, 'pages/l4_production.html', {'filenames': filenames, 'l4_count': l4_count, 'result': []})
            except Exception as er:
                print(er)
                # , 'l4count':l4count l4count = raw_data.objects.filter(Q(l4_status='completed', l4_emp_id=EmpID)).values('baseid__batch_name').annotate(l4count=Count('baseid__batch_name')).exclude(status__in=['hold', 'deleted']).order_by('-baseid__batch_name')
        rawData = []
        return render(request, 'pages/l4_production.html', {'filenames': filenames, 'l4_count': l4_count, 'result': rawData})


@loginrequired
def lfourWithoutProdURLproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    reporting = request.session.get('reporting')
    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)

        q0 = request.POST.get('q0', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)

        q4_1 = request.POST.get('q4_1', None)
        q4_11 = request.POST.getlist('q4_11', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)

        q4_2 = request.POST.get('q4_2', None)
        q4_22 = request.POST.getlist('q4_22', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)

        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        annot_commant = request.POST.get('annot_commant', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l4wpuprod = l4wpu_production.objects.filter(qid_id=eid)
                    l4wpuprod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                     que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l4wpuprod_values = l4wpuprod.values_list('id', flat=True)
                link_objects = [
                    l4wpu_production_link(
                        production_id=l4wpuprod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l4wpu_production_link(
                        production_id=l4wpuprod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    l4wpu_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4wpu_prod_id=l4wpuprod_values,
                                                           l4wpu_status='completed', l4wpu_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l4wpuprod = l4wpu_production.objects.filter(qid_id=eid)
                    l4wpuprod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                     que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)

                l4wpuprod_values = l4wpuprod.values_list('id', flat=True)
                link_objects = [
                    QcQa_production_link(
                        l4wpuproduction_id=l4wpuprod_values, link=value, linkfor='q7_1', prodtype='QA')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l4wpuproduction_id=l4wpuprod_values, link=value, linkfor='q7_2', prodtype='QA')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4wpu_prod_id=l4wpuprod_values,
                                                           l4wpu_status='completed', l4wpu_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l4wpuprod = l4wpu_production.objects.filter(qid_id=eid)
                    l4wpuprod.update(end_time=timezone.now(), que0=q0, que1=q1, que2=q2, que2_1=q2_1, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que4_ans11=','.join(q4_11),  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                     que10_ans1=q10_1, que11_ans1=q11_1, que4_ans2=q4_2, que4_ans22=','.join(q4_22), que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, created_by_id=EmpID)
                l4wpuprod_values = l4wpuprod.values_list('id', flat=True)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4wpu_prod_id=l4wpuprod_values,
                                                           l4wpu_status='hold', l4wpu_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
            status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
        l4wpu_count = raw_data.objects.filter(Q(l4wpu_prod_id__end_time__date=timezone.now().date()), Q(
            l4wpu_status='completed') & Q(l4wpu_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l4wpu_count is not None:
            l4wpu_count = l4wpu_count
        else:
            l4wpu_count = 0

        BaseID = request.GET.get('baseid', None)
        if BaseID != None and BaseID != "":
            request.session['BaseID'] = BaseID
        else:
            BaseID = request.session.get('BaseID')

        reporting_list = userProfile.objects.filter(
            reporting_id=reporting).values_list('id', flat=True)
        query = Q()
        if language:
            query = Q(baseid_id__language__in=language) & (
                Q(l3_emp_id__in=reporting_list) | Q(l4_emp_id__in=reporting_list))

        batcQueue = raw_data.objects.filter(baseid_id=BaseID).exists()
        if batcQueue:
            try:
                with transaction.atomic():
                    rawData = raw_data.objects.select_for_update(skip_locked=True).filter(((Q(l3_status='completed') & Q(l3_prod__general_ques1='A and B are equally good')) | (Q(l4_status='completed') & Q(l4_prod__general_ques1='A and B are equally good'))) & (Q(product_url__isnull=True) | Q(product_url='')) & query & (Q(l4wpu_status='not_picked') & Q(l4wpu_emp_id__isnull=True)) | (Q(l4wpu_status='picked') & Q(l4wpu_emp_id=EmpID))
                                                                                          & Q(baseid_id=BaseID)).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l1_l2_accuracy').exclude(status__in=['hold', 'deleted']).exclude(l1_emp_id=EmpID).exclude(l2_emp_id=EmpID).exclude(l3_emp_id=EmpID).exclude(l4_emp_id=EmpID).order_by('baseid_id', 'id', '-l4wpu_status').first()
                    if rawData:
                        l4wpuprod = l4wpu_production.objects
                        if l4wpuprod.filter(qid_id=rawData['id']).exists():
                            l4wpu_production.objects.filter(
                                qid_id=rawData['id']).update(start_time=timezone.now())
                            raw_data.objects.filter(id=rawData['id']).update(
                                l4wpu_status='picked', l4wpu_emp_id=EmpID)
                        else:
                            prodid = l4wpu_production.objects.create(
                                qid_id=rawData['id'], start_time=timezone.now())
                            raw_data.objects.filter(id=rawData['id']).update(
                                l4wpu_status='picked', l4wpu_emp_id=EmpID, l4wpu_prod_id=prodid.id)
                        if rawData['l1_l2_accuracy'] == 'fail':
                            finl_prod_dict = json.dumps(list(l3_production.objects.filter(
                                qid_id=rawData['id']).values(*list(basic_model_with_kv.keys()))))
                        elif rawData['l1_l2_accuracy'] == 'pass':
                            finl_prod_dict = json.dumps(list(l4_production.objects.filter(
                                qid_id=rawData['id']).values(*list(basic_model_with_kv.keys()))))
                        return render(request, 'pages/l4_WPU_production.html', {'start_time': timezone.now(), 'l4_count': l4wpu_count, 'result': rawData, 'finl_prod_dict': finl_prod_dict})
                    return render(request, 'pages/l4_WPU_production.html', {'filenames': filenames, 'l4_count': l4wpu_count, 'result': []})
            except Exception as er:
                print(er)
        rawData = []
        return render(request, 'pages/l4_WPU_production.html', {'filenames': filenames, 'l4_count': l4wpu_count, 'result': rawData})


@loginrequired
def repetitionsView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    if request.method == 'POST':
        key = request.POST.get('key', None)

        eid = request.POST.get('eid', None)

        rept_commands = request.POST.get('rept_commands', None)
        # q1 = request.POST.get('q1', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    reptprod = Repetitions.objects.filter(qid_id=eid)
                    reptprod.update(end_time=timezone.now(
                    ), rept_commands=rept_commands, is_status='completed')

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(rept_prod_id=reptprod.values_list('id', flat=True),
                                                           rept_status='completed', rept_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    reptprod = Repetitions.objects.filter(qid_id=eid)
                    reptprod.update(end_time=timezone.now(
                    ), rept_commands=rept_commands, is_status='completed')

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(rept_prod_id=reptprod.values_list('id', flat=True),
                                                           rept_status='completed', rept_emp_id=EmpID)
                redirect_url = '/dash/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
    else:
        rept_count = raw_data.objects.filter(Q(l3_prod_id__end_time__date=timezone.now().date()), Q(
            rept_status='completed') & Q(rept_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if rept_count is not None:
            rept_count = rept_count
        else:
            rept_count = 0
        try:
            query = Q()
            if language:
                query = Q(baseid_id__language__in=language)

            first_RECD = basefile.objects.order_by('id').first()
            if first_RECD:
                new_id = int(first_RECD.batch_name[5:])
            else:
                new_id = 1
            batch_name = f'{new_id:05}'

            with transaction.atomic():
                rawData = raw_data.objects.select_for_update(skip_locked=True) \
                    .filter((Q(l3_status='completed') | Q(l4_status='completed')) & query & ~Q(baseid__batch_name__endswith=batch_name) &
                            ((Q(rept_status='not_picked') & Q(rept_emp_id__isnull=True)) | (
                                Q(rept_status='picked') & Q(rept_emp_id=EmpID)))
                            ) \
                    .values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', BatchID=F('baseid__batch_name')) \
                    .exclude(status__in=['hold', 'deleted']).exclude(rept_status='completed') \
                    .order_by('baseid_id', 'id').first()  # .exclude(l3_emp_id=EmpID).exclude(l4_emp_id=EmpID)

                to_find_dup = pd.DataFrame(rawData, index=[0])
                if not to_find_dup.empty:
                    dup_table = find_dups('for display', to_find_dup)
                else:
                    dup_table = pd.DataFrame()

                if rawData and dup_table['status'] == 'dup found' and int(str(rawData['BatchID'])[5:]) > int(batch_name):
                    l3_final_record = l3_production.objects.filter(
                        qid_id=rawData['id'])
                    l4_final_record = l4_production.objects.filter(
                        qid_id=rawData['id'])
                    main_dict = {}
                    if l3_final_record.exists():
                        is_final_data = l3_final_record
                        main_dict.update({'prod': 'QC Production'})
                    elif l4_final_record.exists():
                        is_final_data = l4_final_record
                        main_dict.update({'prod': 'QA Production'})

                    if is_final_data:
                        final_datas = is_final_data.values('id',
                                                           'que0', 'que1', 'que2', 'que2_1', 'is_present_both',
                                                           'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 'que8_ans1', 'que9_ans1',
                                                           'que10_ans1', 'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2',
                                                           'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2',
                                                           'general_ques1', 'general_ques2', 'annotation_comment',
                                                           ).first()
                        final_datas.update(main_dict)
                        rept_obj = Repetitions.objects
                        if rept_obj.filter(qid_id=rawData['id']).exists():
                            rept_obj.filter(qid_id=rawData['id']).update(
                                start_time=timezone.now())
                        else:
                            prodid = rept_obj.create(
                                qid_id=rawData['id'], start_time=timezone.now())
                            raw_data.objects.filter(id=rawData['id']).update(
                                rept_status='picked', rept_emp_id=EmpID, rept_prod_id=prodid.id)

                        return render(request, 'pages/repetitions.html', {'rept_count': rept_count, 'result': rawData, 'curr_datas': final_datas, 'basic_model_with_kv': basic_model_with_kv, 'dup_table': dup_table})
                    return redirect('/api/v8/repetition_process/')
                else:
                    rawData = []
        except Exception as er:
            print(er)
            rawData = []
        return render(request, 'pages/repetitions.html', {'rept_count': rept_count, 'result': rawData})

def error_checker(filterv):
    field_list = list(basic_model_with_kv.keys())
    field_list.append('qid')
    try:
        l3_prod = l3_production.objects.filter(qid_id=filterv).values(*fields_to_compare, 'qid', 'qid__l1_prod', 'qid__l2_prod', 'qid__l3_emp')
        if l3_prod.exists():
            l1_prod_data = l1_production.objects.filter(qid_id = filterv,qid__l3_status='completed') \
                .values('id', *fields_to_compare, 'qid', 'qid__l1_emp__employeeID', 'qid__baseid__batch_name', 'qid__id_value', 'qid__l1_emp')
            l2_prod_data = l2_production.objects.filter(qid_id = filterv,qid__l3_status='completed') \
                .values('id', *fields_to_compare, 'qid', 'qid__l2_emp__employeeID', 'qid__baseid__batch_name', 'qid__id_value', 'qid__l2_emp')

            l1_prod_dict = {item['id']: item for item in l1_prod_data}
            l2_prod_dict = {item['id']: item for item in l2_prod_data}

            for l3_item in l3_prod:
                l1_item = l1_prod_dict.get(l3_item['qid__l1_prod'])
                l2_item = l2_prod_dict.get(l3_item['qid__l2_prod'])
                # qc_error_by = l3_item['qid__l3_emp']

                if l1_item:
                    question_list1 = [
                        field for field in fields_to_compare if l3_item[field] != l1_item[field]]
                    if question_list1:
                        if not da1_da2_error_report.objects.filter(qid_id=l3_item['qid'], error_scope='DA1').exists():
                            da1_da2_error_report.objects.get_or_create(
                                qid_id=l3_item['qid'], ques_ans=question_list1, error_scope='DA1', error_status='Error', error_by_id=l1_item['qid__l1_emp'], status='progress'
                            )

                if l2_item:
                    question_list2 = [
                        field for field in fields_to_compare if l3_item[field] != l2_item[field]]
                    if question_list2:
                        if not da1_da2_error_report.objects.filter(qid_id=l3_item['qid'], error_scope='DA2').exists():
                            da1_da2_error_report.objects.get_or_create(
                                qid_id=l3_item['qid'], ques_ans=question_list2, error_scope='DA2', error_status='Error', error_by_id=l2_item['qid__l2_emp'], status='progress'
                            )
    except Exception as er:
        print(er)
    return "Success"

@loginrequired
def errornotify(request):
    EmpID = request.session.get('empId')
    result1 = da1_da2_error_report.objects.filter(Q(error_by=EmpID) & Q(error_status='Error')).exclude(status='Completed').count()
    result2 = qc_error_report.objects.filter((Q(error_status = 'Denied') | Q(error_status='Error')) & Q(error_by=EmpID)).exclude(master__status='Completed').count()
    result = result1 + result2
    return JsonResponse({'error_count':result})

@loginrequired
def errorreport(request):
    EmpID = request.session.get('empId')
    reportings = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
            'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    filenames = raw_data.objects.values('baseid_id','baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    
    if request.method == 'POST':
        key = request.POST.get('key')

        scopes = request.session['permlist']
        if key == 'getData':
            filename = request.POST.get('filename')

            basic_list = ['qid__baseid__batch_name', 'qid__id_value',
                          'qid', 'ques_ans', 'id', 'error_scope']
            query = Q(status='progress')
            query1 = Q()
            if 'DA1' in scopes or 'DA2' in scopes or 'QC' in scopes:
                query &= Q(error_by=EmpID) & Q(error_status='Error')
                basic_list.append('error_by__employeeID')
            if 'Admin' in scopes or 'Super Admin' in scopes:
                query1 = Q(error_status='Denied', error_by__reporting=EmpID)

            query &= Q(qid__baseid__filename=filename)

            result1 = list(da1_da2_error_report.objects.filter(Q(error_by__reporting=EmpID) | (query & Q(error_by=EmpID)))
                           .values('id', *basic_list).exclude(status='Completed'))
            result2 = list(qc_error_report.objects.filter(query1 | Q(error_by=EmpID, master__qid__baseid__filename=filename, error_status='Error'))
                           .values('id', 'error_by__employeeID', 'error_scope', qid__baseid__batch_name=F('master__qid__baseid__batch_name'), qid__id_value=F('master__qid__id_value'), qid=F('master__qid'), ques_ans=F('master__ques_ans')).exclude(master__status='Completed'))
            result = result1 + result2

            if result:
                context = {'results': result, 'filenames': filenames}
            else:
                context = {'results': [], 'filenames': filenames, 'Alert': json.dumps(
                    {'type': 'info', 'title': 'Info', 'message': 'No Records'}),'reportings':reportings,'locations':locations}
            return render(request, 'pages/error_report.html', context)

        elif key == "error_details":
            qid = request.POST.get('qid')
            id = request.POST.get('id')
            er_obj = da1_da2_error_report.objects.filter(qid_id=qid, id=id)
            qcer_obj = qc_error_report.objects.filter(
                master__qid_id=qid, id=id)
            comns_obj = pd.DataFrame(raw_data.objects.filter(id=qid).values('baseid__batch_name', 'id_value',
                                     'question', 'answer_one', 'answer_two', 'product_url', 'asin', 'title', 'imagepath', 'evidence'))

            da1_er = list(er_obj.filter(Q(error_by=EmpID) & Q(error_scope='DA1') & Q(
                error_status='Error')).values_list('ques_ans', flat=True))
            da2_er = list(er_obj.filter(Q(error_by=EmpID) & Q(error_scope='DA2') & Q(
                error_status='Error')).values_list('ques_ans', flat=True))
            qc_er = list(qcer_obj.filter(Q(error_by=EmpID) & Q(error_scope='QC') & Q(
                error_status='Error')).values_list('master__ques_ans', flat=True))
            tl_er = list(qcer_obj.filter(Q(error_scope='QC') & Q(
                error_status='Denied')).values_list('master__ques_ans', flat=True))

            if da1_er:
                errors = l1_production.objects.filter(qid_id=qid, created_by_id=EmpID).values(
                    *da1_er[0]).annotate(Scope=Value("DA1"))
                comn_qc_tl_errors = l3_production.objects.filter(
                    qid_id=qid).values(*da1_er[0]).annotate(Scope=Value("QC"))
                user_comments = list(qcer_obj.values(
                    'comments').exclude(comments__isnull=True))
                if 'que7_ans1' in da1_er[0] or 'que7_ans2' in da1_er[0]:
                    links1 = list(l1_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                    links2 = list([])
                    links3 = list(QcQa_production_link.objects.filter(l3production_id__in = comn_qc_tl_errors.values_list('id',flat=True)).values('link','linkfor'))
                else:
                    links1 = list([])
                    links2 = list([])
                    links3 = list([])
            if da2_er:
                errors = l2_production.objects.filter(qid_id=qid, created_by_id=EmpID).values(
                    *da2_er[0]).annotate(Scope=Value("DA2"))
                comn_qc_tl_errors = l3_production.objects.filter(
                    qid_id=qid).values(*da2_er[0]).annotate(Scope=Value("QC"))
                user_comments = list(qcer_obj.values(
                    'comments').exclude(comments__isnull=True))
                if 'que7_ans1' in da2_er[0] or 'que7_ans2' in da2_er[0]:
                    links2 = list(l2_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                    links1 = list([])
                    links3 = list(QcQa_production_link.objects.filter(l3production_id__in = comn_qc_tl_errors.values_list('id',flat=True)).values('link','linkfor'))
                else:
                    links1 = list([])
                    links2 = list([])
                    links3 = list([])
            if qc_er:
                if 'DA1' in qcer_obj.values_list('master__error_scope', flat=True):
                    da1_errors = l1_production.objects.filter(qid_id=qid).values(
                        *qc_er[0]).annotate(Scope=Value("DA1"))
                    errors = da1_errors
                elif 'DA2' in qcer_obj.values_list('master__error_scope', flat=True):
                    da2_errors = l2_production.objects.filter(qid_id=qid).values(
                        *qc_er[0]).annotate(Scope=Value("DA2"))
                    errors = da2_errors
                comn_qc_tl_errors = l3_production.objects.filter(
                    qid_id=qid, created_by_id=EmpID).values(*qc_er[0]).annotate(Scope=Value("QC"))
                user_comments = list(qcer_obj.values('master__comments'))
                if 'que7_ans1' in qc_er[0] or 'que7_ans2' in qc_er[0]:
                    links3 = list(QcQa_production_link.objects.filter(l3production_id__in = comn_qc_tl_errors.values_list('id',flat=True)).values('link','linkfor'))
                    links1 = list(l1_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                    links2 = list(l2_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                else:
                    links1 = list([])
                    links2 = list([])
                    links3 = list([])  
            if tl_er:
                if 'DA1' in qcer_obj.values_list('master__error_scope', flat=True):
                    da1_errors = l1_production.objects.filter(qid_id=qid).values(
                        *tl_er[0]).annotate(Scope=Value("DA1"))
                    errors = da1_errors
                elif 'DA2' in qcer_obj.values_list('master__error_scope', flat=True):
                    da2_errors = l2_production.objects.filter(qid_id=qid).values(
                        *tl_er[0]).annotate(Scope=Value("DA2"))
                    errors = da2_errors
                comn_qc_tl_errors = l3_production.objects.filter(
                    qid_id=qid).values(*tl_er[0]).annotate(Scope=Value("QC"))
                user_comments = list(qcer_obj.values('comments').exclude(
                    comments__isnull=True)) + list(qcer_obj.values('master__comments').exclude(comments__isnull=True))
                if 'que7_ans1' in tl_er[0] or 'que7_ans2' in tl_er[0]:
                    links1 = list(l1_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                    links2 = list(l2_production_link.objects.filter(production_id__in = errors.values_list('id',flat=True)).values('link','linkfor'))
                    links3 = list(QcQa_production_link.objects.filter(l3production_id__in = comn_qc_tl_errors.values_list('id',flat=True)).values('link','linkfor'))
                else:
                    links1 = list([])
                    links2 = list([])
                    links3 = list([]) 
                # print(user_comments)

            datas = chain(errors, comn_qc_tl_errors)
            datas = pd.DataFrame(datas).fillna('')
            datas = datas.rename(columns=basic_model_with_kv)
            my_list = list(datas.columns)
            my_list.remove('Scope')
            my_list.insert(0, 'Scope')
            datas = datas[my_list]

            df_transposed = comns_obj.T.reset_index()
            df_transposed.columns = ['Field', 'Value']
            df_transposed = df_transposed.to_html(index=False)

            datas.index = np.arange(1, len(datas) + 1)
            datas = datas.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-hover">') \
                                   .replace('<thead>', '<thead class="thead-light align-item-center">') \
                                   .replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
            return JsonResponse({'datas': datas, 'comns_obj': df_transposed, 'cmnds': json.dumps(user_comments), 'code': 1,'links1':json.dumps(links1),'links2':json.dumps(links2),'links3':json.dumps(links3)})
        elif key == 'error_status':
            qid = request.POST.get('qid')
            id = request.POST.get('id')
            er_status = request.POST.get('er_status')
            if er_status == 'Deny':
                comments = request.POST.get('comments', None)
            if ('DA1' in scopes or 'DA2' in scopes) and 'QC' not in scopes:
                if er_status == 'Accept':
                    da1_da2_error_report.objects.filter(qid_id=qid, id=id, error_status='Error', error_scope__in=scopes, error_by_id=EmpID).update(
                        error_status='Error', status='Completed')
                elif er_status == 'Deny':
                    temp_datas = da1_da2_error_report.objects.filter(
                        qid_id=qid, id=id, error_status='Error', error_scope__in=scopes, error_by_id=EmpID)
                    qc_error_report.objects.create(master_id=temp_datas.values_list('id', flat=True)[
                                                   0], error_status='Error', error_scope='QC', error_by_id=temp_datas.values_list('qid__l3_emp_id', flat=True))
                    temp_datas.update(error_status='Denied', comments=comments)
            if 'QC' in scopes:
                if er_status == 'Accept':
                    qc_query = qc_error_report.objects.filter(master__qid_id=qid, id=id, error_status='Error', error_scope__in=scopes, error_by_id=EmpID)
                    
                    da1_da2_error_report.objects.filter(id__in=qc_query.values_list('master_id',flat=True)).update(status='Completed')
                    qc_query.update(
                        error_status='Error')
                elif er_status == 'Deny':
                    qc_error_report.objects.filter(master__qid_id=qid, id=id, error_status='Error', error_scope__in=scopes, error_by_id=EmpID).update(
                        error_status='Denied', comments=comments)
            if 'Admin' in scopes or 'Super Admin' in scopes:
                scopefor = str(request.POST.get('scopefor')).split(',')
                if 'DA1' in scopefor or 'DA2' in scopefor:
                    mid = qc_error_report.objects.filter(
                        id=id).values_list('master_id', flat=True)
                    da1_da2_error_report.objects.filter(qid_id=qid, error_scope__in=[
                                                        'DA1', 'DA2'], id__in=mid).update(error_status='Error', status='Completed')
                elif 'QC' in scopefor:
                    qc_query = qc_error_report.objects.filter(id=id)
                    da1_da2_error_report.objects.filter(id__in=qc_query.values_list('master_id',flat=True)).update(status='Completed')
                    qc_query.update(
                        error_status='Error')

            return JsonResponse({'code': 1})
        elif key == 'error_report':
            location = request.POST.get('location')
            filename = request.POST.get('filename')
            reporting = request.POST.get('reporting')

            common_filter = Q()
            if location != 'All':
                common_filter &= Q(error_by__location=location)

            if reporting != 'All':
                common_filter &= Q(error_by__reporting=reporting)

            error_da1_da2 = da1_da2_error_report.objects.filter(common_filter & Q(qid__baseid_id=filename)).values(mid = F('id'),Reporting = F('error_by__reporting__employeeID'), File_name = F('qid__baseid__filename')) \
                                                .annotate(review = Count('error_status'),
                                                          DA1_error_count = Count('error_scope' , filter=Q(error_status='Error', error_scope = 'DA1', status = 'Completed')),
                                                          DA2_error_count = Count('error_scope' , filter=Q(error_status='Error', error_scope = 'DA2', status = 'Completed')))

            error_qc = qc_error_report.objects.filter(common_filter & Q(master__qid__baseid_id=filename)).values(mid = F('master_id'),Reporting = F('error_by__reporting__employeeID')) \
                                                .annotate(QC_error_count = Count('error_scope' , filter=Q(error_status='Error', master__status = 'Completed')))
            
            master_df = pd.DataFrame(error_da1_da2)
            qc_df = pd.DataFrame(error_qc)
            if not master_df.empty and not qc_df.empty:
                mrgd = pd.merge(master_df,qc_df, on=['Reporting','mid'],how='left').fillna(0)
                mrgd = mrgd[['Reporting','File_name','review','DA1_error_count','DA2_error_count','QC_error_count']]
                mrgd = mrgd.groupby(['Reporting', 'File_name'])[['review', 'DA1_error_count', 'DA2_error_count', 'QC_error_count']].sum().reset_index()
                
                sum_row = pd.DataFrame({
                    # 'EmployeeID': ['Total'],
                    'Reporting': ['Total'],
                    'File_name': [''],
                    'review': [mrgd['review'].sum()],
                    'DA1_error_count': [mrgd['DA1_error_count'].sum()],
                    'DA2_error_count': [mrgd['DA2_error_count'].sum()],
                    'QC_error_count': [mrgd['QC_error_count'].sum()]
                })
                mrgd = pd.concat([mrgd, sum_row], ignore_index=True)
                mrgd.index = np.arange(1, len(mrgd) + 1)

                mrgd_html = mrgd.to_html()
                context = {'reportings':reportings,'locations':locations,'filename':filename,'location':location,
                            'reporting':reporting,'filenames': filenames,'mrgd_html':mrgd_html}
            elif not master_df.empty:
                master_df = master_df.fillna(0)
                mrgd = master_df[['Reporting','File_name','review','DA1_error_count','DA2_error_count','QC_error_count']]
                mrgd = mrgd.groupby(['Reporting', 'File_name'])[['review', 'DA1_error_count', 'DA2_error_count', 'QC_error_count']].sum().reset_index()
                
                sum_row = pd.DataFrame({
                    # 'EmployeeID': ['Total'],
                    'Reporting': ['Total'],
                    'File_name': [''],
                    'review': [master_df['review'].sum()],
                    'DA1_error_count': [master_df['DA1_error_count'].sum()],
                    'DA2_error_count': [master_df['DA2_error_count'].sum()]
                })
                mrgd = pd.concat([master_df, sum_row], ignore_index=True)
                mrgd.index = np.arange(1, len(mrgd) + 1)
                mrgd_html = mrgd.to_html()
                context = {'reportings':reportings,'locations':locations,'filename':filename,'location':location,
                            'reporting':reporting,'filenames': filenames,'mrgd_html':mrgd_html}
            elif not qc_df.empty:
                qc_df = qc_df.fillna(0)
                mrgd = qc_df[['Reporting','File_name','review','DA1_error_count','DA2_error_count','QC_error_count']]
                mrgd = mrgd.groupby(['Reporting', 'File_name'])[['review', 'DA1_error_count', 'DA2_error_count', 'QC_error_count']].sum().reset_index()
                
                sum_row = pd.DataFrame({
                    # 'EmployeeID': ['Total'],
                    'Reporting': ['Total'],
                    'File_name': [''],
                    'review': [master_df['review'].sum()],
                    'DA1_error_count': [master_df['DA1_error_count'].sum()],
                    'DA2_error_count': [master_df['DA2_error_count'].sum()]
                })
                mrgd = pd.concat([master_df, sum_row], ignore_index=True)
                mrgd.index = np.arange(1, len(mrgd) + 1)
                mrgd_html = mrgd.to_html()
                context = {'reportings':reportings,'locations':locations,'filename':filename,'location':location,
                            'reporting':reporting,'filenames': filenames,'mrgd_html':mrgd_html}
            else:
                mrgd_html = qc_df
                context = {'reportings':reportings,'locations':locations,'filename':filename,'location':location,
                            'reporting':reporting,'filenames': filenames,'mrgd_html':mrgd_html, 'Alert': json.dumps(
                                {'type': 'info', 'title': 'Info', 'message': 'No Records'})}
            return render(request, 'pages/error_report.html', context)

    context = {'reportings':reportings,'locations':locations,
                'filenames': filenames}
    return render(request, 'pages/error_report.html', context)


@loginrequired
def repetitionsreport(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    if request.method == 'POST':
        key = request.POST.get('key')
        selectfor = request.POST.get('selectfor')

        filename = request.POST.get('filename', None)
        if key == 'GetItem':
            if selectfor == 'RawReport':
                datas = raw_data.objects.values(
                    'baseid__batch_name', 'baseid__batch_name', 'id_value', 'question', 'answer_one', 'answer_two')
                datas_df = pd.DataFrame(datas)
                sorted_df = datas_df.sort_values(
                    by=['question', 'id_value', 'answer_one', 'answer_two'])
                duplicates = sorted_df.groupby(
                    ['question', 'answer_one', 'answer_two']).filter(lambda x: len(x) > 1)
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + "Duplicate Files" + \
                    str(timezone.now().date())+'".csv"'
                duplicates.to_csv(path_or_buf=response,
                                  index=False, encoding='utf-8-sig')
                return response
            else:
                query = Q()
                if filename != 'All':
                    query = Q(qid__baseid__filename=filename)
                datas = Repetitions.objects.filter(query, is_status='completed').values(
                    'qid__baseid__batch_name', 'qid__id_value', 'qid__question', 'qid__answer_one', 'qid__answer_two', 'rept_commands', created_at=F('end_time__date'))
                return render(request, 'pages/repetition_report.html', {'filenames': filenames, 'datas': datas, 'filename': filename})
        else:
            return render(request, 'pages/repetition_report.html', {'filenames': filenames})
    else:
        return render(request, 'pages/repetition_report.html', {'filenames': filenames})


def get_records(v, link, tag_name, Scope):
    return [
        Scope,
        v['baseid_id__batch_name'],
        v['baseid_id__filename'],
        v['id_value'],
        v['asin'],
        v['product_url'],
        v['title'],
        v['evidence'],
        v['imagepath'],
        v['question'],
        v['answer_one'],
        v['answer_two'],

        v[f'{tag_name}_prod_id__que0'],
        v[f'{tag_name}_prod_id__que1'],
        v[f'{tag_name}_prod_id__que2'],
        v[f'{tag_name}_prod_id__que2_1'],
        v[f'{tag_name}_prod_id__is_present_both'],

        v[f'{tag_name}_prod_id__que4_ans1'],
        v[f'{tag_name}_prod_id__que4_ans11'],
        v[f'{tag_name}_prod_id__que5_ans1'],
        v[f'{tag_name}_prod_id__que6_ans1'],
        v[f'{tag_name}_prod_id__que7_ans1'],
        " | ".join([i['link'] for i in link if i['linkfor']
                    == 'q7_1' and i[f'{tag_name}production_id'] == v[f'{tag_name}_prod_id']]),
        v[f'{tag_name}_prod_id__que8_ans1'],
        v[f'{tag_name}_prod_id__que9_ans1'],
        v[f'{tag_name}_prod_id__que10_ans1'],
        v[f'{tag_name}_prod_id__que11_ans1'],

        v[f'{tag_name}_prod_id__que4_ans2'],
        v[f'{tag_name}_prod_id__que4_ans22'],
        v[f'{tag_name}_prod_id__que5_ans2'],
        v[f'{tag_name}_prod_id__que6_ans2'],
        v[f'{tag_name}_prod_id__que7_ans2'],
        " | ".join([i['link'] for i in link if i['linkfor']
                    == 'q7_2' and i[f'{tag_name}production_id'] == v[f'{tag_name}_prod_id']]),
        v[f'{tag_name}_prod_id__que8_ans2'],
        v[f'{tag_name}_prod_id__que9_ans2'],
        v[f'{tag_name}_prod_id__que10_ans2'],
        v[f'{tag_name}_prod_id__que11_ans2'],

        v[f'{tag_name}_prod_id__general_ques1'],
        v[f'{tag_name}_prod_id__general_ques2'],

        v[f'{tag_name}_prod_id__annotation_comment'],

        v[f'{tag_name}_emp_id__employeeID'],
        v[f'{tag_name}_emp_id__employeeName'],
        v[f'{tag_name}_emp_id__location'],
        v[f'{tag_name}_prod_id__start_time'],
        v[f'{tag_name}_prod_id__end_time'],
        v['timtakn'],
        v[f'{tag_name}_prod_id__end_time__date'],
        v[f'{tag_name}_emp__reporting__employeeID']
    ]


def get_recordswsome(v, link, tag_name, Scope):
    return [
        Scope,
        v['baseid_id__batch_name'],
        v['baseid_id__filename'],
        v['id_value'],
        v['asin'],
        v['product_url'],
        v['title'],
        v['evidence'],
        v['imagepath'],
        v['question'],
        v['answer_one'],
        v['answer_two'],

        v[f'{tag_name}_prod_id__que0'],
        v[f'{tag_name}_prod_id__que1'],
        v[f'{tag_name}_prod_id__que2'],
        v[f'{tag_name}_prod_id__que2_1'],
        v[f'{tag_name}_prod_id__is_present_both'],

        v[f'{tag_name}_prod_id__que4_ans1'],
        v[f'{tag_name}_prod_id__que4_ans11'],
        v[f'{tag_name}_prod_id__que5_ans1'],
        v[f'{tag_name}_prod_id__que6_ans1'],
        v[f'{tag_name}_prod_id__que7_ans1'],
        " | ".join([i['link'] for i in link if i['linkfor']
                    == 'q7_1' and i[f'{tag_name}production_id'] == v[f'{tag_name}_prod_id']]),
        v[f'{tag_name}_prod_id__que8_ans1'],
        v[f'{tag_name}_prod_id__que9_ans1'],
        v[f'{tag_name}_prod_id__que10_ans1'],
        v[f'{tag_name}_prod_id__que11_ans1'],

        v[f'{tag_name}_prod_id__que4_ans2'],
        v[f'{tag_name}_prod_id__que4_ans22'],
        v[f'{tag_name}_prod_id__que5_ans2'],
        v[f'{tag_name}_prod_id__que6_ans2'],
        v[f'{tag_name}_prod_id__que7_ans2'],
        " | ".join([i['link'] for i in link if i['linkfor']
                    == 'q7_2' and i[f'{tag_name}production_id'] == v[f'{tag_name}_prod_id']]),
        v[f'{tag_name}_prod_id__que8_ans2'],
        v[f'{tag_name}_prod_id__que9_ans2'],
        v[f'{tag_name}_prod_id__que10_ans2'],
        v[f'{tag_name}_prod_id__que11_ans2'],

        v[f'{tag_name}_prod_id__general_ques1'],
        v[f'{tag_name}_prod_id__general_ques2'],

        v[f'{tag_name}_prod_id__annotation_comment'],

        v[f'{tag_name}_emp_id__employeeID'],
        v[f'{tag_name}_emp_id__employeeName'],
        v[f'{tag_name}_emp_id__location'],
        v[f'{tag_name}_prod_id__start_time'],
        v[f'{tag_name}_prod_id__end_time'],
        v['timtakn'],
        v[f'{tag_name}_prod_id__end_time__date'],
        v[f'{tag_name}_emp__reporting__employeeID']
    ]

@loginrequired
def outputDownload(request):
    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')

    if request.method == 'POST':
        key = request.POST.get('key')

        filename = request.POST.get('filename')
        fromdate = request.POST.get('fromDate')
        todate = request.POST.get('toDate')
        reporttype = request.POST.get('reporttype')
        language = request.POST.get('language')
        # location = request.POST.get('location')

        query = Q()
        if language != 'All':
            query &= Q(baseid_id__language=language)
        if filename != 'All':
            query &= Q(baseid_id__filename=filename)

        try:
            if fromdate and todate:
                conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
                conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
                conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
                conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
            else:
                conditions1 = Q()
                conditions2 = Q()
                conditions3 = Q()
                conditions4 = Q()

            if key == 'Download':
                dL1raw = raw_data.objects.filter(conditions1 & query & Q(l1_status='completed')).annotate(timtakn=Sum(F('l1_prod_id__end_time') - F('l1_prod_id__start_time'))).values('id', 'l1_emp__reporting__employeeID', 'l1_prod_id__end_time__date', 'id_value', 'l1_prod_id', 'l1_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l1_prod_id__general_ques1', 'l1_prod_id__general_ques2', 'l1_prod_id__start_time', 'l1_prod_id__end_time',
                                                                                                                                                                                       'l1_emp_id__employeeName', 'l1_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l1_status', 'timtakn', 'l1_prod_id__que0', 'l1_prod_id__que1', 'l1_prod_id__que2', 'l1_prod_id__que2_1', 'l1_prod_id__annotation_comment', 'l1_prod_id__is_status', 'l1_prod_id__is_present_both', 'l1_prod_id__que4_ans1', 'l1_prod_id__que4_ans11', 'l1_prod_id__que5_ans1',
                                                                                                                                                                                       'l1_prod_id__que6_ans1', 'l1_prod_id__que7_ans1', 'l1_prod_id__que8_ans1', 'l1_prod_id__que9_ans1', 'l1_prod_id__que10_ans1', 'l1_prod_id__que11_ans1', 'l1_prod_id__que4_ans2', 'l1_prod_id__que4_ans22', 'l1_prod_id__que5_ans2', 'l1_prod_id__que6_ans2', 'l1_prod_id__que7_ans2',
                                                                                                                                                                                       'l1_prod_id__que8_ans2', 'l1_prod_id__que9_ans2', 'l1_prod_id__que10_ans2', 'l1_prod_id__que11_ans2').exclude(status__in=['hold', 'deleted'])
                l1prodid = dL1raw.values_list('l1_prod_id', flat=True)
                dL1link = l1_production_link.objects.filter(
                    production_id__in=l1prodid).values('linkfor', 'link', l1production_id=F('production_id'))

                dL2raw = raw_data.objects.filter(conditions2 & query & Q(l2_status='completed')).annotate(timtakn=Sum(F('l2_prod_id__end_time') - F('l2_prod_id__start_time'))).values('id', 'l2_emp__reporting__employeeID', 'l2_prod_id__end_time__date', 'id_value', 'l2_prod_id', 'l2_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l2_prod_id__general_ques1', 'l2_prod_id__general_ques2', 'l2_prod_id__start_time', 'l2_prod_id__end_time',
                                                                                                                                                                                       'l2_emp_id__employeeName', 'l2_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l2_status', 'timtakn', 'l2_prod_id__que0', 'l2_prod_id__que1', 'l2_prod_id__que2', 'l2_prod_id__que2_1', 'l2_prod_id__annotation_comment', 'l2_prod_id__is_status', 'l2_prod_id__is_present_both', 'l2_prod_id__que4_ans1', 'l2_prod_id__que4_ans11', 'l2_prod_id__que5_ans1',
                                                                                                                                                                                       'l2_prod_id__que6_ans1', 'l2_prod_id__que7_ans1', 'l2_prod_id__que8_ans1', 'l2_prod_id__que9_ans1', 'l2_prod_id__que10_ans1', 'l2_prod_id__que11_ans1', 'l2_prod_id__que4_ans2', 'l2_prod_id__que4_ans22', 'l2_prod_id__que5_ans2', 'l2_prod_id__que6_ans2', 'l2_prod_id__que7_ans2',
                                                                                                                                                                                       'l2_prod_id__que8_ans2', 'l2_prod_id__que9_ans2', 'l2_prod_id__que10_ans2', 'l2_prod_id__que11_ans2').exclude(status__in=['hold', 'deleted'])
                l2prodid = dL2raw.values_list('l2_prod_id', flat=True)
                dL2link = l2_production_link.objects.filter(
                    production_id__in=l2prodid).values('linkfor', 'link', l2production_id=F('production_id'))

                dL3raw = raw_data.objects.filter(conditions3 & query & Q(l3_status='completed')).annotate(timtakn=Sum(F('l3_prod_id__end_time') - F('l3_prod_id__start_time'))).values('id', 'l3_emp__reporting__employeeID', 'l3_prod_id__end_time__date', 'id_value', 'l3_prod_id', 'l3_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l3_prod_id__general_ques1', 'l3_prod_id__general_ques2', 'l3_prod_id__start_time', 'l3_prod_id__end_time',
                                                                                                                                                                                       'l3_emp_id__employeeName', 'l3_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l3_status', 'timtakn', 'l3_prod_id__que0', 'l3_prod_id__que1', 'l3_prod_id__que2', 'l3_prod_id__que2_1', 'l3_prod_id__annotation_comment', 'l3_prod_id__is_status', 'l3_prod_id__is_present_both', 'l3_prod_id__que4_ans1', 'l3_prod_id__que4_ans11', 'l3_prod_id__que5_ans1',
                                                                                                                                                                                       'l3_prod_id__que6_ans1', 'l3_prod_id__que7_ans1', 'l3_prod_id__que8_ans1', 'l3_prod_id__que9_ans1', 'l3_prod_id__que10_ans1', 'l3_prod_id__que11_ans1', 'l3_prod_id__que4_ans2', 'l3_prod_id__que4_ans22', 'l3_prod_id__que5_ans2', 'l3_prod_id__que6_ans2', 'l3_prod_id__que7_ans2',
                                                                                                                                                                                       'l3_prod_id__que8_ans2', 'l3_prod_id__que9_ans2', 'l3_prod_id__que10_ans2', 'l3_prod_id__que11_ans2').exclude(status__in=['hold', 'deleted'])
                l3prodid = dL3raw.values_list('l3_prod_id', flat=True)
                dL3link = QcQa_production_link.objects.filter(
                    l3production_id__in=l3prodid).values('l3production_id', 'linkfor', 'link')

                dL4raw = raw_data.objects.filter(conditions4 & query & Q(l4_status='completed')).annotate(timtakn=Sum(F('l4_prod_id__end_time') - F('l4_prod_id__start_time'))).values('id', 'l4_emp__reporting__employeeID', 'l4_prod_id__end_time__date', 'id_value', 'l4_prod_id', 'l4_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l4_prod_id__general_ques1', 'l4_prod_id__general_ques2', 'l4_prod_id__start_time', 'l4_prod_id__end_time',
                                                                                                                                                                                       'l4_emp_id__employeeName', 'l4_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l4_status', 'timtakn', 'l4_prod_id__que0', 'l4_prod_id__que1', 'l4_prod_id__que2', 'l4_prod_id__que2_1', 'l4_prod_id__annotation_comment', 'l4_prod_id__is_status', 'l4_prod_id__is_present_both', 'l4_prod_id__que4_ans1', 'l4_prod_id__que4_ans11', 'l4_prod_id__que5_ans1',
                                                                                                                                                                                       'l4_prod_id__que6_ans1', 'l4_prod_id__que7_ans1', 'l4_prod_id__que8_ans1', 'l4_prod_id__que9_ans1', 'l4_prod_id__que10_ans1', 'l4_prod_id__que11_ans1', 'l4_prod_id__que4_ans2', 'l4_prod_id__que4_ans22', 'l4_prod_id__que5_ans2', 'l4_prod_id__que6_ans2', 'l4_prod_id__que7_ans2',
                                                                                                                                                                                       'l4_prod_id__que8_ans2', 'l4_prod_id__que9_ans2', 'l4_prod_id__que10_ans2', 'l4_prod_id__que11_ans2').exclude(status__in=['hold', 'deleted'])
                l4prodid = dL4raw.values_list('l4_prod_id', flat=True)
                dL4link = QcQa_production_link.objects.filter(
                    l4production_id__in=l4prodid).values('l4production_id', 'linkfor', 'link')

                # WPUdL4raw = raw_data.objects.filter(conditions4wpu & query & Q(l4wpu_status='completed')).annotate(timtakn=Sum(F('l4wpu_prod_id__end_time') - F('l4wpu_prod_id__start_time'))).values('id', 'l4wpu_emp__reporting__employeeID', 'l4wpu_prod_id__end_time__date', 'id_value', 'l4wpu_prod_id', 'l4wpu_emp_id__employeeID', 'question', 'asin', 'product_url', 'title', 'evidence', 'imagepath', 'answer_one', 'answer_two', 'l4wpu_prod_id__general_ques1', 'l4wpu_prod_id__general_ques2', 'l4wpu_prod_id__start_time', 'l4wpu_prod_id__end_time',
                #                                                                                                                                                                                       'l4wpu_emp_id__employeeName', 'l4wpu_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l4wpu_status', 'timtakn', 'l4wpu_prod_id__que0', 'l4wpu_prod_id__que1', 'l4wpu_prod_id__que2', 'l4wpu_prod_id__que2_1', 'l4wpu_prod_id__annotation_comment', 'l4wpu_prod_id__is_status', 'l4wpu_prod_id__is_present_both', 'l4wpu_prod_id__que4_ans1', 'l4wpu_prod_id__que4_ans11', 'l4wpu_prod_id__que5_ans1',
                #                                                                                                                                                                                       'l4wpu_prod_id__que6_ans1', 'l4wpu_prod_id__que7_ans1', 'l4wpu_prod_id__que8_ans1', 'l4wpu_prod_id__que9_ans1', 'l4wpu_prod_id__que10_ans1', 'l4wpu_prod_id__que11_ans1', 'l4wpu_prod_id__que4_ans2', 'l4wpu_prod_id__que4_ans22', 'l4wpu_prod_id__que5_ans2', 'l4wpu_prod_id__que6_ans2', 'l4wpu_prod_id__que7_ans2',
                #                                                                                                                                                                                       'l4wpu_prod_id__que8_ans2', 'l4wpu_prod_id__que9_ans2', 'l4wpu_prod_id__que10_ans2', 'l4wpu_prod_id__que11_ans2').exclude(status__in=['hold', 'deleted'])
                # l4wpuprodid = WPUdL4raw.values_list('l4wpu_prod_id', flat=True)
                # dL4wpulink = l4wpu_production_link.objects.filter(
                #     production_id__in=l4wpuprodid).values('production_id', 'linkfor', 'link')

                response = HttpResponse(
                    content_type='text/csv;charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + \
                    reporttype+"|"+str(timezone.now().date())+'".csv"'
                writer = csv.writer(response)

                if reporttype in ['DA1', 'DA2', 'QC/QA', 'QC/QAwsome']:
                    writer.writerow(title)

                if reporttype == 'DA1':
                    for v in dL1raw:
                        records = get_records(v, dL1link, 'l1', reporttype)
                        writer.writerow(records)

                if reporttype == 'DA2':
                    for v in dL2raw:
                        records = get_records(v, dL2link, 'l2', reporttype)
                        writer.writerow(records)

                if reporttype == 'QC/QAwsome':

                    correction_report = qc_error_report.objects.filter(
                        master__status="Completed", error_status="Error"
                    ).select_related('master__qid')

                    scopes = {
                        'DA1': {'scope': 'l1', 'link': dL1link},
                        'DA2': {'scope': 'l2', 'link': dL2link}
                    }

                    for v in dL3raw:
                        master_qid_id = v['id']
                        report = correction_report.filter(master__qid_id=master_qid_id)
                        
                        if report.exists():
                            scope_report = None
                            for scope, info in scopes.items():
                                scope_rec = report.filter(master__error_scope=scope)
                                if scope_rec.exists():
                                    scope_report = scope_rec
                                    scope1 = info['scope']
                                    comnlink = info['link']
                                    break

                            if scope_report:
                                qc_qawsom = {
                                        'baseid_id__batch_name': F('master__qid__baseid_id__batch_name'),
                                        'baseid_id__filename': F('master__qid__baseid_id__filename'),
                                        'id_value': F('master__qid__id_value'),
                                        'asin': F('master__qid__asin'),
                                        'product_url': F('master__qid__product_url'),
                                        'title': F('master__qid__title'),
                                        'evidence': F('master__qid__evidence'),
                                        'imagepath': F('master__qid__imagepath'),
                                        'question': F('master__qid__question'),
                                        'answer_one': F('master__qid__answer_one'),
                                        'answer_two': F('master__qid__answer_two'),
                                        f'{scope1}_status': F(f'master__qid__{scope1}_status'),
                                        f'{scope1}_prod_id': F(f'master__qid__{scope1}_prod_id'),
                                        f'{scope1}_emp_id__employeeID': F(f'master__qid__{scope1}_emp_id__employeeID'),
                                        f'{scope1}_emp_id__employeeName': F(f'master__qid__{scope1}_emp_id__employeeName'),
                                        f'{scope1}_emp_id__location': F(f'master__qid__{scope1}_emp_id__location'),
                                        f'{scope1}_prod_id__start_time': F(f'master__qid__{scope1}_prod_id__start_time'),
                                        f'{scope1}_prod_id__end_time': F(f'master__qid__{scope1}_prod_id__end_time'),
                                        f'{scope1}_prod_id__end_time__date': F(f'master__qid__{scope1}_prod_id__end_time__date'),

                                        f'{scope1}_prod_id__que0': F(f'master__qid__{scope1}_prod_id__que0'),
                                        f'{scope1}_prod_id__que1': F(f'master__qid__{scope1}_prod_id__que1'),
                                        f'{scope1}_prod_id__que2': F(f'master__qid__{scope1}_prod_id__que2'),
                                        f'{scope1}_prod_id__que2_1': F(f'master__qid__{scope1}_prod_id__que2_1'),
                                        f'{scope1}_prod_id__is_present_both': F(f'master__qid__{scope1}_prod_id__is_present_both'),
                                        f'{scope1}_prod_id__que4_ans1': F(f'master__qid__{scope1}_prod_id__que4_ans1'),
                                        f'{scope1}_prod_id__que4_ans11': F(f'master__qid__{scope1}_prod_id__que4_ans11'),
                                        f'{scope1}_prod_id__que5_ans1': F(f'master__qid__{scope1}_prod_id__que5_ans1'),
                                        f'{scope1}_prod_id__que6_ans1': F(f'master__qid__{scope1}_prod_id__que6_ans1'),
                                        f'{scope1}_prod_id__que7_ans1': F(f'master__qid__{scope1}_prod_id__que7_ans1'),
                                        f'{scope1}_prod_id__que8_ans1': F(f'master__qid__{scope1}_prod_id__que8_ans1'),
                                        f'{scope1}_prod_id__que9_ans1': F(f'master__qid__{scope1}_prod_id__que9_ans1'),
                                        f'{scope1}_prod_id__que10_ans1': F(f'master__qid__{scope1}_prod_id__que10_ans1'),
                                        f'{scope1}_prod_id__que11_ans1': F(f'master__qid__{scope1}_prod_id__que11_ans1'),
                                        f'{scope1}_prod_id__que4_ans2': F(f'master__qid__{scope1}_prod_id__que4_ans2'),
                                        f'{scope1}_prod_id__que4_ans22': F(f'master__qid__{scope1}_prod_id__que4_ans22'),
                                        f'{scope1}_prod_id__que5_ans2': F(f'master__qid__{scope1}_prod_id__que5_ans2'),
                                        f'{scope1}_prod_id__que6_ans2': F(f'master__qid__{scope1}_prod_id__que6_ans2'),
                                        f'{scope1}_prod_id__que7_ans2': F(f'master__qid__{scope1}_prod_id__que7_ans2'),
                                        f'{scope1}_prod_id__que8_ans2': F(f'master__qid__{scope1}_prod_id__que8_ans2'),
                                        f'{scope1}_prod_id__que9_ans2': F(f'master__qid__{scope1}_prod_id__que9_ans2'),
                                        f'{scope1}_prod_id__que10_ans2': F(f'master__qid__{scope1}_prod_id__que10_ans2'),
                                        f'{scope1}_prod_id__que11_ans2': F(f'master__qid__{scope1}_prod_id__que11_ans2'),
                                        f'{scope1}_prod_id__general_ques1': F(f'master__qid__{scope1}_prod_id__general_ques1'),
                                        f'{scope1}_prod_id__general_ques2': F(f'master__qid__{scope1}_prod_id__general_ques2'),
                                        f'{scope1}_prod_id__annotation_comment': F(f'master__qid__{scope1}_prod_id__annotation_comment'),
                                        f'{scope1}_emp__reporting__employeeID': F(f'master__qid__{scope1}_emp__reporting__employeeID')
                                    }

                                comnq = scope_report.annotate(
                                    timtakn=Sum(F(f'master__qid__{scope1}_prod_id__end_time') - F(f'master__qid__{scope1}_prod_id__start_time'))
                                ).values('timtakn', f'{scope1}_prod_id', **qc_qawsom).first()

                                records = get_recordswsome(comnq, comnlink, scope1, 'QC')
                            else:
                                records = get_records(v, dL3link, 'l3', 'QC')
                        else:
                            records = get_records(v, dL3link, 'l3', 'QC')
                        writer.writerow(records)

                    if dL3raw.count() + dL4raw.count() == dL2raw.count():
                        for v in dL4raw:
                            records = get_records(v, dL4link, 'l4', 'QA')
                            writer.writerow(records)
                    else:
                        for v in dL4raw:
                            records = get_records(v, dL4link, 'l4', 'QA')
                            writer.writerow(records)
                        excluded_ids = Q(id_value__in=dL4raw.values_list('id_value', flat=True)) | Q(id_value__in=dL3raw.values_list('id_value', flat=True))
                        for v in dL1raw.filter(l1_l2_accuracy='pass').exclude(excluded_ids):
                            records = get_records(v, dL1link.filter(l1production_id = v['l1_prod_id']).all(), 'l1', 'QA')
                            writer.writerow(records)

                if reporttype == 'QC/QA':
                    for v in dL3raw:
                        records = get_records(v, dL3link, 'l3', 'QC')
                        writer.writerow(records)

                    if dL3raw.count() + dL4raw.count() == dL2raw.count():
                        for v in dL4raw:
                            records = get_records(v, dL4link, 'l4', 'QA')
                            writer.writerow(records)
                    else:
                        for v in dL4raw:
                            records = get_records(v, dL4link, 'l4', 'QA')
                            writer.writerow(records)
                        excluded_ids = Q(id_value__in=dL4raw.values_list('id_value', flat=True)) | Q(
                            id_value__in=dL3raw.values_list('id_value', flat=True))
                        for v in dL1raw.filter(l1_l2_accuracy='pass').exclude(excluded_ids):
                            records = get_records(v, dL1link.filter(
                                l1production_id=v['l1_prod_id']).all(), 'l1', 'QA')
                            writer.writerow(records)
                return response
            else:
                dL1raw = raw_data.objects.filter(
                    conditions1 & query & Q(l1_status='completed')).exists()
                dL2raw = raw_data.objects.filter(
                    conditions2 & query & Q(l2_status='completed')).exists()
                dL3raw = raw_data.objects.filter(
                    conditions3 & query & Q(l3_status='completed')).exists()
                dL4raw = raw_data.objects.filter(
                    conditions4 & query & Q(l4_status='completed')).exists()
                # WPUdL4raw = raw_data.objects.filter(
                #     conditions4wpu & query & Q(l4wpu_status='completed')).exists() #, 'WPUdL4raw': WPUdL4raw
        except Exception as er:
            print(er)
        return render(request, 'pages/outputDownload.html', {'langs': langs, 'filenames': filenames, 'dL1raw': dL1raw, 'dL2raw': dL2raw, 'dL3raw': dL3raw, 'dL4raw': dL4raw, 'fromdate': fromdate, 'toDate': todate, 'language': language, 'filename': filename})
    else:
        return render(request, 'pages/outputDownload.html', {'filenames': filenames, 'langs': langs})

@loginrequired
def ConsolidateOutput(request):
    filename = request.POST.get('filename')
    fromdate = request.POST.get('fromDate')
    todate = request.POST.get('toDate')
    language = request.POST.get('language')
    key = request.POST.get('key')

    if filename == 'All':
        query1 = Q()
    else:
        query1 = Q(baseid_id__filename=filename)

    if language == 'All':
        query = Q()
    else:
        query = Q(baseid_id__language=language)

    if fromdate and todate:
        conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
        conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
        conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
        conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
    else:
        conditions1 = Q()
        conditions2 = Q()
        conditions3 = Q()
        conditions4 = Q()
    try:
        status = Q()
        status &= Q(l1_status="completed")
        status &= Q(l2_status="completed")
        status |= Q(l3_status="completed")
        status |= Q(l1_l2_accuracy="pass")

        rawtable = raw_data.objects
        cons = rawtable.filter(conditions1 | conditions2 | conditions3 | conditions4 & status, query, query1).values(
            'id_value',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'question',
            'asin',
            'product_url',
            'imagepath',
            'evidence',
            'answer_one',
            'answer_two',
            *l1list if rawtable.filter(conditions1 & Q(l1_status='completed') & query & query1) else [],
            *l2list if rawtable.filter(conditions2 & Q(l2_status='completed') & query & query1) else [],
            *l3list if rawtable.filter(conditions3 & Q(l3_status='completed') & query & query1) else [],
            *l4list if rawtable.filter(conditions4 & Q(l1_l2_accuracy="pass") & query & query1) else []
        ).exclude(status__in=['hold', 'deleted'])

        cnstable = pd.DataFrame(cons)
        cnstable.fillna('')

        # l1genq1 = 'l1_prod_id__general_ques1'
        # l2genq1 = 'l2_prod_id__general_ques1'
        # l3genq1 = 'l3_prod_id__general_ques1'
        # l4genq1 = 'l4_prod_id__general_ques1'

        # stat = []
        # if l1genq1 in cnstable.columns:
        #     stat.append('l1_status')
        #     cnstable[l1genq1] = cnstable[l1genq1].apply(
        #         lambda x: x.strip("[]").strip("''").replace("', '", ", ") if pd.notna(x) else x)

        # if l2genq1 in cnstable.columns:
        #     stat.append('l2_status')
        #     cnstable[l2genq1] = cnstable[l2genq1].apply(
        #         lambda x: x.strip("[]").strip("''").replace("', '", ", ") if pd.notna(x) else x)

        # if l3genq1 in cnstable.columns:
        #     stat.append('l3_status')
        #     cnstable[l3genq1] = cnstable[l3genq1].apply(
        #         lambda x: x.strip("[]").strip("''").replace("', '", ", ") if pd.notna(x) else x)

        # if l4genq1 in cnstable.columns:
        #     stat.append('l4_status')
        #     cnstable[l4genq1] = cnstable[l4genq1].apply(
        #         lambda x: x.strip("[]").strip("''").replace("', '", ", ") if pd.notna(x) else x)

        l1link = pd.DataFrame(l1_production_link.objects.filter(production_id__in=cons.values_list('l1_prod_id', flat=True)).values(
            'link', 'linkfor', id_value=F('production_id__qid_id__id_value'), batch=F('production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l2link = pd.DataFrame(l2_production_link.objects.filter(production_id__in=cons.values_list('l2_prod_id', flat=True)).values(
            'link', 'linkfor', id_value=F('production_id__qid_id__id_value'), batch=F('production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l3link = pd.DataFrame(QcQa_production_link.objects.filter(l3production_id__in=cons.values_list(
            'l3_prod_id', flat=True), prodtype='QC').values('prodtype', 'link', 'linkfor', id_value=F('l3production_id__qid_id__id_value'), batch=F('l3production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l4link = pd.DataFrame(QcQa_production_link.objects.filter(l4production_id__in=cons.values_list(
            'l4_prod_id', flat=True), prodtype='QA').values('prodtype', 'link', 'linkfor', id_value=F('l4production_id__qid_id__id_value'), batch=F('l4production_id__qid_id__baseid_id__batch_name'))).fillna('')

        if not cnstable.empty:
            df_cleaned = cnstable.dropna(axis=1, how='all')
            df_cleaned['DA1-Total Time Taken'] = df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l1_prod_id__start_time', 'l1_prod_id__end_time']) else None
            df_cleaned['DA2-Total Time Taken'] = df_cleaned['l2_prod_id__end_time'] - df_cleaned['l2_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l2_prod_id__start_time', 'l2_prod_id__end_time']) else None
            df_cleaned['QC-Total Time Taken'] = df_cleaned['l3_prod_id__end_time'] - df_cleaned['l3_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l3_prod_id__start_time', 'l3_prod_id__end_time']) else None
            df_cleaned['QA-Total Time Taken'] = df_cleaned['l4_prod_id__end_time'] - df_cleaned['l4_prod_id__start_time'] if all(
                col in df_cleaned.columns for col in ['l4_prod_id__start_time', 'l4_prod_id__end_time']) else None
            # print(df_cleaned['l1_prod_id__start_time'],"==",  df_cleaned['l1_prod_id__end_time'],df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'])
            mrgd = df_cleaned

        links = []
        keys = []
        if not l1link.empty:
            l1link['prodtype'] = 'DA1'
            links.append(l1link)
            keys.append('l1')

        if not l2link.empty:
            l2link['prodtype'] = 'DA2'
            links.append(l2link)
            keys.append('l2')

        if not l3link.empty:
            l3link['prodtype'] = 'QC'
            links.append(l3link)
            keys.append('l3')

        if not l4link.empty:
            l4link['prodtype'] = 'QA'
            links.append(l4link)
            keys.append('l4')

        if links:
            merged_df = pd.concat(links, keys=keys)
            filtered_df = merged_df[merged_df['linkfor'].isin(
                ['q7_1', 'q7_2'])]

            vals = []
            filtered_df1 = merged_df['linkfor'].isin(['q7_1'])
            filtered_df2 = merged_df['linkfor'].isin(['q7_2'])
            if filtered_df1.any():
                vals.append('q7_1')
            if filtered_df2.any():
                vals.append('q7_2')

            linkstable = filtered_df.pivot_table(
                index=['id_value', 'prodtype', 'batch'], columns='linkfor', values='link', aggfunc=lambda x: ' | '.join(filter(None, x))).reset_index()

            pivot_df = linkstable.pivot(
                index=['id_value', 'batch'], columns='prodtype', values=vals).reset_index()
            pivot_df.columns = [f'{col[1]}_{col[0]}' if col[1]
                                != '' else col[0] for col in pivot_df.columns]

            dataout_df = pivot_df.rename(
                columns={'id_value': 'id_value', 'batch': 'baseid_id__batch_name'})

            dataout_df = dataout_df.where(pd.notna(dataout_df), None)

            mrgd = pd.merge(mrgd, dataout_df, on=[
                            'id_value', 'baseid_id__batch_name'], how='outer')
        if not cnstable.empty:
            columns_to_drop = [
                col for col in mrgd.columns if col.endswith(('_y', '_x', '_z'))]
            mrgd = mrgd.drop(columns=columns_to_drop)
            # mrgd = mrgd.drop(columns=stat)

            df_cleaned = mrgd.dropna(axis=1, how='all')
            mrgd = df_cleaned.drop_duplicates()

            mrgd.rename(columns=ColumnName, inplace=True)

            existing_columns = [col for col in order if col in mrgd.columns]
            mrgd = mrgd[existing_columns]

            if key == "withoutdata":
                mrgd = mrgd.drop(
                    columns=[col for col in without if col in mrgd.columns])
                lable = str(key)+'"OverallReport"'
            else:
                lable = '"OverallReport"'

            if not mrgd.empty:
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'

                mrgd.to_csv(path_or_buf=response,
                            index=False, encoding='utf-8-sig')

                return response
        else:
            return render(request, 'pages/outputDownload.html', {'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'No Records'})})
    except Exception as er:
        print(er)
        return render(request, 'pages/outputDownload.html', {'Alert': json.dumps({'type': 'error', 'title': 'Error', 'message': str(er)})})

@loginrequired
def target(request):
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    filenames = raw_data.objects.filter().values('baseid_id', filename=F('baseid__filename')).exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    EmpID = request.session.get('empId')

    qa_queue_view = QA_queue.objects.values('queue_date', 'queue_batch__batch_name', 'queue_batch__filename', 'queue_percentage', 'created_by__employeeID').annotate(
        created_at=TruncMinute('created_at')).exclude(queue_batch__filename__contains='Deleted')

    # Default values for variables
    scope = ""
    targetfor = ""
    file = ""
    date = ""
    queue = ""
    location = []

    if request.method == 'POST':
        scope = request.POST.get('scope')
        targetfor = request.POST.get('targetfor')

        if targetfor == 'Queue':
            file = request.POST.get('batch')
            date = request.POST.get('date')
            queue = request.POST.get('queuev')

            queueObj = QA_queue.objects

            if queueObj.filter(queue_batch_id=file, queue_date=date).exists():
                if date and targetfor and not queue:
                    try:
                        fordate = QA_queue.objects.filter(queue_batch_id=file, queue_date=date).values(
                            'queue_percentage')[0]
                        prcet = fordate['queue_percentage']
                    except:
                        prcet = 0
                    return JsonResponse({'status': 'Success', 'code': 200, 'fordate': prcet})

                queueObj.filter(queue_batch_id=file, queue_date=date).update(queue_batch_id=file, queue_date=date,
                                                                             queue_percentage=queue, created_by_id=EmpID)
            else:
                queueObj.create(queue_batch_id=file, queue_date=date,
                                queue_percentage=queue, created_by_id=EmpID)

            # Redirect to the same view after form submission
            return redirect('/api/v8/target/')

        else:
            scope = request.POST.get('scope')
            location = request.POST.get('location')
            date = request.POST.get('date')
            # print(scope, location, date)

            if 'All' in location:
                query = Q()
            else:
                query = Q(userprofile_id__location=location)

            if 'All' in scope:
                query1 = ~Q(role='Admin') & ~Q(role='Super Admin')
                query3 = Q()
            else:
                query1 = Q(role=scope)
                query3 = Q(targetfor=scope)

            tdatas = Roles.objects.filter(query, query1)
            targetusers = tdatas.values(
                'id',
                'userprofile_id__employeeName',
                'role',
                'userprofile_id__location',
                'userprofile_id__employeeName',
                empid=F('userprofile_id'),
            )

            existing_targetdata = targetsetting.objects.filter(query3, target_date=date,
                                                               targetempid_id__in=tdatas.values_list('userprofile_id')).values('target', 'targetfor', empid=F('targetempid_id'))

            mlist = []
            for d in targetusers:
                for d2 in existing_targetdata:
                    if d['empid'] == d2['empid'] and d['role'] == d2['targetfor']:
                        d.update(d2)
                mlist.append(d)

            datais = bool(targetusers)

            return render(request, 'pages/targetsetpage.html', {
                'datais': datais,
                'targetusers': mlist,
                'locations': locations,
                'filenames': filenames,
                'selected_scope': scope,
                'selected_targetfor': targetfor,
                'selected_file': file,
                'selected_date': date,
                'selected_queuev': queue,
                'selected_location': location
            })

    else:
        return render(request, 'pages/targetsetpage.html', {
            'datais': False,
            'qa_queue_view': qa_queue_view,
            'locations': locations,
            'filenames': filenames,
            'selected_scope': scope,
            'selected_targetfor': targetfor,
            'selected_file': file,
            'selected_date': date,
            'selected_queuev': queue,
            'selected_location': location,
        })

@loginrequired
def save_table_data(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        try:
            table_data = json.loads(request.POST.get('tableData'))
            target_date = request.POST.get('target_date')

            for row_data in table_data:
                employee_id = row_data['employeeID']
                targetfor = row_data['role']
                percentage_val = row_data['percentageval']

                if percentage_val != '':
                    if int(percentage_val) != 0 and int(percentage_val) != None:
                        targetsetting.objects.update_or_create(
                            targetempid_id=employee_id,
                            targetfor=targetfor,
                            target_date=target_date,
                            defaults={
                                'target': percentage_val,
                                'created_by_id': EmpID
                            }
                        )
            response_data = {'message': 'Data saved successfully'}
            return JsonResponse(response_data)
        except Exception as er:
            print(er)
            response_data = {'message': f'Error: {str(er)}'}
            return JsonResponse(response_data, status=500)


@loginrequired
def batchwisetracking(request):
    queue()
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    tls = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
        'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        location = request.POST.get('location')
        filename = request.POST.get('filename')
        reporting = request.POST.get('reporting')

        l1_count_filter = Q(l1_status='completed') & Q(
            l1_prod_id__end_time__date__range=(from_date, to_date))
        l2_count_filter = Q(l2_status='completed') & Q(
            l2_prod_id__end_time__date__range=(from_date, to_date))
        l3_count_filter = Q(l3_status='completed') & Q(
            l3_prod_id__end_time__date__range=(from_date, to_date))
        l4_count_filter = Q(l4_status='completed') & Q(
            l4_prod_id__end_time__date__range=(from_date, to_date))

        if location != 'All':
            l1_count_filter &= Q(l1_emp__location=location)
            l2_count_filter &= Q(l2_emp__location=location)
            l3_count_filter &= Q(l3_emp__location=location)
            l4_count_filter &= Q(l4_emp__location=location)

        reporting_filter = Q()
        if reporting != 'All':
            reporting_filter = Q(l1_emp__reporting=reporting) | Q(l2_emp__reporting=reporting) | \
                Q(l3_emp__reporting=reporting) | Q(l4_emp__reporting=reporting)

        common_filter = Q()
        if filename != 'All':
            common_filter = Q(baseid_id__filename=filename)

        final_filter = common_filter & reporting_filter
        prod_url_present = Q(product_url__isnull=False) & ~Q(product_url='')
        prod_url_absent = Q(product_url__isnull=True) | Q(product_url='')

        trackdata = raw_data.objects.filter(final_filter).values(
            'baseid_id__created_at__date',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'baseid_id__created_by_id__location'
        ).annotate(
            inputcount=Count('baseid_id__batch_name'),
            wtoutprodurl=Count('id_value', filter=prod_url_absent),
            da1_count=Count('l1_status', filter=l1_count_filter),
            da2_count=Count('l2_status', filter=l2_count_filter),
            qc_queue=Count('l1_l2_accuracy', filter=Q(l1_l2_accuracy='fail') & l1_count_filter & l2_count_filter),
            qc_count=Count('l3_status', filter=l3_count_filter),
            qa_queue=Count('l1_l2_accuracy', filter=Q(l1_l2_accuracy='pass') & l1_count_filter & l2_count_filter),
            qa_count=Count('l4_status', filter=l4_count_filter),
            
        ).exclude(status__in=['hold', 'deleted'])

        bq_tie_calc = raw_data.objects.filter(final_filter).values(
                        'baseid_id__created_at__date',
                        'baseid_id__batch_name',
                        'baseid_id__filename',
                        'baseid_id__created_by_id__location'
                        ).annotate(
                            inputcount=Count('baseid_id__batch_name'),

                            withprodurl=Count('id_value', filter=prod_url_present),
                            wtoutprodurl=Count('id_value', filter=prod_url_absent),
                            
                            # Product URL and "A and B are equally good" condition for DA1 to DA4
                            wpu_da1_both=Count('l1_prod__general_ques1', filter=Q(l1_prod__general_ques1='A and B are equally good') & prod_url_present & l1_count_filter),
                            wpu_da2_both=Count('l2_prod__general_ques1', filter=Q(l2_prod__general_ques1='A and B are equally good') & prod_url_present & l2_count_filter),
                            wpu_da3_both=Count('l3_prod__general_ques1', filter=Q(l3_prod__general_ques1='A and B are equally good') & prod_url_present & l3_count_filter),
                            wpu_da4_both=Count('l4_prod__general_ques1', filter=Q(l4_prod__general_ques1='A and B are equally good') & prod_url_present & l4_count_filter),
                            
                            wopu_da1_both=Count('l1_prod__general_ques1', filter=Q(l1_prod__general_ques1='A and B are equally good') & prod_url_absent & l1_count_filter),
                            wopu_da2_both=Count('l2_prod__general_ques1', filter=Q(l2_prod__general_ques1='A and B are equally good') & prod_url_absent & l2_count_filter),
                            wopu_da3_both=Count('l3_prod__general_ques1', filter=Q(l3_prod__general_ques1='A and B are equally good') & prod_url_absent & l3_count_filter),
                            wopu_da4_both=Count('l4_prod__general_ques1', filter=Q(l4_prod__general_ques1='A and B are equally good') & prod_url_absent & l4_count_filter),

                            qa_with_both = Count('l1_prod__general_ques1', filter=Q(l1_prod__general_ques1='A and B are equally good',l1_l2_accuracy='pass') & ~Q(l4_status='completed') & prod_url_present),
                            qa_without_both = Count('l1_prod__general_ques1', filter=Q(l1_prod__general_ques1='A and B are equally good',l1_l2_accuracy='pass') & ~Q(l4_status='completed') & prod_url_absent),
                            
                            # QC/QA ratio calculations
                            qcqa_with_produrl=ExpressionWrapper(
                                (Cast(F('wpu_da3_both'), FloatField()) + Cast(F('wpu_da4_both'), FloatField()) + Cast(F('qa_with_both'), FloatField())) / Cast(F('withprodurl'), FloatField()),
                                output_field=FloatField()
                            ),
                            qcqa_without_produrl=ExpressionWrapper(
                                (Cast(F('wopu_da3_both'), FloatField()) + Cast(F('wopu_da4_both'), FloatField()) + Cast(F('qa_without_both'), FloatField())) / Cast(F('wtoutprodurl'), FloatField()),
                                output_field=FloatField()
                            )
                        )
        return render(request, 'pages/batchwisetracking.html', {'reporting': reporting, 'tls': tls, 'trackdata': trackdata, 'bq_tie_calc':bq_tie_calc, 'locations': locations, 'filenames': filenames, 'from_date': from_date, 'to_date': to_date, 'location': location, 'filename': filename})
    else:
        return render(request, 'pages/batchwisetracking.html', {'tls': tls, 'locations': locations, 'filenames': filenames})


@loginrequired
def userwisetracking(request):
    queue()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    scopes = Roles.objects.filter(Q(role__isnull=False) & ~Q(role='')).values(
        'role').exclude(role__in=['Admin', 'Super Admin']).distinct()
    if request.method == 'POST':
        key = request.POST.get('key')
        date = request.POST.get('date')
        location = request.POST.get('location')
        scope = request.POST.get('scope')

        userid = Roles.objects.filter(role=scope).values_list(
            'userprofile_id', flat=True)
        qscopes = Q()
        if 'DA1' in userid:
            qscopes = Q(l1_emp_id__in=userid)
        elif 'DA2' in userid:
            qscopes = Q(l2_emp_id__in=userid)
        elif 'QC' in userid:
            qscopes = Q(l3_emp_id__in=userid)
        elif 'QA' in userid:
            qscopes = Q(l4_emp_id__in=userid)

        if scope == 'DA1':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l1_emp_id__location=location
                                                ).values(empid=F('l1_emp_id')).annotate(
                count=Count('l1_status', Q(l1_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'DA2':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l2_emp_id__location=location
                                                ).values(empid=F('l2_emp_id')).annotate(
                count=Count('l2_status', Q(l2_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QC':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l3_emp_id__location=location
                                                ).values(empid=F('l3_emp_id')).annotate(
                count=Count('l3_status', Q(l3_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QA':
            trackdata = raw_data.objects.filter(qscopes,
                                                baseid_id__created_at__date=date,
                                                l4_emp_id__location=location
                                                ).values(empid=F('l4_emp_id')).annotate(
                count=Count('l4_status', Q(l4_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])

        targetdata = targetsetting.objects.filter(targetempid_id__in=userid, targetempid__location=location, target_date__date=date).values(
            'targetempid_id__employeeID', 'target', 'targetempid__location', empid=F('targetempid_id'))

        df_trackdata = pd.DataFrame(trackdata)
        df_targetdata = pd.DataFrame(targetdata)
        datais = False
        if not df_targetdata.empty and not df_trackdata.empty:
            mrgd = pd.merge(df_trackdata, df_targetdata,
                            on='empid', how='right')
            if not mrgd.empty:
                mrgd.fillna(0, inplace=True)
                mrgd['Achieved %'] = mrgd.apply(lambda row: round(
                    (int(row['count']) / int(row['target'])) * 100, 2) if not pd.isna(row['count']) else 0, axis=1)
                mrgd['Completed Count'] = mrgd['count'].astype(int)
                mrgd.index = np.arange(1, len(mrgd) + 1)
                mrgd = mrgd.drop(columns=['empid'])
                mrgd = mrgd.rename(columns={'targetempid_id__employeeID': 'Employee Id',
                                   'targetempid__location': 'Location', 'target': 'Target Count'})
                # mrgd.reset_index(drop=True, inplace=True)
                ord = ['Employee Id', 'Location', 'Target Count',
                       'Completed Count', 'Achieved %']
                mrgd = mrgd[ord]
                if key == 'Download':
                    lable = 'UserwiseTracking_Report'
                    response = HttpResponse(
                        content_type='text/csv; charset=utf-8-sig')
                    response['Content-Disposition'] = 'attachment; filename="' + lable + \
                        str(timezone.now().date())+'".csv"'
                    mrgd.to_csv(path_or_buf=response,
                                index=False, encoding='utf-8-sig')

                    return response
                else:
                    mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-hover">').replace('<thead>',
                                                                                                                                       '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                    datais = True
                    return render(request, 'pages/userwisetracking.html', {'datais': datais, 'mrgd': mrgd, 'locations': locations, 'scopes': scopes, 'date': date, 'location': location, 'scope': scope})
        return render(request, 'pages/userwisetracking.html', {'datais': datais, 'locations': locations, 'scopes': scopes, 'date': date, 'location': location, 'scope': scope, 'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'Agents have No Target'})})
    else:
        return render(request, 'pages/userwisetracking.html', {'datais': False, 'locations': locations, 'scopes': scopes})


@loginrequired
def hourlytarget(request):
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    if request.method == 'POST':
        scope = request.POST.get('scope')
        location = request.POST.get('location')
        date = request.POST.get('date')
        key = request.POST.get('btnkey')

        role = Q()
        if not scope == 'All':
            role = Q(targetfor=scope)

        locprod = Q()
        loctarget = Q()
        if not location == 'All':
            locprod = Q(created_by__location=location)
            loctarget = Q(targetempid__location=location)

        prod_Date = Q(end_time__date=date)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        def getcount(filename):
            if filename:
                count = raw_data.objects.filter(
                    baseid__filename=filename).count()
                return count
            else:
                return 0

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(prod_Date, locprod).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                empname=F('created_by__employeeName')
            ).annotate(
                source_table=Value(str(table_name), output_field=CharField()),
                crtdhr=ExtractHour('end_time'),
                count=Count('created_by_id'),
                filename=F('qid__baseid__filename'),
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productionhourly = list(chain(*querysets))

        targetdata = targetsetting.objects.filter(role, loctarget, target_date__date=date).values(
            'target', 'targetempid__location', empid=F('targetempid_id__employeeID'), empname=F('targetempid__employeeName'))
        qsifttime = ShiftTime.objects.filter(created_at__date=date).annotate(
            shifttime=ExtractHour(Sum(F('endtime') - F('starttime')))
        ).values('shifttime', empid=F('userprofile__employeeID'))

        df_prodhoure = pd.DataFrame(productionhourly)
        df_targetdata = pd.DataFrame(targetdata)
        df_sifttime = pd.DataFrame(qsifttime)
        if not df_prodhoure.empty and not df_targetdata.empty:
            mrgd = pd.merge(df_prodhoure, df_targetdata, on=[
                            'empid', 'empname'], how='outer')
            mrgd = mrgd.pivot_table(index=['empid', 'empname', 'filename', 'targetempid__location', 'target'],
                                    columns='crtdhr',
                                    values='count',
                                    fill_value=0).reset_index()
            if not mrgd.empty:
                if not df_sifttime.empty:
                    droplist = ['houretarget', 'shifttime']
                    mrgd = pd.merge(mrgd, df_sifttime, on='empid',
                                    how='left').fillna(0)

                    mrgd['houretarget'] = mrgd.apply(lambda row: round(
                        int(row['target']) / 8, 2), axis=1).astype(int)

                    # mrgd['houretarget'] = mrgd.apply(lambda row: round((int(row['target']) * getcount(row['filename'])) / 100,2), axis=1)
                    # mrgd['houretarget'] = mrgd.apply(lambda row: round(int(row['houretarget']) / int(row['shifttime']) if int(row['shifttime']) != 0 else int(11),1), axis=1)
                else:
                    droplist = ['houretarget']
                    mrgd['houretarget'] = mrgd.apply(lambda row: round(
                        int(row['target']) / 8, 2), axis=1).astype(int)

                    # mrgd['houretarget'] = mrgd.apply(lambda row: round((int(row['target']) * getcount(row['filename'])) / 100,2), axis=1)
                    # mrgd['houretarget'] = mrgd.apply(lambda row: round(int(row['houretarget']) / int(11),1), axis=1)

                tablecolumn = ['empid', 'filename', 'empname',
                               'targetempid__location', 'target', 'Hourly Target']
                mrgd = mrgd.rename(columns=lambda x: str(
                    x) if x not in tablecolumn else x)
                mrgd = mrgd.fillna(0)
                mrgd.insert(mrgd.columns.get_loc('target') + 1,
                            'Hourly Target', mrgd['houretarget'])
                mrgd = mrgd.drop(columns=droplist)

                # mrgd = mrgd[tablecolumn]
                mrgd = mrgd.rename(columns=rnmhourlycolumn)
                mrgd.index = np.arange(1, len(mrgd) + 1)

                if key == 'Download':
                    lable = 'Hourly_Report'
                    response = HttpResponse(
                        content_type='text/csv; charset=utf-8-sig')
                    response['Content-Disposition'] = 'attachment; filename="' + lable + \
                        str(timezone.now().date())+'".csv"'
                    mrgd.to_csv(path_or_buf=response,
                                index=False, encoding='utf-8-sig')

                    return response
                else:
                    mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                    '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                    return render(request, 'pages/hourly_target.html', {'houretarget': mrgd, 'locations': locations,  'scope': scope, 'location': location, 'date': date, 'key': key})
        return render(request, 'pages/hourly_target.html', {'locations': locations, 'date': date, 'scope': scope, 'location': location, 'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'No records / Make sure that targets are set.'})})
    else:
        return render(request, 'pages/hourly_target.html', {'locations': locations})


@loginrequired
def resetuser(request):
    EmpID = request.session.get('empId')
    filenames = raw_data.objects.filter().values(
        'baseid_id', 'baseid__filename').exclude(status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    tls = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
        'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')
    if request.method == 'POST':
        keyval = request.POST.get('keyval')
        key = request.POST.get('key')
        if key == 'GetItem':
            batch_name = request.POST.get('batch_name')
            id_vals = request.POST.get('id_value')
            targetusers = raw_data.objects.filter(baseid_id=batch_name, id_value=id_vals).values(
                'id',
                'baseid__batch_name',
                'id_value',
                'asin',
                'l1_emp__employeeID',
                'l1_status',
                'l2_emp__employeeID',
                'l2_status',
                'l3_emp__employeeID',
                'l3_status',
                'l4_emp__employeeID',
                'l4_status'
            )
            return render(request, 'pages/filebaseduserchech.html', {'tls': tls, 'filenames': filenames, 'targetusers': targetusers, 'batch_name': batch_name})

        if key == "userassign":
            batch_name = request.POST.get('batch_name1')
            scope = request.POST.get('scope1')
            reporting = request.POST.get('reporting')
            status_data = request.POST.get('hold_unhold')
            assignuser_id = Roles.objects.filter(role=scope, userprofile__reporting_id=EmpID).values(
                'id', 'role', 'userprofile__employeeID', 'userprofile_id').order_by('userprofile__employeeID')

            reporting_query = Q()
            if reporting != 'All':
                if scope == "DA1":
                    reporting_query = Q(l1_emp__reporting_id=reporting)
                if scope == "DA2":
                    reporting_query = Q(l2_emp__reporting_id=reporting)
                if scope == "QC":
                    reporting_query = Q(l3_emp__reporting_id=reporting)
                if scope == "QA":
                    reporting_query = Q(l4_emp__reporting_id=reporting)

            if status_data == 'hold':
                if scope == "DA1":
                    query1 = Q(l1_status=status_data)
                if scope == "DA2":
                    query2 = Q(l2_status=status_data)
                if scope == "QC":
                    query3 = Q(l3_status=status_data)
                if scope == "QA":
                    query4 = Q(l4_status=status_data)
                exc = Q()

            elif status_data == 'picked':
                if scope == "DA1":
                    query1 = Q(l1_status='picked')
                if scope == "DA2":
                    query2 = Q(l2_status='picked')
                if scope == "QC":
                    query3 = Q(l3_status='picked')
                if scope == "QA":
                    query4 = Q(l4_status='picked')
                exc = Q()
            else:
                if scope == "DA1":
                    query1 = Q(l1_status='not_picked')
                    exc = Q(l1_status='completed') | Q(l1_status='picked')
                if scope == "DA2":
                    query2 = Q(l2_status='not_picked')
                    exc = Q(l2_status='completed') | Q(l2_status='picked')
                if scope == "QC":
                    query3 = Q(l3_status='not_moved') & Q(l1_status='completed') & Q(
                        l2_status='completed') & Q(l1_l2_accuracy='fail')
                    exc = Q(l3_status='completed') | Q(l3_status='picked')
                if scope == "QA":
                    query4 = Q(l4_status='not_picked') & Q(l1_status='completed') & Q(
                        l2_status='completed') & Q(l1_l2_accuracy='pass')
                    exc = Q(l4_status='completed') | Q(l4_status='picked')

            if scope == "DA1":
                asignuser = raw_data.objects.filter(query1 & reporting_query &
                                                    Q(baseid_id=batch_name)
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status',
                    location1=F('l1_loc'),
                    location2=F('l2_loc')
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "DA2":
                asignuser = raw_data.objects.filter(query2 & reporting_query &
                                                    Q(baseid_id=batch_name)
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status',
                    location1=F('l1_loc'),
                    location2=F('l2_loc')
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QC":
                asignuser = raw_data.objects.filter(query3 & reporting_query &
                                                    Q(baseid_id=batch_name)
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status',
                    location1=F('l1_loc'),
                    location2=F('l2_loc')
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QA":
                asignuser = raw_data.objects.filter(query4 & reporting_query &
                                                    Q(baseid_id=batch_name)
                                                    ).values(
                    'id',
                    'id_value',
                    'l1_emp__employeeID',
                    'l1_status',
                    'l2_emp__employeeID',
                    'l2_status',
                    'l3_emp__employeeID',
                    'l3_status',
                    'l4_emp__employeeID',
                    'l4_status',
                    'status',
                    location1=F('l1_loc'),
                    location2=F('l2_loc')
                ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            return render(request, 'pages/filebaseduserchech.html', {'tls': tls, 'assignuser_id': assignuser_id, 'batch_name1': batch_name, 'status_data': status_data, 'scope': scope, 'asignuser': asignuser, 'reporting': reporting, 'filenames': filenames})

        if keyval == 'assignuser':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigemployee = request.POST.get('assigningemployee_id')
            assigning_for = request.POST.get('assigning_for')
            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l1_emp_id=assigemployee, l1_status='picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l2_emp_id=assigemployee, l2_status='picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l3_emp_id=assigemployee, l3_status='picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l4_emp_id=assigemployee, l4_status='picked')
        if keyval == 'hold':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigning_for = request.POST.get('assigning_for')

            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l1_status='picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l2_status='picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l3_status='picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(
                        baseid_id=filename, id_value=id_value).update(l4_status='picked')
        if keyval == 'reset':
            id_values = request.POST.getlist('idval[]')
            filename = request.POST.get('filename')
            assigning_for = request.POST.get('assigning_for')

            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l1_status='not_picked', l1_loc=None, l1_emp=None)
                    # raw_data.objects.filter(baseid_id = filename, id_value=id_value).delete()
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l2_status='not_picked', l2_loc=None, l2_emp=None)
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l3_status='not_moved', l3_emp=None, l1_l2_accuracy=None)
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(baseid_id=filename, id_value=id_value).update(
                        l4_status='not_picked', l4_emp=None, l1_l2_accuracy=None)
        return JsonResponse({'status': 'success', 'code': 200})
    else:
        queue()
        return render(request, 'pages/filebaseduserchech.html', {'tls': tls, 'datais': False, 'filenames': filenames})


@loginrequired
def ut_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range=(fromdate, todate))
        if not 'All' == location:
            query &= Q(created_by__location=location)

        if not 'All' == filename:
            query &= Q(qid__baseid__filename=filename)

        if not 'All' == language:
            query &= Q(qid__baseid__language=language)

        querysets = []
        for table_name in ['l1_production', 'l2_production', 'l3_production', 'l4_production']:
            queryset = globals()[table_name].objects.filter(query).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                filename=F('qid__baseid__filename'),
                language=F('qid__baseid__language'),
                location=F('created_by__location'),
                empname=F('created_by__employeeName')
            ).annotate(
                productiontime=Sum(F('end_time') - F('start_time')),
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['Percentage %'] = round(
                df_production['productiontime'] / timedelta(hours=9) * 100, 2)
            df_production['productiontime'] = pd.to_timedelta(
                df_production['productiontime']).astype(str).str.split().str[-1].str[:8]
            df_production.rename(columns=utcolumns, inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename',
                     'Location', 'Language', 'Production Time', 'Percentage %']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                lable = 'UT_Report'
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'
                df_production.to_csv(path_or_buf=response,
                                     index=False, encoding='utf-8-sig')

                return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                                  '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'ut_report': df_production, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language})
        else:
            # df_production.loc['Total'] = df_production.iloc[:, 3:-1].sum()
            # df_production.loc['Total','Utilization %'] =
            return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language})
    else:
        return render(request, 'pages/ut_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames})


@loginrequired
def aht_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')
        scope = request.POST.get('scope')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range=(fromdate, todate))
        if not 'All' in location:
            query &= Q(created_by__location=location)

        if not 'All' in filename:
            query &= Q(qid__baseid__filename=filename)

        if not 'All' in language:
            query &= Q(qid__baseid__language=language)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(query).values(
                date=F('created_at__date'),
                empid=F('created_by__employeeID'),
                filename=F('qid__baseid__filename'),
                language=F('qid__baseid__language'),
                location=F('created_by__location'),
                empname=F('created_by__employeeName')
            ).annotate(
                productiontime=Sum(F('end_time') - F('start_time')),
                prodcount=Count('created_by__employeeID')
            ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['AHT'] = (df_production['productiontime'] / df_production['prodcount']).apply(lambda x: '{:02}:{:02}:{:.2f}'.format(
                # ().astype(str).str.split().str[-1]
                int(x.seconds // 3600), int((x.seconds % 3600) // 60), x.seconds % 60 + x.microseconds / 1e6))
            df_production['productiontime'] = pd.to_timedelta(
                df_production['productiontime']).astype(str).str.split().str[-1].str[:8]
            utcolumns.update({'prodcount': 'Production Count'})
            df_production.rename(columns=utcolumns, inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename',
                     'Location', 'Language', 'Production Time', 'Production Count', 'AHT']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                lable = 'AHT_Report'
                response = HttpResponse(
                    content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + lable + \
                    str(timezone.now().date())+'".csv"'
                df_production.to_csv(path_or_buf=response,
                                     index=False, encoding='utf-8-sig')
                return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                                  '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
                return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'aht_report': df_production, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language, 'scope': scope})
        else:
            return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames, 'fromdate': fromdate, 'todate': todate, 'filename': filename, 'location': location, 'language': language, 'scope': scope})
    else:
        return render(request, 'pages/aht_report.html', {'langs': langs, 'locations': locations, 'filenames': filenames})


@loginrequired
def ck_report(request):
    filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
        status__in=['hole', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    tls = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
        'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')

    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        baseID = request.POST.get('batch')
        location = request.POST.get('location')
        language = request.POST.get('language')
        reporting = request.POST.get('reporting')

        query = Q()
        if fromdate and todate:
            query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
        if 'All' != location:
            query &= Q(l1_loc=location)
            query &= Q(l2_loc=location)

        if 'All' != baseID:
            query &= Q(baseid_id=baseID)

        if 'All' != reporting:
            query &= Q(l1_emp__reporting_id=reporting)
            query &= Q(l2_emp__reporting_id=reporting)

        if 'All' != language:
            query &= Q(baseid__language=language)

        datas = raw_data.objects.filter(query, l1_status='completed', l2_status='completed').values(
            # ,'baseid__batch_name'
            'id_value', 'l1_prod_id__general_ques1', 'l2_prod_id__general_ques1').exclude(status__in=['hole', 'deleted'])
        df_datas = pd.DataFrame(datas)

        ############################ ACR #############################
        filtered_data = raw_data.objects.filter(
            query &
            (Q(l3_status='completed') | Q(l4_status='completed'))
        ).values('question', 'answer_one', 'answer_two').annotate(count=Count('id_value')).filter(count__gt=1)

        if filtered_data:
            matching_query = Q(
                Q(answer_one__in=[data['answer_one'] for data in filtered_data]) &
                Q(answer_two__in=[data['answer_two']
                  for data in filtered_data])
            ) | Q(
                Q(answer_one__in=[data['answer_two'] for data in filtered_data]) &
                Q(answer_two__in=[data['answer_one']
                  for data in filtered_data])
            )

            aggregated_data = filtered_data.filter(matching_query).values('question').annotate(
                acr_dup=Count('id_value'),
                acr_match=Sum(Case(When(l1_l2_accuracy='pass', then=1),
                              default=0, output_field=IntegerField())),
                acr_not_match=Sum(Case(
                    When(l1_l2_accuracy='fail', then=1), default=0, output_field=IntegerField())),
                is_tie=Sum(Case(
                    When(Q(l3_prod__general_ques1='A and B are equally good') | Q(
                        l4_prod__general_ques1='A and B are equally good'), then=1),
                    default=0,
                    output_field=IntegerField()
                ))
            )

            total_counts = aggregated_data.aggregate(
                total=Sum('acr_dup'),
                total_match=Sum('acr_match'),
                total_mismatch=Sum('acr_not_match'),
                total_tie=Sum('is_tie')
            )

            total_count = total_counts['total'] or 0
            match_count = total_counts['total_match'] or 0
            mismatch_count = total_counts['total_mismatch'] or 0
            tie_count = total_counts['total_tie'] or 0

            acr_with_tie = aggregated_data.filter(
                Q(l3_prod__general_ques1='A and B are equally good') | Q(
                    l4_prod__general_ques1='A and B are equally good')
            ).aggregate(
                total_match=Sum('acr_match'),
                total_mismatch=Sum('acr_not_match')
            )

            acr_with_tie_match = acr_with_tie['total_match'] or 0
            acr_with_tie_mismatch = acr_with_tie['total_mismatch'] or 0

            non_tie_count = total_count - tie_count
            acr_without_tie_match = match_count - acr_with_tie_match
            acr_without_tie_mismatch = mismatch_count - acr_with_tie_mismatch

            acr_percentage = (match_count / total_count) * \
                100 if total_count > 0 else 0
            acr_with_tie_percentage = (
                acr_with_tie_match / tie_count) * 100 if tie_count > 0 else 0
            acr_without_tie_percentage = (
                acr_without_tie_match / non_tie_count) * 100 if non_tie_count > 0 else 0

            result = {
                'Category': ['ACR', 'ACR With Tie', 'ACR Without Tie'],
                'Count': [total_count * 2, tie_count * 2, non_tie_count * 2],
                'Match': [match_count * 2, acr_with_tie_match * 2, acr_without_tie_match * 2],
                'Mismatch': [mismatch_count * 2, acr_with_tie_mismatch * 2, acr_without_tie_mismatch * 2],
                'ACR %': [f"{acr_percentage:.2f}%", f"{acr_with_tie_percentage:.2f}%", f"{acr_without_tie_percentage:.2f}%"]
            }
            acr_df = pd.DataFrame(result).to_html()

            acr_raw_datas = raw_data.objects.filter(query & (Q(l3_status='completed') | Q(l4_status='completed'))) \
                                            .values('id_value', 'question', 'answer_one', 'answer_two', *l1list, *l2list, *l3list, *l4list)
            raw_files = pd.DataFrame(acr_raw_datas)
            raw_files.rename(columns=ColumnName, inplace=True)
            existing_columns = [
                col for col in order if col in raw_files.columns]
            raw_files = raw_files[existing_columns]
            raw_files = raw_files.to_csv(index=False)
            encoded_csv = base64.b64encode(
                raw_files.encode('utf-8')).decode('utf-8')
        else:
            acr_df = []
            encoded_csv = []
        ################################# ACR End ##################################

        if not df_datas.empty:
            df_datas.replace('', pd.NA, inplace=True)

            df_datas = df_datas[df_datas['l1_prod_id__general_ques1'].isin(
                df_datas['l2_prod_id__general_ques1'])]
            df_datas = df_datas[df_datas['l2_prod_id__general_ques1'].isin(
                df_datas['l1_prod_id__general_ques1'])]

            # df_datas = df_datas.dropna(
            #     subset=['l1_prod_id__general_ques1', 'l2_prod_id__general_ques1'], how='any')

            # 'baseid__batch_name':'Batch Name',
            df_datas = df_datas.rename(
                columns={'l1_prod_id__general_ques1': 'DA1', 'l2_prod_id__general_ques1': 'DA2'})
            pivot_table = pd.pivot_table(df_datas, values='id_value', index=[
                                         'DA1'], columns='DA2', aggfunc='count', fill_value=0, margins=True, margins_name='Total')  # 'Batch Name',

            try:
                answer1 = pivot_table.loc['A is better than B',
                                          'A is better than B']
            except:
                answer1 = 0
            try:
                answer2 = pivot_table.loc['B is better than A',
                                          'B is better than A']
            except:
                answer2 = 0
            try:
                both = pivot_table.loc['A and B are equally good',
                                       'A and B are equally good']
            except:
                both = 0
            try:
                neither = pivot_table.loc['A and B are both unacceptable to present in front of a customer',
                                          'A and B are both unacceptable to present in front of a customer']
            except:
                neither = 0

            pivotsum = answer1 + answer2 + both + neither

            total = int(pivot_table.loc['Total', 'Total'])

            # Total Row Values
            rowtotal = np.array(pivot_table.loc['Total'].values.flatten())
            # Total Column Values
            coltotal = np.array(pivot_table['Total'].values)

            main_list = np.array(
                ['A is better than B', 'B is better than A', 'A and B are equally good', 'A and B are both unacceptable to present in front of a customer', 'Total'])

            onel_list = np.array(pivot_table.columns.values)  # Column Names

            onel_missing_values = np.setdiff1d(main_list, onel_list)
            onel_missing_indices = np.where(
                np.isin(main_list, onel_missing_values))[0]

            for index in onel_missing_indices:
                rowtotal = np.insert(rowtotal, index, 0)
            # print(rowtotal,"rowtotal")

            two_list = np.array(pivot_table.index.values)  # Row Values

            two_missing_values = np.setdiff1d(main_list, two_list)
            two_missing_indices = np.where(
                np.isin(main_list, two_missing_values))[0]

            for index in two_missing_indices:
                coltotal = np.insert(coltotal, index, 0)
            # print(coltotal,"coltotal")

            rowtotal = rowtotal[(rowtotal != total)]
            coltotal = coltotal[(coltotal != total)]

            try:
                npdot = np.dot(rowtotal, coltotal)
            except:
                npdot = 0

            sqtotal = total ** 2

            new_df = {}
            new_df['P0'] = round((pivotsum / total)*100, 2)
            new_df['Pe'] = round((npdot / sqtotal) * 100, 2)
            new_df['1- Pe'] = round((1 - (npdot / sqtotal)) * 100, 2)
            new_df['P0 - Pe'] = round(((new_df['P0'] -
                                      new_df['Pe']) / 100)*100, 2)
            new_df['k'] = round((new_df['P0 - Pe'] / new_df['1- Pe']) * 100, 2)

            ck_report = pivot_table.to_html()
            final_ck = new_df

            return render(request, 'pages/ck_report.html', {'raw_files': encoded_csv, 'acr_df': acr_df, 'reporting': reporting, 'tls': tls, 'langs': langs, 'locations': locations, 'filenames': filenames, 'ck_report': ck_report, 'final_ck': final_ck, 'baseID': baseID, 'fromdate': fromdate, 'todate': todate, 'location': location, 'language': language})
        return render(request, 'pages/ck_report.html', {'acr_df': acr_df, 'reporting': reporting, 'fromdate': fromdate, 'todate': todate, 'location': location, 'language': language, 'tls': tls, 'langs': langs, 'locations': locations, 'baseID': baseID, 'filenames': filenames, 'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'No Records'})})
    else:
        return render(request, 'pages/ck_report.html', {'tls': tls, 'langs': langs, 'locations': locations, 'filenames': filenames})


@loginrequired
def qualityreport(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
        status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    language_list = Languages.objects.filter(
        Q(language__isnull=False) & ~Q(language='')).values('language').distinct()

    if request.method == 'POST':
        try:
            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            filename = request.POST.get('filename')
            location = request.POST.get('location')
            scope = request.POST.get('scope')
            key = request.POST.get('key')
            language_sl = request.POST.get('language')
            options = request.POST.get('options')

            # print(fromdate,todate,filename,location,scope,key,language_sl,options)
            totalcount = Q()

            raw_data_query = Q(l1_status="completed",
                               l2_status="completed", l3_status="completed")

            if filename != "ALL":
                totalcount &= Q(baseid__filename=filename)
                raw_data_query &= Q(baseid__filename=filename)
            total_data_count = raw_data.objects.filter(totalcount).count()
            if location != "ALL":

                raw_data_query &= Q(Q(l1_loc=location) | Q(l2_loc=location))

            if language_sl != "ALL":

                raw_data_query &= Q(baseid__language=[language_sl])

            raw_data_query &= Q(
                l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(
                l3_prod__end_time__date__range=(fromdate, todate))

            qc_ount = raw_data.objects.filter(raw_data_query).count()

            # print("Total number of data after filtering : ",total_data_count, "qc_count : ", qc_ount)

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                             'baseid__batch_name',
                                                                             'l1_emp__employeeName',
                                                                             'l1_emp__employeeID',
                                                                             'l2_emp__employeeID',
                                                                             'l1_loc',
                                                                             'l2_emp__employeeName',
                                                                             'l2_loc',
                                                                             'id_value',
                                                                             'question',
                                                                             'asin',
                                                                             'title',
                                                                             'product_url',
                                                                             'imagepath',
                                                                             'evidence',
                                                                             'answer_one',
                                                                             'answer_two',
                                                                             'l1_status',
                                                                             'l2_status',
                                                                             'l4_status',
                                                                             'l3_status',
                                                                             'l1_l2_accuracy',
                                                                             "l1_prod__que0",
                                                                             "l1_prod__que1",
                                                                             "l1_prod__que2",
                                                                             "l1_prod__que2_1",
                                                                             "l1_prod__is_present_both",
                                                                             "l1_prod__que4_ans1",
                                                                             "l1_prod__que4_ans11",
                                                                             "l1_prod__que5_ans1",
                                                                             "l1_prod__que6_ans1",
                                                                             "l1_prod__que7_ans1",
                                                                             "l1_prod__que8_ans1",
                                                                             "l1_prod__que9_ans1",
                                                                             "l1_prod__que10_ans1",
                                                                             "l1_prod__que11_ans1",
                                                                             "l1_prod__que4_ans2",
                                                                             "l1_prod__que4_ans22",
                                                                             "l1_prod__que5_ans2",
                                                                             "l1_prod__que6_ans2",
                                                                             "l1_prod__que7_ans2",
                                                                             "l1_prod__que8_ans2",
                                                                             "l1_prod__que9_ans2",
                                                                             "l1_prod__que10_ans2",
                                                                             "l1_prod__que11_ans2",
                                                                             "l1_prod__general_ques1",
                                                                             "l1_prod__general_ques2",
                                                                             "l1_prod__annotation_comment",
                                                                             "l2_prod__que0",
                                                                             "l2_prod__que1",
                                                                             "l2_prod__que2",
                                                                             "l2_prod__que2_1",
                                                                             "l2_prod__is_present_both",
                                                                             "l2_prod__que4_ans1",
                                                                             "l2_prod__que4_ans11",
                                                                             "l2_prod__que5_ans1",
                                                                             "l2_prod__que6_ans1",
                                                                             "l2_prod__que7_ans1",
                                                                             "l2_prod__que8_ans1",
                                                                             "l2_prod__que9_ans1",
                                                                             "l2_prod__que10_ans1",
                                                                             "l2_prod__que11_ans1",
                                                                             "l2_prod__que4_ans2",
                                                                             "l2_prod__que4_ans22",
                                                                             "l2_prod__que5_ans2",
                                                                             "l2_prod__que6_ans2",
                                                                             "l2_prod__que7_ans2",
                                                                             "l2_prod__que8_ans2",
                                                                             "l2_prod__que9_ans2",
                                                                             "l2_prod__que10_ans2",
                                                                             "l2_prod__que11_ans2",
                                                                             "l2_prod__general_ques1",
                                                                             "l2_prod__general_ques2",
                                                                             "l2_prod__annotation_comment",
                                                                             "l3_prod__que0",
                                                                             "l3_prod__que1",
                                                                             "l3_prod__que2",
                                                                             "l3_prod__que2_1",
                                                                             "l3_prod__is_present_both",
                                                                             "l3_prod__que4_ans1",
                                                                             "l3_prod__que4_ans11",
                                                                             "l3_prod__que5_ans1",
                                                                             "l3_prod__que6_ans1",
                                                                             "l3_prod__que7_ans1",
                                                                             "l3_prod__que8_ans1",
                                                                             "l3_prod__que9_ans1",
                                                                             "l3_prod__que10_ans1",
                                                                             "l3_prod__que11_ans1",
                                                                             "l3_prod__que4_ans2",
                                                                             "l3_prod__que4_ans22",
                                                                             "l3_prod__que5_ans2",
                                                                             "l3_prod__que6_ans2",
                                                                             "l3_prod__que7_ans2",
                                                                             "l3_prod__que8_ans2",
                                                                             "l3_prod__que9_ans2",
                                                                             "l3_prod__que10_ans2",
                                                                             "l3_prod__que11_ans2",
                                                                             "l3_prod__general_ques1",
                                                                             "l3_prod__general_ques2",
                                                                             "l3_prod__annotation_comment")

            # print("Total number of data after filtering : ",total_data_count, "qc_count : ", qc_ount)
            # changed by(Prasanth)
            ##################### New Code #############################
            raw_data_values_df = pd.DataFrame(raw_data_values)

            if scope == 'DA1':
                result_df = userwisequalityreportDA1(raw_data_values_df)
            if scope == 'DA2':
                result_df = userwisequalityreportDA2(raw_data_values_df)
            if scope == 'ALL':
                fromfun1 = userwisequalityreportDA1(raw_data_values_df)
                fromfun2 = userwisequalityreportDA2(raw_data_values_df)
                result_df = pd.concat([fromfun1, fromfun2], ignore_index=True)
            ##########################################################################

            # result_df = pd.DataFrame()

            # for row in raw_data_values:

            #     if scope == 'DA1':
            #         print("Total number of data after filtering : ")
            #         fromfun = userwisequalityreportDA1(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun], ignore_index=True)

            #     elif scope == 'DA2':

            #         fromfun = userwisequalityreportDA2(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun], ignore_index=True)

            #     elif scope == 'ALL':

            #         fromfun1 = userwisequalityreportDA1(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun1], ignore_index=True)

            #         fromfun2 = userwisequalityreportDA2(row)

            #         result_df = pd.concat(
            #             [result_df, fromfun2], ignore_index=True)

            error_counts = []

            # Loop through columns 15 to 38 (inclusive)
            for i in range(15, 38):
                # Count the number of False values in the current column
                count = (result_df.iloc[:, i] == False).sum()
                # Append the count to the error_counts list
                error_counts.append(count)

            if key == 'Download':
                if options == 'USER':

                    csv_buffer = StringIO()
                    ucw_columns = [
                        "baseid__filename", "baseid__batch_name", "Employee_Name", "Employee_id", "Location", "id_value",
                        "question", "asin", "title", "product_url", "imagepath", "evidence", "answer_one",
                        "answer_two", "PRODUCTION", "Q1. Is the context link valid?", "Q2: Do you understand the query?",
                        "Q3: What is the query type?", "Q3.A: Select the entity?", "Q4: Are both answers present?",
                        "Q5: Is the answer A free of any sensitive content?", "Q6: Do you think that the answer A is relevant?",
                        "Q7: Do you think that the answer A is informative/helpful?", "Q8: Is the answer A factually correct?",
                        "Q9: Do you think the answer A is clear?", "Q10: Do you think the answer A is objective?",
                        "Q11: Do you think the answer A has an appropriate tone?", "Q12: Is the answer A from the perspective of Amazon’s virtual assistant?",
                        "Q5: Is the answer B free of any sensitive content?", "Q6: Do you think that the answer B is relevant?",
                        "Q7: Do you think that the answer B is informative/helpful?", "Q8: Is the answer B factually correct?",
                        "Q9: Do you think the answer B is clear?", "Q10: Do you think the answer B is objective?",
                        "Q11: Do you think the answer B has an appropriate tone?", "Q12: Is the answer B from the perspective of Amazon’s virtual assistant?",
                        "Q13: Which answer is better based on the quality criteria?", "Audited_count", "Total_error",
                        "Field_count", "Audited_count_wise_accuracy", "field_count_wise_accuracy"
                    ]

                    result_df = result_df[ucw_columns]
                    result_df.to_csv(csv_buffer, index=True, encoding='utf-8')

                    # Set up the response
                    response = HttpResponse(
                        csv_buffer.getvalue(), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'

                    return response

                elif options == 'FIELD':
                    rows = [
                        'Q1. Is the context link valid?',
                        'Q2: Do you understand the query?',
                        'Q3: What is the query type?',
                        'Q3.A: Select the entity?',
                        'Q4: Are both answers present?',
                        'Q5: Is the answer A free of any sensitive content?',
                        'Q6: Do you think that the answer A is relevant?',
                        'Q7: Do you think that the answer A is informative/helpful?',
                        'Q8: Is the answer A factually correct?',
                        'Q9: Do you think the answer A is clear?',
                        'Q10: Do you think the answer A is objective?',
                        'Q11: Do you think the answer A has an appropriate tone?',
                        'Q12: Is the answer A from the perspective of Amazon’s virtual assistant?',
                        'Q5: Is the answer B free of any sensitive content?',
                        'Q6: Do you think that the answer B is relevant?',
                        'Q7: Do you think that the answer B is informative/helpful?',
                        'Q8: Is the answer B factually correct?',
                        'Q9: Do you think the answer B is clear?',
                        'Q10: Do you think the answer B is objective?',
                        'Q11: Do you think the answer B has an appropriate tone?',
                        'Q12: Is the answer B from the perspective of Amazon’s virtual assistant?',
                        'Q13: Which answer is better based on the quality criteria?',
                        'Over All'
                    ]

                    new_df = pd.DataFrame(rows, columns=['PRODUCTION'])
                    new_df['Total_Input_count'] = total_data_count
                    new_df['processed_count'] = qc_ount
                    new_df['Total_error'] = result_df.iloc[:, 14:39].apply(
                        lambda col: (col == False).sum(), axis=1)
                    for index, count in enumerate(error_counts):
                        new_df.at[index, 'Total_error'] = count
                    new_df['Accuracy__on_total_input'] = round(
                        ((1 - (new_df['Total_error'] / new_df['Total_Input_count'])) * 100), 2)
                    new_df['Disagreement__on_total_input'] = round(
                        ((new_df['Total_error'] / new_df['Total_Input_count']))*100, 2)
                    new_df['Accuracy__on_processed_count'] = round(
                        ((1 - (new_df['Total_error'] / new_df['processed_count'])) * 100), 2)
                    new_df['Disagreement__on_processed_count'] = round(
                        ((new_df['Total_error'] / new_df['processed_count']))*100, 2)
                    total_input_count_sum = new_df['Total_Input_count'].iloc[:-1].sum()
                    processed_count_sum = new_df['processed_count'].iloc[:-1].sum()
                    Total_error_sum = new_df['Total_error'].iloc[:-1].sum()
                    # Accuracy__on_total_input_sum = new_df['Accuracy__on_total_input'].sum(
                    # )
                    # Disagreement__on_total_input_sum = new_df['Disagreement__on_total_input'].sum(
                    # )

                    new_df.iloc[-1, 1] = total_input_count_sum
                    new_df.iloc[-1, 2] = processed_count_sum
                    new_df.iloc[-1, 3] = Total_error_sum
                    new_df.iloc[-1, 4] = round((1-Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1, 5] = round((Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1,
                                6] = round((1-Total_error_sum/processed_count_sum)*100, 2)
                    new_df.iloc[-1,
                                7] = round((Total_error_sum/processed_count_sum)*100, 2)

                    new_df['Accuracy__on_total_input'] = new_df['Accuracy__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_total_input'] = new_df['Disagreement__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Accuracy__on_processed_count'] = new_df['Accuracy__on_processed_count'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_processed_count'] = new_df['Disagreement__on_processed_count'].map(
                        lambda x: f"{x}%")

                    csv_data = new_df.to_csv(index=True, encoding='utf-8')

                    response = HttpResponse(csv_data, content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                    return response

            else:

                if options == 'USER':

                    result_df['audit_count_ft'] = result_df.groupby(['PRODUCTION', 'Employee_id'])[
                        'Employee_Name'].transform('count')
                    result_df['total_error_ft'] = result_df.groupby(['PRODUCTION', 'Employee_id'])[
                        'Total_error'].transform('sum')

                    result_df = result_df.drop_duplicates(
                        subset=['PRODUCTION', 'Employee_id'], keep='first')

                    result_df['field_count_ft'] = result_df['audit_count_ft'] * 25

                    result_df['field_wise_accuracy_ft'] = round(
                        (1 - (result_df['total_error_ft'] / result_df['field_count_ft']))*100)

                    data_list = result_df.to_dict(orient='records')

                    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list, 'response_data_list': data_list})

                elif options == 'FIELD':
                    rows = [
                        'Q1. Is the context link valid?',
                        'Q2: Do you understand the query?',
                        'Q3: What is the query type?',
                        'Q3.A: Select the entity?',
                        'Q4: Are both answers present?',
                        'Q5: Is the answer A free of any sensitive content?',
                        'Q6: Do you think that the answer A is relevant?',
                        'Q7: Do you think that the answer A is informative/helpful?',
                        'Q8: Is the answer A factually correct?',
                        'Q9: Do you think the answer A is clear?',
                        'Q10: Do you think the answer A is objective?',
                        'Q11: Do you think the answer A has an appropriate tone?',
                        'Q12: Is the answer A from the perspective of Amazon’s virtual assistant?',
                        'Q5: Is the answer B free of any sensitive content?',
                        'Q6: Do you think that the answer B is relevant?',
                        'Q7: Do you think that the answer B is informative/helpful?',
                        'Q8: Is the answer B factually correct?',
                        'Q9: Do you think the answer B is clear?',
                        'Q10: Do you think the answer B is objective?',
                        'Q11: Do you think the answer B has an appropriate tone?',
                        'Q12: Is the answer B from the perspective of Amazon’s virtual assistant?',
                        'Q13: Which answer is better based on the quality criteria?',
                        'Over All'
                    ]

                    new_df = pd.DataFrame(rows, columns=['PRODUCTION'])
                    new_df['Total_Input_count'] = total_data_count
                    new_df['processed_count'] = qc_ount
                    new_df['Total_error'] = result_df.iloc[:, 14:39].apply(
                        lambda col: (col == False).sum(), axis=1)
                    for index, count in enumerate(error_counts):
                        new_df.at[index, 'Total_error'] = count
                    new_df['Accuracy__on_total_input'] = round(
                        ((1 - (new_df['Total_error'] / new_df['Total_Input_count'])) * 100), 2)
                    new_df['Disagreement__on_total_input'] = round(
                        ((new_df['Total_error'] / new_df['Total_Input_count']))*100, 2)
                    new_df['Accuracy__on_processed_count'] = round(
                        ((1 - (new_df['Total_error'] / new_df['processed_count'])) * 100), 2)
                    new_df['Disagreement__on_processed_count'] = round(
                        ((new_df['Total_error'] / new_df['processed_count']))*100, 2)
                    total_input_count_sum = new_df['Total_Input_count'].iloc[:-1].sum()
                    processed_count_sum = new_df['processed_count'].iloc[:-1].sum()
                    Total_error_sum = new_df['Total_error'].iloc[:-1].sum()
                    Accuracy__on_total_input_sum = new_df['Accuracy__on_total_input'].sum(
                    )
                    Disagreement__on_total_input_sum = new_df['Disagreement__on_total_input'].sum(
                    )

                    new_df.iloc[-1, 1] = total_input_count_sum
                    new_df.iloc[-1, 2] = processed_count_sum
                    new_df.iloc[-1, 3] = Total_error_sum
                    new_df.iloc[-1, 4] = round((1-Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1, 5] = round((Total_error_sum /
                                               total_input_count_sum)*100, 2)
                    new_df.iloc[-1,
                                6] = round((1-Total_error_sum/processed_count_sum)*100, 2)
                    new_df.iloc[-1,
                                7] = round((Total_error_sum/processed_count_sum)*100, 2)

                    new_df['Accuracy__on_total_input'] = new_df['Accuracy__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_total_input'] = new_df['Disagreement__on_total_input'].map(
                        lambda x: f"{x}%")
                    new_df['Accuracy__on_processed_count'] = new_df['Accuracy__on_processed_count'].map(
                        lambda x: f"{x}%")
                    new_df['Disagreement__on_processed_count'] = new_df['Disagreement__on_processed_count'].map(
                        lambda x: f"{x}%")

                    # print(new_df)

                    # new_df['Audited_count'] = result_df.apply(lambda row: row[:-2].eq(True).sum(), axis=1)

                    # new_df['Field_count'] = new_df['Audited_count'] * 25
                    # new_df['Audited_count_wise_accuracy'] = round((1 - (new_df['Total_error'] / new_df['Audited_count'])) * 100)
                    # new_df['field_count_wise_accuracy'] = round((1 - (new_df['Total_error'] / new_df['Field_count'])) * 100)
                    data_list = new_df.to_dict(orient='records')
                    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list, 'data_list2': data_list})
        except Exception as er:
            print('Quality report : ', er)
            return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list, 'Alert': json.dumps({'type': 'info', 'title': 'Info', 'message': 'No Records'})})
    else:
        return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames, 'language': language_list})


def userwisequalityreportDA1(userid):

    df_report = userid  # pd.DataFrame([userid])

    df_report['PRODUCTION'] = 'DA1'

    the_audit_count = 27

    if (df_report['l1_prod__que0'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que2_1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__is_present_both'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans11'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que5_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que7_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que9_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que10_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que11_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que4_ans22'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que5_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que6_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que7_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que8_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que9_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que10_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__que11_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__general_ques1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__general_ques2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l1_prod__annotation_comment'].empty):
        the_audit_count = the_audit_count-1

    df_report['Q1. Is the context link valid?'] = (
        df_report['l1_prod__que0'] == df_report['l3_prod__que0'])
    df_report['Q2: Do you understand the query?'] = (
        df_report['l1_prod__que1'] == df_report['l3_prod__que1'])
    df_report['Q3: What is the query type?'] = (
        df_report['l1_prod__que2'] == df_report['l3_prod__que2'])
    df_report['Q3.A: Select the entity?'] = (
        df_report['l1_prod__que2_1'] == df_report['l3_prod__que2_1'])
    df_report['Q4: Are both answers present?'] = (
        df_report['l1_prod__is_present_both'] == df_report['l3_prod__is_present_both'])
    df_report['Q5: Is the answer A free of any sensitive content?'] = (
        df_report['l1_prod__que4_ans1'] == df_report['l3_prod__que4_ans1'])
    df_report['Q6: Do you think that the answer A is relevant?'] = (
        df_report['l1_prod__que5_ans1'] == df_report['l3_prod__que5_ans1'])
    df_report['Q7: Do you think that the answer A is informative/helpful?'] = (
        df_report['l1_prod__que6_ans1'] == df_report['l3_prod__que6_ans1'])
    df_report['Q8: Is the answer A factually correct?'] = (
        df_report['l1_prod__que7_ans1'] == df_report['l3_prod__que7_ans1'])
    df_report['Q9: Do you think the answer A is clear?'] = (
        df_report['l1_prod__que8_ans1'] == df_report['l3_prod__que8_ans1'])
    df_report['Q10: Do you think the answer A is objective?'] = (
        df_report['l1_prod__que9_ans1'] == df_report['l3_prod__que9_ans1'])
    df_report['Q11: Do you think the answer A has an appropriate tone?'] = (
        df_report['l1_prod__que10_ans1'] == df_report['l3_prod__que10_ans1'])
    df_report['Q12: Is the answer A from the perspective of Amazon’s virtual assistant?'] = (
        df_report['l1_prod__que11_ans1'] == df_report['l3_prod__que11_ans1'])
    df_report['Q5: Is the answer B free of any sensitive content?'] = (
        df_report['l1_prod__que4_ans2'] == df_report['l3_prod__que4_ans2'])
    df_report['Q6: Do you think that the answer B is relevant?'] = (
        df_report['l1_prod__que5_ans2'] == df_report['l3_prod__que5_ans2'])
    df_report['Q7: Do you think that the answer B is informative/helpful?'] = (
        df_report['l1_prod__que6_ans2'] == df_report['l3_prod__que6_ans2'])
    df_report['Q8: Is the answer B factually correct?'] = (
        df_report['l1_prod__que7_ans2'] == df_report['l3_prod__que7_ans2'])
    df_report['Q9: Do you think the answer B is clear?'] = (
        df_report['l1_prod__que8_ans2'] == df_report['l3_prod__que8_ans2'])
    df_report['Q10: Do you think the answer B is objective?'] = (
        df_report['l1_prod__que9_ans2'] == df_report['l3_prod__que9_ans2'])
    df_report['Q11: Do you think the answer B has an appropriate tone?'] = (
        df_report['l1_prod__que10_ans2'] == df_report['l3_prod__que10_ans2'])
    df_report['Q12: Is the answer B from the perspective of Amazon’s virtual assistant?'] = (
        df_report['l1_prod__que11_ans2'] == df_report['l3_prod__que11_ans2'])
    df_report['Q13: Which answer is better based on the quality criteria?'] = (
        df_report['l1_prod__general_ques1'] == df_report['l3_prod__general_ques1'])

    columns_to_remove = [
        'l1_status',
        'l2_status',
        'l4_status',
        'l3_status',
        'l1_l2_accuracy',
        "l1_prod__que0",
        "l1_prod__que1",
        "l1_prod__que2",
        "l1_prod__que2_1",
        "l1_prod__is_present_both",
        "l1_prod__que4_ans1",
        "l1_prod__que4_ans11",
        "l1_prod__que5_ans1",
        "l1_prod__que6_ans1",
        "l1_prod__que7_ans1",
        "l1_prod__que8_ans1",
        "l1_prod__que9_ans1",
        "l1_prod__que10_ans1",
        "l1_prod__que11_ans1",
        "l1_prod__que4_ans2",
        "l1_prod__que4_ans22",
        "l1_prod__que5_ans2",
        "l1_prod__que6_ans2",
        "l1_prod__que7_ans2",
        "l1_prod__que8_ans2",
        "l1_prod__que9_ans2",
        "l1_prod__que10_ans2",
        "l1_prod__que11_ans2",
        "l1_prod__general_ques1",
        "l1_prod__general_ques2",
        "l1_prod__annotation_comment",
        "l2_prod__que0",
        "l2_prod__que1",
        "l2_prod__que2",
        "l2_prod__que2_1",
        "l2_prod__is_present_both",
        "l2_prod__que4_ans1",
        "l2_prod__que4_ans11",
        "l2_prod__que5_ans1",
        "l2_prod__que6_ans1",
        "l2_prod__que7_ans1",
        "l2_prod__que8_ans1",
        "l2_prod__que9_ans1",
        "l2_prod__que10_ans1",
        "l2_prod__que11_ans1",
        "l2_prod__que4_ans2",
        "l2_prod__que4_ans22",
        "l2_prod__que5_ans2",
        "l2_prod__que6_ans2",
        "l2_prod__que7_ans2",
        "l2_prod__que8_ans2",
        "l2_prod__que9_ans2",
        "l2_prod__que10_ans2",
        "l2_prod__que11_ans2",
        "l2_prod__general_ques1",
        "l2_prod__general_ques2",
        "l2_prod__annotation_comment",
        "l3_prod__que0",
        "l3_prod__que1",
        "l3_prod__que2",
        "l3_prod__que2_1",
        "l3_prod__is_present_both",
        "l3_prod__que4_ans1",
        "l3_prod__que4_ans11",
        "l3_prod__que5_ans1",
        "l3_prod__que6_ans1",
        "l3_prod__que7_ans1",
        "l3_prod__que8_ans1",
        "l3_prod__que9_ans1",
        "l3_prod__que10_ans1",
        "l3_prod__que11_ans1",
        "l3_prod__que4_ans2",
        "l3_prod__que4_ans22",
        "l3_prod__que5_ans2",
        "l3_prod__que6_ans2",
        "l3_prod__que7_ans2",
        "l3_prod__que8_ans2",
        "l3_prod__que9_ans2",
        "l3_prod__que10_ans2",
        "l3_prod__que11_ans2",
        "l3_prod__general_ques1",
        "l3_prod__general_ques2",
        "l3_prod__annotation_comment"
    ]

    df_report = df_report.drop(columns=columns_to_remove)

    new_column_names = {'l1_emp__employeeID': 'Employee_id',
                        'l1_emp__employeeName': 'Employee_Name', 'l1_loc': 'Location'}

    df_report.rename(columns=new_column_names, inplace=True)

    df_report['Audited_count'] = the_audit_count

    df_report['Total_error'] = df_report.apply(
        lambda row: row[:-2].eq(False).sum(), axis=1)

    df_report['Field_count'] = df_report['Audited_count']*25

    df_report['Audited_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Audited_count']))*100)

    df_report['field_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Field_count']))*100)

    return df_report


def userwisequalityreportDA2(userid):

    df_report = userid  # pd.DataFrame([userid])

    # comparing l2 == l3
    df_report['PRODUCTION'] = 'DA2'

    the_audit_count = 27

    if (df_report['l2_prod__que0'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que2_1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__is_present_both'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans11'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que5_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que7_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que9_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que10_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que11_ans1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que4_ans22'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que5_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que6_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que7_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que8_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que9_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que10_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__que11_ans2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__general_ques1'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__general_ques2'].empty):
        the_audit_count = the_audit_count-1

    if (df_report['l2_prod__annotation_comment'].empty):
        the_audit_count = the_audit_count-1

    df_report['Q1. Is the context link valid?'] = (
        df_report['l2_prod__que0'] == df_report['l3_prod__que0'])
    df_report['Q2: Do you understand the query?'] = (
        df_report['l2_prod__que1'] == df_report['l3_prod__que1'])
    df_report['Q3: What is the query type?'] = (
        df_report['l2_prod__que2'] == df_report['l3_prod__que2'])
    df_report['Q3.A: Select the entity?'] = (
        df_report['l2_prod__que2_1'] == df_report['l3_prod__que2_1'])
    df_report['Q4: Are both answers present?'] = (
        df_report['l2_prod__is_present_both'] == df_report['l3_prod__is_present_both'])
    df_report['Q5: Is the answer A free of any sensitive content?'] = (
        df_report['l2_prod__que4_ans1'] == df_report['l3_prod__que4_ans1'])
    df_report['Q6: Do you think that the answer A is relevant?'] = (
        df_report['l2_prod__que5_ans1'] == df_report['l3_prod__que5_ans1'])
    df_report['Q7: Do you think that the answer A is informative/helpful?'] = (
        df_report['l2_prod__que6_ans1'] == df_report['l3_prod__que6_ans1'])
    df_report['Q8: Is the answer A factually correct?'] = (
        df_report['l2_prod__que7_ans1'] == df_report['l3_prod__que7_ans1'])
    df_report['Q9: Do you think the answer A is clear?'] = (
        df_report['l2_prod__que8_ans1'] == df_report['l3_prod__que8_ans1'])
    df_report['Q10: Do you think the answer A is objective?'] = (
        df_report['l2_prod__que9_ans1'] == df_report['l3_prod__que9_ans1'])
    df_report['Q11: Do you think the answer A has an appropriate tone?'] = (
        df_report['l2_prod__que10_ans1'] == df_report['l3_prod__que10_ans1'])
    df_report['Q12: Is the answer A from the perspective of Amazon’s virtual assistant?'] = (
        df_report['l2_prod__que11_ans1'] == df_report['l3_prod__que11_ans1'])
    df_report['Q5: Is the answer B free of any sensitive content?'] = (
        df_report['l2_prod__que4_ans2'] == df_report['l3_prod__que4_ans2'])
    df_report['Q6: Do you think that the answer B is relevant?'] = (
        df_report['l2_prod__que5_ans2'] == df_report['l3_prod__que5_ans2'])
    df_report['Q7: Do you think that the answer B is informative/helpful?'] = (
        df_report['l2_prod__que6_ans2'] == df_report['l3_prod__que6_ans2'])
    df_report['Q8: Is the answer B factually correct?'] = (
        df_report['l2_prod__que7_ans2'] == df_report['l3_prod__que7_ans2'])
    df_report['Q9: Do you think the answer B is clear?'] = (
        df_report['l2_prod__que8_ans2'] == df_report['l3_prod__que8_ans2'])
    df_report['Q10: Do you think the answer B is objective?'] = (
        df_report['l2_prod__que9_ans2'] == df_report['l3_prod__que9_ans2'])
    df_report['Q11: Do you think the answer B has an appropriate tone?'] = (
        df_report['l2_prod__que10_ans2'] == df_report['l3_prod__que10_ans2'])
    df_report['Q12: Is the answer B from the perspective of Amazon’s virtual assistant?'] = (
        df_report['l2_prod__que11_ans2'] == df_report['l3_prod__que11_ans2'])
    df_report['Q13: Which answer is better based on the quality criteria?'] = (
        df_report['l2_prod__general_ques1'] == df_report['l3_prod__general_ques1'])

    columns_to_remove = [
        'l1_status',
        'l2_status',
        'l4_status',
        'l3_status',
        'l1_l2_accuracy',
        "l1_prod__que0",
        "l1_prod__que1",
        "l1_prod__que2",
        "l1_prod__que2_1",
        "l1_prod__is_present_both",
        "l1_prod__que4_ans1",
        "l1_prod__que4_ans11",
        "l1_prod__que5_ans1",
        "l1_prod__que6_ans1",
        "l1_prod__que7_ans1",
        "l1_prod__que8_ans1",
        "l1_prod__que9_ans1",
        "l1_prod__que10_ans1",
        "l1_prod__que11_ans1",
        "l1_prod__que4_ans2",
        "l1_prod__que4_ans22",
        "l1_prod__que5_ans2",
        "l1_prod__que6_ans2",
        "l1_prod__que7_ans2",
        "l1_prod__que8_ans2",
        "l1_prod__que9_ans2",
        "l1_prod__que10_ans2",
        "l1_prod__que11_ans2",
        "l1_prod__general_ques1",
        "l1_prod__general_ques2",
        "l1_prod__annotation_comment",
        "l2_prod__que0",
        "l2_prod__que1",
        "l2_prod__que2",
        "l2_prod__que2_1",
        "l2_prod__is_present_both",
        "l2_prod__que4_ans1",
        "l2_prod__que4_ans11",
        "l2_prod__que5_ans1",
        "l2_prod__que6_ans1",
        "l2_prod__que7_ans1",
        "l2_prod__que8_ans1",
        "l2_prod__que9_ans1",
        "l2_prod__que10_ans1",
        "l2_prod__que11_ans1",
        "l2_prod__que4_ans2",
        "l2_prod__que4_ans22",
        "l2_prod__que5_ans2",
        "l2_prod__que6_ans2",
        "l2_prod__que7_ans2",
        "l2_prod__que8_ans2",
        "l2_prod__que9_ans2",
        "l2_prod__que10_ans2",
        "l2_prod__que11_ans2",
        "l2_prod__general_ques1",
        "l2_prod__general_ques2",
        "l2_prod__annotation_comment",
        "l3_prod__que0",
        "l3_prod__que1",
        "l3_prod__que2",
        "l3_prod__que2_1",
        "l3_prod__is_present_both",
        "l3_prod__que4_ans1",
        "l3_prod__que4_ans11",
        "l3_prod__que5_ans1",
        "l3_prod__que6_ans1",
        "l3_prod__que7_ans1",
        "l3_prod__que8_ans1",
        "l3_prod__que9_ans1",
        "l3_prod__que10_ans1",
        "l3_prod__que11_ans1",
        "l3_prod__que4_ans2",
        "l3_prod__que4_ans22",
        "l3_prod__que5_ans2",
        "l3_prod__que6_ans2",
        "l3_prod__que7_ans2",
        "l3_prod__que8_ans2",
        "l3_prod__que9_ans2",
        "l3_prod__que10_ans2",
        "l3_prod__que11_ans2",
        "l3_prod__general_ques1",
        "l3_prod__general_ques2",
        "l3_prod__annotation_comment"
    ]

    df_report = df_report.drop(columns=columns_to_remove)

    new_column_names = {'l2_emp__employeeID': 'Employee_id',
                        'l2_emp__employeeName': 'Employee_Name', 'l2_loc': 'Location'}

    df_report.rename(columns=new_column_names, inplace=True)

    df_report['Audited_count'] = the_audit_count

    df_report['Total_error'] = df_report.apply(
        lambda row: row[:-2].eq(False).sum(), axis=1)

    df_report['Field_count'] = df_report['Audited_count']*25

    df_report['Audited_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Audited_count']))*100)

    df_report['field_count_wise_accuracy'] = round(
        (1 - (df_report['Total_error'] / df_report['Field_count']))*100)
    return df_report


def format_columns(col):
    if col.name != 'Questions':
        return col.astype(str) + '%'
    return col


@loginrequired
def iaa(request):
    batchname = basefile.objects.filter(Q(filename__isnull=False) & ~Q(
        filename='')).values('filename').order_by('-id').distinct()

    if request.method == 'POST':

        totaldata = pd.DataFrame()

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        batchname_filter = request.POST.get('batchname')
        key = request.POST.get('key')

        from datetime import datetime, timedelta

        fromdates = datetime.strptime(fromdate, '%Y-%m-%d')
        todates = datetime.strptime(todate, '%Y-%m-%d')

        date_difference = (todates - fromdates).days

        list_of_dates = [
            fromdates + timedelta(days=i) for i in range(date_difference + 1)]

        formatted_dates = [date.strftime('%Y-%m-%d')
                           for date in list_of_dates]

        question_list = [
            'Questions',
            'Q1. Is the context link valid? ',
            'Q2. Do you understand the query?',
            'Q3. What is the query type?',
            'Q3-A. select_the_entity',
            'Q4. are_both_answers_present',
            'Q5. is_the_answer_a_free_of_sensitive_content',
            # 'Q5-A. Sensitive Content Dimension',
            'Q6. is_the_answer_a_is_relevant',
            'Q7. do_you_think_that_answer_a_is_informative/helpful for the customers',
            'Q8. is_the_answer_a_is_factually_correct',
            'Q9. do_you_think_that_answer_a_is_clear',
            'Q10. do_you_think_that_answer_a_is_objective',
            'Q11. do_you_think_that_answer_a_has_appropriate_tone',
            'Q12. is_the_answer_a_from_amazons_virtual_assistant_perspective',
            'Q5. is_the_answer_b_free_of_sensitive_content',
            # 'Q5-A. Sensitive Content Dimension ',
            'Q6. is_the_answer_b_is_relevant',
            'Q7. do_you_think_that_answer_b_is_informative/helpful for the customers ',
            'Q8. is_the_answer_b_is_factually_correct ',
            'Q9. do_you_think_that_answer_b_is_clear',
            'Q10. do_you_think_that_answer_b_is_objective ',
            'Q11. do_you_think_that_answer_b_has_appropriate_tone ',
            'Q12. is_the_answer_b_from_amazons_virtual_assistant_perspective',
            'Q13. which_answer_is_better_based_on_the_quality_criteria '
        ]

        for formatted_date in formatted_dates:

            # iterating for date wise data
            dayvalues = iaa_date_wise(
                formatted_date, formatted_date, batchname_filter)

            if not dayvalues.empty:

                totaldata = pd.merge(
                    totaldata, dayvalues, left_index=True, right_index=True, how='right')

        raw_data_query = Q(l1_status="completed",
                           l2_status="completed", l3_status="completed")

        if batchname_filter != "ALL":

            raw_data_query &= Q(baseid__filename=batchname_filter)

        raw_data_query &= Q(
            l1_prod__end_time__date__range=(fromdate, todate))
        raw_data_query &= Q(
            l2_prod__end_time__date__range=(fromdate, todate))
        raw_data_query &= Q(
            l3_prod__end_time__date__range=(fromdate, todate))

        raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                         'baseid__batch_name',
                                                                         'l1_emp__employeeName',
                                                                         'l1_emp__employeeID',
                                                                         'l2_emp__employeeID',
                                                                         'l1_loc',
                                                                         'l2_emp__employeeName',
                                                                         'l2_loc',
                                                                         'id_value',
                                                                         'question',
                                                                         'asin',
                                                                         'title',
                                                                         'product_url',
                                                                         'imagepath',
                                                                         'evidence',
                                                                         'answer_one',
                                                                         'answer_two',
                                                                         'l1_status',
                                                                         'l2_status',
                                                                         'l4_status',
                                                                         'l3_status',
                                                                         'l1_l2_accuracy',
                                                                         "l1_prod__que0",
                                                                         "l1_prod__que1",
                                                                         "l1_prod__que2",
                                                                         "l1_prod__que2_1",
                                                                         "l1_prod__is_present_both",
                                                                         "l1_prod__que4_ans1",
                                                                         "l1_prod__que4_ans11",
                                                                         "l1_prod__que5_ans1",
                                                                         "l1_prod__que6_ans1",
                                                                         "l1_prod__que7_ans1",
                                                                         "l1_prod__que8_ans1",
                                                                         "l1_prod__que9_ans1",
                                                                         "l1_prod__que10_ans1",
                                                                         "l1_prod__que11_ans1",
                                                                         "l1_prod__que4_ans2",
                                                                         "l1_prod__que4_ans22",
                                                                         "l1_prod__que5_ans2",
                                                                         "l1_prod__que6_ans2",
                                                                         "l1_prod__que7_ans2",
                                                                         "l1_prod__que8_ans2",
                                                                         "l1_prod__que9_ans2",
                                                                         "l1_prod__que10_ans2",
                                                                         "l1_prod__que11_ans2",
                                                                         "l1_prod__general_ques1",
                                                                         "l1_prod__general_ques2",
                                                                         "l1_prod__annotation_comment",
                                                                         "l2_prod__que0",
                                                                         "l2_prod__que1",
                                                                         "l2_prod__que2",
                                                                         "l2_prod__que2_1",
                                                                         "l2_prod__is_present_both",
                                                                         "l2_prod__que4_ans1",
                                                                         "l2_prod__que4_ans11",
                                                                         "l2_prod__que5_ans1",
                                                                         "l2_prod__que6_ans1",
                                                                         "l2_prod__que7_ans1",
                                                                         "l2_prod__que8_ans1",
                                                                         "l2_prod__que9_ans1",
                                                                         "l2_prod__que10_ans1",
                                                                         "l2_prod__que11_ans1",
                                                                         "l2_prod__que4_ans2",
                                                                         "l2_prod__que4_ans22",
                                                                         "l2_prod__que5_ans2",
                                                                         "l2_prod__que6_ans2",
                                                                         "l2_prod__que7_ans2",
                                                                         "l2_prod__que8_ans2",
                                                                         "l2_prod__que9_ans2",
                                                                         "l2_prod__que10_ans2",
                                                                         "l2_prod__que11_ans2",
                                                                         "l2_prod__general_ques1",
                                                                         "l2_prod__general_ques2",
                                                                         "l2_prod__annotation_comment",
                                                                         "l3_prod__que0",
                                                                         "l3_prod__que1",
                                                                         "l3_prod__que2",
                                                                         "l3_prod__que2_1",
                                                                         "l3_prod__is_present_both",
                                                                         "l3_prod__que4_ans1",
                                                                         "l3_prod__que4_ans11",
                                                                         "l3_prod__que5_ans1",
                                                                         "l3_prod__que6_ans1",
                                                                         "l3_prod__que7_ans1",
                                                                         "l3_prod__que8_ans1",
                                                                         "l3_prod__que9_ans1",
                                                                         "l3_prod__que10_ans1",
                                                                         "l3_prod__que11_ans1",
                                                                         "l3_prod__que4_ans2",
                                                                         "l3_prod__que4_ans22",
                                                                         "l3_prod__que5_ans2",
                                                                         "l3_prod__que6_ans2",
                                                                         "l3_prod__que7_ans2",
                                                                         "l3_prod__que8_ans2",
                                                                         "l3_prod__que9_ans2",
                                                                         "l3_prod__que10_ans2",
                                                                         "l3_prod__que11_ans2",
                                                                         "l3_prod__general_ques1",
                                                                         "l3_prod__general_ques2",
                                                                         "l3_prod__annotation_comment")

        result_df = pd.DataFrame(raw_data_values)

        new_columns_list = []

        columns_to_compare = [
            ("l1_prod__que0",                 "l2_prod__que0",
             "l3_prod__que0"),
            ("l1_prod__que1",                 "l2_prod__que1",
             "l3_prod__que1"),
            ("l1_prod__que2",                 "l2_prod__que2",
             "l3_prod__que2"),
            ("l1_prod__que2_1",                 "l2_prod__que2_1",
             "l3_prod__que2_1"),
            ("l1_prod__is_present_both",
             "l2_prod__is_present_both",                "l3_prod__is_present_both"),
            ("l1_prod__que4_ans1",                 "l2_prod__que4_ans1",
             "l3_prod__que4_ans1"),
            # ("l1_prod__que4_ans11",                 "l2_prod__que4_ans11",                "l3_prod__que4_ans11"),
            ("l1_prod__que5_ans1",                 "l2_prod__que5_ans1",
             "l3_prod__que5_ans1"),
            ("l1_prod__que6_ans1",                 "l2_prod__que6_ans1",
             "l3_prod__que6_ans1"),
            ("l1_prod__que7_ans1",                 "l2_prod__que7_ans1",
             "l3_prod__que7_ans1"),
            ("l1_prod__que8_ans1",                 "l2_prod__que8_ans1",
             "l3_prod__que8_ans1"),
            ("l1_prod__que9_ans1",                 "l2_prod__que9_ans1",
             "l3_prod__que9_ans1"),
            ("l1_prod__que10_ans1",                 "l2_prod__que10_ans1",
             "l3_prod__que10_ans1"),
            ("l1_prod__que11_ans1",                 "l2_prod__que11_ans1",
             "l3_prod__que11_ans1"),
            ("l1_prod__que4_ans2",                 "l2_prod__que4_ans2",
             "l3_prod__que4_ans2"),
            ("l1_prod__que4_ans22",                 "l2_prod__que4_ans22",
             "l3_prod__que4_ans22"),
            # ("l1_prod__que5_ans2",                 "l2_prod__que5_ans2",                "l3_prod__que5_ans2"),
            ("l1_prod__que6_ans2",                 "l2_prod__que6_ans2",
             "l3_prod__que6_ans2"),
            ("l1_prod__que7_ans2",                 "l2_prod__que7_ans2",
             "l3_prod__que7_ans2"),
            ("l1_prod__que8_ans2",                 "l2_prod__que8_ans2",
             "l3_prod__que8_ans2"),
            ("l1_prod__que9_ans2",                 "l2_prod__que9_ans2",
             "l3_prod__que9_ans2"),
            ("l1_prod__que10_ans2",                 "l2_prod__que10_ans2",
             "l3_prod__que10_ans2"),
            ("l1_prod__que11_ans2",                 "l2_prod__que11_ans2",
             "l3_prod__que11_ans2"),
            ("l1_prod__general_ques1",
             "l2_prod__general_ques1",                "l3_prod__general_ques1")
        ]

        # Loop through each set of three columns and perform the comparison
        for i, (col1, col2, col3) in enumerate(columns_to_compare):
            result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
            result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
            result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
            new_column_col = f'new_column_{i}'
            new_columns_list.append(new_column_col)
            # Add the values
            result_df[f'new_column_{i}'] = (
                result_df[f'compare_{i}_l1_l2'].astype(int) +
                result_df[f'compare_{i}_l1_l3'].astype(int) +
                result_df[f'compare_{i}_l2_l3'].astype(int)
            )

        # Drop the intermediate comparison columns if needed
        result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                                   [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                                   [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

        result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(
            0).sum()
        result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(
            1).sum()
        result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(
            3).sum()

        result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + \
            result_df.loc['Total number of ones'] + \
            result_df.loc['Total number of threes']

        result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)] = (
            (result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

        percentage_df = pd.DataFrame(
            result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)]).transpose()

        columns_to_remove = [
            'l1_status',
            'l2_status',
            'l4_status',
            'l3_status',
            'l1_l2_accuracy',
            "l1_prod__que0",
            "l1_prod__que1",
            "l1_prod__que2",
            "l1_prod__que2_1",
            "l1_prod__is_present_both",
            "l1_prod__que4_ans1",
            "l1_prod__que4_ans11",
            "l1_prod__que5_ans1",
            "l1_prod__que6_ans1",
            "l1_prod__que7_ans1",
            "l1_prod__que8_ans1",
            "l1_prod__que9_ans1",
            "l1_prod__que10_ans1",
            "l1_prod__que11_ans1",
            "l1_prod__que4_ans2",
            "l1_prod__que4_ans22",
            "l1_prod__que5_ans2",
            "l1_prod__que6_ans2",
            "l1_prod__que7_ans2",
            "l1_prod__que8_ans2",
            "l1_prod__que9_ans2",
            "l1_prod__que10_ans2",
            "l1_prod__que11_ans2",
            "l1_prod__general_ques1",
            "l1_prod__general_ques2",
            "l1_prod__annotation_comment",
            "l2_prod__que0",
            "l2_prod__que1",
            "l2_prod__que2",
            "l2_prod__que2_1",
            "l2_prod__is_present_both",
            "l2_prod__que4_ans1",
            "l2_prod__que4_ans11",
            "l2_prod__que5_ans1",
            "l2_prod__que6_ans1",
            "l2_prod__que7_ans1",
            "l2_prod__que8_ans1",
            "l2_prod__que9_ans1",
            "l2_prod__que10_ans1",
            "l2_prod__que11_ans1",
            "l2_prod__que4_ans2",
            "l2_prod__que4_ans22",
            "l2_prod__que5_ans2",
            "l2_prod__que6_ans2",
            "l2_prod__que7_ans2",
            "l2_prod__que8_ans2",
            "l2_prod__que9_ans2",
            "l2_prod__que10_ans2",
            "l2_prod__que11_ans2",
            "l2_prod__general_ques1",
            "l2_prod__general_ques2",
            "l2_prod__annotation_comment",
            "l3_prod__que0",
            "l3_prod__que1",
            "l3_prod__que2",
            "l3_prod__que2_1",
            "l3_prod__is_present_both",
            "l3_prod__que4_ans1",
            "l3_prod__que4_ans11",
            "l3_prod__que5_ans1",
            "l3_prod__que6_ans1",
            "l3_prod__que7_ans1",
            "l3_prod__que8_ans1",
            "l3_prod__que9_ans1",
            "l3_prod__que10_ans1",
            "l3_prod__que11_ans1",
            "l3_prod__que4_ans2",
            "l3_prod__que4_ans22",
            "l3_prod__que5_ans2",
            "l3_prod__que6_ans2",
            "l3_prod__que7_ans2",
            "l3_prod__que8_ans2",
            "l3_prod__que9_ans2",
            "l3_prod__que10_ans2",
            "l3_prod__que11_ans2",
            "l3_prod__general_ques1",
            "l3_prod__general_ques2",
            "l3_prod__annotation_comment"
        ]

        percentage_df = percentage_df.drop(columns=columns_to_remove)

        percentage_df.reset_index(inplace=True)

        melted_percentage_df = pd.melt(percentage_df)
        # print(melted_percentage_df)
        totaldata = pd.merge(
            totaldata, melted_percentage_df.drop(index=range(1, 18))['value'], left_index=True, right_index=True, how='right')

        totaldata['questions'] = question_list[:len(totaldata)]

        totaldata.columns = totaldata.iloc[0]

        totaldata = totaldata[1:].reset_index(drop=True)

        totaldata.index = np.arange(1, len(totaldata) + 1)

        totaldata = totaldata[[
            'Questions'] + [col for col in totaldata.columns if col != 'Questions']]

        # Convert all decimal values to floats with 2 decimal places
        totaldata.iloc[:, 1:] = totaldata.iloc[:,
                                               1:].astype(float).round(2)

        # Assuming your DataFrame is named df
        num_columns = totaldata.shape[1]

        totaldata.loc['OVER ALL'] = None

        # print(f"The number of columns in the DataFrame is: {num_columns}")

        for i in range(1, num_columns):  # Loop from 1 to 10
            average_value = round(totaldata.iloc[:, i].mean(), 2)
            print(
                f"The average value of column {totaldata.columns[i]} is: {average_value}")
            totaldata.loc['OVER ALL', totaldata.columns[i]] = average_value

        totaldata = totaldata.apply(format_columns, axis=0)

        if key == 'Download':

            csv_data = totaldata.to_csv(index=True, encoding='utf-8')

            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
            return response

        else:
            # print(totaldata)
            tabledata = totaldata.to_html().replace('<table border="1" class="dataframe">', '<table id="dftable" class="table table-hover">').replace('<thead>',
                                                                                                                                                      '<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">', '<tr>').replace('<th></th>', '<th>S.No</th>')
            return render(request, 'pages/iaa.html', {'batchname': batchname, 'tabledata': tabledata})

    return render(request, 'pages/iaa.html', {'batchname': batchname})


def iaa_date_wise(fromdate, todate, batchname_filter):
    raw_data_query = Q(l1_status="completed",
                       l2_status="completed", l3_status="completed")

    if batchname_filter != "ALL":

        raw_data_query &= Q(baseid__filename=batchname_filter)

    raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
    raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
    raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))

    raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                                                                     'baseid__batch_name',
                                                                     'l1_emp__employeeName',
                                                                     'l1_emp__employeeID',
                                                                     'l2_emp__employeeID',
                                                                     'l1_loc',
                                                                     'l2_emp__employeeName',
                                                                     'l2_loc',
                                                                     'id_value',
                                                                     'question',
                                                                     'asin',
                                                                     'title',
                                                                     'product_url',
                                                                     'imagepath',
                                                                     'evidence',
                                                                     'answer_one',
                                                                     'answer_two',
                                                                     'l1_status',
                                                                     'l2_status',
                                                                     'l4_status',
                                                                     'l3_status',
                                                                     'l1_l2_accuracy',
                                                                     "l1_prod__que0",
                                                                     "l1_prod__que1",
                                                                     "l1_prod__que2",
                                                                     "l1_prod__que2_1",
                                                                     "l1_prod__is_present_both",
                                                                     "l1_prod__que4_ans1",
                                                                     "l1_prod__que4_ans11",
                                                                     "l1_prod__que5_ans1",
                                                                     "l1_prod__que6_ans1",
                                                                     "l1_prod__que7_ans1",
                                                                     "l1_prod__que8_ans1",
                                                                     "l1_prod__que9_ans1",
                                                                     "l1_prod__que10_ans1",
                                                                     "l1_prod__que11_ans1",
                                                                     "l1_prod__que4_ans2",
                                                                     "l1_prod__que4_ans22",
                                                                     "l1_prod__que5_ans2",
                                                                     "l1_prod__que6_ans2",
                                                                     "l1_prod__que7_ans2",
                                                                     "l1_prod__que8_ans2",
                                                                     "l1_prod__que9_ans2",
                                                                     "l1_prod__que10_ans2",
                                                                     "l1_prod__que11_ans2",
                                                                     "l1_prod__general_ques1",
                                                                     "l1_prod__general_ques2",
                                                                     "l1_prod__annotation_comment",
                                                                     "l2_prod__que0",
                                                                     "l2_prod__que1",
                                                                     "l2_prod__que2",
                                                                     "l2_prod__que2_1",
                                                                     "l2_prod__is_present_both",
                                                                     "l2_prod__que4_ans1",
                                                                     "l2_prod__que4_ans11",
                                                                     "l2_prod__que5_ans1",
                                                                     "l2_prod__que6_ans1",
                                                                     "l2_prod__que7_ans1",
                                                                     "l2_prod__que8_ans1",
                                                                     "l2_prod__que9_ans1",
                                                                     "l2_prod__que10_ans1",
                                                                     "l2_prod__que11_ans1",
                                                                     "l2_prod__que4_ans2",
                                                                     "l2_prod__que4_ans22",
                                                                     "l2_prod__que5_ans2",
                                                                     "l2_prod__que6_ans2",
                                                                     "l2_prod__que7_ans2",
                                                                     "l2_prod__que8_ans2",
                                                                     "l2_prod__que9_ans2",
                                                                     "l2_prod__que10_ans2",
                                                                     "l2_prod__que11_ans2",
                                                                     "l2_prod__general_ques1",
                                                                     "l2_prod__general_ques2",
                                                                     "l2_prod__annotation_comment",
                                                                     "l3_prod__que0",
                                                                     "l3_prod__que1",
                                                                     "l3_prod__que2",
                                                                     "l3_prod__que2_1",
                                                                     "l3_prod__is_present_both",
                                                                     "l3_prod__que4_ans1",
                                                                     "l3_prod__que4_ans11",
                                                                     "l3_prod__que5_ans1",
                                                                     "l3_prod__que6_ans1",
                                                                     "l3_prod__que7_ans1",
                                                                     "l3_prod__que8_ans1",
                                                                     "l3_prod__que9_ans1",
                                                                     "l3_prod__que10_ans1",
                                                                     "l3_prod__que11_ans1",
                                                                     "l3_prod__que4_ans2",
                                                                     "l3_prod__que4_ans22",
                                                                     "l3_prod__que5_ans2",
                                                                     "l3_prod__que6_ans2",
                                                                     "l3_prod__que7_ans2",
                                                                     "l3_prod__que8_ans2",
                                                                     "l3_prod__que9_ans2",
                                                                     "l3_prod__que10_ans2",
                                                                     "l3_prod__que11_ans2",
                                                                     "l3_prod__general_ques1",
                                                                     "l3_prod__general_ques2",
                                                                     "l3_prod__annotation_comment")

    result_df = pd.DataFrame(raw_data_values)

    if result_df.empty:

        return result_df

    new_columns_list = []

    # List of columns to compare
    columns_to_compare = [
        ("l1_prod__que0",                 "l2_prod__que0",                "l3_prod__que0"),
        ("l1_prod__que1",                 "l2_prod__que1",                "l3_prod__que1"),
        ("l1_prod__que2",                 "l2_prod__que2",                "l3_prod__que2"),
        ("l1_prod__que2_1",                 "l2_prod__que2_1",
         "l3_prod__que2_1"),
        ("l1_prod__is_present_both",
         "l2_prod__is_present_both",                "l3_prod__is_present_both"),
        ("l1_prod__que4_ans1",                 "l2_prod__que4_ans1",
         "l3_prod__que4_ans1"),
        # ("l1_prod__que4_ans11",                 "l2_prod__que4_ans11",                "l3_prod__que4_ans11"),
        ("l1_prod__que5_ans1",                 "l2_prod__que5_ans1",
         "l3_prod__que5_ans1"),
        ("l1_prod__que6_ans1",                 "l2_prod__que6_ans1",
         "l3_prod__que6_ans1"),
        ("l1_prod__que7_ans1",                 "l2_prod__que7_ans1",
         "l3_prod__que7_ans1"),
        ("l1_prod__que8_ans1",                 "l2_prod__que8_ans1",
         "l3_prod__que8_ans1"),
        ("l1_prod__que9_ans1",                 "l2_prod__que9_ans1",
         "l3_prod__que9_ans1"),
        ("l1_prod__que10_ans1",                 "l2_prod__que10_ans1",
         "l3_prod__que10_ans1"),
        ("l1_prod__que11_ans1",                 "l2_prod__que11_ans1",
         "l3_prod__que11_ans1"),
        ("l1_prod__que4_ans2",                 "l2_prod__que4_ans2",
         "l3_prod__que4_ans2"),
        ("l1_prod__que4_ans22",                 "l2_prod__que4_ans22",
         "l3_prod__que4_ans22"),
        # ("l1_prod__que5_ans2",                 "l2_prod__que5_ans2",                "l3_prod__que5_ans2"),
        ("l1_prod__que6_ans2",                 "l2_prod__que6_ans2",
         "l3_prod__que6_ans2"),
        ("l1_prod__que7_ans2",                 "l2_prod__que7_ans2",
         "l3_prod__que7_ans2"),
        ("l1_prod__que8_ans2",                 "l2_prod__que8_ans2",
         "l3_prod__que8_ans2"),
        ("l1_prod__que9_ans2",                 "l2_prod__que9_ans2",
         "l3_prod__que9_ans2"),
        ("l1_prod__que10_ans2",                 "l2_prod__que10_ans2",
         "l3_prod__que10_ans2"),
        ("l1_prod__que11_ans2",                 "l2_prod__que11_ans2",
         "l3_prod__que11_ans2"),
        ("l1_prod__general_ques1",
         "l2_prod__general_ques1",                "l3_prod__general_ques1")
    ]

    # Loop through each set of three columns and perform the comparison
    for i, (col1, col2, col3) in enumerate(columns_to_compare):
        result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
        result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
        result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
        new_column_col = f'new_column_{i}'
        new_columns_list.append(new_column_col)
        # Add the values
        result_df[f'new_column_{i}'] = (
            result_df[f'compare_{i}_l1_l2'].astype(int) +
            result_df[f'compare_{i}_l1_l3'].astype(int) +
            result_df[f'compare_{i}_l2_l3'].astype(int)
        )

    # Drop the intermediate comparison columns if needed
    result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                               [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                               [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

    result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(
        0).sum()
    result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(
        1).sum()
    result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(
        3).sum()

    result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + \
        result_df.loc['Total number of ones'] + \
        result_df.loc['Total number of threes']

    result_df.loc['percentage for '+str(fromdate)] = ((result_df.loc['Total number of ones'] +
                                                       result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

    percentage_df = pd.DataFrame(
        result_df.loc['percentage for '+str(fromdate)]).transpose()

    columns_to_remove = [
        'l1_status',
        'l2_status',
        'l4_status',
        'l3_status',
        'l1_l2_accuracy',
        "l1_prod__que0",
        "l1_prod__que1",
        "l1_prod__que2",
        "l1_prod__que2_1",
        "l1_prod__is_present_both",
        "l1_prod__que4_ans1",
        "l1_prod__que4_ans11",
        "l1_prod__que5_ans1",
        "l1_prod__que6_ans1",
        "l1_prod__que7_ans1",
        "l1_prod__que8_ans1",
        "l1_prod__que9_ans1",
        "l1_prod__que10_ans1",
        "l1_prod__que11_ans1",
        "l1_prod__que4_ans2",
        "l1_prod__que4_ans22",
        "l1_prod__que5_ans2",
        "l1_prod__que6_ans2",
        "l1_prod__que7_ans2",
        "l1_prod__que8_ans2",
        "l1_prod__que9_ans2",
        "l1_prod__que10_ans2",
        "l1_prod__que11_ans2",
        "l1_prod__general_ques1",
        "l1_prod__general_ques2",
        "l1_prod__annotation_comment",
        "l2_prod__que0",
        "l2_prod__que1",
        "l2_prod__que2",
        "l2_prod__que2_1",
        "l2_prod__is_present_both",
        "l2_prod__que4_ans1",
        "l2_prod__que4_ans11",
        "l2_prod__que5_ans1",
        "l2_prod__que6_ans1",
        "l2_prod__que7_ans1",
        "l2_prod__que8_ans1",
        "l2_prod__que9_ans1",
        "l2_prod__que10_ans1",
        "l2_prod__que11_ans1",
        "l2_prod__que4_ans2",
        "l2_prod__que4_ans22",
        "l2_prod__que5_ans2",
        "l2_prod__que6_ans2",
        "l2_prod__que7_ans2",
        "l2_prod__que8_ans2",
        "l2_prod__que9_ans2",
        "l2_prod__que10_ans2",
        "l2_prod__que11_ans2",
        "l2_prod__general_ques1",
        "l2_prod__general_ques2",
        "l2_prod__annotation_comment",
        "l3_prod__que0",
        "l3_prod__que1",
        "l3_prod__que2",
        "l3_prod__que2_1",
        "l3_prod__is_present_both",
        "l3_prod__que4_ans1",
        "l3_prod__que4_ans11",
        "l3_prod__que5_ans1",
        "l3_prod__que6_ans1",
        "l3_prod__que7_ans1",
        "l3_prod__que8_ans1",
        "l3_prod__que9_ans1",
        "l3_prod__que10_ans1",
        "l3_prod__que11_ans1",
        "l3_prod__que4_ans2",
        "l3_prod__que4_ans22",
        "l3_prod__que5_ans2",
        "l3_prod__que6_ans2",
        "l3_prod__que7_ans2",
        "l3_prod__que8_ans2",
        "l3_prod__que9_ans2",
        "l3_prod__que10_ans2",
        "l3_prod__que11_ans2",
        "l3_prod__general_ques1",
        "l3_prod__general_ques2",
        "l3_prod__annotation_comment"
    ]

    percentage_df = percentage_df.drop(columns=columns_to_remove)

    percentage_df.reset_index(inplace=True)

    melted_percentage_df = pd.melt(percentage_df)

    # print(melted_percentage_df.drop(index=range(1,18)),"###################################")

    # fefg = melted_percentage_df.drop(index=range(1,18))['value']

    # print(fefg,"dfuhgjilhf")

    return melted_percentage_df.drop(index=range(1, 18))['value']


@csrf_exempt
def unsure_report_tl(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
    status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    if request.method == "POST":
        
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')




        # If fromdate and todate are the same, include the entire day by adding 23:59:59 to todate
        if fromdate == todate:
                            # Convert the string dates to datetime objects
            fromdate = datetime.strptime(fromdate, '%Y-%m-%d')
            todate = datetime.strptime(todate, '%Y-%m-%d')
            todate = todate + timedelta(days=1) - timedelta(seconds=1)

        filename_selected = request.POST.get('filename')
        scope = request.POST.get('scope')

        if scope == 'DA1':
            results = []
            # Query to get reporting_id and corresponding user ids
            reporting_groups = userProfile.objects.values('reporting_id').annotate(user_ids=Count('id'))

            # Create a dictionary that maps reporting_id to a list of corresponding user ids
            reporting_mapping = {}
            for group in reporting_groups:
                reporting_id = group['reporting_id']
                if reporting_id is not None:
                    user_ids = list(userProfile.objects.filter(reporting_id=reporting_id).values_list('id', flat=True))
                    reporting_mapping[reporting_id] = user_ids
            # print({'reporting_mapping': reporting_mapping})



            l1_prod_results = {}

            # Iterate over each reporting group
            for reporting_id, user_ids in reporting_mapping.items():
                # print(reporting_id)

                unsure_percentage_one_calculation = 0
                unsure_percentage_two_calculation = 0
                unsure_percentage_both_calculation = 0
                basefile_instance = get_object_or_404(basefile, filename=filename_selected)
                if filename_selected != 'ALL':
                    raw_data_entries = raw_data.objects.filter(l1_emp__id__in=user_ids, baseid = basefile_instance.pk)
                else:
                    raw_data_entries = raw_data.objects.filter(l1_emp__id__in=user_ids)
                
                l1_prod_entries = raw_data_entries.values_list('l1_prod__id', flat=True).distinct()

                
                l1_production_entries = l1_production.objects.filter(
                    id__in=l1_prod_entries, 
                    start_time__range=(fromdate, todate)  
                )

                
                que8_ans1_values = l1_production_entries.values_list('que7_ans1', flat=True)

                user_profile = userProfile.objects.get(pk=reporting_id)
        
                
                employee_name = user_profile.employeeName
                total_production_count = len(que8_ans1_values)
                unsure_count_answer_one = l1_production_entries.filter(que7_ans1='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_one_calculation = (unsure_count_answer_one/total_production_count) * 100
                unsure_count_answer_two = l1_production_entries.filter(que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_two_calculation = (unsure_count_answer_two/total_production_count) * 100
                unsure_count_both_DA1 = l1_production_entries.filter(que7_ans1='Unsure', que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_both_calculation = (unsure_count_both_DA1/total_production_count) * 100

                results.append({
                    'employee_name': employee_name,
                    'total_production_count': total_production_count,
                    'unsure_count_answer_one': unsure_count_answer_one,
                    'unsure_percentage_one': unsure_percentage_one_calculation,
                    'unsure_count_answer_two': unsure_count_answer_two,
                    'unsure_percentage_two': unsure_percentage_two_calculation,
                    'unsure_count_both': unsure_count_both_DA1,
                    'unsure_percentage_both': unsure_percentage_both_calculation
                })

            total_production_count_t = sum(item['total_production_count'] for item in results)
            unsure_count_answer_one_t = sum(item['unsure_count_answer_one'] for item in results)
            unsure_count_answer_two_t = sum(item['unsure_count_answer_two'] for item in results)
            unsure_count_both_t = sum(item['unsure_count_both'] for item in results)
            unsure_percentage_one_calculation_t = 0
            if total_production_count_t > 0:
                unsure_percentage_one_calculation_t = (unsure_count_answer_one_t/total_production_count_t) * 100
            unsure_percentage_two_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_two_calculation_t = (unsure_count_answer_two_t/total_production_count_t) * 100
            unsure_percentage_both_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_both_calculation_t = (unsure_count_both_t/total_production_count_t) * 100

            results.append({
                'employee_name': 'total', 
                'total_production_count': total_production_count_t, 
                'unsure_count_answer_one': unsure_count_answer_one_t, 
                'unsure_percentage_one': unsure_percentage_one_calculation_t, 
                'unsure_count_answer_two': unsure_count_answer_two_t, 
                'unsure_percentage_two': unsure_percentage_two_calculation_t, 
                'unsure_count_both': unsure_count_both_t, 
                'unsure_percentage_both': unsure_percentage_both_calculation_t
            })

            return render(request, 'reporting_mapping.html', {'reporting_mapping': results, 'filenames': filenames,  'fromdate': fromdate, 'todate': todate,'filename_selected':filename_selected,'scope':scope})
        else:
            results = []
            # Query to get reporting_id and corresponding user ids
            reporting_groups = userProfile.objects.values('reporting_id').annotate(user_ids=Count('id'))

            # Create a dictionary that maps reporting_id to a list of corresponding user ids
            reporting_mapping = {}
            for group in reporting_groups:
                reporting_id = group['reporting_id']
                if reporting_id is not None:
                    user_ids = list(userProfile.objects.filter(reporting_id=reporting_id).values_list('id', flat=True))
                    reporting_mapping[reporting_id] = user_ids
            # print({'reporting_mapping': reporting_mapping})



            l1_prod_results = {}

            # Iterate over each reporting group
            for reporting_id, user_ids in reporting_mapping.items():
                # print(reporting_id)

                unsure_percentage_one_calculation = 0
                unsure_percentage_two_calculation = 0
                unsure_percentage_both_calculation = 0
                basefile_instance = get_object_or_404(basefile, filename=filename_selected)
                if filename_selected != 'ALL':
                    raw_data_entries = raw_data.objects.filter(l2_emp__id__in=user_ids, baseid = basefile_instance.pk)
                else:
                    raw_data_entries = raw_data.objects.filter(l2_emp__id__in=user_ids)
                l2_prod_entries = raw_data_entries.values_list('l2_prod__id', flat=True).distinct()

                
                l2_production_entries = l2_production.objects.filter(
                    id__in=l2_prod_entries, 
                    start_time__range=(fromdate, todate)  
                )

                
                que8_ans1_values = l2_production_entries.values_list('que7_ans1', flat=True)

                user_profile = userProfile.objects.get(pk=reporting_id)
        
                
                employee_name = user_profile.employeeName
                total_production_count = len(que8_ans1_values)
                unsure_count_answer_one = l2_production_entries.filter(que7_ans1='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_one_calculation = (unsure_count_answer_one/total_production_count) * 100
                unsure_count_answer_two = l2_production_entries.filter(que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_two_calculation = (unsure_count_answer_two/total_production_count) * 100
                unsure_count_both_DA1 = l2_production_entries.filter(que7_ans1='Unsure', que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_both_calculation = (unsure_count_both_DA1/total_production_count) * 100

                results.append({
                    'employee_name': employee_name,
                    'total_production_count': total_production_count,
                    'unsure_count_answer_one': unsure_count_answer_one,
                    'unsure_percentage_one': unsure_percentage_one_calculation,
                    'unsure_count_answer_two': unsure_count_answer_two,
                    'unsure_percentage_two': unsure_percentage_two_calculation,
                    'unsure_count_both': unsure_count_both_DA1,
                    'unsure_percentage_both': unsure_percentage_both_calculation
                })

            total_production_count_t = sum(item['total_production_count'] for item in results)
            unsure_count_answer_one_t = sum(item['unsure_count_answer_one'] for item in results)
            unsure_count_answer_two_t = sum(item['unsure_count_answer_two'] for item in results)
            unsure_count_both_t = sum(item['unsure_count_both'] for item in results)
            unsure_percentage_one_calculation_t = 0
            if total_production_count_t > 0:
                unsure_percentage_one_calculation_t = (unsure_count_answer_one_t/total_production_count_t) * 100
            unsure_percentage_two_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_two_calculation_t = (unsure_count_answer_two_t/total_production_count_t) * 100
            unsure_percentage_both_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_both_calculation_t = (unsure_count_both_t/total_production_count_t) * 100

            results.append({
                'employee_name': 'total', 
                'total_production_count': total_production_count_t, 
                'unsure_count_answer_one': unsure_count_answer_one_t, 
                'unsure_percentage_one': unsure_percentage_one_calculation_t, 
                'unsure_count_answer_two': unsure_count_answer_two_t, 
                'unsure_percentage_two': unsure_percentage_two_calculation_t, 
                'unsure_count_both': unsure_count_both_t, 
                'unsure_percentage_both': unsure_percentage_both_calculation_t
            })
            # print(results)

            return render(request, 'reporting_mapping.html', {'reporting_mapping': results, 'filenames': filenames,  'fromdate': fromdate, 'todate': todate,'filename_selected':filename_selected,'scope':scope})    

    return render(request, 'reporting_mapping.html',{'filenames': filenames})




@csrf_exempt
def unsure_report_loc(request):
    filenames = raw_data.objects.values('baseid_id__filename').exclude(
    status__in=['hold', 'deleted']).order_by('-baseid_id').distinct()
    locations = userProfile.objects.filter(
        Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    
    if request.method == "POST":
        
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')




        # If fromdate and todate are the same, include the entire day by adding 23:59:59 to todate
        if fromdate == todate:
                            # Convert the string dates to datetime objects
            fromdate = datetime.strptime(fromdate, '%Y-%m-%d')
            todate = datetime.strptime(todate, '%Y-%m-%d')
            todate = todate + timedelta(days=1) - timedelta(seconds=1)

        filename_selected = request.POST.get('filename')
        scope = request.POST.get('scope')

        if scope == 'DA1':
            results = []

            l1_prod_results = {}

            # Iterate over each reporting group
            for  locations_f in locations:
                # print(reporting_id)

                unsure_percentage_one_calculation = 0
                unsure_percentage_two_calculation = 0
                unsure_percentage_both_calculation = 0
                basefile_instance = get_object_or_404(basefile, filename=filename_selected)
                if filename_selected != 'ALL':
                    raw_data_entries = raw_data.objects.filter(l1_loc=locations_f.get('location'), baseid = basefile_instance.pk)
                else:
                    raw_data_entries = raw_data.objects.filter(l1_loc=locations_f.get('location'))
               
                l1_prod_entries = raw_data_entries.values_list('l1_prod__id', flat=True).distinct()

                
                l1_production_entries = l1_production.objects.filter(
                    id__in=l1_prod_entries, 
                    start_time__range=(fromdate, todate)  
                )

                
                que8_ans1_values = l1_production_entries.values_list('que7_ans1', flat=True)

                # user_profile = userProfile.objects.get(pk=reporting_id)
        
                
                employee_name = locations_f.get('location')
                total_production_count = len(que8_ans1_values)
                unsure_count_answer_one = l1_production_entries.filter(que7_ans1='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_one_calculation = (unsure_count_answer_one/total_production_count) * 100
                unsure_count_answer_two = l1_production_entries.filter(que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_two_calculation = (unsure_count_answer_two/total_production_count) * 100
                unsure_count_both_DA1 = l1_production_entries.filter(que7_ans1='Unsure', que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_both_calculation = (unsure_count_both_DA1/total_production_count) * 100

                results.append({
                    'employee_name': employee_name,
                    'total_production_count': total_production_count,
                    'unsure_count_answer_one': unsure_count_answer_one,
                    'unsure_percentage_one': unsure_percentage_one_calculation,
                    'unsure_count_answer_two': unsure_count_answer_two,
                    'unsure_percentage_two': unsure_percentage_two_calculation,
                    'unsure_count_both': unsure_count_both_DA1,
                    'unsure_percentage_both': unsure_percentage_both_calculation
                })

            total_production_count_t = sum(item['total_production_count'] for item in results)
            unsure_count_answer_one_t = sum(item['unsure_count_answer_one'] for item in results)
            unsure_count_answer_two_t = sum(item['unsure_count_answer_two'] for item in results)
            unsure_count_both_t = sum(item['unsure_count_both'] for item in results)
            unsure_percentage_one_calculation_t = 0
            if total_production_count_t > 0:
                unsure_percentage_one_calculation_t = (unsure_count_answer_one_t/total_production_count_t) * 100
            unsure_percentage_two_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_two_calculation_t = (unsure_count_answer_two_t/total_production_count_t) * 100
            unsure_percentage_both_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_both_calculation_t = (unsure_count_both_t/total_production_count_t) * 100

            results.append({
                'employee_name': 'total', 
                'total_production_count': total_production_count_t, 
                'unsure_count_answer_one': unsure_count_answer_one_t, 
                'unsure_percentage_one': unsure_percentage_one_calculation_t, 
                'unsure_count_answer_two': unsure_count_answer_two_t, 
                'unsure_percentage_two': unsure_percentage_two_calculation_t, 
                'unsure_count_both': unsure_count_both_t, 
                'unsure_percentage_both': unsure_percentage_both_calculation_t
            })

            return render(request, 'reporting_mapping.html', {'reporting_mapping': results, 'filenames': filenames,  'fromdate': fromdate, 'todate': todate,'filename_selected':filename_selected,'scope':scope})
        else:
            results = []
            # Query to get reporting_id and corresponding user ids

            l1_prod_results = {}

            # Iterate over each reporting group
            for locations_f in locations:
                # print(reporting_id)

                unsure_percentage_one_calculation = 0
                unsure_percentage_two_calculation = 0
                unsure_percentage_both_calculation = 0
                basefile_instance = get_object_or_404(basefile, filename=filename_selected)
                if filename_selected != 'ALL':
                    raw_data_entries = raw_data.objects.filter(l2_loc = locations_f.get('location'), baseid = basefile_instance.pk)
                else:
                    raw_data_entries = raw_data.objects.filter(l2_loc = locations_f.get('location'))
                l2_prod_entries = raw_data_entries.values_list('l2_prod__id', flat=True).distinct()

                
                l2_production_entries = l2_production.objects.filter(
                    id__in=l2_prod_entries, 
                    start_time__range=(fromdate, todate)  
                )

                
                que8_ans1_values = l2_production_entries.values_list('que7_ans1', flat=True)


        
                
                employee_name = locations_f.get('location')
                total_production_count = len(que8_ans1_values)
                unsure_count_answer_one = l2_production_entries.filter(que7_ans1='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_one_calculation = (unsure_count_answer_one/total_production_count) * 100
                unsure_count_answer_two = l2_production_entries.filter(que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_two_calculation = (unsure_count_answer_two/total_production_count) * 100
                unsure_count_both_DA1 = l2_production_entries.filter(que7_ans1='Unsure', que7_ans2='Unsure').count()
                if total_production_count > 0:
                    unsure_percentage_both_calculation = (unsure_count_both_DA1/total_production_count) * 100

                results.append({
                    'employee_name': employee_name,
                    'total_production_count': total_production_count,
                    'unsure_count_answer_one': unsure_count_answer_one,
                    'unsure_percentage_one': unsure_percentage_one_calculation,
                    'unsure_count_answer_two': unsure_count_answer_two,
                    'unsure_percentage_two': unsure_percentage_two_calculation,
                    'unsure_count_both': unsure_count_both_DA1,
                    'unsure_percentage_both': unsure_percentage_both_calculation
                })

            total_production_count_t = sum(item['total_production_count'] for item in results)
            unsure_count_answer_one_t = sum(item['unsure_count_answer_one'] for item in results)
            unsure_count_answer_two_t = sum(item['unsure_count_answer_two'] for item in results)
            unsure_count_both_t = sum(item['unsure_count_both'] for item in results)
            unsure_percentage_one_calculation_t = 0
            if total_production_count_t > 0:
                unsure_percentage_one_calculation_t = (unsure_count_answer_one_t/total_production_count_t) * 100
            unsure_percentage_two_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_two_calculation_t = (unsure_count_answer_two_t/total_production_count_t) * 100
            unsure_percentage_both_calculation_t = 0
            if total_production_count_t > 0:
                    unsure_percentage_both_calculation_t = (unsure_count_both_t/total_production_count_t) * 100

            results.append({
                'employee_name': 'total', 
                'total_production_count': total_production_count_t, 
                'unsure_count_answer_one': unsure_count_answer_one_t, 
                'unsure_percentage_one': unsure_percentage_one_calculation_t, 
                'unsure_count_answer_two': unsure_count_answer_two_t, 
                'unsure_percentage_two': unsure_percentage_two_calculation_t, 
                'unsure_count_both': unsure_count_both_t, 
                'unsure_percentage_both': unsure_percentage_both_calculation_t
            })
            # print(results)

            return render(request, 'reporting_mapping.html', {'reporting_mapping': results, 'filenames': filenames , 'fromdate': fromdate, 'todate': todate,'filename_selected':filename_selected,'scope':scope})    

    return render(request, 'reporting_mapping.html',{'filenames': filenames})


def acr_report(request):
    filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
        status__in=['hole', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    tls = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
        'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')

    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        baseID = request.POST.get('batch')
        location = request.POST.get('location')
        language = request.POST.get('language')
        reporting = request.POST.get('reporting')

        query = Q()
        if fromdate and todate:
            query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
           
        if 'All' != location:
            query &= Q(l1_loc=location)
            

        if 'All' != baseID:
            query &= Q(baseid_id=baseID)
        else :
            query &= Q(baseid_id=baseID)

        if 'All' != reporting:
            query &= Q(l1_emp__reporting_id=reporting)
            

        if 'All' != language:
            query &= Q(baseid__language=language)

        duplicates = (
            raw_data.objects
            .filter(baseid_id=baseID)  # Filter for baseid == 1
            .values('question', 'answer_one', 'answer_two')
            .annotate(count=Count('id'))
            .filter(count__gt=1)  # Only include duplicates
        )

        # Count the number of duplicate instances
        duplicate_count = sum(duplicate['count'] for duplicate in duplicates)



def find_duplicates_view(request):
    filenames = raw_data.objects.values('baseid_id', 'baseid_id__filename').exclude(
        status__in=['hole', 'deleted']).order_by('-baseid_id').distinct()
    langs = Languages.objects.values('language')
    locations = Location.objects.values('location')
    tls = Roles.objects.filter(role__in=['Super Admin', 'Admin']).values(
        'userprofile_id', 'userprofile__employeeID').order_by('userprofile__employeeID')

    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        baseID = request.POST.get('batch')
        location = request.POST.get('location')
        language = request.POST.get('language')
        reporting = request.POST.get('reporting')
               
        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range=(fromdate, todate))
           
        if 'All' != location:
            query &= Q(qid__l1_loc=location)
            

        if 'All' != baseID:
            query &= Q(qid__baseid=baseID)
        else :
            query &= Q(qid__baseid=baseID)

        if 'All' != reporting:
            query &= Q(qid__l1_emp__reporting__employeeID=reporting)
            

        if 'All' != language:
            query &= Q(qid__baseid__language=language)

        duplicates_per = (
            l1_production.objects
            .filter(query)
            .values('qid__baseid','qid__question', 'qid__answer_one', 'qid__answer_two')
            .annotate(count=Count('id')).filter(count__gt=1)
        )


        # Step 2: Initialize counts
        matching_count = 0
        mismatching_count = 0

        # Step 3: Iterate through duplicates and compare additional fields
        for duplicate in duplicates_per:
            # Get the baseid to filter related instances
            baseid = duplicate['qid__baseid']

            # Retrieve all instances with this baseid
            instances = l1_production.objects.filter(qid__baseid=baseid)

            # Step 4: Assume the first instance as the reference for comparison
            reference_instance = instances.first()
            
            if reference_instance:
                # Initialize flags to check for matches
                all_match = True

                # Check all specified fields for matching
                for instance in instances:
                    if (reference_instance.que0 != instance.que0 or
                        reference_instance.que1 != instance.que1 or
                        reference_instance.que2 != instance.que2 or
                        reference_instance.que2_1 != instance.que2_1 or
                        reference_instance.is_present_both != instance.is_present_both or
                        reference_instance.que4_ans1 != instance.que4_ans1 or
                        reference_instance.que4_ans11 != instance.que4_ans11 or
                        reference_instance.que5_ans1 != instance.que5_ans1 or
                        reference_instance.que6_ans1 != instance.que6_ans1 or
                        reference_instance.que7_ans1 != instance.que7_ans1 or
                        reference_instance.que8_ans1 != instance.que8_ans1 or
                        reference_instance.que9_ans1 != instance.que9_ans1 or
                        reference_instance.que10_ans1 != instance.que10_ans1 or
                        reference_instance.que11_ans1 != instance.que11_ans1 or
                        reference_instance.que4_ans2 != instance.que4_ans2 or
                        reference_instance.que4_ans22 != instance.que4_ans22 or
                        reference_instance.que5_ans2 != instance.que5_ans2 or
                        reference_instance.que6_ans2 != instance.que6_ans2 or
                        reference_instance.que7_ans2 != instance.que7_ans2 or
                        reference_instance.que8_ans2 != instance.que8_ans2 or
                        reference_instance.que9_ans2 != instance.que9_ans2 or
                        reference_instance.que10_ans2 != instance.que10_ans2 or
                        reference_instance.que11_ans2 != instance.que11_ans2 or
                        reference_instance.general_ques1 != instance.general_ques1 or
                        reference_instance.general_ques2 != instance.general_ques2 or
                        reference_instance.annotation_comment != instance.annotation_comment):
                        all_match = False
                        break

                # Increment the corresponding counter based on match status
                if all_match:
                    matching_count += 1
                else:
                    mismatching_count += 1

        # total duplicate fields
        duplicates = (
            raw_data.objects
            .filter(baseid_id=baseID)  # Filter for baseid == 1
            .values('question', 'answer_one', 'answer_two')
            .annotate(count=Count('id'))
            .filter(count__gt=1)  # Only include duplicates
        )

        # Count total the number of duplicate instances
        duplicate_count = sum(duplicate['count'] for duplicate in duplicates)

        if mismatching_count == 0:
            acr_percentage = 0
        else:
            acr_percentage = 1- mismatching_count/duplicate_count
        return render(request, 'find_duplicates.html', {'duplicate_sets': duplicate_count,'acr_percentage':acr_percentage,'matching_count':matching_count,'mismatching_count':mismatching_count,'reporting': reporting, 'tls': tls, 'langs': langs, 'locations': locations, 'filenames': filenames,  'baseID': baseID, 'fromdate': fromdate, 'todate': todate, 'location': location, 'language': language})


    return render(request, 'find_duplicates.html', {'tls': tls, 'langs': langs, 'locations': locations, 'filenames': filenames})





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import main_error_datas, error_marked_datas


def da1_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(error_by='DA1',qid__l1_employeeid=current_user)
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_emp='processing').first() or 
            related_errors.filter(picked_by_emp__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_emp = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da1 = 'Yes'
                selected_error.picked_by_emp = 'completed'
                selected_error.comment_by_emp = comment

            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.da1 = 'No'
                selected_error.comment_by_emp = comment

            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)


def da2_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(error_by='DA2',qid__l2_employeeid=current_user)
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_emp='processing').first() or 
            related_errors.filter(picked_by_emp__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_emp = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da2 = 'Yes'
                selected_error.comment_by_emp = comment
                selected_error.picked_by_emp = 'completed'
            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.comment_by_emp = comment
                selected_error.da2 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)

def da3_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(
            Q(qid__l3_employeeid=current_user) & (Q(error_by='QA') | Q(error_by='QC') )
        )
      
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_emp='processing').first() or 
            related_errors.filter(picked_by_emp__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_emp = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da3 = 'Yes'
                selected_error.picked_by_emp = 'completed'
                selected_error.comment_by_emp = comment

            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.da3 = 'No'
                selected_error.comment_by_emp = comment

            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)



def tl_da1_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(qid__picked_by__employeeID=current_user,error_by='DA1',da1='No')
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da1 = 'Yes'
                selected_error.picked_by_tl = 'completed'
                selected_error.comment_by_tl = comment
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da1 = 'No'
                selected_error.comment_by_tl = comment
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)


def tl_da2_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(qid__picked_by__employeeID=current_user,error_by='DA2',da2='No')
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da2 = 'Yes'
                selected_error.picked_by_tl = 'completed'
                selected_error.comment_by_tl = comment
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da2 = 'No'
                selected_error.comment_by_tl = comment
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)


def tl_da3_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:

        related_errors = error_marked_datas.objects.filter((Q(error_by='QA') | Q(error_by='QC')) & (Q(da3='No') & Q(qid__picked_by__employeeID=current_user)))

        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.qid:  # Ensure qid is not None

            context['selected_error3']['batch_name'] = selected_error.qid.batch_name
            context['selected_error3']['file_name'] = selected_error.qid.file_name
            context['selected_error3']['id_value'] = selected_error.qid.id_value
            context['selected_error3']['asin'] = selected_error.qid.asin
            context['selected_error3']['product_url'] = selected_error.qid.product_url
            context['selected_error3']['title'] = selected_error.qid.title
            context['selected_error3']['evidence'] = selected_error.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.qid.imagepath
            context['selected_error3']['question'] = selected_error.qid.question
            context['selected_error3']['answer_1'] = selected_error.qid.answer_1
            context['selected_error3']['answer_2'] = selected_error.qid.answer_2
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.qid.que0
            context['selected_error2']['que1'] = selected_error.qid.que1
            context['selected_error2']['que2'] = selected_error.qid.que2
            context['selected_error2']['que2_1'] = selected_error.qid.que2_1
            context['selected_error2']['is_present_both'] = selected_error.qid.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.qid.que4_ans1
            context['selected_error2']['que4_ans11'] = selected_error.qid.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.qid.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.qid.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.qid.que7_ans1
            context['selected_error2']['que7a_ans1'] = selected_error.qid.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.qid.que8_ans1
            context['selected_error2']['que8a_ans1'] = selected_error.qid.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.qid.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.qid.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.qid.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.qid.que4_ans2
            context['selected_error2']['que4_ans22'] = selected_error.qid.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.qid.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.qid.que6_ans2
            context['selected_error2']['que7b_ans2'] = selected_error.qid.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.qid.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.qid.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.qid.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.qid.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.qid.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.qid.general_ques1
            context['selected_error2']['general_ques2'] = selected_error.qid.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.qid.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]

        fields = list(context['selected_error2'].keys())

        # Replace field names with words
        context['selected_error2'] = {
            word: context['selected_error2'][field] for field, word in zip(fields, words)
        }
        # Handle form submission
        print(context['selected_error3'])
        if request.method == 'POST':
            action = request.POST.get('action')
            comment = request.POST.get('comment')
            
            if action == 'accept':
                selected_error.da3 = 'Yes'
                selected_error.picked_by_tl = 'completed'
                selected_error.comment_by_tl = comment
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da3 = 'No'
                selected_error.comment_by_tl = comment

            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)
