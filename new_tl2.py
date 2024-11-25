

def tl2_da1_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(picked_by_tl = 'completed',error_by='DA1',da1='No')
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing',picked_tl_emp_id=current_user).first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl2 = 'processing'
        selected_error.picked_tl_emp_id = current_user
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
                selected_error.picked_by_tl2 = 'completed'
                selected_error.comment_by_tl2 = comment
            elif action == 'deny':
                selected_error.picked_by_tl2 = 'completed'
                selected_error.da3 = 'No'
                selected_error.comment_by_tl2 = comment 

            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)

def tl2_da2_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = error_marked_datas.objects.filter(picked_by_tl = 'completed',error_by='DA2',da2='No')
        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl='processing',picked_tl_emp_id=current_user).first() or 
            related_errors.filter(picked_by_tl__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl2 = 'processing'
        selected_error.picked_tl_emp_id = current_user
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
                selected_error.picked_by_tl2 = 'completed'
                selected_error.comment_by_tl2 = comment
            elif action == 'deny':
                selected_error.picked_by_tl2 = 'completed'
                selected_error.da3 = 'No'
                selected_error.comment_by_tl2 = comment 
            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)


def tl2_da3_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:

        related_errors = error_marked_datas.objects.filter((Q(error_by='QA') | Q(error_by='QC')) & (Q(da3='No')  & Q(picked_by_tl = 'completed')))

        print(related_errors.values('error_by'))
        # Check conditions for `picked_by_emp`
        selected_error = (
            related_errors.filter(picked_by_tl2='processing',picked_tl_emp_id=current_user).first() or 
            related_errors.filter(picked_by_tl2__isnull=True).first()
        )

        if not selected_error:
            context['error'] = 'No matching error data found'
            return render(request, 'err.html', context)

        selected_error.picked_by_tl2 = 'processing'
        selected_error.picked_tl_emp_id = current_user
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
                selected_error.picked_by_tl2 = 'completed'
                selected_error.comment_by_tl2 = comment
            elif action == 'deny':
                selected_error.picked_by_tl2 = 'completed'
                selected_error.da3 = 'No'
                selected_error.comment_by_tl2 = comment

            selected_error.save()
            return redirect(request.path)
    except Exception as e:
        context['error'] = str(e)

    return render(request, 'err.html', context)
