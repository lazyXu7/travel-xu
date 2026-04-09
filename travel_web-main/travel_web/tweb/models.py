from django.db import models


# Create your models here.
class City(models.Model):
    Cid = models.AutoField(primary_key=True)
    Cname = models.CharField(max_length=10, unique=True, null=False)
    Cum_X = models.IntegerField(null=False)

    class Meta:
        db_table = 'city'


class Snack(models.Model):
    Sid = models.AutoField(primary_key=True)
    S_name = models.CharField(max_length=255, null=True)
    S_city = models.ForeignKey('City', to_field='Cname', on_delete=models.RESTRICT, db_column='S_city', null=True)
    S_pic_url = models.CharField(max_length=255, null=True)
    S_Introduce = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'snack'


class ScenicZone(models.Model):
    """景点模型"""
    SZid = models.AutoField(primary_key=True)
    SZ_name = models.CharField(max_length=50, null=True)
    SZ_city = models.ForeignKey(City, to_field='Cname', on_delete=models.RESTRICT, db_column='SZ_city', null=True)
    SZ_message = models.IntegerField(null=True)
    SZ_score = models.FloatField(null=True)
    SZ_popularity = models.IntegerField(null=True)
    SZ_address = models.TextField(null=True)
    SZ_time = models.CharField(max_length=100, null=True)
    SZ_introduce = models.TextField(null=True)
    SZ_pic_url = models.CharField(max_length=255, null=True)
    SZ_sIntroduce = models.TextField(null=True)
    # 行程规划新增字段
    SZ_latitude = models.FloatField(null=True, blank=True)  # 纬度
    SZ_longitude = models.FloatField(null=True, blank=True)  # 经度
    SZ_duration = models.IntegerField(default=3)  # 建议游览时长（小时）
    SZ_tags = models.CharField(max_length=255, null=True, blank=True)  # 景点标签，逗号分隔

    class Meta:
        db_table = 'scenic_zone'


class User(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    UID = models.AutoField(primary_key=True)
    Uname = models.CharField(max_length=20, unique=True, null=False)
    Uemail = models.CharField(max_length=255, unique=True, null=True)
    Upwd = models.CharField(max_length=16, null=False)
    jurisdiction = models.CharField(max_length=20, null=False)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    avatar = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'user'


class Comment(models.Model):
    """景点评论"""
    CID = models.AutoField(primary_key=True)
    C_scenic_name = models.CharField(max_length=100, null=False)
    C_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    C_content = models.TextField(null=False)
    C_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'
        ordering = ['-C_time']


class Favorite(models.Model):
    """景点收藏"""
    FID = models.AutoField(primary_key=True)
    F_scenic_name = models.CharField(max_length=100, null=False)
    F_pic_url = models.CharField(max_length=255, null=True)
    F_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    F_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorite'
        ordering = ['-F_time']


class Hotel(models.Model):
    """酒店模型"""
    HID = models.AutoField(primary_key=True)
    H_name = models.CharField(max_length=100, null=False)  # 酒店名称
    H_province = models.CharField(max_length=50, null=True)  # 省份
    H_city = models.CharField(max_length=50, null=True)  # 城市
    H_address = models.CharField(max_length=255, null=True)  # 地址
    H_score = models.FloatField(default=4.0)  # 评分
    H_price = models.IntegerField(null=True)  # 价格
    H_rooms = models.IntegerField(default=10)  # 剩余房源
    H_pic_url = models.CharField(max_length=500, null=True)  # 图片
    H_introduce = models.TextField(null=True)  # 介绍
    H_tel = models.CharField(max_length=50, null=True)  # 电话
    H_type = models.CharField(max_length=50, null=True)  # 酒店类型（经济型/豪华型等）
    H_star = models.IntegerField(default=3)  # 星级

    class Meta:
        db_table = 'hotel'
        ordering = ['-H_score', '-HID']


class HotelComment(models.Model):
    """酒店评论"""
    HCID = models.AutoField(primary_key=True)
    HC_hotel_name = models.CharField(max_length=100, null=False)
    HC_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_comments')
    HC_content = models.TextField(null=False)
    HC_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotel_comment'
        ordering = ['-HC_time']


class HotelFavorite(models.Model):
    """酒店收藏"""
    HFID = models.AutoField(primary_key=True)
    HF_hotel_name = models.CharField(max_length=100, null=False)
    HF_pic_url = models.CharField(max_length=255, null=True)
    HF_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_favorites')
    HF_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hotel_favorite'
        ordering = ['-HF_time']


class HotelOrder(models.Model):
    """酒店订单"""
    STATUS_CHOICES = [
        ('paid', '已支付'),
        ('cancelled', '已取消'),
    ]
    PAYMENT_METHODS = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('bankcard', '银行卡'),
    ]

    OID = models.AutoField(primary_key=True)  # 订单ID
    O_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_orders')  # 用户
    O_hotel_name = models.CharField(max_length=100, null=False)  # 酒店名称
    O_hotel_pic = models.CharField(max_length=500, null=True)  # 酒店图片
    O_hotel_address = models.CharField(max_length=255, null=True)  # 酒店地址
    O_checkin_date = models.DateField(null=False)  # 入住日期
    O_checkout_date = models.DateField(null=False)  # 退房日期
    O_room_count = models.IntegerField(default=1)  # 房间数量
    O_room_type = models.CharField(max_length=50, null=True)  # 房间类型
    O_total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 总价
    O_payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='alipay')  # 支付方式
    O_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')  # 订单状态
    O_create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    O_cancel_time = models.DateTimeField(null=True, blank=True)  # 取消时间

    class Meta:
        db_table = 'hotel_order'
        ordering = ['-O_create_time']
