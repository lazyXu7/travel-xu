import json
import random
import string
import requests
import os
import urllib3
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from tweb.models import User, Comment, Favorite, Hotel, HotelComment, HotelFavorite, HotelOrder, ScenicZone, City
from django.conf import settings

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GAODE_API_KEY = "441d40f9bc7eabfc3540e4951f9b681c"

# 热门城市静态列表
HOT_CITIES = ['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '苏州', '南京']

# 城市三字码映射（机场代码）
CITY_AIRPORT_CODES = {
    '北京': 'PEK', '上海': 'SHA', '广州': 'CAN', '深圳': 'SZX',
    '杭州': 'HGH', '成都': 'CTU', '重庆': 'CKG', '西安': 'XIY',
    '南京': 'NKG', '武汉': 'WUH', '厦门': 'XMN', '昆明': 'KMG',
    '青岛': 'TAO', '大连': 'DLC', '长沙': 'CSX', '郑州': 'CGO',
    '沈阳': 'SHE', '海口': 'HAK', '三亚': 'SYX', '天津': 'TSN',
    '哈尔滨': 'HRB', '乌鲁木齐': 'URC', '兰州': 'LHW', '贵阳': 'KWE',
    '南宁': 'NNG', '福州': 'FOC', '太原': 'TYN', '拉萨': 'LXA',
    '呼和浩特': 'HET', '长春': 'CGQ', '石家庄': 'SJW', '宁波': 'NGB',
    '温州': 'WNZ', '珠海': 'ZUH', '东莞': 'DGQ', '佛山': 'FUO',
    '无锡': 'WUX', '常州': 'CZX', '徐州': 'XUZ', '扬州': 'YTY',
}

# 火车站编码映射
STATION_CODES = {
    '北京': {'name': '北京', 'code': 'BJP'},
    '北京南': {'name': '北京南', 'code': 'VNP'},
    '北京西': {'name': '北京西', 'code': 'BXP'},
    '上海': {'name': '上海', 'code': 'SHH'},
    '上海虹桥': {'name': '上海虹桥', 'code': 'AOH'},
    '上海南': {'name': '上海南', 'code': 'SNH'},
    '广州': {'name': '广州', 'code': 'GZQ'},
    '广州南': {'name': '广州南', 'code': 'IZQ'},
    '深圳': {'name': '深圳', 'code': 'SZQ'},
    '深圳北': {'name': '深圳北', 'code': 'SZQ'},
    '杭州': {'name': '杭州', 'code': 'HZH'},
    '杭州东': {'name': '杭州东', 'code': 'HGH'},
    '成都': {'name': '成都', 'code': 'CDW'},
    '成都东': {'name': '成都东', 'code': 'ICW'},
    '重庆': {'name': '重庆', 'code': 'CQW'},
    '重庆北': {'name': '重庆北', 'code': 'CYW'},
    '西安': {'name': '西安', 'code': 'XAY'},
    '西安北': {'name': '西安北', 'code': 'EAY'},
    '南京': {'name': '南京', 'code': 'NJH'},
    '南京南': {'name': '南京南', 'code': 'NKH'},
    '武汉': {'name': '武汉', 'code': 'WHN'},
    '厦门': {'name': '厦门', 'code': 'XMS'},
    '青岛': {'name': '青岛', 'code': 'QDK'},
    '大连': {'name': '大连', 'code': 'DLT'},
    '长沙': {'name': '长沙', 'code': 'CSQ'},
    '郑州': {'name': '郑州', 'code': 'ZZF'},
    '沈阳': {'name': '沈阳', 'code': 'SYT'},
    '天津': {'name': '天津', 'code': 'TJP'},
    '哈尔滨': {'name': '哈尔滨', 'code': 'HBB'},
    '济南': {'name': '济南', 'code': 'JNK'},
    '福州': {'name': '福州', 'code': 'FZS'},
    '昆明': {'name': '昆明', 'code': 'KMM'},
    '贵阳': {'name': '贵阳', 'code': 'GIW'},
    '南宁': {'name': '南宁', 'code': 'NNZ'},
    '太原': {'name': '太原', 'code': 'TYV'},
    '兰州': {'name': '兰州', 'code': 'LZJ'},
    '乌鲁木齐': {'name': '乌鲁木齐', 'code': 'WCR'},
    '拉萨': {'name': '拉萨', 'code': 'LSO'},
    '呼和浩特': {'name': '呼和浩特', 'code': 'HHC'},
    '长春': {'name': '长春', 'code': 'CTC'},
    '石家庄': {'name': '石家庄', 'code': 'SJP'},
    '苏州': {'name': '苏州', 'code': 'SZH'},
    '宁波': {'name': '宁波', 'code': 'NGH'},
    '温州': {'name': '温州', 'code': 'RZH'},
    '珠海': {'name': '珠海', 'code': 'ZIQ'},
    '东莞': {'name': '东莞', 'code': 'RTQ'},
    '佛山': {'name': '佛山', 'code': 'FQQ'},
    '无锡': {'name': '无锡', 'code': 'WXS'},
    '常州': {'name': '常州', 'code': 'CZD'},
    '徐州': {'name': '徐州', 'code': 'XZD'},
    '扬州': {'name': '扬州', 'code': 'YZH'},
}


def get_random_score():
    """生成随机评分 4.0-4.9"""
    return round(random.uniform(4.0, 4.9), 1)


def index(request):
    """主页"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')
    return render(request, 'index.html', {
        'cities': HOT_CITIES,
        'user_id': user_id,
        'username': username
    })


def scenic(request):
    """旅游推荐页"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')
    return render(request, 'scenic.html', {
        'cities': HOT_CITIES,
        'user_id': user_id,
        'username': username
    })


@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            username = json_data.get('username')
            password = json_data.get('password')
            user = User.objects.filter(Uname=username, Upwd=password).first()
            if user:
                request.session['user_id'] = user.UID
                request.session['username'] = user.Uname
                return JsonResponse({"message": "1"})
            return JsonResponse({"message": "3"})
        except:
            return JsonResponse({"message": "4"})


def sign(request):
    return render(request, 'sign.html')


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            username = json_data.get('username')
            password = json_data.get('password')
            email = json_data.get('email', '')
            if not username or not password:
                return JsonResponse({'message': '3', 'msg': '用户名和密码不能为空'})
            if User.objects.filter(Uname=username).exists():
                return JsonResponse({'message': '4', 'msg': '用户名已存在'})
            if email and User.objects.filter(Uemail=email).exists():
                return JsonResponse({'message': '5', 'msg': '邮箱已被使用'})
            user = User.objects.create(Uname=username, Upwd=password, Uemail=email if email else None, jurisdiction='user')
            return JsonResponse({'message': '1', 'msg': '注册成功'})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'message': '2', 'msg': f'注册失败: {str(e)}'})


def search(request):
    """搜索城市景点API"""
    city_name = request.GET.get('city', '')
    if not city_name:
        return JsonResponse({'message': '0'})

    city_name = city_name.strip()

    # 直接从高德API搜索景点
    scenics_data = search_from_gaode(city_name)
    if scenics_data:
        return JsonResponse({
            'message': '1',
            'scenics': scenics_data,
            'is_gaode': True
        })

    return JsonResponse({'message': '2'})


