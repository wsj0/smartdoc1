import uuid
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
import os
# Create your models here.

#为防止后来上传文件因重名而覆盖之前文件，动态定义文件上传路径


def user_directory_path(instance,filename):
    ext=filename.split('.')[-1]
    filename='{}.{}'.format(uuid.uuid4().hex[:10],ext)
    sub_folder='file'
    if ext.lower() in ["jpg","png","gif"]:
        sub_folder='picture'
    if ext.lower() in ["pdf", "docx", "txt"]:
        sub_folder = 'document'
    #/id/sub_folder/filename
    return os.path.join(str(instance.author.id),sub_folder,filename)

#通用的一个表
class AbstractModel(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    create_date=models.DateField(auto_now_add=True)
    mod_date=models.DateField(auto_now=True)

    class Meta:
        abstract=True

class Product(AbstractModel):
    """产品"""
    name=models.TextField(max_length=30,verbose_name="Product Name")
    code=models.TextField(max_length=30,verbose_name="Product Code")

    def __str__(self):
        return self.name
    #在完成创建或更新后，自动跳转回的一个绝对url
    def get_absolute_url(self):
        return reverse('smartdoc:product_detail',args=[str(self.id)])

    # 并用@property把它伪装成属性，
    # 统计属于同一产品的文档数量
    @property
    def document_count(self):
        return Document.objects.filter(product_id=self.id).count()

    class Meta:
        #按照修改时间的逆序
        ordering=['-mod_date']
        verbose_name='产品'

class Category(AbstractModel):
    """文档类型"""
    name=models.CharField(max_length=30,unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('smartdoc:category_detail',args=[self.id])

    @property
    def document_count(self):
        return Document.objects.filter(category_id=self.id).count()

    class Meta:
        ordering=['-mod_date']
        verbose_name='文档文类'

class Document(AbstractModel):
    """文件"""
    title=models.TextField(max_length=30,verbose_name="Title")
    version_no=models.IntegerField(blank=True,default=1,verbose_name="Version No")
    #用user_directory_path动态定义一个上传路径
    doc_file=models.FileField(upload_to=user_directory_path,
                              blank=True,null=True)
    #设置级联删除，主表删除数据，从表也删除
    product=models.ForeignKey(Product,
                              on_delete=models.CASCADE,
                              related_name='documents',)#在产品主表中对应的外键属性

    category=models.ForeignKey(Category,on_delete=models.CASCADE,
                                related_name='documents',)
    def __str__(self):
        return self.title
    #获取上传路径的文件类型名
    def get_format(self):
        return self.doc_file.url.split('.')[-1].upper()

    def get_absolute_url(self):
        return reverse('smartdoc:document_detail',args=[str(self.product.id),str(self.id)])

    class Meta:
        ordering=['-mod_date']
        verbose_name='文档'