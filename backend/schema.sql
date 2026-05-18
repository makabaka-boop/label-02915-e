-- 商品管理系统 数据库初始化脚本
-- MySQL 8.0+ / charset: utf8mb4

CREATE DATABASE IF NOT EXISTS product_mgmt DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE product_mgmt;

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname    VARCHAR(50)  NOT NULL DEFAULT '',
    avatar      VARCHAR(255) NOT NULL DEFAULT '',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1=启用 0=禁用',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 分类表
CREATE TABLE IF NOT EXISTS category (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1=启用 0=禁用',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 商品表
CREATE TABLE IF NOT EXISTS product (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category_id BIGINT       NOT NULL,
    price       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock       INT          NOT NULL DEFAULT 0,
    image       VARCHAR(500) NOT NULL DEFAULT '',
    description TEXT,
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1=上架 0=下架',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES category(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT       DEFAULT NULL,
    username    VARCHAR(50)  NOT NULL DEFAULT '',
    module      VARCHAR(50)  NOT NULL DEFAULT '',
    action      VARCHAR(50)  NOT NULL DEFAULT '',
    method      VARCHAR(200) NOT NULL DEFAULT '',
    ip          VARCHAR(50)  NOT NULL DEFAULT '',
    params      TEXT,
    result      TEXT,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_module (module),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 测试数据
-- ============================================================

-- 用户 (密码经前端 SHA-256 后再 bcrypt 存储)
-- admin / admin123  (sha256 → bcrypt)
-- zhangsan / test123
-- lisi / test123
-- wangwu / test123
-- zhaoliu / test123 (禁用状态)
INSERT INTO sys_user (username, password_hash, nickname, status, created_at) VALUES
('admin',    '$2b$12$3Yi3ny7pb9K2h07LGKQ5Y.9jzqd/z2U2rmVGysmKSITAqw8w8.JZG', '超级管理员', 1, '2026-01-01 09:00:00');

-- 分类
INSERT INTO category (name, sort_order, status, created_at) VALUES
('电子产品', 1, 1, '2026-01-01 09:00:00'),
('服装鞋帽', 2, 1, '2026-01-01 09:00:00'),
('食品饮料', 3, 1, '2026-01-01 09:00:00'),
('家居用品', 4, 1, '2026-01-01 09:00:00'),
('图书文具', 5, 1, '2026-01-05 10:00:00'),
('运动户外', 6, 1, '2026-01-05 10:00:00'),
('美妆个护', 7, 1, '2026-01-10 11:00:00'),
('母婴用品', 8, 0, '2026-01-15 14:00:00');

-- 商品 (category_id 对应上面的分类)
INSERT INTO product (name, category_id, price, stock, image, description, status, created_at) VALUES
-- 电子产品 (category_id=1)
('iPhone 16 Pro Max 256GB',     1, 9999.00,  58,  '/uploads/product_01.png', '苹果最新旗舰手机，A18 Pro芯片，钛金属边框', 1, '2026-01-10 09:00:00'),
('MacBook Pro 14英寸 M4',       1, 14999.00, 32,  '/uploads/product_02.png', 'Apple M4芯片，16GB内存，512GB固态硬盘',      1, '2026-01-10 09:05:00'),
('AirPods Pro 3',               1, 1899.00,  120, '/uploads/product_03.png', '主动降噪，自适应音频，USB-C充电',            1, '2026-01-12 10:00:00'),
('iPad Air 6 11英寸',           1, 4799.00,  45,  '/uploads/product_04.png', 'M3芯片，Liquid Retina显示屏',               1, '2026-01-15 11:00:00'),
('Sony WH-1000XM6 头戴耳机',   1, 2499.00,  78,  '/uploads/product_05.png', '行业领先降噪，30小时续航',                   1, '2026-01-18 14:00:00'),
('小米14 Ultra',                1, 5999.00,  0,   '/uploads/product_06.png', '骁龙8 Gen3，徕卡光学镜头，已售罄',           0, '2026-01-20 09:30:00'),

-- 服装鞋帽 (category_id=2)
('优衣库轻薄羽绒服',            2, 499.00,   200, '/uploads/product_07.png', '轻便保暖，可收纳设计，多色可选',             1, '2026-01-11 10:00:00'),
('Nike Air Force 1 白色',       2, 799.00,   150, '/uploads/product_08.png', '经典款休闲运动鞋，百搭白色',                 1, '2026-01-11 10:30:00'),
('Levi''s 501 经典直筒牛仔裤',  2, 599.00,   88,  '/uploads/product_09.png', '经典版型，100%纯棉牛仔面料',                 1, '2026-01-14 09:00:00'),
('阿迪达斯三叶草卫衣',          2, 449.00,   65,  '/uploads/product_10.png', '经典三叶草Logo，纯棉面料，宽松版型',         1, '2026-01-16 15:00:00'),
('波司登极寒系列羽绒服',        2, 1299.00,  5,   '/uploads/product_11.png', '零下30度抗寒，鹅绒填充',                     0, '2026-02-01 09:00:00'),

-- 食品饮料 (category_id=3)
('三只松鼠坚果大礼包',          3, 128.00,   500, '/uploads/product_12.png', '每日坚果混合装，10袋/盒',                    1, '2026-01-12 08:00:00'),
('农夫山泉矿泉水 550ml*24瓶',  3, 36.00,    800, '/uploads/product_13.png', '天然矿泉水，整箱装',                         1, '2026-01-12 08:30:00'),
('瑞幸咖啡挂耳包 精品系列',     3, 89.00,    320, '/uploads/product_14.png', '现磨挂耳咖啡，10包装',                       1, '2026-01-15 10:00:00'),
('良品铺子猪肉脯 200g',         3, 39.90,    450, '/uploads/product_15.png', '靖江特产，蜜汁味猪肉脯',                     1, '2026-01-18 11:00:00'),
('元气森林气泡水 480ml*15瓶',   3, 59.00,    600, '/uploads/product_16.png', '0糖0脂0卡，白桃味',                          1, '2026-01-20 14:00:00'),

-- 家居用品 (category_id=4)
('小米智能台灯 Pro',            4, 249.00,   180, '/uploads/product_17.png', 'Ra95高显色，无蓝光危害，APP控制',             1, '2026-01-13 09:00:00'),
('无印良品懒人沙发',            4, 599.00,   40,  '/uploads/product_18.png', '舒适填充颗粒，可拆洗外套',                   1, '2026-01-14 10:00:00'),
('戴森V15吸尘器',               4, 4490.00,  22,  '/uploads/product_19.png', '激光探测灰尘，整机HEPA过滤',                 1, '2026-01-17 11:00:00'),
('南极人四件套纯棉床品',        4, 199.00,   300, '/uploads/product_20.png', '全棉磨毛，1.8m床适用',                       1, '2026-01-19 08:00:00'),

-- 图书文具 (category_id=5)
('三体（全三册）',              5, 68.00,    250, '/uploads/product_21.png', '刘慈欣科幻巨著，雨果奖获奖作品',             1, '2026-01-20 09:00:00'),
('得力中性笔 0.5mm 黑色 12支', 5, 15.90,    1000,'/uploads/product_22.png', '顺滑书写，速干不晕染',                       1, '2026-01-20 09:30:00'),
('Moleskine经典笔记本',         5, 158.00,   60,  '/uploads/product_23.png', '硬面精装，A5尺寸，点阵内页',                 1, '2026-01-22 10:00:00'),

-- 运动户外 (category_id=6)
('迪卡侬跑步机 T520B',         6, 2999.00,  15,  '/uploads/product_24.png', '家用折叠跑步机，减震跑带',                   1, '2026-01-25 09:00:00'),
('李宁羽毛球拍 风刃900',       6, 899.00,   42,  '/uploads/product_25.png', '全碳素球拍，进攻型',                         1, '2026-01-25 10:00:00'),
('骆驼户外冲锋衣',              6, 399.00,   90,  '/uploads/product_26.png', '三合一可拆卸，防风防水',                     1, '2026-01-28 11:00:00'),

-- 美妆个护 (category_id=7)
('兰蔻小黑瓶精华 50ml',        7, 760.00,   70,  '/uploads/product_27.png', '第二代小黑瓶，微生态护肤',                   1, '2026-02-01 09:00:00'),
('欧莱雅男士洁面乳',            7, 49.90,    400, '/uploads/product_28.png', '控油清洁，温和不紧绷',                       1, '2026-02-01 10:00:00'),
('SK-II神仙水 230ml',           7, 1190.00,  35,  '/uploads/product_29.png', '经典护肤精华露，改善肤质',                   1, '2026-02-05 14:00:00');

-- 操作日志 (仅商品和分类模块)
INSERT INTO operation_log (user_id, username, module, action, method, ip, created_at) VALUES
(1, 'admin',    '分类', '新增', 'POST /api/categories',       '192.168.1.100', '2026-01-10 09:05:00'),
(1, 'admin',    '分类', '新增', 'POST /api/categories',       '192.168.1.100', '2026-01-10 09:06:00'),
(1, 'admin',    '分类', '新增', 'POST /api/categories',       '192.168.1.100', '2026-01-10 09:07:00'),
(1, 'admin',    '分类', '新增', 'POST /api/categories',       '192.168.1.100', '2026-01-10 09:08:00'),
(1, 'admin',    '商品', '新增', 'POST /api/products',         '192.168.1.100', '2026-01-10 09:10:00'),
(1, 'admin',    '商品', '新增', 'POST /api/products',         '192.168.1.100', '2026-01-10 09:15:00'),
(1, 'admin',    '商品', '新增', 'POST /api/products',         '192.168.1.100', '2026-01-10 09:20:00'),
(2, 'zhangsan', '商品', '新增', 'POST /api/products',         '192.168.1.101', '2026-01-15 08:45:00'),
(2, 'zhangsan', '商品', '修改', 'PUT /api/products/3',        '192.168.1.101', '2026-01-15 09:00:00'),
(2, 'zhangsan', '商品', '删除', 'DELETE /api/products/99',    '192.168.1.101', '2026-01-15 09:10:00'),
(3, 'lisi',     '分类', '修改', 'PUT /api/categories/2',      '192.168.1.102', '2026-01-20 10:15:00'),
(3, 'lisi',     '商品', '新增', 'POST /api/products',         '192.168.1.102', '2026-01-20 10:30:00'),
(1, 'admin',    '商品', '修改', 'PUT /api/products/6',        '192.168.1.100', '2026-02-01 08:20:00'),
(4, 'wangwu',   '商品', '新增', 'POST /api/products',         '10.0.0.50',     '2026-02-10 09:30:00'),
(4, 'wangwu',   '分类', '新增', 'POST /api/categories',       '10.0.0.50',     '2026-02-10 10:00:00'),
(1, 'admin',    '商品', '新增', 'POST /api/products',         '192.168.1.100', '2026-02-20 09:15:00'),
(1, 'admin',    '商品', '修改', 'PUT /api/products/10',       '192.168.1.100', '2026-02-20 09:30:00');