def search_from_gaode(city_name):
    """从高德API搜索景点"""
    url = "https://restapi.amap.com/v3/place/text"
    scenics = []

    for keyword in ["景点", "公园", "博物馆", "古迹", "景区"]:
        if len(scenics) >= 10:
            break

        params = {
            "key": GAODE_API_KEY,
            "keywords": f"{city_name} {keyword}",
            "city": city_name,
            "citylimit": "true",
            "offset": 5,
            "page": 1,
            "extensions": "all"
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") != "1":
                continue

            pois = data.get("pois", [])
            for poi in pois:
                if len(scenics) >= 10:
                    break

                name = poi.get("name", "")
                if any(s['name'] == name for s in scenics):
                    continue

                photos = poi.get("photos", [])
                pic_url = photos[0].get("url", "") if photos else ""

                tel = poi.get("tel", "")

                # 构建更丰富的介绍
                address = poi.get("address", "")
                intro_parts = []

                if address:
                    intro_parts.append(f"地址：{address}")
                if tel:
                    intro_parts.append(f"电话：{tel}")

                # 高德的introduction字段可能有更详细介绍
                introduction = poi.get("introduction", "")
                if introduction:
                    intro_parts.append(introduction[:200] if len(introduction) > 200 else introduction)
                elif address:
                    intro_parts.append(f"{name}是{city_name}的热门景点，风景优美，是旅游观光的好去处。")

                intro = " | ".join(intro_parts) if intro_parts else f"{name}是{city_name}的热门景点，欢迎游览。"

                # 获取省份和城市
                province = poi.get("pname", city_name)  # 省份，默认使用搜索城市
                scenic_city = poi.get("cityname", city_name)  # 城市

                scenics.append({
                    'id': '',
                    'name': name,
                    'pic_url': pic_url,
                    'score': get_random_score(),
                    'intro': intro,
                    'tel': tel,
                    'open_time': poi.get('open_time', ''),
                    'address': address,
                    'province': province,
                    'city': scenic_city,
                })
        except:
            continue

    return scenics


def sz(request):
    """景点详情页"""
    scenic_name = request.GET.get('name', '')
    user_id = request.session.get('user_id')

    gaode_data = get_scenic_from_gaode(scenic_name) if scenic_name else None

    # 获取该景点的评论
    comments = []
    if scenic_name:
        comments = Comment.objects.filter(C_scenic_name=scenic_name).select_related('C_user')[:20]

    # 检查用户是否已收藏
    is_favorited = False
    if user_id and scenic_name:
        is_favorited = Favorite.objects.filter(F_user_id=user_id, F_scenic_name=scenic_name).exists()

    context = {
        'sz': scenic_name or '景点详情',
        'sz_time': gaode_data.get('open_time', '以景区公示为准') if gaode_data else '未知',
        'sz_address': gaode_data.get('address', '暂无地址信息') if gaode_data else '未知',
        'sz_pic_url': gaode_data.get('photo', '') if gaode_data else '',
        'sz_introduce': gaode_data.get('intro', '暂无详细介绍') if gaode_data else '未找到该景点信息',
        'sz_score': get_random_score(),
        'sz_popularity': 0,
        'sz_province': gaode_data.get('province', '') if gaode_data else '',
        'sz_city': gaode_data.get('city', '') if gaode_data else '',
        'comments': comments,
        'is_favorited': is_favorited,
        'user_id': user_id,
        'username': request.session.get('username', ''),
    }

    return render(request, 'sz.html', context)


@require_http_methods(["POST"])
def add_comment(request):
    """添加评论"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        scenic_name = json_data.get('scenic_name', '')
        content = json_data.get('content', '').strip()

        if not scenic_name or not content:
            return JsonResponse({'message': '0', 'msg': '评论内容不能为空'})

        Comment.objects.create(
            C_scenic_name=scenic_name,
            C_user_id=request.session['user_id'],
            C_content=content
        )
        return JsonResponse({'message': '1', 'msg': '评论成功'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@require_http_methods(["POST"])
def toggle_favorite(request):
    """切换收藏状态"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        scenic_name = json_data.get('scenic_name', '')
        pic_url = json_data.get('pic_url', '')

        if not scenic_name:
            return JsonResponse({'message': '0', 'msg': '景点名称不能为空'})

        favorite = Favorite.objects.filter(
            F_user_id=request.session['user_id'],
            F_scenic_name=scenic_name
        ).first()

        if favorite:
            favorite.delete()
            return JsonResponse({'message': '1', 'action': 'removed', 'msg': '已取消收藏'})
        else:
            Favorite.objects.create(
                F_scenic_name=scenic_name,
                F_pic_url=pic_url,
                F_user_id=request.session['user_id']
            )
            return JsonResponse({'message': '1', 'action': 'added', 'msg': '收藏成功'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


def profile(request):
    """个人中心"""
    if 'user_id' not in request.session:
        return render(request, 'login.html', {'error': '请先登录'})

    user = User.objects.filter(UID=request.session['user_id']).first()
    favorites = Favorite.objects.filter(F_user=request.session['user_id'])
    comments = Comment.objects.filter(C_user=request.session['user_id']).order_by('-C_time')[:10]

    return render(request, 'profile.html', {
        'user': user,
        'favorites': favorites,
        'comments': comments,
        'username': request.session.get('username', ''),
    })


def logout(request):
    """退出登录"""
    request.session.flush()
    return render(request, 'login.html', {'msg': '已退出登录'})


def get_scenic_from_gaode(scenic_name):
    """从高德API获取景点详情"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": GAODE_API_KEY,
        "keywords": scenic_name,
        "extensions": "all"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "1":
            pois = data.get("pois", [])
            for poi in pois:
                if poi.get("name") == scenic_name:
                    photos = poi.get("photos", [])
                    introduction = poi.get("introduction", "")

                    if not introduction or len(introduction) < 20:
                        address = poi.get("address", "")
                        introduction = f"{scenic_name}位于{address}，是一处风景秀丽的旅游景点。这里环境优美，设施完善，是游客休闲观光的好去处。"
                    elif len(introduction) > 500:
                        introduction = introduction[:500] + "..."

                    return {
                        'name': poi.get("name", scenic_name),
                        'address': poi.get("address", "暂无地址信息"),
                        'intro': introduction,
                        'open_time': poi.get('open_time', ''),
                        'photo': photos[0].get("url", "") if photos else "",
                        'province': poi.get("pname", ""),
                        'city': poi.get("cityname", "")
                    }
    except Exception:
        pass
    return None


# 存储验证码 (生产环境应使用Redis)
VERIFICATION_CODES = {}


def generate_code():
    """生成6位验证码"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email, code):
    """发送验证码邮件"""
    try:
        # 邮件配置 - 请修改为你的邮箱配置
        EMAIL_HOST = getattr(settings, 'EMAIL_HOST', 'smtp.qq.com')
        EMAIL_PORT = getattr(settings, 'EMAIL_PORT', 587)
        EMAIL_HOST_USER = getattr(settings, 'EMAIL_HOST_USER', '')
        EMAIL_HOST_PASSWORD = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        EMAIL_USE_TLS = getattr(settings, 'EMAIL_USE_TLS', True)

        if not EMAIL_HOST_USER:
            return False, "邮件服务未配置"

        subject = '旅游网站验证码'
        content = f'''
        您好！
        您的验证码是：<b>{code}</b>
        验证码5分钟内有效，请勿泄露给他人。
        如果这不是您本人的操作，请忽略此邮件。
        '''

        send_mail(
            subject=subject,
            message='',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=content,
            fail_silently=False
        )
        return True, "发送成功"
    except Exception as e:
        return False, str(e)


@csrf_exempt
@require_http_methods(["POST"])
def send_reset_code(request):
    """发送重置密码验证码"""
    try:
        json_data = json.loads(request.body)
        email = json_data.get('email', '').strip()

        if not email:
            return JsonResponse({'message': '0', 'msg': '请输入邮箱地址'})

        # 验证邮箱是否已注册
        user = User.objects.filter(Uemail=email).first()
        if not user:
            return JsonResponse({'message': '0', 'msg': '该邮箱未注册'})

        # 生成验证码
        code = generate_code()
        VERIFICATION_CODES[email] = {'code': code, 'time': random.time()}

        # 发送邮件
        success, msg = send_verification_email(email, code)
        if success:
            return JsonResponse({'message': '1', 'msg': '验证码已发送到邮箱'})
        else:
            return JsonResponse({'message': '0', 'msg': f'发送失败: {msg}'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    """重置密码"""
    try:
        json_data = json.loads(request.body)
        email = json_data.get('email', '').strip()
        code = json_data.get('code', '').strip()
        new_password = json_data.get('new_password', '').strip()

        if not all([email, code, new_password]):
            return JsonResponse({'message': '0', 'msg': '请填写完整信息'})

        if len(new_password) < 6 or len(new_password) > 16:
            return JsonResponse({'message': '0', 'msg': '密码需要在6-16位之间'})

        # 验证验证码
        saved = VERIFICATION_CODES.get(email)
        if not saved or saved['code'] != code:
            return JsonResponse({'message': '0', 'msg': '验证码错误'})

        # 检查验证码是否过期 (5分钟)
        import time
        if time.time() - saved['time'] > 300:
            del VERIFICATION_CODES[email]
            return JsonResponse({'message': '0', 'msg': '验证码已过期'})

        # 更新密码
        user = User.objects.filter(Uemail=email).first()
        if user:
            user.Upwd = new_password
            user.save()
            del VERIFICATION_CODES[email]
            return JsonResponse({'message': '1', 'msg': '密码重置成功'})

        return JsonResponse({'message': '0', 'msg': '用户不存在'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """更新个人信息"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        user = User.objects.filter(UID=request.session['user_id']).first()
        if not user:
            return JsonResponse({'message': '0', 'msg': '用户不存在'})

        json_data = json.loads(request.body)

        # 更新字段
        if 'birthday' in json_data:
            user.birthday = json_data['birthday'] or None
        if 'gender' in json_data:
            user.gender = json_data['gender'] or None
        if 'location' in json_data:
            user.location = json_data['location'] or ''
        if 'avatar' in json_data:
            user.avatar = json_data['avatar'] or ''

        user.save()
        return JsonResponse({'message': '1', 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def login_v2(request):
    """支持邮箱登录的新登录接口"""
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            username_or_email = json_data.get('username', '').strip()
            password = json_data.get('password', '')

            if not username_or_email or not password:
                return JsonResponse({'message': '0', 'msg': '请输入用户名/邮箱和密码'})

            # 支持用户名或邮箱登录
            user = User.objects.filter(Uname=username_or_email, Upwd=password).first()
            if not user:
                user = User.objects.filter(Uemail=username_or_email, Upwd=password).first()

            if user:
                request.session['user_id'] = user.UID
                request.session['username'] = user.Uname
                return JsonResponse({'message': '1', 'msg': '登录成功', 'email': user.Uemail})
            return JsonResponse({'message': '0', 'msg': '用户名/邮箱或密码错误'})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'message': '0', 'msg': f'登录异常: {str(e)}'})


# ==================== 酒店相关视图 ====================

def hotel_index(request):
    """酒店推荐首页"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')

    # 热门城市
    hot_cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '苏州', '南京']

    return render(request, 'hotel.html', {
        'hot_cities': hot_cities,
        'user_id': user_id,
        'username': username,
    })


def search_hotels_from_gaode(city_name):
    """从高德API搜索酒店"""
    url = "https://restapi.amap.com/v3/place/text"
    hotels = []

    params = {
        "key": GAODE_API_KEY,
        "keywords": "酒店",
        "city": city_name,
        "citylimit": "true",
        "offset": 20,
        "page": 1,
        "extensions": "all"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "1":
            return hotels

        pois = data.get("pois", [])
        for poi in pois:
            name = poi.get("name", "")
            if not name or "酒店" not in name:
                continue

            photos = poi.get("photos", [])
            pic_url = photos[0].get("url", "") if photos else ""

            # 获取省份和城市
            province = poi.get("pname", "")
            city = poi.get("cityname", "")

            # 获取详细地址（包含区县信息）
            address = poi.get("address", "")
            business_area = poi.get("business_area", "")  # 商圈/区域

            # 构建完整地址
            full_address = address
            if business_area and business_area not in address:
                full_address = f"{business_area}{address}"

            # 随机生成一些数据
            import random
            score = round(random.uniform(4.0, 4.9), 1)
            price = random.choice([128, 158, 198, 228, 268, 298, 358, 398, 458, 528])
            rooms = random.randint(5, 30)
            hotel_type = random.choice(['经济型', '舒适型', '高档型', '豪华型', '商务酒店'])
            star = random.choice([3, 3, 4, 4, 5])
            introduce = f"{name}位于{city}{full_address}，设施齐全，服务周到，是您出差旅游的理想选择。"

            hotels.append({
                'id': hash(name) % 100000,  # 生成临时ID
                'name': name,
                'province': province,
                'city': city,
                'address': full_address,
                'score': score,
                'price': price,
                'rooms': rooms,
                'pic_url': pic_url,
                'intro': introduce,
                'type': hotel_type,
                'star': star,
                'location': poi.get("location", ""),
            })

    except Exception as e:
        print(f"[*] 高德API请求出错: {e}")

    return hotels


def hotel_search(request):
    """搜索城市酒店API - 直接从高德API获取"""
    city_name = request.GET.get('city', '')
    if not city_name:
        return JsonResponse({'message': '0'})

    city_name = city_name.strip()

    # 直接从高德API搜索酒店
    hotels = search_hotels_from_gaode(city_name)

    if hotels:
        return JsonResponse({
            'message': '1',
            'hotels': hotels,
            'is_gaode': True
        })

    # 高德也没有数据时返回空
    return JsonResponse({
        'message': '1',
        'hotels': [],
        'msg': f'暂无 {city_name} 的酒店数据'
    })


def hotel_detail(request):
    """酒店详情页"""
    hotel_id = request.GET.get('id', '')
    hotel_name = request.GET.get('name', '')
    user_id = request.session.get('user_id')

    hotel = None
    if hotel_id:
        hotel = Hotel.objects.filter(HID=hotel_id).first()
    elif hotel_name:
        hotel = Hotel.objects.filter(H_name=hotel_name).first()

    if not hotel:
        return render(request, 'hotel_detail.html', {
            'error': '酒店不存在',
            'user_id': user_id,
            'username': request.session.get('username', ''),
        })

    # 获取该酒店的评论
    comments = []
    if hotel.H_name:
        comments = HotelComment.objects.filter(HC_hotel_name=hotel.H_name).select_related('HC_user')[:20]

    # 检查用户是否已收藏
    is_favorited = False
    if user_id and hotel.H_name:
        is_favorited = HotelFavorite.objects.filter(HF_user_id=user_id, HF_hotel_name=hotel.H_name).exists()

    context = {
        'hotel': hotel,
        'hotel_name': hotel.H_name,
        'hotel_province': hotel.H_province or '',
        'hotel_city': hotel.H_city or '',
        'hotel_address': hotel.H_address or '',
        'hotel_score': hotel.H_score,
        'hotel_price': hotel.H_price,
        'hotel_rooms': hotel.H_rooms,
        'hotel_pic_url': hotel.H_pic_url or '',
        'hotel_introduce': hotel.H_introduce or '',
        'hotel_tel': hotel.H_tel or '',
        'hotel_type': hotel.H_type or '',
        'hotel_star': hotel.H_star,
        'comments': comments,
        'is_favorited': is_favorited,
        'user_id': user_id,
        'username': request.session.get('username', ''),
    }

    return render(request, 'hotel_detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def hotel_add_comment(request):
    """添加酒店评论"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        hotel_name = json_data.get('hotel_name', '')
        content = json_data.get('content', '').strip()

        if not hotel_name:
            return JsonResponse({'message': '0', 'msg': '酒店名称不能为空'})
        if not content:
            return JsonResponse({'message': '0', 'msg': '评论内容不能为空'})
        if len(content) > 500:
            return JsonResponse({'message': '0', 'msg': '评论内容过长'})

        user_id = request.session['user_id']
        user = User.objects.filter(UID=user_id).first()
        if not user:
            return JsonResponse({'message': '0', 'msg': '用户不存在'})

        HotelComment.objects.create(
            HC_hotel_name=hotel_name,
            HC_user=user,
            HC_content=content
        )

        return JsonResponse({'message': '1', 'msg': '评论成功'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def hotel_toggle_favorite(request):
    """切换酒店收藏"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        hotel_name = json_data.get('hotel_name', '')
        pic_url = json_data.get('pic_url', '')

        if not hotel_name:
            return JsonResponse({'message': '0', 'msg': '酒店名称不能为空'})

        user_id = request.session['user_id']
        user = User.objects.filter(UID=user_id).first()
        if not user:
            return JsonResponse({'message': '0', 'msg': '用户不存在'})

        # 检查是否已收藏
        existing = HotelFavorite.objects.filter(HF_user_id=user_id, HF_hotel_name=hotel_name).first()

        if existing:
            existing.delete()
            return JsonResponse({'message': '1', 'msg': '已取消收藏', 'action': 'removed'})
        else:
            HotelFavorite.objects.create(
                HF_hotel_name=hotel_name,
                HF_pic_url=pic_url,
                HF_user=user
            )
            return JsonResponse({'message': '1', 'msg': '收藏成功', 'action': 'added'})

    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


def ticket_index(request):
    """交通票务首页"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')
    return render(request, 'ticket.html', {
        'user_id': user_id,
        'username': username
    })


def hotel_pay(request):
    """酒店支付页面"""
    user_id = request.session.get('user_id')
    if not user_id:
        return render(request, 'login.html', {'error': '请先登录'})

    username = request.session.get('username', '')
    return render(request, 'hotel_pay.html', {
        'user_id': user_id,
        'username': username,
    })


@csrf_exempt
@require_http_methods(["POST"])
def hotel_create_order(request):
    """创建酒店订单"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        hotel_name = json_data.get('hotel_name', '')
        hotel_pic = json_data.get('hotel_pic', '')
        hotel_address = json_data.get('hotel_address', '')
        checkin_date = json_data.get('checkin_date', '')
        checkout_date = json_data.get('checkout_date', '')
        room_count = json_data.get('room_count', 1)
        room_type = json_data.get('room_type', '标准间')
        total_price = json_data.get('total_price', 0)
        payment_method = json_data.get('payment_method', 'alipay')

        if not hotel_name:
            return JsonResponse({'message': '0', 'msg': '酒店名称不能为空'})
        if not checkin_date or not checkout_date:
            return JsonResponse({'message': '0', 'msg': '请选择入住和退房日期'})

        user_id = request.session['user_id']
        user = User.objects.filter(UID=user_id).first()
        if not user:
            return JsonResponse({'message': '0', 'msg': '用户不存在'})

        # 创建订单
        order = HotelOrder.objects.create(
            O_user=user,
            O_hotel_name=hotel_name,
            O_hotel_pic=hotel_pic,
            O_hotel_address=hotel_address,
            O_checkin_date=checkin_date,
            O_checkout_date=checkout_date,
            O_room_count=room_count,
            O_room_type=room_type,
            O_total_price=total_price,
            O_payment_method=payment_method,
            O_status='paid'
        )

        return JsonResponse({
            'message': '1',
            'msg': '订单创建成功',
            'order_id': f'HOT{order.OID:08d}'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def hotel_cancel_order(request):
    """取消酒店订单"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        order_id = json_data.get('order_id', 0)

        user_id = request.session['user_id']
        order = HotelOrder.objects.filter(OID=order_id, O_user_id=user_id).first()

        if not order:
            return JsonResponse({'message': '0', 'msg': '订单不存在'})

        if order.O_status == 'cancelled':
            return JsonResponse({'message': '0', 'msg': '订单已取消'})

        # 更新订单状态
        from django.utils import timezone
        order.O_status = 'cancelled'
        order.O_cancel_time = timezone.now()
        order.save()

        return JsonResponse({'message': '1', 'msg': '订单取消成功'})

    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


def get_user_orders(request):
    """获取用户订单列表API"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        user_id = request.session['user_id']
        status = request.GET.get('status', '')

        orders = HotelOrder.objects.filter(O_user_id=user_id)
        if status:
            orders = orders.filter(O_status=status)

        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.OID,
                'order_id': f'HOT{order.OID:08d}',
                'hotel_name': order.O_hotel_name,
                'hotel_pic': order.O_hotel_pic or '',
                'hotel_address': order.O_hotel_address or '',
                'checkin_date': order.O_checkin_date.strftime('%Y-%m-%d') if order.O_checkin_date else '',
                'checkout_date': order.O_checkout_date.strftime('%Y-%m-%d') if order.O_checkout_date else '',
                'room_count': order.O_room_count,
                'room_type': order.O_room_type or '',
                'total_price': float(order.O_total_price),
                'payment_method': order.O_payment_method,
                'payment_method_name': dict(HotelOrder.PAYMENT_METHODS).get(order.O_payment_method, order.O_payment_method),
                'status': order.O_status,
                'status_name': dict(HotelOrder.STATUS_CHOICES).get(order.O_status, order.O_status),
                'create_time': order.O_create_time.strftime('%Y-%m-%d %H:%M') if order.O_create_time else '',
                'cancel_time': order.O_cancel_time.strftime('%Y-%m-%d %H:%M') if order.O_cancel_time else '',
            })

        return JsonResponse({
            'message': '1',
            'orders': orders_data
        })

    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
def train_search(request):
    """搜索火车票"""
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            departure_date = json_data.get('departureDate', '')
            departure_city = json_data.get('departureCity', '')
            arrival_city = json_data.get('arrivalCity', '')
            train_type = json_data.get('trainType', '高铁')

            if not all([departure_date, departure_city, arrival_city]):
                return JsonResponse({'message': '0', 'msg': '请填写完整信息'})

            # 获取车站编码
            from_station = STATION_CODES.get(departure_city, {'code': departure_city[:2]})
            to_station = STATION_CODES.get(arrival_city, {'code': arrival_city[:2]})
            from_code = from_station.get('code', departure_city[:2])
            to_code = to_station.get('code', arrival_city[:2])

            # 1. 优先使用航讯讯API获取火车票余票
            trains = search_train_from_hangxx(from_code, to_code, departure_date)

            # 2. 如果航讯讯失败，尝试其他API
            if not trains:
                trains = search_train_from_mgtv(departure_city, arrival_city, departure_date)

            if not trains:
                trains = search_train_from_lolimi(departure_city, arrival_city, departure_date, train_type)

            if trains:
                result_trains = process_train_data(trains)
                if result_trains:
                    return JsonResponse({
                        'message': '1',
                        'trains': result_trains,
                        'source': 'api'
                    })

            # 所有API都失败，使用演示数据
            result_trains = generate_demo_trains(departure_city, arrival_city, departure_date)
            return JsonResponse({
                'message': '1',
                'trains': result_trains,
                'source': 'demo'
            })

        except requests.exceptions.Timeout:
            result_trains = generate_demo_trains(
                json_data.get('departureCity', ''),
                json_data.get('arrivalCity', ''),
                json_data.get('departureDate', '')
            )
            return JsonResponse({'message': '1', 'trains': result_trains, 'source': 'demo'})
        except Exception as e:
            import traceback
            traceback.print_exc()
            result_trains = generate_demo_trains(
                json_data.get('departureCity', ''),
                json_data.get('arrivalCity', ''),
                json_data.get('departureDate', '')
            )
            return JsonResponse({'message': '1', 'trains': result_trains, 'source': 'demo'})
    else:
        return JsonResponse({'message': '0', 'msg': '请求方式错误'})


def search_train_from_hangxx(from_code, to_code, date):
    """使用航讯讯API查询火车票余票"""
    try:
        url = 'https://api.hangxx.com/restapi/trainQuery/ticketBalance'
        params = {
            'authCode': 'cdb4ce7b53978f9281cc6e519784380b',
            'leaveCode': from_code,
            'arriveCode': to_code,
            'queryDate': date,
            'ticketType': 'A'
        }
        resp = requests.get(url, params=params, timeout=10, verify=False)
        data = resp.json()
        if data.get('code') == 200:
            trains = data.get('data', [])
            # 处理航讯讯返回的数据格式
            result = []
            for t in trains:
                result.append({
                    'train_code': t.get('station_train_code', ''),
                    'train_type': t.get('train_class_name', ''),
                    'from_station': t.get('from_station_name', ''),
                    'to_station': t.get('to_station_name', ''),
                    'start_time': t.get('start_time', ''),
                    'arrive_time': t.get('arrive_time', ''),
                    'duration': t.get('lishi', ''),
                    'prices': [
                        {'type': '二等座', 'price': t.get('ze_price'), 'left': t.get('ze_num', '无')},
                        {'type': '一等座', 'price': t.get('zy_price'), 'left': t.get('zy_num', '无')},
                        {'type': '商务座', 'price': t.get('swz_price'), 'left': t.get('swz_num', '无')},
                        {'type': '硬座', 'price': None, 'left': t.get('yz_num', '无')},
                        {'type': '软卧', 'price': None, 'left': t.get('rw_num', '无')},
                    ]
                })
            return result
    except Exception as e:
        pass
    return []


def search_train_from_mgtv(departure_city, arrival_city, date):
    """使用mgtv API查询火车票"""
    try:
        url = 'https://tools.mgtv100.com/external/v1/pear/highSpeedTicket'
        params = {
            'from': departure_city,
            'to': arrival_city,
            'time': date
        }
        resp = requests.post(url, data=params, timeout=10, verify=False)
        data = resp.json()
        if data.get('code') == 200:
            return data.get('data', [])
    except Exception:
        pass
    return []


def search_train_from_lolimi(departure_city, arrival_city, departure_date, train_type):
    """使用lolimi API查询火车票"""
    try:
        url = 'https://api.lolimi.cn/API/hc/api'
        params = {
            'type': 'json',
            'departure': departure_city,
            'arrival': arrival_city,
            'date': departure_date,
            'form': train_type
        }
        resp = requests.get(url, params=params, timeout=10, verify=False)
        data = resp.json()
        if data.get('code') == 200:
            return data.get('data', [])
    except:
        pass
    return []


def process_train_data(trains):
    """处理火车数据"""
    result_trains = []
    for train in trains:
        # 处理不同API返回的数据格式
        train_num = train.get('trainNum') or train.get('TrainNumber') or train.get('train_code') or train.get('station_train_code', '')
        depart_station = train.get('departStation') or train.get('start') or train.get('from_station', '') or train.get('from_station_name', '')
        dest_station = train.get('destStation') or train.get('end') or train.get('to_station', '') or train.get('to_station_name', '')
        depart_time = train.get('departTime') or train.get('DepartTime') or train.get('start_time', '')
        arrive_time = train.get('arriveTime') or train.get('ArriveTime') or train.get('end_time') or train.get('arrive_time', '')
        duration = train.get('duration') or train.get('TimeDifference') or train.get('lishi') or train.get('cost_time', '')

        # 获取车站编码
        from_code = ''
        to_code = ''
        for name, info in STATION_CODES.items():
            if depart_station and name in depart_station:
                from_code = info.get('code', '')
                break
            if name == depart_station:
                from_code = info.get('code', '')
                break
        for name, info in STATION_CODES.items():
            if dest_station and name in dest_station:
                to_code = info.get('code', '')
                break
            if name == dest_station:
                to_code = info.get('code', '')
                break

        # 判断车次类型
        if train_num.startswith('G'):
            train_type_name = '高铁'
        elif train_num.startswith('D'):
            train_type_name = '动车'
        elif train_num.startswith('Z'):
            train_type_name = '直达'
        elif train_num.startswith('T'):
            train_type_name = '特快'
        elif train_num.startswith('K'):
            train_type_name = '快速'
        else:
            train_type_name = train.get('train_type') or '火车'

        train_info = {
            'trainNum': train_num,
            'trainType': train_type_name,
            'departStation': depart_station,
            'destStation': dest_station,
            'departTime': depart_time,
            'arriveTime': arrive_time,
            'duration': duration,
            'fromCode': from_code,
            'toCode': to_code,
            'prices': []
        }

        # 处理座位信息
        seats = train.get('prices') or train.get('SeatList') or train.get('seat_list', []) or []
        for seat in seats:
            seat_name = seat.get('seatName') or seat.get('SeatName') or seat.get('seat_name') or seat.get('type', '')
            price = seat.get('price') or seat.get('SeatPrice') or seat.get('seat_price', 0)
            left = seat.get('leftNumber') or seat.get('Seatresidue') or seat.get('left_ticket', 0) or seat.get('left', '有')

            if seat_name and (float(price or 0) > 0 or left in ['有', '若干', '充足']):
                train_info['prices'].append({
                    'type': seat_name,
                    'price': int(float(price)) if price else 0,
                    'left': left
                })

        result_trains.append(train_info)

    return result_trains


def generate_demo_trains(departure_city, arrival_city, departure_date):
    """生成演示用火车数据（当API不可用时）"""
    import random
    from datetime import datetime, timedelta

    # 常用车次
    high_speed_trains = [
        ('G1', 'G'), ('G2', 'G'), ('G3', 'G'), ('G5', 'G'), ('G7', 'G'),
        ('G10', 'G'), ('G12', 'G'), ('G13', 'G'), ('G14', 'G'), ('G17', 'G'),
        ('G21', 'G'), ('G23', 'G'), ('G101', 'G'), ('G102', 'G'), ('G103', 'G'),
        ('G105', 'G'), ('G107', 'G'), ('G109', 'G'), ('G111', 'G'), ('G113', 'G'),
        ('G123', 'G'), ('G125', 'G'), ('G127', 'G'), ('G129', 'G'), ('G131', 'G'),
    ]
    bullet_trains = [
        ('D1', 'D'), ('D2', 'D'), ('D3', 'D'), ('D4', 'D'), ('D5', 'D'),
        ('D101', 'D'), ('D102', 'D'), ('D103', 'D'), ('D105', 'D'),
        ('D201', 'D'), ('D202', 'D'), ('D211', 'D'), ('D215', 'D'),
    ]

    # 随机选择车次
    all_trains = high_speed_trains + bullet_trains
    random.shuffle(all_trains)
    selected_trains = all_trains[:8]

    trains = []
    base_hour = 6  # 起始时间

    for i, (train_num, train_code) in enumerate(selected_trains):
        # 生成发车时间（每隔1-2小时一班）
        hour = base_hour + i * random.randint(1, 2)
        if hour >= 23:
            hour = hour % 24

        minute = random.choice([0, 10, 15, 20, 30, 35, 40, 45, 50, 55])
        depart_time = f"{hour:02d}:{minute:02d}"

        # 计算到达时间（根据距离2-8小时）
        duration_hours = random.randint(2, 8)
        duration_minutes = random.randint(0, 59)
        duration_str = f"{duration_hours}小时{duration_minutes}分"

        # 计算到达时间
        arrive_hour = (hour + duration_hours) % 24
        arrive_minute = (minute + duration_minutes) % 60
        if (minute + duration_minutes) >= 60:
            arrive_hour = (arrive_hour + 1) % 24
        arrive_time = f"{arrive_hour:02d}:{arrive_minute:02d}"

        # 座位类型和价格
        base_price = random.randint(200, 800)
        seats = [
            {'type': '二等座', 'price': base_price, 'left': random.randint(10, 200)},
            {'type': '一等座', 'price': int(base_price * 1.5), 'left': random.randint(5, 80)},
            {'type': '商务座', 'price': int(base_price * 2.5), 'left': random.randint(0, 20)},
        ]

        # 高铁有商务座，动车可能没有
        if train_code == 'D':
            seats = [s for s in seats if s['type'] != '商务座' or random.random() > 0.5]

        # 获取车站编码
        from_info = STATION_CODES.get(departure_city, {'code': departure_city[:2].upper()})
        to_info = STATION_CODES.get(arrival_city, {'code': arrival_city[:2].upper()})

        trains.append({
            'trainNum': train_num,
            'trainType': '高铁' if train_code == 'G' else '动车',
            'departStation': f"{departure_city}站",
            'destStation': f"{arrival_city}站",
            'fromCode': from_info.get('code', ''),
            'toCode': to_info.get('code', ''),
            'departTime': depart_time,
            'arriveTime': arrive_time,
            'duration': duration_str,
            'prices': seats
        })

    # 按发车时间排序
    trains.sort(key=lambda x: x['departTime'])
    return trains


# ============ 航班查询API ============
@csrf_exempt
def flight_search(request):
    """搜索航班"""
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
            departure_city = json_data.get('departureCity', '')
            arrival_city = json_data.get('arrivalCity', '')
            departure_date = json_data.get('departureDate', '')

            if not all([departure_city, arrival_city]):
                return JsonResponse({'message': '0', 'msg': '请填写出发地和目的地'})

            from_code = CITY_AIRPORT_CODES.get(departure_city, departure_city[:3].upper())
            to_code = CITY_AIRPORT_CODES.get(arrival_city, arrival_city[:3].upper())

            # 1. 优先使用航讯讯API获取航班信息
            flights = search_flights_from_hangxx(from_code, to_code, departure_date)

            # 2. 如果航讯讯失败，尝试其他API
            if not flights:
                flights = search_flights_from_api(from_code, to_code, departure_date)

            if flights:
                return JsonResponse({
                    'message': '1',
                    'flights': flights,
                    'source': 'api'
                })
            else:
                flights = generate_demo_flights(departure_city, arrival_city, departure_date)
                return JsonResponse({
                    'message': '1',
                    'flights': flights,
                    'source': 'demo'
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            flights = generate_demo_flights(
                json_data.get('departureCity', ''),
                json_data.get('arrivalCity', ''),
                json_data.get('departureDate', '')
            )
            return JsonResponse({'message': '1', 'flights': flights, 'source': 'demo'})
    else:
        return JsonResponse({'message': '0', 'msg': '请求方式错误'})


def search_flights_from_hangxx(from_code, to_code, date):
    """使用航讯讯API查询航班"""
    try:
        url = 'https://api.hangxx.com/restapi/airQuery/flightTime'
        params = {
            'authCode': 'cdb4ce7b53978f9281cc6e519784380b',
            'leaveCode': from_code,
            'arriveCode': to_code,
            'queryDate': date
        }
        resp = requests.get(url, params=params, timeout=10, verify=False)
        data = resp.json()
        if data.get('code') == 200:
            flight_infos = data.get('flightInfos', [])
            result = []
            for f in flight_infos:
                result.append({
                    'flightNo': f.get('flightNo', ''),
                    'airline': f.get('airlineCompany', ''),
                    'departCity': f.get('leaveCity', ''),
                    'departAirport': f.get('leavePort', ''),
                    'departAirportCode': f.get('leavePortCode', ''),
                    'departTime': f.get('planLeaveTime', '')[-5:] if f.get('planLeaveTime') else '',
                    'arriveCity': f.get('arriveCity', ''),
                    'arriveAirport': f.get('arrivePort', ''),
                    'arriveAirportCode': f.get('arrivePortCode', ''),
                    'arriveTime': f.get('planArriveTime', '')[-5:] if f.get('planArriveTime') else '',
                    'duration': '',  # 航讯讯不直接返回，需要计算
                    'state': f.get('state', ''),
                })
            return result
    except Exception as e:
        pass
    return []


def search_flights_from_api(from_code, to_code, date):
    """从其他API搜索航班"""
    try:
        url = 'https://open.6api.net/flight/getTicket'
        params = {
            'start': from_code,
            'end': to_code
        }
        resp = requests.get(url, params=params, timeout=10, verify=False)
        data = resp.json()
        if data.get('code') == 0:
            return process_flight_data(data.get('data', []))
    except Exception:
        pass
    return []


def process_flight_data(flights_data):
    """处理航班数据"""
    result = []
    for flight in flights_data:
        # 兼容不同API返回格式
        flight_info = {
            'flightNum': flight.get('flightNo') or flight.get('flight_num') or flight.get('airline_code', ''),
            'airline': flight.get('airline') or flight.get('airline_name') or flight.get('airlineCompany', ''),
            'departAirport': flight.get('depart_airport') or flight.get('start_airport', '') or flight.get('departAirport', ''),
            'departCity': flight.get('depart_city') or flight.get('departAirport', '') or flight.get('leavePort', ''),
            'arriveAirport': flight.get('arrive_airport') or flight.get('end_airport', '') or flight.get('arriveAirport', ''),
            'arriveCity': flight.get('arrive_city') or flight.get('arriveAirport', '') or flight.get('arrivePort', ''),
            'departTime': flight.get('depart_time') or flight.get('start_time', '') or flight.get('departTime', ''),
            'arriveTime': flight.get('arrive_time') or flight.get('end_time', '') or flight.get('arriveTime', ''),
            'duration': flight.get('duration') or flight.get('cost_time', '') or flight.get('flightDuration', ''),
            'planeType': flight.get('plane_type') or flight.get('aircraft', ''),
            'state': flight.get('state', ''),
            'prices': []
        }

        # 处理价格舱位
        prices = flight.get('prices') or flight.get('seats') or flight.get('price_list', []) or []
        for price in prices:
            cabin = price.get('cabin') or price.get('seat_type') or price.get('type', '')
            amount = price.get('price') or price.get('ticket_price', 0)
            left = price.get('left') or price.get('left_tickets', 0)

            if cabin and float(amount or 0) > 0:
                flight_info['prices'].append({
                    'type': cabin,
                    'price': int(float(amount)),
                    'left': left
                })

        result.append(flight_info)

    return result


def generate_demo_flights(departure_city, arrival_city, departure_date):
    """生成演示用航班数据"""
    import random

    airlines = [
        ('CA', '中国国航'), ('MU', '东方航空'), ('CZ', '南方航空'),
        ('HU', '海南航空'), ('3U', '四川航空'), ('KN', '中国联航'),
        ('MF', '厦门航空'), ('SC', '山东航空'), ('FM', '上海航空')
    ]

    plane_types = ['波音737', '波音777', '波音787', '空客A320', '空客A330', '空客A350']
    airport_names = {
        'PEK': '首都机场', 'SHA': '虹桥机场', 'CAN': '白云机场', 'SZX': '宝安机场',
        'HGH': '萧山机场', 'CTU': '双流机场', 'CKG': '江北机场', 'XIY': '咸阳机场',
        'NKG': '禄口机场', 'WUH': '天河机场', 'XMN': '高崎机场', 'KMG': '长水机场',
        'TAO': '流亭机场', 'DLC': '周水子机场', 'CSX': '黄花机场', 'CGO': '新郑机场',
        'SHE': '桃仙机场', 'HAK': '美兰机场', 'SYX': '凤凰机场', 'TSN': '滨海机场',
        'HRB': '太平机场', 'URC': '地窝堡机场', 'LHW': '中川机场', 'KWE': '龙洞堡机场'
    }

    from_code = CITY_AIRPORT_CODES.get(departure_city, departure_city[:3].upper())
    to_code = CITY_AIRPORT_CODES.get(arrival_city, arrival_city[:3].upper())
    from_airport = airport_names.get(from_code, f'{departure_city}机场')
    to_airport = airport_names.get(to_code, f'{arrival_city}机场')

    flights = []
    base_hour = 6
    selected_airlines = random.sample(airlines, min(8, len(airlines)))

    for i, (code, name) in enumerate(selected_airlines):
        hour = base_hour + i * random.randint(1, 2)
        if hour >= 22:
            hour = hour % 22
        minute = random.choice([0, 10, 20, 30, 40, 50])

        depart_time = f"{hour:02d}:{minute:02d}"
        duration_hours = random.randint(1, 5)
        duration_minutes = random.randint(0, 59)
        arrive_hour = (hour + duration_hours) % 24
        arrive_minute = (minute + duration_minutes) % 60
        arrive_time = f"{arrive_hour:02d}:{arrive_minute:02d}"

        base_price = random.randint(300, 1200)

        flights.append({
            'flightNum': f"{code}{random.randint(100, 9999)}",
            'airline': name,
            'departAirport': from_airport,
            'departCity': departure_city,
            'departAirportCode': from_code,
            'arriveAirport': to_airport,
            'arriveCity': arrival_city,
            'arriveAirportCode': to_code,
            'departTime': depart_time,
            'arriveTime': arrive_time,
            'duration': f"{duration_hours}小时{duration_minutes}分",
            'planeType': random.choice(plane_types),
            'prices': [
                {'type': '经济舱', 'price': base_price, 'left': random.randint(20, 150)},
                {'type': '商务舱', 'price': int(base_price * 2.5), 'left': random.randint(0, 10)},
                {'type': '头等舱', 'price': int(base_price * 4), 'left': random.randint(0, 4)}
            ]
        })

    flights.sort(key=lambda x: x['departTime'])
    return flights


# ============ 智能行程规划 ============

def trip_index(request):
    """行程规划首页"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')
    return render(request, 'trip.html', {
        'user_id': user_id,
        'username': username
    })


@csrf_exempt
@require_http_methods(["POST"])
def generate_itinerary(request):
    """生成智能行程规划"""
    try:
        json_data = json.loads(request.body)
        city_name = json_data.get('city', '').strip()
        days = int(json_data.get('days', 1))
        start_date = json_data.get('start_date', '')
        preference = json_data.get('preference', '')

        if not city_name:
            return JsonResponse({'message': '0', 'msg': '请选择目的地城市'})

        if days < 1 or days > 7:
            return JsonResponse({'message': '0', 'msg': '游玩天数需在1-7天之间'})

        # 获取该城市的景点
        scenics = ScenicZone.objects.filter(
            SZ_city__Cname=city_name,
            SZ_score__isnull=False
        )

        if not scenics.exists():
            return JsonResponse({'message': '0', 'msg': f'暂无{city_name}的景点数据'})

        # 转换为列表
        scenic_list = []
        for s in scenics:
            scenic_list.append({
                'id': s.SZid,
                'name': s.SZ_name,
                'score': s.SZ_score or 4.5,
                'popularity': s.SZ_popularity or 1000,
                'duration': s.SZ_duration or 3,
                'latitude': s.SZ_latitude,
                'longitude': s.SZ_longitude,
                'address': s.SZ_address or '',
                'time': s.SZ_time or '',
                'pic_url': s.SZ_pic_url or '',
                'tags': s.SZ_tags or '',
                'introduce': s.SZ_introduce or '',
            })

        # 生成行程
        itinerary = plan_itinerary(scenic_list, days, preference)

        return JsonResponse({
            'message': '1',
            'city': city_name,
            'days': days,
            'itinerary': itinerary
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'message': '0', 'msg': f'生成行程失败: {str(e)}'})


def plan_itinerary(scenic_list, days, preference=''):
    """行程规划核心算法 - 优化版，考虑实际交通时间"""
    import math
    from datetime import datetime, timedelta

    # 过滤有效景点（有评分）
    valid_scenics = [s for s in scenic_list if s['score'] > 0]

    if not valid_scenics:
        return []

    # 计算景点评分权重（评分 + 热度归一化）
    max_pop = max(s['popularity'] for s in valid_scenics) if valid_scenics else 1
    for s in valid_scenics:
        pop_score = (s['popularity'] / max_pop) * 2
        s['weight'] = s['score'] + pop_score

    # 根据偏好调整权重
    if preference:
        preference_map = {
            '亲子': ['博物馆', '动物园', '乐园', '公园'],
            '情侣': ['古镇', '海滩', '山水', '夜景'],
            '独自': ['古镇', '山水', '古迹', '博物馆'],
            '摄影': ['山水', '日出', '日落', '自然景观'],
            '美食': ['老街', '古镇', '夜市'],
        }
        preferred_tags = preference_map.get(preference, [])
        for s in valid_scenics:
            tags = s['tags'].split(',') if s['tags'] else []
            if any(t in tags for t in preferred_tags):
                s['weight'] *= 1.3

    # 计算起始日期
    base_date = datetime.now().date()

    # 生成每天的行程
    daily_plan = []
    used_scenics = set()

    # 时间配置（单位：分钟）
    DAILY_START_HOUR = 9      # 每天开始时间
    DAILY_END_HOUR = 20       # 每天结束时间（留有余量）
    LUNCH_START = 720         # 12:00 = 720分钟
    LUNCH_END = 780           # 13:00 = 780分钟
    MIN_TRAVEL_GAP = 10       # 景点间最短间隔（分钟）

    for day in range(1, days + 1):
        day_plan = {
            'day': day,
            'date': (base_date + timedelta(days=day - 1)).strftime('%Y-%m-%d'),
            'scenics': [],
            'total_hours': 0,
            'total_budget': 0,
            'travel_time_total': 0  # 今日总交通时间
        }

        # 每日有效游玩时间：9:00-20:00，减去午餐1小时
        available_minutes = (DAILY_END_HOUR - DAILY_START_HOUR) * 60 - 60  # 720分钟

        current_minutes = DAILY_START_HOUR * 60  # 从9:00开始（540分钟）
        daily_used = []

        # 优先选择未使用的景点
        remaining = [s for s in valid_scenics if id(s) not in used_scenics]

        # 如果景点不够，循环使用
        if len(remaining) < 2:
            remaining = valid_scenics

        # 按权重排序剩余景点
        remaining.sort(key=lambda x: x['weight'], reverse=True)

        # 使用贪心算法选择景点
        while remaining and len(daily_used) < 5:
            # 找最佳下一个景点
            best_idx = find_best_next_scenic(
                daily_used, remaining, current_minutes,
                LUNCH_START, LUNCH_END, available_minutes
            )

            if best_idx is None:
                break

            scenic = remaining.pop(best_idx)
            duration = scenic['duration']

            # 计算交通时间
            travel_minutes = 0
            travel_info = '起点'
            distance_km = 0

            if daily_used:
                prev = daily_used[-1]
                travel_info, distance_km, travel_minutes = get_driving_info(
                    prev.get('longitude'), prev.get('latitude'),
                    scenic.get('longitude'), scenic.get('latitude')
                )

            # 检查午餐时间
            arrival_time = current_minutes + travel_minutes
            if arrival_time < LUNCH_START and arrival_time + duration * 60 > LUNCH_START:
                # 到达时间在午餐前，但会占用午餐时间，需要午餐
                current_minutes = LUNCH_END
                travel_minutes = 0  # 不重复计算
                travel_info = f"午餐后继续"
            elif arrival_time >= LUNCH_START and arrival_time < LUNCH_END:
                # 到达时正在午餐，跳过午餐
                current_minutes = LUNCH_END

            # 检查时间是否足够
            total_needed = travel_minutes + duration * 60
            if current_minutes + total_needed > DAILY_END_HOUR * 60:
                # 放回景点，因为今天时间不够
                remaining.append(scenic)
                break

            # 估算门票（真实数据应从景区API获取）
            ticket_price = int(scenic['score'] * 10 + random.randint(0, 60))

            # 计算时间
            start_time = datetime.strptime(
                f"{int((current_minutes + travel_minutes) // 60)}:{int((current_minutes + travel_minutes) % 60):02d}",
                '%H:%M'
            )
            end_minutes = current_minutes + travel_minutes + duration * 60
            end_time = datetime.strptime(
                f"{int(end_minutes // 60)}:{int(end_minutes % 60):02d}",
                '%H:%M'
            )

            # 格式化交通信息
            travel_info_display = travel_info if travel_info and travel_info != '起点' else ''
            distance_display = f"{distance_km:.1f}公里" if distance_km and distance_km > 0 else ''

            scenic_entry = {
                'id': scenic['id'],
                'name': scenic['name'],
                'duration': duration,
                'start': start_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M'),
                'ticket_price': ticket_price,
                'address': scenic['address'],
                'pic_url': scenic['pic_url'],
                'score': scenic['score'],
                'tags': scenic['tags'],
                'tips': generate_tips(scenic),
                'transport': travel_info_display,
                'distance': distance_display,
                'travel_minutes': int(travel_minutes) if travel_minutes else 0
            }

            day_plan['scenics'].append(scenic_entry)
            day_plan['total_hours'] += duration
            day_plan['total_budget'] += ticket_price
            day_plan['travel_time_total'] += int(travel_minutes) if travel_minutes else 0

            daily_used.append(scenic)
            used_scenics.add(id(scenic))

            # 更新当前时间
            current_minutes = end_minutes + MIN_TRAVEL_GAP
            available_minutes -= (travel_minutes + duration * 60 + MIN_TRAVEL_GAP)

        daily_plan.append(day_plan)

    return daily_plan


def find_best_next_scenic(daily_used, remaining, current_minutes,
                          lunch_start, lunch_end, available_minutes):
    """
    综合评分选择下一个景点
    评分公式: score / (travel_time + visit_time) * weight
    """
    if not remaining:
        return None

    DAILY_END_MINUTES = 20 * 60  # 20:00

    best_idx = None
    best_score = -1

    for i, scenic in enumerate(remaining):
        duration = scenic['duration']
        travel_minutes = 0
        distance_km = 0

        if daily_used:
            _, distance_km, travel_minutes = get_driving_info(
                daily_used[-1].get('longitude'), daily_used[-1].get('latitude'),
                scenic.get('longitude'), scenic.get('latitude')
            )

        arrival = current_minutes + travel_minutes

        # 午餐时间处理
        if arrival < lunch_start and arrival + duration * 60 > lunch_start:
            travel_minutes += (lunch_end - arrival)
            arrival = lunch_end
        elif lunch_start <= arrival < lunch_end:
            arrival = lunch_end

        # 检查时间是否足够
        total_time = travel_minutes + duration * 60
        if current_minutes + total_time > DAILY_END_MINUTES:
            continue

        # 剩余可用时间
        remaining_time = min(available_minutes, DAILY_END_MINUTES - current_minutes)

        # 综合评分：权重高 + 时间合理
        # 评分 = 景点权重 / (总需要时间 / 60)
        time_cost = total_time / 60  # 转换为小时
        score = scenic['weight'] / max(time_cost, 1)

        # 距离惩罚：如果交通时间超过游览时间的50%，降低评分
        if duration > 0 and travel_minutes > duration * 60 * 0.5:
            score *= 0.7

        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx


def get_driving_info(origin_lon, origin_lat, dest_lon, dest_lat):
    """
    获取驾车路线信息（距离和时间）
    优先使用高德API，失败则使用估算
    """
    if not origin_lat or not origin_lon or not dest_lat or not dest_lon:
        # 没有坐标，使用默认估算（城市内景点间距离约5-15公里）
        distance = random.uniform(5, 15)
        # 城市交通：平均2.5分钟/公里 + 步行到上车点3分钟 + 等车5分钟 + 下车步行2分钟
        travel_minutes = int(distance * 2.5) + 10
        return generate_transport_info(distance, origin_lat, dest_lat), distance, travel_minutes

    try:
        # 调用高德API
        url = "https://restapi.amap.com/v3/direction/driving"
        params = {
            "key": "441d40f9bc7eabfc3540e4951f9b681c",
            "origin": f"{origin_lon},{origin_lat}",
            "destination": f"{dest_lon},{dest_lat}",
            "strategy": 10  # 速度优先
        }
        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "1" and data.get("route"):
                paths = data["route"].get("paths", [])
                if paths:
                    path = paths[0]
                    distance = int(path["distance"]) / 1000  # 米转公里
                    duration = int(path["duration"]) / 60  # 秒转分钟
                    return generate_transport_info(distance, origin_lat, dest_lat), distance, duration
    except Exception:
        pass

    # API失败，使用估算（根据直线距离计算）
    distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
    # 直线距离乘以1.5得到实际路程（考虑绕路和红绿灯）
    actual_distance = distance * 1.5
    # 城市交通：平均2.5分钟/公里 + 步行/等车10分钟
    travel_minutes = int(actual_distance * 2.5) + 10
    return generate_transport_info(actual_distance, origin_lat, dest_lat), actual_distance, travel_minutes


def generate_tips(scenic):
    """生成游览小贴士"""
    tips_pool = [
        "建议提前购票，避免排队",
        "景区较大，建议穿舒适的鞋子",
        "带上防晒用品和饮用水",
        "周末人流量较大，建议错峰出行",
        "可以请导游或使用语音导览",
        "注意查看天气预报，合理安排行程",
        "拍照建议在早晨或傍晚光线好的时候",
        "留意景区开放时间，合理规划",
    ]
    return random.choice(tips_pool)


def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（公里），使用简化的Haversine公式"""
    if not lat1 or not lon1 or not lat2 or not lon2:
        return random.uniform(5, 15)

    import math
    R = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def generate_transport_info(distance, from_lat, to_lat):
    """生成交通信息文本"""
    if not distance:
        return "步行前往"

    if distance < 2:
        return f"步行约{distance * 12:.0f}分钟"
    elif distance < 5:
        return f"步行/骑行约{distance * 12:.0f}分钟"
    elif distance < 10:
        return f"打车/公交约{distance * 2.5:.0f}分钟"
    else:
        return f"打车约{distance * 2:.0f}分钟"


@csrf_exempt
@require_http_methods(["POST"])
def save_itinerary(request):
    """保存行程到收藏"""
    if 'user_id' not in request.session:
        return JsonResponse({'message': '0', 'msg': '请先登录'})

    try:
        json_data = json.loads(request.body)
        itinerary_data = json.dumps(json_data.get('itinerary', []), ensure_ascii=False)

        # 可以在这里保存到数据库，目前存储到session
        request.session['saved_itinerary'] = itinerary_data

        return JsonResponse({'message': '1', 'msg': '行程已保存到个人中心'})
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


# ============ 智能AI对话模块 ============

@csrf_exempt
@require_http_methods(["POST"])
def travel_chat(request):
    """
    智能旅游问答API - 基于LangChain的带记忆对话
    
    请求参数：
    - api_key: OpenAI API密钥
    - session_id: 会话ID
    - message: 用户消息
    - model: 模型名称（默认gpt-3.5-turbo）
    - temperature: 创造性参数（0.0-1.0）
    - chat_type: 对话类型（qa=问答，itinerary=行程规划）
    """
    try:
        json_data = json.loads(request.body)
        api_key = json_data.get('api_key', '')
        session_id = json_data.get('session_id', 'default')
        message = json_data.get('message', '')
        model = json_data.get('model', 'gpt-3.5-turbo')
        temperature = float(json_data.get('temperature', 0.7))
        chat_type = json_data.get('chat_type', 'qa')
        
        if not message:
            return JsonResponse({'message': '0', 'msg': '消息内容不能为空'})
        
        if not api_key:
            return JsonResponse({'message': '0', 'msg': '请提供API密钥'})
        
        # 导入并调用LangChain模块
        from .travel_chat import get_travel_response
        from django.middleware.csrf import get_token
        
        response = get_travel_response(
            session_id=session_id,
            user_input=message,
            api_key=api_key,
            chat_type=chat_type,
            model=model,
            temperature=temperature
        )
        
        return JsonResponse({
            'message': '1',
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'message': '0', 'msg': f'服务错误: {str(e)}'})


@csrf_exempt
@require_http_methods(["POST"])
def reset_chat(request):
    """
    重置对话会话
    
    请求参数：
    - session_id: 会话ID
    """
    try:
        json_data = json.loads(request.body)
        session_id = json_data.get('session_id', 'default')
        
        from .travel_chat import reset_travel_chat
        reset_travel_chat(session_id)
        
        return JsonResponse({'message': '1', 'msg': '对话已重置'})
        
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def get_conversation_history(request):
    """
    获取对话历史
    
    请求参数：
    - session_id: 会话ID
    """
    try:
        json_data = json.loads(request.body)
        session_id = json_data.get('session_id', 'default')
        
        from .travel_chat import travel_chat_manager
        history = travel_chat_manager.get_conversation_history(session_id)
        
        return JsonResponse({
            'message': '1',
            'history': history
        })
        
    except Exception as e:
        return JsonResponse({'message': '0', 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def generate_scenic_intro(request):
    """
    AI生成景点简介API
    
    请求参数：
    - api_key: OpenAI API密钥
    - scenic_name: 景点名称
    - city: 所在城市
    - tags: 景点标签（可选）
    - scenic_type: 景点类型（可选）
    - model: 模型名称（可选）
    """
    try:
        json_data = json.loads(request.body)
        api_key = json_data.get('api_key', '')
        scenic_name = json_data.get('scenic_name', '')
        city = json_data.get('city', '')
        tags = json_data.get('tags', '')
        scenic_type = json_data.get('scenic_type', '景点')
        model = json_data.get('model', 'gpt-3.5-turbo')
        
        if not scenic_name:
            return JsonResponse({'message': '0', 'msg': '景点名称不能为空'})
        
        if not city:
            return JsonResponse({'message': '0', 'msg': '请提供景点所在城市'})
        
        if not api_key:
            return JsonResponse({'message': '0', 'msg': '请提供API密钥'})
        
        from .travel_chat import scenic_intro_generator
        
        intro = scenic_intro_generator.generate_intro(
            scenic_name=scenic_name,
            city=city,
            tags=tags,
            scenic_type=scenic_type,
            api_key=api_key,
            model=model
        )
        
        return JsonResponse({
            'message': '1',
            'intro': intro,
            'scenic_name': scenic_name
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'message': '0', 'msg': f'生成失败: {str(e)}'})


def ai_chat_page(request):
    """AI智能对话页面"""
    user_id = request.session.get('user_id')
    username = request.session.get('username', '')
    return render(request, 'ai_chat.html', {
        'user_id': user_id,
        'username': username
    })

