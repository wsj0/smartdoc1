import datetime
import json

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .forms import *
# Create your views here.
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView

from smartdoc.models import *

#显示产品对象
class ProductList(ListView):
    model = Product

#显示产品详情
class ProductDetail(DetailView):
    model = Product

#创建产品
#method_decorator将类伪装成函数
# login_required在用户试图访问某个页面,会要求登录.
@method_decorator(login_required,name='dispatch')
#分离权限验证和核心的业务逻辑
# @method_decorator(permission_required('smartdoc.add_product',
# raise_exception=True),name='dispatch')
class ProductCreate(CreateView):
    model = Product
    template_name = 'smartdoc/form.html'
    form_class = ProductForm

 #表单验证
    #form.instance联系起来.用户提供self.request.user
    def form_valid(self, form):
        form.instance.author=self.request.user
        return super().form_valid(form)

@method_decorator(login_required,name='dispatch')
# @method_decorator(permission_required('smartdoc.change_product',
# raise_exception=True),name='dispatch')
class ProductUpdate(UpdateView):
    model = Product
    template_name = 'smartdoc/form.html'
    form_class = ProductForm
    #判断对象是否为用户所创建
    def get_object(self, queryset=None):
        obj=super().get_object(queryset=queryset)
        if obj.author!=self.request.user:
            raise Http404()
        return obj

class CategoryList(ListView):
    model = Category

class CategoryDetail(DetailView):
    model = Category

@method_decorator(login_required, name='dispatch')
class CategoryCreate(CreateView):
    model = Category
    template_name = 'smartdoc/form.html'
    form_class = CategoryForm

    def form_valid(self, form):
        form.instance.author=self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class CategoryUpdate(UpdateView):
    model = Category
    template_name = 'smartdoc/form.html'
    form_class = CategoryForm

class DocumentList(ListView):
    model = Document

class DocumentDetail(DetailView):
    model = Document

@method_decorator(login_required, name='dispatch')
class DocumentCreate(CreateView):
    model = Document
    template_name = 'smartdoc/form.html'
    form_class = DocumentForm

    def form_valid(self, form):
        form.instance.author=self.request.user
        form.instance.product=Product.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class DocumentUpdate(UpdateView):
    model = Document
    template_name = 'smartdoc/form.html'
    form_class = DocumentForm

#取消csrftoken验证
@csrf_exempt
def document_search(request):
    q=request.GET.get('q',None)
    if q:
        document_list=Document.objects.filter(Q(title__icontains=q)|
                                              Q(product__name__icontains=q)|
                                              Q(product__code__icontains=q))
        context={'document_list':document_list}
        return render(request,'smartdoc/document_search.html',context)
    return render(request,'smartdoc/document_search.html')

@csrf_exempt
def doc_ajax_search(request):
    q=request.GET.get('q','')
    if q:
        document_list=Document.objects.filter(Q(title__icontains=q)|
                                              Q(product__name__icontains=q)|
                                              Q(product__code__icontains=q))
        data=[]
        for document in document_list:
            data.append(
                {'title':document.title,
                 'product_name':document.product.name,
                 'category_name':document.category.name,
                 'format':document.doc_file.url.split('.')[-1].upper(),
                 'size': "{:.1f}KB".format(document.doc_file.size / 1024),
                 'version':document.version_no,
                 'date':str(document.mod_date),
                 'product_id':document.product.id,
                 'id':document.id,
                 'url':document.doc_file.url,
                 }
            )
        json_data=json.dumps(data)
        print(json_data)
        return HttpResponse(json_data,content_type='application/json')
    return HttpResponse(json.dumps({"a":1}),content_type='application/json')


#datatime类型数据无法被json序列化
#把日期转为字符串格式
#class MyEncoder(json.JSONDecodeError):
#    def default(self,obj):
#        if isinstance(obj,datetime.datetime):
#            return obj.strftime('%Y-%m-%d')
#        elif isinstance(obj,datetime.date):
#            return obj.strftime('%Y-%m-%d')
#
#        return json.JSONEncoder.default(self,obj)
