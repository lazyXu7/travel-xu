-- =============================================
-- 旅游信息查询系统数据库清理脚本
-- 执行前请务必备份数据库！
-- =============================================

-- 按依赖顺序删除多余的表
-- 注意：外键约束删除需要按特定顺序

-- 1. 删除 django_admin_log (操作日志)
DROP TABLE IF EXISTS django_admin_log CASCADE;

-- 2. 删除 auth_user 和 auth_group 之间的多对多关系表
DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;
DROP TABLE IF EXISTS auth_user_groups CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;

-- 3. 删除 auth 相关的核心表
DROP TABLE IF EXISTS auth_user CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;

-- 4. 删除 django_content_type (内容类型表，已不需要)
DROP TABLE IF EXISTS django_content_type CASCADE;

-- =============================================
-- 清理后的保留表说明：
-- =============================================
-- 
-- 业务表 (您的项目实际使用的表):
--   - city              城市信息
--   - scenic_zone       景点信息
--   - user              用户信息
--   - comment           景点评论
--   - favorite          景点收藏
--   - hotel             酒店信息
--   - hotel_comment     酒店评论
--   - hotel_favorite    酒店收藏
--   - hotel_order       酒店订单
--   - snack             美食信息 (managed=False，不归Django管理)
--
-- Django运行必需表:
--   - django_migrations 数据库迁移记录
--   - django_session    用户会话
--
-- =============================================

-- 验证清理结果：查看当前所有表
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
