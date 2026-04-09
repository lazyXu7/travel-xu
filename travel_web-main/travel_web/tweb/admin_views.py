# ============ 后台管理系统 ============
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from tweb.models import User, Comment, Favorite, HotelComment, HotelFavorite, HotelOrder, Hotel, ScenicZone, City


# 后台登录页面
def admin_login(request):
    """后台登录页面"""
    # 如果已登录，直接跳转控制台
    if request.session.get('admin_logged_in'):
        return redirect('admin_dashboard')

    return render(request, 'admin/login.html')


# 后台登录验证
@csrf_exempt
def admin_login_check(request):
    """后台登录验证"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # 验证管理员账号
        if username == 'root' and password == 'root':
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = username
            return JsonResponse({'status': 'success', 'message': '登录成功'})
        else:
            return JsonResponse({'status': 'error', 'message': '用户名或密码错误'})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


# 后台登出
def admin_logout(request):
    """后台登出"""
    request.session.flush()
    return redirect('/login/')


# 登录装饰器
def admin_required(view_func):
    """后台登录验证装饰器"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ============ 控制台 ============
@admin_required
def admin_dashboard(request):
    """控制台首页"""
    return render(request, 'admin/dashboard.html')


@admin_required
def admin_get_stats(request):
    """获取统计数据"""
    # 用户统计
    total_users = User.objects.count()

    # 订单统计
    total_orders = HotelOrder.objects.count()

    # 评论数
    total_comments = Comment.objects.count() + HotelComment.objects.count()

    # 最近注册的用户
    recent_users = list(User.objects.order_by('-UID')[:10].values(
        'UID', 'Uname', 'Uemail', 'jurisdiction'
    ))

    return JsonResponse({
        'status': 'success',
        'data': {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_comments': total_comments,
            'recent_users': recent_users
        }
    })


# ============ 用户管理 ============
@admin_required
def admin_user_list(request):
    """用户列表页面"""
    return render(request, 'admin/user_list.html')


@admin_required
def admin_get_users(request):
    """获取用户列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    keyword = request.GET.get('keyword', '')

    users = User.objects.all()

    if keyword:
        users = users.filter(Uname__icontains=keyword)

    total = users.count()
    users = users.order_by('-UID')[(page - 1) * page_size: page * page_size]

    data = []
    for u in users:
        # 统计用户评论数
        comment_count = Comment.objects.filter(C_user=u).count() + HotelComment.objects.filter(HC_user=u).count()
        # 统计用户收藏数
        favorite_count = Favorite.objects.filter(F_user=u).count() + HotelFavorite.objects.filter(HF_user=u).count()
        # 统计用户订单数
        order_count = HotelOrder.objects.filter(O_user=u).count()

        data.append({
            'UID': u.UID,
            'Uname': u.Uname,
            'Uemail': u.Uemail or '',
            'jurisdiction': u.jurisdiction,
            'gender': u.gender or '',
            'location': u.location or '',
            'birthday': str(u.birthday) if u.birthday else '',
            'comment_count': comment_count,
            'favorite_count': favorite_count,
            'order_count': order_count
        })

    return JsonResponse({
        'status': 'success',
        'data': {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@admin_required
@csrf_exempt
def admin_delete_user(request):
    """删除用户"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            User.objects.filter(UID=user_id).delete()
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


# ============ 评论管理 ============
@admin_required
def admin_comment_list(request):
    """评论列表页面"""
    return render(request, 'admin/comment_list.html')


