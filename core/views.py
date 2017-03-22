from django.shortcuts import render,render_to_response
from core.models import *
from django.http import HttpResponse, HttpResponseRedirect
from PIL import Image,ImageDraw,ImageFont
from math import ceil
import random
import os
import sys
import io as cStringIO
from datetime import datetime,timedelta
import hashlib
from django.core.files.storage import default_storage
import json
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import *
from django.db import connection
from django.utils import timezone
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.
from django.utils.decorators import available_attrs
from django.views.decorators.http import require_http_methods
import urllib.parse
import urllib.request
import base64
def my_custom_sql(sql,*para):
    cursor = connection.cursor()

    cursor.execute(sql,*para)

    #cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
    row = cursor.fetchall()

    return row


def error(req):
    '''
    维护页面
    '''
    return render(req, 'inc/error.html', locals())


def index(req):
    '''
    首页
    '''

    return render(req, 'web/index.html', locals())


def education(req):
    '''
    教育咨询
    '''

    return render(req, 'web/education.html', locals())


def highschool(req):
    '''
    初高中申请
    '''

    return render(req, 'web/highschool.html', locals())


def mxztc(req):
    '''
    名校直通车
    '''

    return render(req, 'web/mxztc.html', locals())

def cydkzx(req):
    '''
    创业贷款咨询
    '''

    return render(req, 'web/cydkzx.html', locals())

def courseguide(req):
    '''
    课程辅导
    '''

    return render(req, 'web/course-guide.html', locals())
