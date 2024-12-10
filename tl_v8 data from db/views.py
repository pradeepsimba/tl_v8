def da1_error_data_view(request):
    current_user = request.session.get('employeeID')
    context = {}
    
    try:


        # Fetch related error_marked_datas rows
        related_errors = Audit_annotation.objects.filter(
                                                            Q(audit_errorid__da1_error_count__gt=0) &
                                                            Q(audit_errorid__qid__l1_emp__employeeID=current_user)
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
            'que4_ans1', 'que5_ans1', 'que6_ans1', 'que7_ans1',
            'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1',
            'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2',
            'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2',
            'general_ques1', 'annotation_comment'
        ]
        
        

        context['selected_error'] = {field: getattr(selected_error, field, None) for field in fields}

        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both',
            'que4_ans1', 'que5_ans1', 'que6_ans1', 'que7_ans1',
            'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1',
            'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2',
            'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2',
            'general_ques1', 'annotation_comment'
        ]

        fields = list(context['selected_error'].keys())

        # Replace field names with words
        context['selected_error'] = {
            word: context['selected_error'][field] for field, word in zip(fields, words)
        }
       
        context['selected_error2'] = {}
        context['selected_error3'] = {}
        if selected_error.audit_errorid:  # Ensure qid is not None

            # context['selected_error3']['batch_name'] = selected_error.audit_errorid.qid.batch_name
            # context['selected_error3']['file_name'] = selected_error.audit_errorid.qid.file_name
            context['selected_error3']['id_value'] = selected_error.audit_errorid.qid.id_value
            context['selected_error3']['asin'] = selected_error.audit_errorid.qid.asin
            context['selected_error3']['product_url'] = selected_error.audit_errorid.qid.product_url
            context['selected_error3']['title'] = selected_error.audit_errorid.qid.title
            context['selected_error3']['evidence'] = selected_error.audit_errorid.qid.evidence
            context['selected_error3']['imagepath'] = selected_error.audit_errorid.qid.imagepath
            context['selected_error3']['question'] = selected_error.audit_errorid.qid.question
            context['selected_error3']['answer_1'] = selected_error.audit_errorid.qid.answer_one
            context['selected_error3']['answer_2'] = selected_error.audit_errorid.qid.answer_two
            context['selected_error3']['comment_by_emp'] = selected_error.comment_by_emp

            # context['selected_error2']['scope'] = selected_error.qid.scope
            context['selected_error2']['que0'] = selected_error.audit_errorid.qid.l1_prod.que0
            context['selected_error2']['que1'] = selected_error.audit_errorid.qid.l1_prod.que1
            context['selected_error2']['que2'] = selected_error.audit_errorid.qid.l1_prod.que2
            context['selected_error2']['que2_1'] = selected_error.audit_errorid.qid.l1_prod.que2_1
            context['selected_error2']['is_present_both'] = selected_error.audit_errorid.qid.l1_prod.is_present_both
            context['selected_error2']['que4_ans1'] = selected_error.audit_errorid.qid.l1_prod.que4_ans1
            # context['selected_error2']['que4_ans11'] = selected_error.audit_errorid.qid.l1_prod.que4_ans11
            context['selected_error2']['que5_ans1'] = selected_error.audit_errorid.qid.l1_prod.que5_ans1
            context['selected_error2']['que6_ans1'] = selected_error.audit_errorid.qid.l1_prod.que6_ans1
            context['selected_error2']['que7_ans1'] = selected_error.audit_errorid.qid.l1_prod.que7_ans1
            # context['selected_error2']['que7a_ans1'] = selected_error.audit_errorid.qid.l1_prod.que7a_ans1
            context['selected_error2']['que8_ans1'] = selected_error.audit_errorid.qid.l1_prod.que8_ans1
            # context['selected_error2']['que8a_ans1'] = selected_error.audit_errorid.qid.l1_prod.que8a_ans1
            context['selected_error2']['que9_ans1'] = selected_error.audit_errorid.qid.l1_prod.que9_ans1
            context['selected_error2']['que10_ans1'] = selected_error.audit_errorid.qid.l1_prod.que10_ans1
            context['selected_error2']['que11_ans1'] = selected_error.audit_errorid.qid.l1_prod.que11_ans1
            context['selected_error2']['que4_ans2'] = selected_error.audit_errorid.qid.l1_prod.que4_ans2
            # context['selected_error2']['que4_ans22'] = selected_error.audit_errorid.qid.l1_prod.que4_ans22
            context['selected_error2']['que5_ans2'] = selected_error.audit_errorid.qid.l1_prod.que5_ans2
            context['selected_error2']['que6_ans2'] = selected_error.audit_errorid.qid.l1_prod.que6_ans2
            # context['selected_error2']['que7b_ans2'] = selected_error.audit_errorid.qid.l1_prod.que7b_ans2
            context['selected_error2']['que7_ans2'] = selected_error.audit_errorid.qid.l1_prod.que7_ans2
            context['selected_error2']['que8_ans2'] = selected_error.audit_errorid.qid.l1_prod.que8_ans2
            context['selected_error2']['que9_ans2'] = selected_error.audit_errorid.qid.l1_prod.que9_ans2
            context['selected_error2']['que10_ans2'] = selected_error.audit_errorid.qid.l1_prod.que10_ans2
            context['selected_error2']['que11_ans2'] = selected_error.audit_errorid.qid.l1_prod.que11_ans2
            context['selected_error2']['general_ques1'] = selected_error.audit_errorid.qid.l1_prod.general_ques1
            # context['selected_error2']['general_ques2'] = selected_error.audit_errorid.qid.l1_prod.general_ques2
            context['selected_error2']['annotation_comment'] = selected_error.audit_errorid.qid.l1_prod.annotation_comment
        words = [
            'que0', 'que1', 'que2', 'que2_1', 'is_present_both',
            'que4_ans1', 'que5_ans1', 'que6_ans1', 'que7_ans1',
            'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1',
            'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2',
            'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2',
            'general_ques1', 'annotation_comment'
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
