
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
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da1 = 'Yes'
                selected_error.picked_by_emp = 'completed'
            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.da1 = 'No'
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

        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_emp='processing').first() or 
            related_errors.filter(picked_by_emp__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err2.html', context)

        selected_error.picked_by_emp = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da2 = 'Yes'
                selected_error.picked_by_emp = 'completed'
            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.da2 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err2.html', context)

def da3_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(
            Q(qid__l3_employeeid=current_user) & (Q(error_by='QA') | Q(error_by='QC') )
        )
        
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_emp='processing').first() or 
            related_errors.filter(picked_by_emp__isnull=True).first()
        )
        
        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err3.html', context)

        selected_error.picked_by_emp = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da3 = 'Yes'
                selected_error.picked_by_emp = 'completed'
            elif action == 'deny':
                selected_error.picked_by_emp = 'completed'
                selected_error.da3 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err2.html', context)


def tl_da1_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:

        related_errors = error_marked_datas.objects.filter(error_by='DA1',da1='No')

        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err2.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da1 = 'Yes'
                selected_error.picked_by_tl = 'completed'
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da1 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'tlerr1.html', context)


def tl_da2_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:

        related_errors = error_marked_datas.objects.filter(error_by='DA2',da2='No')

        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err2.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da2 = 'Yes'
                selected_error.picked_by_tl = 'completed'
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da2 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'tlerr2.html', context)


def tl_da3_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:

        related_errors = error_marked_datas.objects.filter((Q(error_by='QA') | Q(error_by='QC')) & Q(da3='No'))

        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing').first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err2.html', context)

        selected_error.picked_by_tl = 'processing'
        selected_error.save()

        # Include all fields in the context dynamically
        fields = [
            'error_by','id', 'qid', 'que0', 'que1', 'que2', 'que2_1', 'is_present_both', 
            'que4_ans1', 'que4_ans11', 'que5_ans1', 'que6_ans1', 'que7_ans1', 
            'que7a_ans1', 'que8_ans1', 'que8a_ans1', 'que9_ans1', 'que10_ans1', 
            'que11_ans1', 'que4_ans2', 'que4_ans22', 'que5_ans2', 'que6_ans2', 
            'que7b_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 
            'que11_ans2', 'general_ques1', 'general_ques2', 'annotation_comment'
        ]
        
        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}
        
                # Handle form submission
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'accept':
                selected_error.da3 = 'Yes'
                selected_error.picked_by_tl = 'completed'
            elif action == 'deny':
                selected_error.picked_by_tl = 'completed'
                selected_error.da3 = 'No'
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'tlerr2.html', context)