def has_perm():
    """
    Decorator to make a view only accept particular authorized user.  Usage::



    Note that request methods should be in uppercase.
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(req, *args, **kwargs):
            userid=''
            try:
                userid = req.session.get('userid', '0')
                if user.objects.filter(id=userid):
                    return func(req,*args, **kwargs)
                else:
                    return HttpResponseRedirect('/r/login')
            except Exception as e:
                return HttpResponse(str(e)+' <a href="/r/login">返回登录</a>')
        return inner
    return decorator

@has_perm()
def backend_index(req,url):
    usersSum=user.objects.all().count()
    articleSum=article.objects.all().count()
    carouselSum=carousel.objects.all().count()
    pictureSum=picture.objects.all().count()
    return render(req,'backend/index.html',locals())
@has_perm()
def ajax_get_carousel(req):
    """
    异步获取轮播, 数据格式是table的tr
    :param req:
    :return:
    """
    cs = carousel.objects.all()
    ps = picture.objects.all()
    return render_to_response('backend/inclusion_tag_carousel.html',locals())

@csrf_exempt
@has_perm()
def edit_carousel(req):
    '''
    获取轮播管理页面。
    -----
    如果是post就是修改
    :param req:
    :return:
    '''
    if req.method=='GET':
        cs=carousel.objects.all()
        ps=picture.objects.all()
        return render(req, 'backend/carousel.html',locals())
    elif req.method=='POST':
        r = {}
        post_args = req.POST
        try:
            c = carousel.objects.get(id=post_args.get('id'))
            c.title = post_args.get('title')

            c.link = post_args.get('link')
            c.caption = post_args.get('caption')
        except Exception as e:
            r['msg'] = 'object not exist.due to \n %s' % ( str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r,ensure_ascii=False))

        try:
            r['msg'] = '%s saved.' % (c.title)
            r['status'] = '200'
            pr=c.imgs.all()
            pr.delete()
            p=picture.objects.get(id=post_args.get('pid'))
            c.imgs.add(p)
            c.save()
            return HttpResponse(json.dumps(r,ensure_ascii=False))
        except Exception as e:
            r['msg'] = '%s failed saving.due to \n %s' % (c.title, str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r,ensure_ascii=False))

@has_perm()
def add_carousel(req):
    """
    添加新的轮播.
    :param req:
    :return:
    """
    r = {}
    post_args=req.POST
    c=carousel()
    c.title=post_args.get('title')
    p=picture.objects.get(id=post_args.get('pid'))
    c.link = post_args.get('link')
    c.caption = post_args.get('caption')
    try:
        r['msg']='%s saved.' % (c.title)
        r['status']='200'
        c.save()
        c.imgs.add(p)

        return HttpResponse(json.dumps(r,ensure_ascii=False))
    except Exception as e:
        r['msg']='%s failed saving.due to \n %s' % (c.title,str(e))
        r['status'] = '500'
        return HttpResponse(json.dumps(r,ensure_ascii=False))

@has_perm()
def del_carousel(req):
    """
    批量删除轮播,
    :param post参数,接收名字为ids的数组:
    :return:
    """
    r = {}
    try:

        post_args = req.POST
        c=carousel.objects.filter(id__in=post_args.getlist('ids[]'))
        r['msg'] = '%s deleted.' % (",".join([x.title for x in c]))

        for x in c:

            c.delete()
        r['status']='200'
        return HttpResponse(json.dumps(r,ensure_ascii=False))
    except Exception as e:
        r['msg']='failed deleting.due to \n %s' % (str(e))
        r['status'] = '500'
        return HttpResponse(json.dumps(r,ensure_ascii=False))

@csrf_exempt
@has_perm()
def gallery(req):
    """
    GET方法获取图片库页面
    POST方法修改图片
    :param req:
    :return:
    """
    if req.method == 'GET':
        return render(req,'backend/gallery.html',locals())
    elif req.method=='POST':
        r = {}
        post_args = req.POST
        img = req.FILES
        try:
            p = picture.objects.get(id=post_args.get('id'))
            p.title = post_args.get('title')
            p.caption = post_args.get('caption')
        except Exception as e:
            r['msg'] = 'object not exist.due to \n %s' % ( str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r,ensure_ascii=False))

        try:
            r['msg'] = '%s saved.' % (p.title)
            r['status'] = '200'
            p.filepath = default_storage.save('core/static/uploads/' + str(p.id)+'.jpg', img['img'])[4:]
            p.save()
            return HttpResponse(json.dumps(r))
        except Exception as e:
            r['msg'] = '%s failed saving.due to \n %s' % (p.title, str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r,ensure_ascii=False))

@has_perm()
def add_picture(req):
    """
    添加新的图片
    :param req:
    :return:
    """
    r = {}
    post_args = req.POST
    img = req.FILES
    p = picture()
    p.title = post_args.get('title')

    p.caption = post_args.get('caption')
    try:
        r['msg'] = '%s saved.' % (p.title)
        r['status'] = '200'
        p.filepath = default_storage.save('core/static/uploads/' + str(p.title) + '.jpg', img['img'])[4:]
        p.save()
        return HttpResponse(json.dumps(r))
    except Exception as e:
        r['msg'] = '%s failed saving.due to \n %s' % (p.title, str(e))
        r['status'] = '500'
        return HttpResponse(json.dumps(r, ensure_ascii=False))

@has_perm()
def del_picture(req):
    """
    删除图片,并删除本地文件
    :param req,id:
    :return:
    """
    r = {}
    try:
        post_args = req.POST
        p=picture.objects.get(id=post_args.get('id'))
        r['msg'] = '%s deleted.' % (p.title)

        os.remove(str(os.path.dirname(__file__))+ str(p.filepath))
        p.delete()
        r['status']='200'
        return HttpResponse(json.dumps(r,ensure_ascii=False))
    except Exception as e:
        r['msg']='failed deleting.due to \n %s' % (str(e))
        r['status'] = '500'
        return HttpResponse(json.dumps(r,ensure_ascii=False))

@has_perm()
def ajax_get_pictures(req):
    """
    异步获取图片库的tbody对象
    :param req:
    :return:
    """
    ps=picture.objects.all()
    return render_to_response('backend/inclusion_tag_gallery.html',locals())

@has_perm()
@csrf_exempt
def content(req):
    """
    GET方法获取文章管理页面
    POST方法批量删除文章
    :param req:
    :return:
    """
    if req.method == 'GET':
        return render(req,'backend/content.html',locals())
    elif req.method=='POST':#POST method 做删除操作
        r = {}
        try:

            post_args = req.POST
            c = article.objects.filter(id__in=post_args.getlist('ids[]'))
            r['msg'] = '%s deleted.' % (",".join([x.title for x in c]))

            for x in c:
                c.delete()
            r['status'] = '200'
            return HttpResponse(json.dumps(r, ensure_ascii=False))
        except Exception as e:
            r['msg'] = 'failed deleting.due to \n %s' % (str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r, ensure_ascii=False))


@has_perm()
def ajax_get_content(req):
    """
    异步获取文章tbody内容
    :param req:
    :return:
    """
    ats = article.objects.all()
    return render_to_response('backend/inclusion_tag_content.html', locals())

@has_perm()
def edit_content(req):
    """
    GET方法获得修改文章的页面
    POST方法修改文章详情
    :param req:
    :return:
    """
    r = {}
    if req.method == 'GET':

        try:
            args=req.GET
            id=args.get('id')
            if id=='new':
                title=''
                content=''
                viewedTimes=''
                type=''

                return  render(req,'backend/edit_content.html',locals())
            else:
                c=article.objects.get(id=id)
                title = c.title
                content = c.content
                viewedTimes = c.viewedTimes
                type = c.type
                dimDate=c.dimDate
                return render(req, 'backend/edit_content.html', locals())
        except Exception as e:
            r['msg']=str(e)
            return  HttpResponse(json.dumps(r,ensure_ascii=False))
    elif req.method=='POST':

        try:
            args=req.POST
            id=args.get('id')
            title=args.get('title')
            cont=args.get('content')
            type=args.get('type')
            if id!='new':
                c=article.objects.get(id=id)
                c.title=title
                c.content=cont
                c.type=type
                r['status']='200'
                r['msg']='成功修改文章'
                c.save()
                return HttpResponseRedirect('/r/editcontent?id='+str(c.id))
            else:
                c = article()
                c.title = title
                c.content = cont
                c.type = type
                c.viewedTimes=0
                r['status']='200'
                r['msg']='成功新加文章'
                c.save()
                return HttpResponseRedirect('/r/editcontent?id='+str(c.id))
        except Exception as e:
            r['status'] = '500'
            r['msg'] = '失败 | '+str(e)
            return HttpResponse(json.dumps(r, ensure_ascii=False))

def login_backend(req):
    """
    GET方法获得登录页面
    POST方法验证登录并跳转
    :param req:
    :return:
    """
    if req.method=='GET':
        if 'userid' in req.session:
            return HttpResponseRedirect('/r/index')
        req.session['veriCode'] = newcode()
        return render(req,'backend/login.html',locals())
    else:
        r={}
        try:
            args = req.POST
            u=user.objects.filter(username=args.get('username'))
            if u:
                pwd = args.get('pwd')+u[0].salt

                md5=hashlib.md5()
                md5.update(pwd.encode())
                md5=md5.hexdigest()

                if args.get('img-verification') == req.session['veriCode']:
                    u=user.objects.filter(username=args.get('username'),pwd=md5)
                    if user:
                        req.session['username']=u[0].username
                        req.session['userid']=u[0].id
                        if u[0].avt:
                            req.session['avt']=u[0].avt.filepath
                        del req.session['veriCode']
                        r['status']='200'
                        r['msg']='成功登录.'
                        return HttpResponse(json.dumps(r, ensure_ascii=False))
                    else:
                        #info = '登录失败'
                        r['status'] = '403'
                        r['msg'] = '用户名或密码错误.'
                        return HttpResponse(json.dumps(r, ensure_ascii=False))
                else:
                    #info = '验证码错误'
                    r['status'] = '403'
                    r['msg'] = '验证码错误.'
                    return HttpResponse(json.dumps(r, ensure_ascii=False))
            else:
                #info='登录失败'
                r['status'] = '403'
                r['msg'] = '用户名或者密码错误,或已被禁用'
                return HttpResponse(json.dumps(r, ensure_ascii=False))
        except Exception as e :
            r['status'] = '403'
            r['msg'] = str(e)
            return HttpResponse(json.dumps(r, ensure_ascii=False))

@csrf_exempt
def logout(req):
    """
    注销

    :param req:
    :return:
    """
    r={}
    try:
        req.session.delete()
        r['status'] = '200'
        r['msg'] = '成功注销'
        return HttpResponse(json.dumps(r, ensure_ascii=False))
    except:
        r['status'] = '500'
        r['msg'] = '不知道为什么,居然注销失败了'
        return HttpResponse(json.dumps(r, ensure_ascii=False))

@has_perm()
@csrf_exempt
def add_user(req):
    """

    添加新用户.

    :param req:
    :return:
    """
    r = {}
    try:

        args=req.POST
        if user.objects.filter(username=args.get('username')):
            r['status']='500'
            r['msg']='用户名已经存在'
            return HttpResponse(json.dumps(r, ensure_ascii=False))
        else:

            pwd = args.get('pwd')
            mp = hashlib.md5()
            s = str(timezone.now()).encode()
            mp_src = mp.update(s)
            mp_src = mp.hexdigest()[:4]
            pwd = pwd + mp_src
            md5 = hashlib.md5()
            md5.update(pwd.encode())
            md5 = md5.hexdigest()
            p = picture.objects.get(id=args.get('pid'))
            u, created = user.objects.get_or_create(username=args.get('username'), salt=mp_src,
                                                        pwd=md5,avt=p)
            r['status']='200'
            r['msg']='成功新加用户.'
            if created == True:
                return HttpResponse(json.dumps(r, ensure_ascii=False))
            else:
                r['status'] = '200'
                r['msg'] = '没有成功新加用户.'
                return HttpResponse(json.dumps(r, ensure_ascii=False))
    except Exception as e:
        r['status']='500'
        r['msg']=str(e)
    return HttpResponse(json.dumps(r, ensure_ascii=False))

@has_perm()
def del_user(req):
    """
    删除用户
    :param req:
    :return:
    """
    r = {}
    try:

        args = req.POST
        u = user.objects.filter(id__in=args.getlist('ids[]'))
        r['msg'] = '%s deleted.' % (",".join([x.username for x in u]))

        for x in u:
            u.delete()

        r['status'] = '200'
        return HttpResponse(json.dumps(r, ensure_ascii=False))
    except Exception as e:
        r['status'] = '500'
        r['msg'] = str(e)
    return HttpResponse(json.dumps(r, ensure_ascii=False))

@has_perm()
def edit_user(req):
    """
    GET方法查看用户和自己头像修改
    POST方法修改用户数据
    :param req:
    :return:
    """
    if req.method=='GET':
        ps=picture.objects.all()
        return render(req,'backend/user.html',locals())
    else:
        r = {}
        post_args = req.POST
        try:
            u = user.objects.get(id=post_args.get('id'))
            pwd = post_args.get('pwd')
        except Exception as e:
            r['msg'] = 'object not exist.due to \n %s' % (str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r, ensure_ascii=False))

        try:
            if pwd:
                mp = hashlib.md5()
                s = str(timezone.now()).encode()
                mp_src = mp.update(s)
                mp_src = mp.hexdigest()[:4]
                pwd = pwd + mp_src
                md5 = hashlib.md5()
                md5.update(pwd.encode())
                md5 = md5.hexdigest()
                u.pwd=md5
                u.salt=mp_src

            r['msg'] = '%s saved.' % (u.username )
            r['status'] = '200'
            p = picture.objects.get(id=post_args.get('pid'))
            u.avt=p
            u.save()
            return HttpResponse(json.dumps(r, ensure_ascii=False))
        except Exception as e:
            r['msg'] = '%s failed saving.due to \n %s' % (u.username, str(e))
            r['status'] = '500'
            return HttpResponse(json.dumps(r, ensure_ascii=False))


@has_perm()
def ajax_get_user(req):
    us=user.objects.all()
    ps=picture.objects.all()
    return render_to_response('backend/inclusion_tag_user.html',locals())


def newcode():
    '''
    生成新的4位数的图片验证码
    :return:
    '''
    CODE_WIDTH=90
    CODE_HEIGHT=30
    background = (random.randrange(230, 255), random.randrange(230, 255), random.randrange(230, 255))
    im = Image.new('RGB', (CODE_WIDTH, CODE_HEIGHT), background)
    # create
    draw = ImageDraw.Draw(im)
    for i in range(random.randrange(6 - 2, 6)):
        line_color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        xy = (
            random.randrange(0, int(CODE_WIDTH * 0.2)),
            random.randrange(0, CODE_HEIGHT),
            random.randrange(3 * int(CODE_WIDTH / 4), CODE_WIDTH),
            random.randrange(0, CODE_HEIGHT)
        )
        draw.line(xy, fill=line_color, width=int(25 * 0.1))
    j = int(25 * 0.3)
    k = int(25 * 0.5)
    x = random.randrange(j, k)  # starts point
    mp = hashlib.md5()
    s=str(timezone.now()).encode()
    mp_src = mp.update(s)
    mp_src = mp.hexdigest()
    rand_str = mp_src
    for i in rand_str:
        # 上下抖动量,字数越多,上下抖动越大
        m = int(len(rand_str))
        y = random.randrange(1, 3)

        if i in ('+', '=', '?'):
            # 对计算符号等特殊字符放大处理
            m = ceil(25 * 0.8)
        else:
            # 字体大小变化量,字数越少,字体大小变化越多
            m = random.randrange(0, int(45 / 25) + int(25 / 5))

        #font = ImageFont.truetype("/home/ubuntu/wpc/core/static/timesnewrome/times.ttf", 25 + int(ceil(m)))
        font = ImageFont.truetype("core/static/timesnewrome/times.ttf", 25 + int(ceil(m)))

        draw.text((x, y), i, font=font, fill=random.choice(['black','darkblue','red']))
        x += 25 * 0.9

    del x
    del draw
    buf =open('core/static/temp.png','wb')
    im.save(buf, 'png')
    buf.close()
    return rand_str[:4]


@csrf_exempt
def refreshcode(req):
    try:
        req.session['veriCode']=newcode()
        return HttpResponse('1')
    except Exception as e:
        return HttpResponse(e)


@cache_page(60 * 2)
def filebrowser(req):
    """
    浏览图片库并给tinymce返回路径.
    :param req:
    :return:
    """
    ps=picture.objects.all()
    return render_to_response('backend/tinymce_file_browser.html',locals())