@admin_required
def admin_get_comments(request):
    """获取评论列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    comment_type = request.GET.get('type', 'all')  # all, scenic, hotel

    all_comments = []

    if comment_type in ['all', 'scenic']:
        scenic_comments = Comment.objects.all().values(
            'CID', 'C_content', 'C_time', 'C_scenic_name', 'C_user__Uname'
        )
        for c in scenic_comments:
            all_comments.append({
                'id': c['CID'],
                'type': 'scenic',
                'content': c['C_content'],
                'time': c['C_time'].strftime('%Y-%m-%d %H:%M'),
                'target_name': c['C_scenic_name'],
                'user_name': c['C_user__Uname']
            })

    if comment_type in ['all', 'hotel']:
        hotel_comments = HotelComment.objects.all().values(
            'HCID', 'HC_content', 'HC_time', 'HC_hotel_name', 'HC_user__Uname'
        )
        for c in hotel_comments:
            all_comments.append({
                'id': c['HCID'],
                'type': 'hotel',
                'content': c['HC_content'],
                'time': c['HC_time'].strftime('%Y-%m-%d %H:%M'),
                'target_name': c['HC_hotel_name'],
                'user_name': c['HC_user__Uname']
            })

    # 按时间排序
    all_comments.sort(key=lambda x: x['time'], reverse=True)

    total = len(all_comments)
    start = (page - 1) * page_size
    end = start + page_size
    data = all_comments[start:end]

    return JsonResponse({
        'status': 'success',
        'data': {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@admin_required
@csrf_exempt
def admin_delete_comment(request):
    """删除评论"""
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment_type = request.POST.get('type', 'scenic')

        try:
            if comment_type == 'hotel':
                HotelComment.objects.filter(HCID=comment_id).delete()
            else:
                Comment.objects.filter(CID=comment_id).delete()
            return JsonResponse({'status': 'success', 'message': '删除成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


# ============ 订单管理 ============
@admin_required
def admin_order_list(request):
    """订单列表页面"""
    return render(request, 'admin/order_list.html')


@admin_required
def admin_get_orders(request):
    """获取订单列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    status = request.GET.get('status', '')

    orders = HotelOrder.objects.all().select_related('O_user')

    if status:
        orders = orders.filter(O_status=status)

    total = orders.count()
    orders = orders[(page - 1) * page_size: page * page_size]

    data = []
    for o in orders:
        data.append({
            'OID': o.OID,
            'order_no': f'H{timezone.now().year}{str(o.OID).zfill(8)}',
            'user_name': o.O_user.Uname if o.O_user else '已删除用户',
            'hotel_name': o.O_hotel_name,
            'checkin_date': str(o.O_checkin_date),
            'checkout_date': str(o.O_checkout_date),
            'room_count': o.O_room_count,
            'room_type': o.O_room_type or '',
            'total_price': float(o.O_total_price),
            'payment_method': o.O_payment_method,
            'status': o.O_status,
            'create_time': o.O_create_time.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({
        'status': 'success',
        'data': {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@admin_required
@csrf_exempt
def admin_update_order_status(request):
    """更新订单状态"""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        try:
            HotelOrder.objects.filter(OID=order_id).update(O_status=status)
            return JsonResponse({'status': 'success', 'message': '更新成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '请求方式错误'})


# ============ 酒店管理 ============
@admin_required
def admin_hotel_list(request):
    """酒店列表页面"""
    return render(request, 'admin/hotel_list.html')


@admin_required
def admin_get_hotels(request):
    """获取酒店列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    keyword = request.GET.get('keyword', '')

    hotels = Hotel.objects.all()

    if keyword:
        hotels = hotels.filter(H_name__icontains=keyword)

    total = hotels.count()
    hotels = hotels.order_by('-HID')[(page - 1) * page_size: page * page_size]

    data = []
    for h in hotels:
        # 统计评论数
        comment_count = HotelComment.objects.filter(HC_hotel_name=h.H_name).count()
        # 统计收藏数
        favorite_count = HotelFavorite.objects.filter(HF_hotel_name=h.H_name).count()

        data.append({
            'HID': h.HID,
            'H_name': h.H_name,
            'H_city': h.H_city or '',
            'H_address': h.H_address or '',
            'H_score': h.H_score,
            'H_price': h.H_price,
            'H_rooms': h.H_rooms,
            'H_star': h.H_star,
            'H_type': h.H_type or '',
            'H_tel': h.H_tel or '',
            'comment_count': comment_count,
            'favorite_count': favorite_count
        })

    return JsonResponse({
        'status': 'success',
        'data': {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


# ============ 景点管理 ============
@admin_required
def admin_scenic_list(request):
    """景点列表页面"""
    return render(request, 'admin/scenic_list.html')


@admin_required
def admin_get_scenics(request):
    """获取景点列表"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    keyword = request.GET.get('keyword', '')

    scenics = ScenicZone.objects.all()

    if keyword:
        scenics = scenics.filter(SZ_name__icontains=keyword)

    total = scenics.count()
    scenics = scenics.order_by('-SZid')[(page - 1) * page_size: page * page_size]

    data = []
    for s in scenics:
        comment_count = Comment.objects.filter(C_scenic_name=s.SZ_name).count()
        favorite_count = Favorite.objects.filter(F_scenic_name=s.SZ_name).count()

        data.append({
            'SZid': s.SZid,
            'SZ_name': s.SZ_name,
            'SZ_city': s.SZ_city.Cname if s.SZ_city else '',
            'SZ_address': s.SZ_address or '',
            'SZ_score': s.SZ_score,
            'SZ_popularity': s.SZ_popularity,
            'SZ_time': s.SZ_time or '',
            'comment_count': comment_count,
            'favorite_count': favorite_count
        })

    return JsonResponse({
        'status': 'success',
        'data': {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@admin_required
@csrf_exempt
def admin_add_scenic(request):
    """添加景点"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        city_name = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()
        score = request.POST.get('score', '4.5').strip()
        popularity = request.POST.get('popularity', '1000').strip()
        open_time = request.POST.get('open_time', '').strip()
        introduce = request.POST.get('introduce', '').strip()
        pic_url = request.POST.get('pic_url', '').strip()

        if not name:
            return JsonResponse({'status': 'error', 'message': '景点名称不能为空'})

        if ScenicZone.objects.filter(SZ_name=name).exists():
            return JsonResponse({'status': 'error', 'message': '该景点已存在'})

        city = None
        if city_name:
            city, _ = City.objects.get_or_create(Cname=city_name)

        scenic = ScenicZone.objects.create(
            SZ_name=name,
            SZ_city=city,
            SZ_address=address,
            SZ_score=float(score) if score else 4.5,
            SZ_popularity=int(popularity) if popularity else 1000,
            SZ_time=open_time,
            SZ_introduce=introduce,
            SZ_pic_url=pic_url
        )

        return JsonResponse({'status': 'success', 'message': '添加成功', 'data': {'id': scenic.SZid}})

    return JsonResponse({'status': 'error', 'message': '请求方式错误'})
