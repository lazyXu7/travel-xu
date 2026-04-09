"""
清空所有用户数据的脚本
运行方式: python manage.py shell < clear_users.py
或者直接运行: python clear_users.py
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_web.settings')
django.setup()

from tweb.models import User, Comment, Favorite

def clear_all_data():
    """清空所有用户相关数据"""
    print("[*] 开始清空数据...")
    print("=" * 50)

    # 统计
    user_count = User.objects.count()
    comment_count = Comment.objects.count()
    favorite_count = Favorite.objects.count()

    print(f"\n[*] 当前数据统计:")
    print(f"  - 用户数量: {user_count}")
    print(f"  - 评论数量: {comment_count}")
    print(f"  - 收藏数量: {favorite_count}")

    # 清空数据
    print("\n[*] 正在清空数据...")
    Favorite.objects.all().delete()
    Comment.objects.all().delete()
    User.objects.all().delete()

    print("\n[*] 数据清空完成！")
    print(f"已删除: {user_count} 个用户, {comment_count} 条评论, {favorite_count} 条收藏")

    # 清空 session 表
    from django.contrib.sessions.models import Session
    session_count = Session.objects.count()
    Session.objects.all().delete()
    print(f"已删除: {session_count} 个 session 记录")

    print("=" * 50)
    print("[*] 所有数据已清空，可以重新注册新账号了！")
    print("=" * 50)

if __name__ == "__main__":
    clear_all_data()
