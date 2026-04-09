# -*- coding: utf-8 -*-
"""
初始化演示数据脚本
运行方式: python manage.py shell < init_demo_data.py
或者: python init_demo_data.py (在项目根目录)
"""
import os
import sys
import django
import requests
import time
import random

# 设置Django环境
sys.path.insert(0, 'e:/gra/travel_web-main/travel_web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')
django.setup()

from tweb.models import User, Hotel, HotelOrder, ScenicZone, Comment, Favorite, City, HotelComment, HotelFavorite
from decimal import Decimal

GAODE_API_KEY = "441d40f9bc7eabfc3540e4951f9b681c"

# 热门城市列表
CITIES = [
    "北京", "上海", "广州", "深圳", "杭州",
    "成都", "重庆", "西安", "苏州", "南京",
    "厦门", "青岛", "武汉", "长沙", "昆明"
]


def get_city_location(city_name):
    """获取城市坐标用于排序"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": GAODE_API_KEY, "address": city_name, "output": "JSON"}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        if data.get("status") == "1" and data.get("geocodes"):
            return int(float(data["geocodes"][0]["location"].split(",")[0]))
    except:
        pass
    return CITIES.index(city_name) + 1


def search_attractions_from_gaode(city_name):
    """从高德API搜索景点"""
    url = "https://restapi.amap.com/v3/place/text"
    attractions = []
    keywords_list = ["景点", "公园", "博物馆", "景区", "古迹"]

    for keyword in keywords_list:
        if len(attractions) >= 10:
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
            data = requests.get(url, params=params, timeout=10).json()
            if data.get("status") != "1":
                continue
            for poi in data.get("pois", []):
                if len(attractions) >= 10:
                    break
                name = poi.get("name", "")
                if any(a["name"] == name for a in attractions):
                    continue
                photos = poi.get("photos", [])
                attractions.append({
                    "name": name,
                    "address": poi.get("address", ""),
                    "location": poi.get("location", ""),
                    "rating": poi.get("rating", ""),
                    "intro": poi.get("introduction", "") or f"{name}是{city_name}的热门景点。",
                    "poi_id": poi.get("id", ""),
                    "pic_url": photos[0].get("url", "") if photos else "",
                    "open_time": poi.get("opening_time", "") or "以景区公示为准"
                })
            time.sleep(0.15)
        except:
            pass
    return attractions


def init_demo_data():
    print("=" * 50)
    print("演示数据初始化工具")
    print("=" * 50)

    # 1. 创建/更新城市数据
    print("\n[1/4] 导入城市数据...")
    created_cities = []
    for i, city_name in enumerate(CITIES, 1):
        cum_x = get_city_location(city_name)
        time.sleep(0.1)
        city, created = City.objects.update_or_create(
            Cname=city_name,
            defaults={"Cum_X": cum_x}
        )
        created_cities.append(city)
        print(f"  [{i}/{len(CITIES)}] {'新增' if created else '更新'}: {city_name}")

    print(f"  共 {len(created_cities)} 个城市")

    # 2. 创建演示景点数据（从高德API获取）
    print("\n[2/4] 从高德API导入景点数据...")
    scenic_count = 0
    for i, city_name in enumerate(CITIES, 1):
        city = City.objects.filter(Cname=city_name).first()
        if not city:
            continue

        print(f"\n  [{i}/{len(CITIES)}] {city_name}...")
        attractions = search_attractions_from_gaode(city_name)

        for attr in attractions:
            intro = attr.get("intro", "") or f"{attr['name']}是{city_name}的热门景点。"
            if len(intro) > 300:
                intro = intro[:300]

            _, created = ScenicZone.objects.update_or_create(
                SZ_name=attr["name"],
                defaults={
                    "SZ_city": city,
                    "SZ_score": float(attr.get("rating", 4.5)) if attr.get("rating") else round(random.uniform(4.0, 4.9), 1),
                    "SZ_popularity": random.randint(500, 10000),
                    "SZ_address": attr.get("address", ""),
                    "SZ_time": attr.get("open_time", "以景区公示为准"),
                    "SZ_introduce": intro,
                    "SZ_sIntroduce": intro[:200],
                    "SZ_pic_url": attr.get("pic_url", ""),
                    "SZ_message": 0
                }
            )
            scenic_count += 1
            print(f"    + {attr['name']}")
        time.sleep(0.3)

    print(f"\n  景点导入完成，共 {ScenicZone.objects.count()} 个景点")

    # 3. 创建演示用户
    print("\n[3/4] 创建演示用户...")
    demo_users = [
        {'Uname': 'testuser1', 'Upwd': '123456', 'Uemail': 'test1@example.com', 'jurisdiction': 'user'},
        {'Uname': 'testuser2', 'Upwd': '123456', 'Uemail': 'test2@example.com', 'jurisdiction': 'user'},
        {'Uname': 'testuser3', 'Upwd': '123456', 'Uemail': 'test3@example.com', 'jurisdiction': 'user'},
        {'Uname': 'testuser4', 'Upwd': '123456', 'Uemail': 'test4@example.com', 'jurisdiction': 'user'},
        {'Uname': 'testuser5', 'Upwd': '123456', 'Uemail': 'test5@example.com', 'jurisdiction': 'user'},
    ]

    created_users = []
    for user_data in demo_users:
        if not User.objects.filter(Uname=user_data['Uname']).exists():
            user = User.objects.create(**user_data)
            created_users.append(user)
            print(f"  创建用户: {user.Uname}")
        else:
            user = User.objects.get(Uname=user_data['Uname'])
            created_users.append(user)
            print(f"  用户已存在: {user.Uname}")

    print(f"  共 {len(created_users)} 个用户")

    # 4. 创建演示酒店
    print("\n[4/4] 创建演示酒店...")
    demo_hotels = [
        {
            'H_name': '北京饭店',
            'H_province': '北京',
            'H_city': '北京',
            'H_address': '东城区东长安街33号',
            'H_score': 4.7,
            'H_price': 688,
            'H_rooms': 20,
            'H_pic_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
            'H_introduce': '位于王府井商业区，靠近天安门广场。',
            'H_tel': '010-65137766',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '上海外滩酒店',
            'H_province': '上海',
            'H_city': '上海',
            'H_address': '黄浦区外滩中山东一路',
            'H_score': 4.8,
            'H_price': 888,
            'H_rooms': 15,
            'H_pic_url': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800',
            'H_introduce': '外滩一线江景，五星级服务。',
            'H_tel': '021-63234343',
            'H_type': '豪华型',
            'H_star': 5
        },
        {
            'H_name': '杭州西湖国宾馆',
            'H_province': '浙江',
            'H_city': '杭州',
            'H_address': '西湖区西湖风景名胜区',
            'H_score': 4.9,
            'H_price': 1288,
            'H_rooms': 10,
            'H_pic_url': 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
            'H_introduce': '紧邻西湖，环境优雅。',
            'H_tel': '0571-87997788',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '成都锦江宾馆',
            'H_province': '四川',
            'H_city': '成都',
            'H_address': '锦江区人民南路二段80号',
            'H_score': 4.5,
            'H_price': 588,
            'H_rooms': 25,
            'H_pic_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800',
            'H_introduce': '成都市中心老牌五星级酒店。',
            'H_tel': '028-85506666',
            'H_type': '舒适型',
            'H_star': 5
        },
        {
            'H_name': '广州白天鹅宾馆',
            'H_province': '广东',
            'H_city': '广州',
            'H_address': '荔湾区沙面南街1号',
            'H_score': 4.6,
            'H_price': 788,
            'H_rooms': 18,
            'H_pic_url': 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800',
            'H_introduce': '中国第一家中外合作五星级酒店。',
            'H_tel': '020-81886968',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '深圳华侨城洲际酒店',
            'H_province': '广东',
            'H_city': '深圳',
            'H_address': '南山区华侨城深南大道9009号',
            'H_score': 4.7,
            'H_price': 998,
            'H_rooms': 12,
            'H_pic_url': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800',
            'H_introduce': '靠近世界之窗和欢乐谷。',
            'H_tel': '0755-88888888',
            'H_type': '豪华型',
            'H_star': 5
        },
        {
            'H_name': '西安威斯汀大酒店',
            'H_province': '陕西',
            'H_city': '西安',
            'H_address': '雁塔区雁塔路甲字1号',
            'H_score': 4.6,
            'H_price': 658,
            'H_rooms': 22,
            'H_pic_url': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
            'H_introduce': '位于大雁塔旁，地理位置优越。',
            'H_tel': '029-87888888',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '重庆解放碑威斯汀酒店',
            'H_province': '重庆',
            'H_city': '重庆',
            'H_address': '渝中区解放碑商业中心',
            'H_score': 4.5,
            'H_price': 598,
            'H_rooms': 20,
            'H_pic_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
            'H_introduce': '重庆解放碑核心商圈。',
            'H_tel': '023-63888888',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '苏州园林酒店',
            'H_province': '江苏',
            'H_city': '苏州',
            'H_address': '姑苏区观前街',
            'H_score': 4.8,
            'H_price': 758,
            'H_rooms': 16,
            'H_pic_url': 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
            'H_introduce': '融合苏州园林风格的高端酒店。',
            'H_tel': '0512-67788888',
            'H_type': '高档型',
            'H_star': 5
        },
        {
            'H_name': '南京金陵饭店',
            'H_province': '江苏',
            'H_city': '南京',
            'H_address': '鼓楼区新街口中山路2号',
            'H_score': 4.7,
            'H_price': 698,
            'H_rooms': 24,
            'H_pic_url': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800',
            'H_introduce': '南京地标性五星级酒店。',
            'H_tel': '025-84711888',
            'H_type': '豪华型',
            'H_star': 5
        },
    ]

    created_hotels = []
    for hotel_data in demo_hotels:
        if not Hotel.objects.filter(H_name=hotel_data['H_name']).exists():
            hotel = Hotel.objects.create(**hotel_data)
            created_hotels.append(hotel)
            print(f"  创建酒店: {hotel.H_name}")
        else:
            hotel = Hotel.objects.get(H_name=hotel_data['H_name'])
            created_hotels.append(hotel)
            print(f"  酒店已存在: {hotel.H_name}")

    print(f"  共 {len(created_hotels)} 家酒店")

    # 5. 创建演示评论和收藏
    print("\n[5/6] 创建演示评论和收藏...")
    all_scenics = list(ScenicZone.objects.all()[:50])

    comment_count = 0
    if created_users and all_scenics:
        for i in range(30):
            user = random.choice(created_users)
            scenic = random.choice(all_scenics)
            if not Comment.objects.filter(C_user=user, C_scenic_name=scenic.SZ_name).exists():
                Comment.objects.create(
                    C_user=user,
                    C_scenic_name=scenic.SZ_name,
                    C_content=f"这个地方太棒了！风景优美，值得一去。{random.choice(['', '强烈推荐！', '下次还会再来', '非常满意', '超出预期！'])}"
                )
                comment_count += 1

    print(f"  创建评论: {comment_count} 条")

    favorite_count = 0
    if created_users and all_scenics:
        for i in range(20):
            user = random.choice(created_users)
            scenic = random.choice(all_scenics)
            if not Favorite.objects.filter(F_user=user, F_scenic_name=scenic.SZ_name).exists():
                Favorite.objects.create(
                    F_user=user,
                    F_scenic_name=scenic.SZ_name,
                    F_pic_url=scenic.SZ_pic_url
                )
                favorite_count += 1

    print(f"  创建收藏: {favorite_count} 个")

    # 6. 创建演示订单
    print("\n[6/6] 创建演示订单...")
    payment_methods = ['alipay', 'wechat', 'bankcard']
    room_types = ['标准间', '大床房', '双床房', '套房']
    statuses = ['paid', 'paid', 'paid', 'paid', 'cancelled']

    order_count = 0
    for i in range(30):
        user = random.choice(created_users)
        hotel = random.choice(created_hotels)
        days_ago = random.randint(1, 30)
        checkin_date = django.utils.timezone.now().date() - django.utils.timezone.timedelta(days=days_ago)
        checkout_date = checkin_date + django.utils.timezone.timedelta(days=random.randint(1, 5))

        if not HotelOrder.objects.filter(
            O_user=user,
            O_hotel_name=hotel.H_name,
            O_checkin_date=checkin_date
        ).exists():
            HotelOrder.objects.create(
                O_user=user,
                O_hotel_name=hotel.H_name,
                O_hotel_pic=hotel.H_pic_url,
                O_hotel_address=hotel.H_address,
                O_checkin_date=checkin_date,
                O_checkout_date=checkout_date,
                O_room_count=random.randint(1, 2),
                O_room_type=random.choice(room_types),
                O_total_price=Decimal(str(hotel.H_price * random.randint(1, 3))),
                O_payment_method=random.choice(payment_methods),
                O_status=random.choice(statuses),
                O_create_time=django.utils.timezone.now() - django.utils.timezone.timedelta(days=days_ago, hours=random.randint(0, 12))
            )
            order_count += 1

    print(f"  创建订单: {order_count} 个")

    # 输出统计
    print("\n" + "=" * 50)
    print("数据统计")
    print("=" * 50)
    print(f"城市总数: {City.objects.count()}")
    print(f"景点总数: {ScenicZone.objects.count()}")
    print(f"酒店总数: {Hotel.objects.count()}")
    print(f"用户总数: {User.objects.count()}")
    print(f"评论总数: {Comment.objects.count()}")
    print(f"收藏总数: {Favorite.objects.count()}")
    print(f"订单总数: {HotelOrder.objects.count()}")

    print("\n初始化完成!")
    print("\n测试账号信息:")
    print("  管理员: 用户名 root, 密码 root")
    print("  用户: 用户名 testuser1, 密码 123456")

if __name__ == '__main__':
    init_demo_data()
