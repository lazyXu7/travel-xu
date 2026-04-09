# -*- coding: utf-8 -*-
"""
更新景点扩展数据脚本
从高德API获取景点的经纬度、开放时间、标签等信息
运行方式: python update_scenic_data.py
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

from tweb.models import ScenicZone

GAODE_API_KEY = "441d40f9bc7eabfc3540e4951f9b681c"


def get_geocode(address):
    """根据地址获取经纬度"""
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": GAODE_API_KEY,
        "address": address,
        "output": "JSON"
    }
    try:
        data = requests.get(url, params=params, timeout=10).json()
        if data.get("status") == "1" and data.get("geocodes"):
            location = data["geocodes"][0]["location"].split(",")
            return float(location[0]), float(location[1])
    except:
        pass
    return None, None


def get_scenic_detail_from_gaode(scenic_name):
    """从高德API获取景点详细信息"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": GAODE_API_KEY,
        "keywords": scenic_name,
        "extensions": "all"
    }
    try:
        data = requests.get(url, params=params, timeout=10).json()
        if data.get("status") == "1" and data.get("pois"):
            for poi in data.get("pois", []):
                if poi.get("name") == scenic_name:
                    location = poi.get("location", "")
                    photos = poi.get("photos", [])
                    return {
                        "latitude": float(location.split(",")[1]) if location else None,
                        "longitude": float(location.split(",")[0]) if location else None,
                        "open_time": poi.get("opening_time", ""),
                        "intro": poi.get("introduction", ""),
                        "tag": poi.get("tag", "")
                    }
    except:
        pass
    return None


def classify_tags(score, name):
    """根据景点名称和评分自动分类标签"""
    tags = []
    
    # 基于名称的标签
    keywords = {
        "古镇": ["古镇", "老街", "古街", "古城", "古村"],
        "山水": ["山", "湖", "江", "河", "瀑布", "峡谷", "森林公园"],
        "海滩": ["海", "岛", "沙滩", "海岸"],
        "古迹": ["故宫", "陵", "庙", "寺", "塔", "长城", "古建筑"],
        "主题公园": ["乐园", "欢乐谷", "世界之窗", "动物园", "海洋馆"],
        "博物馆": ["博物馆", "展览馆", "纪念馆"],
        "自然景观": ["日出", "云海", "草原", "沙漠", "湿地"],
    }
    
    for tag, keyword_list in keywords.items():
        if any(kw in name for kw in keyword_list):
            tags.append(tag)
            break
    
    # 基于评分的标签
    if score and score >= 4.8:
        tags.append("5A景区")
    elif score and score >= 4.5:
        tags.append("热门景点")
    
    return ",".join(tags) if tags else "旅游景点"


def estimate_duration(score, name, popularity):
    """估算游览时长（小时）"""
    # 基础时长
    base_duration = 3
    
    # 根据评分调整
    if score and score >= 4.8:
        base_duration += 1
    elif score and score >= 4.5:
        base_duration += 0.5
    
    # 根据热度调整
    if popularity and popularity >= 8000:
        base_duration += 1
    elif popularity and popularity >= 5000:
        base_duration += 0.5
    
    # 根据名称关键词调整
    if any(kw in name for kw in ["故宫", "长城", "陵", "园"]):
        base_duration += 1
    if any(kw in name for kw in ["博物馆", "展览"]):
        base_duration = 2
    
    return min(int(base_duration), 8)  # 最大8小时


def update_scenic_data():
    """更新所有景点的扩展数据"""
    print("=" * 50)
    print("景点数据更新工具")
    print("=" * 50)
    
    # 获取所有景点
    scenics = ScenicZone.objects.all()
    total = scenics.count()
    updated = 0
    failed = 0
    
    print(f"\n共 {total} 个景点需要更新...")
    
    for i, scenic in enumerate(scenics, 1):
        name = scenic.SZ_name or ""
        city = scenic.SZ_city.Cname if scenic.SZ_city else ""
        
        print(f"\n[{i}/{total}] {name} ({city})...")
        
        # 获取高德API数据
        detail = get_scenic_detail_from_gaode(name)
        
        if detail:
            # 更新经纬度
            if detail.get("latitude") and detail.get("longitude"):
                scenic.SZ_latitude = detail["latitude"]
                scenic.SZ_longitude = detail["longitude"]
                print(f"  位置: ({detail['latitude']}, {detail['longitude']})")
            
            # 更新开放时间
            if detail.get("open_time"):
                scenic.SZ_time = detail["open_time"]
                print(f"  开放时间: {detail['open_time']}")
            
            # 更新介绍
            if detail.get("intro"):
                scenic.SZ_introduce = detail["intro"]
            
            # 更新标签
            tags = classify_tags(scenic.SZ_score, name)
            scenic.SZ_tags = tags
            print(f"  标签: {tags}")
        else:
            # 如果API没有数据，使用默认数据
            scenic.SZ_tags = classify_tags(scenic.SZ_score, name)
            
            # 尝试从地址获取经纬度
            if scenic.SZ_address and (not scenic.SZ_latitude or not scenic.SZ_longitude):
                lng, lat = get_geocode(f"{city}{scenic.SZ_address}")
                if lng and lat:
                    scenic.SZ_longitude = lng
                    scenic.SZ_latitude = lat
                    print(f"  位置(地址解析): ({lat}, {lng})")
        
        # 更新游览时长
        scenic.SZ_duration = estimate_duration(scenic.SZ_score, name, scenic.SZ_popularity)
        print(f"  游览时长: {scenic.SZ_duration}小时")
        
        scenic.save()
        updated += 1
        
        # 避免API限流
        time.sleep(0.2)
    
    print("\n" + "=" * 50)
    print(f"更新完成!")
    print(f"  成功更新: {updated} 个")
    print(f"  更新失败: {failed} 个")
    print("=" * 50)


if __name__ == '__main__':
    update_scenic_data()
