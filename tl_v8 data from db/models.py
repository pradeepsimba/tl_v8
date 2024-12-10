class Audit_annotation(models.Model):
    audit_errorid = models.ForeignKey(Audit_Error,null=True,blank=True,on_delete=models.CASCADE, related_name='Audit_errorid')

    da1 = models.CharField(max_length=800,blank=True,null=True)
    da2 = models.CharField(max_length=800,blank=True,null=True)
    da3 = models.CharField(max_length=800,blank=True,null=True) 
    
    picked_by_emp = models.CharField(max_length=800,blank=True,null=True) 
    picked_by_tl = models.CharField(max_length=800,blank=True,null=True)

    comment_by_emp = models.TextField(blank=True, null=True)
    comment_by_tl = models.TextField(blank=True, null=True)

    picked_by_tl2 = models.CharField(max_length=800,blank=True,null=True)
    picked_tl_emp_id = models.CharField(max_length=800,blank=True,null=True)
    comment_by_tl2 = models.TextField(blank=True, null=True)

    audit_scope = models.CharField(max_length=800,blank=True,null=True)

    audit_mark = models.CharField(max_length=800,blank=True,null=True)

    created_by = models.ForeignKey(userProfile,null=True,blank=True,on_delete=models.RESTRICT,related_name='Annotation_createdby')
    created_at =models.DateTimeField(auto_now_add=True,null=True,blank=True)
