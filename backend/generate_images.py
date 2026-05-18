"""为商品生成专业展示图

每个商品根据类型绘制独特的产品插画（手机、笔记本电脑、瓶装饮料等），
搭配品牌配色与分类标签，风格接近电商白底主图。
"""
import os
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
FORCE = os.environ.get("FORCE_REGENERATE", "0") == "1"
VERSION = "v4"
VERSION_FILE = f".generated_{VERSION}"
W, H = 400, 400


# ════════════════════════════════════════════
# 字体 / 颜色工具
# ════════════════════════════════════════════

def _load_font(size, bold=False):
    names = (
        ["NotoSansCJK-Bold.ttc", "DejaVuSans-Bold.ttf"]
        if bold else
        ["NotoSansCJK-Regular.ttc", "DejaVuSans.ttf"]
    )
    dirs = [
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/opentype/noto",
        "/usr/share/fonts/noto-cjk",
        "/usr/share/fonts/truetype/dejavu",
        "/System/Library/Fonts",
    ]
    for d in dirs:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()


def font(size):
    return _load_font(size, bold=False)


def bold(size):
    return _load_font(size, bold=True)


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lighten(c, f=0.3):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c)


def darken(c, f=0.3):
    return tuple(max(0, int(v * (1 - f))) for v in c)


def alpha_blend(fg, bg, alpha):
    return tuple(int(f * alpha + b * (1 - alpha)) for f, b in zip(fg, bg))


# ════════════════════════════════════════════
# 画布工具
# ════════════════════════════════════════════

def new_canvas(cat_color):
    """创建带有轻柔渐变背景的画布"""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    top = (250, 250, 252)
    bot = lighten(cat_color, 0.92)
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img, draw


def add_text(draw, name, brand, brand_color, cat_name, cat_color):
    """在画布底部添加商品名、品牌、分类标签"""
    # 商品名（最多两行）
    nf = bold(18)
    lines = textwrap.wrap(name, width=16)[:2]
    ty = 318
    for ln in lines:
        try:
            bb = draw.textbbox((0, 0), ln, font=nf)
            tw = bb[2] - bb[0]
        except Exception:
            tw = len(ln) * 18
        draw.text(((W - tw) // 2, ty), ln, fill=(30, 30, 30), font=nf)
        ty += 24

    # 品牌（左下）
    bf = font(12)
    draw.ellipse([14, 374, 22, 382], fill=brand_color)
    draw.text((26, 371), brand, fill=brand_color, font=bf)

    # 分类标签（右下）
    lf = font(11)
    try:
        bb = draw.textbbox((0, 0), cat_name, font=lf)
        lw = bb[2] - bb[0]
    except Exception:
        lw = len(cat_name) * 11
    lx = W - lw - 18
    draw.rounded_rectangle([lx - 6, 370, lx + lw + 6, 386], radius=8,
                           fill=lighten(cat_color, 0.82))
    draw.text((lx, 372), cat_name, fill=cat_color, font=lf)


def oval_shadow(img, bbox, blur=8, opacity=0.12):
    """在指定区域下方绘制椭圆投影"""
    shadow = Image.new("RGB", img.size, (255, 255, 255))
    sd = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = bbox
    sy = y1 - 5
    sd.ellipse([x0 + 10, sy, x1 - 10, sy + 20],
               fill=tuple(int(255 * (1 - opacity)) for _ in range(3)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    from PIL import ImageChops
    img_arr = img.copy()
    return ImageChops.multiply(img_arr, shadow)


# ════════════════════════════════════════════
# 产品绘制函数
# ════════════════════════════════════════════

def draw_phone(draw, img, color, accent):
    """智能手机"""
    cx, cy = 200, 160
    bw, bh = 90, 170
    x0, y0 = cx - bw // 2, cy - bh // 2
    x1, y1 = cx + bw // 2, cy + bh // 2
    # 阴影
    draw.rounded_rectangle([x0 + 4, y0 + 6, x1 + 4, y1 + 6], radius=18,
                           fill=lighten(color, 0.7))
    # 机身
    draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=color,
                           outline=darken(color, 0.15), width=2)
    # 屏幕
    sm = 6
    scr_color = lighten(accent, 0.75)
    draw.rounded_rectangle([x0 + sm, y0 + 16, x1 - sm, y1 - 10],
                           radius=10, fill=scr_color)
    # 屏幕渐变光泽
    for i in range(30):
        t = i / 30
        c = alpha_blend((255, 255, 255), scr_color, 0.15 * (1 - t))
        draw.line([(x0 + sm, y0 + 16 + i), (x1 - sm, y0 + 16 + i)], fill=c)
    # 灵动岛
    iw = 30
    draw.rounded_rectangle([cx - iw // 2, y0 + 6, cx + iw // 2, y0 + 13],
                           radius=4, fill=darken(color, 0.5))
    # 摄像头模组（背面暗示）
    cam_x, cam_y = x1 - 22, y0 + 28
    for dx, dy in [(0, 0), (12, 0), (6, 12)]:
        draw.ellipse([cam_x + dx - 5, cam_y + dy - 5,
                      cam_x + dx + 5, cam_y + dy + 5],
                     fill=darken(color, 0.35),
                     outline=darken(color, 0.5), width=1)


def draw_laptop(draw, img, color, accent):
    """笔记本电脑"""
    cx, cy = 200, 155
    # 屏幕部分
    sw, sh = 160, 110
    sx0, sy0 = cx - sw // 2, cy - sh // 2 - 15
    sx1, sy1 = cx + sw // 2, cy + sh // 2 - 15
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=6, fill=color,
                           outline=darken(color, 0.2), width=2)
    # 屏幕内容
    draw.rounded_rectangle([sx0 + 8, sy0 + 8, sx1 - 8, sy1 - 4], radius=3,
                           fill=lighten(accent, 0.8))
    # 屏幕光泽
    for i in range(25):
        t = i / 25
        c = alpha_blend((255, 255, 255), lighten(accent, 0.8), 0.12 * (1 - t))
        draw.line([(sx0 + 8, sy0 + 8 + i), (sx1 - 8, sy0 + 8 + i)], fill=c)
    # Logo
    draw.ellipse([cx - 6, (sy0 + sy1) // 2 - 6, cx + 6, (sy0 + sy1) // 2 + 6],
                 fill=lighten(accent, 0.65))
    # 键盘底座
    bw, bh_k = 180, 12
    bx0 = cx - bw // 2
    by0 = sy1
    draw.polygon([(bx0, by0), (bx0 + bw, by0),
                  (bx0 + bw + 8, by0 + bh_k), (bx0 - 8, by0 + bh_k)],
                 fill=darken(color, 0.1), outline=darken(color, 0.25))
    # 触控板线
    draw.rounded_rectangle([cx - 25, by0 + 2, cx + 25, by0 + bh_k - 2],
                           radius=2, outline=darken(color, 0.2), width=1)


def draw_earbuds(draw, img, color, accent):
    """耳机充电盒 + 耳塞"""
    cx, cy = 200, 155
    # 充电盒
    cw, ch = 80, 60
    x0, y0 = cx - cw // 2, cy - 10
    x1, y1 = x0 + cw, y0 + ch
    # 盒身阴影
    draw.rounded_rectangle([x0 + 3, y0 + 4, x1 + 3, y1 + 4], radius=20,
                           fill=lighten(color, 0.65))
    # 盒身
    draw.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(245, 245, 245),
                           outline=darken(color, 0.05), width=2)
    # 盒盖线
    draw.arc([x0, y0 - 5, x1, y0 + 25], 0, 180, fill=(200, 200, 200), width=1)
    # 指示灯
    draw.ellipse([cx - 3, y0 + ch // 2 - 2, cx + 3, y0 + ch // 2 + 2],
                 fill=lighten(accent, 0.4))
    # 左耳塞
    for ox in [-32, 32]:
        ex = cx + ox
        ey = cy - 35
        draw.ellipse([ex - 12, ey - 12, ex + 12, ey + 12],
                     fill=(240, 240, 240), outline=(200, 200, 200), width=1)
        draw.ellipse([ex - 5, ey - 5, ex + 5, ey + 5],
                     fill=(180, 180, 180))
        # 耳机柄
        stem_x = ex + (3 if ox > 0 else -3)
        draw.rounded_rectangle([stem_x - 3, ey + 8, stem_x + 3, ey + 28],
                               radius=3, fill=(235, 235, 235),
                               outline=(200, 200, 200), width=1)


def draw_tablet(draw, img, color, accent):
    """平板电脑"""
    cx, cy = 200, 155
    tw, th = 160, 120
    x0, y0 = cx - tw // 2, cy - th // 2
    x1, y1 = cx + tw // 2, cy + th // 2
    # 阴影
    draw.rounded_rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], radius=12,
                           fill=lighten(color, 0.7))
    # 机身
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=color,
                           outline=darken(color, 0.15), width=2)
    # 屏幕
    m = 8
    scr = lighten(accent, 0.78)
    draw.rounded_rectangle([x0 + m, y0 + m, x1 - m, y1 - m], radius=6,
                           fill=scr)
    for i in range(20):
        t = i / 20
        c = alpha_blend((255, 255, 255), scr, 0.1 * (1 - t))
        draw.line([(x0 + m, y0 + m + i), (x1 - m, y0 + m + i)], fill=c)
    # 前置摄像头
    draw.ellipse([cx - 3, y0 + 2, cx + 3, y0 + 6], fill=darken(color, 0.3))


def draw_headphones(draw, img, color, accent):
    """头戴式耳机"""
    cx, cy = 200, 160
    # 头梁
    draw.arc([cx - 55, cy - 80, cx + 55, cy + 10], 180, 0,
             fill=color, width=8)
    # 调节带
    draw.arc([cx - 45, cy - 70, cx + 45, cy + 5], 180, 0,
             fill=lighten(color, 0.3), width=3)
    # 左耳罩
    for side in [-1, 1]:
        ex = cx + side * 52
        ey = cy + 10
        # 连接臂
        draw.rounded_rectangle([ex - 6, cy - 20, ex + 6, ey - 10],
                               radius=4, fill=color)
        # 耳罩阴影
        draw.ellipse([ex - 28 + 2, ey - 28 + 3, ex + 28 + 2, ey + 32 + 3],
                     fill=lighten(color, 0.6))
        # 耳罩
        draw.ellipse([ex - 28, ey - 28, ex + 28, ey + 32],
                     fill=color, outline=darken(color, 0.2), width=2)
        # 耳垫
        draw.ellipse([ex - 20, ey - 20, ex + 20, ey + 24],
                     fill=darken(color, 0.15))
        # 内部
        draw.ellipse([ex - 14, ey - 14, ex + 14, ey + 18],
                     fill=lighten(color, 0.2))


def draw_jacket(draw, img, color, accent):
    """夹克/羽绒服"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.15)
    lc = lighten(c, 0.2)
    # 身体
    body = [(cx - 50, cy - 70), (cx + 50, cy - 70),
            (cx + 55, cy + 60), (cx + 35, cy + 65),
            (cx - 35, cy + 65), (cx - 55, cy + 60)]
    draw.polygon(body, fill=c, outline=dc, width=2)
    # 左袖
    draw.polygon([(cx - 50, cy - 60), (cx - 90, cy + 10),
                  (cx - 80, cy + 15), (cx - 45, cy - 30)],
                 fill=lc, outline=dc, width=1)
    # 右袖
    draw.polygon([(cx + 50, cy - 60), (cx + 90, cy + 10),
                  (cx + 80, cy + 15), (cx + 45, cy - 30)],
                 fill=lc, outline=dc, width=1)
    # 领子
    draw.polygon([(cx - 20, cy - 70), (cx, cy - 55),
                  (cx + 20, cy - 70)], fill=dc)
    draw.polygon([(cx - 18, cy - 70), (cx - 8, cy - 55),
                  (cx, cy - 62)], fill=lighten(c, 0.3))
    draw.polygon([(cx + 18, cy - 70), (cx + 8, cy - 55),
                  (cx, cy - 62)], fill=lighten(c, 0.35))
    # 拉链
    draw.line([(cx, cy - 55), (cx, cy + 63)], fill=darken(c, 0.4), width=2)
    # 口袋
    for side in [-1, 1]:
        px = cx + side * 22
        draw.rounded_rectangle([px - 15, cy + 20, px + 15, cy + 30],
                               radius=2, outline=dc, width=1)


def draw_shoe(draw, img, color, accent):
    """运动鞋侧面"""
    cx, cy = 200, 170
    c = color
    dc = darken(c, 0.2)
    # 鞋底
    draw.rounded_rectangle([cx - 75, cy + 20, cx + 70, cy + 35], radius=6,
                           fill=(240, 240, 240), outline=(200, 200, 200), width=2)
    # 中底
    draw.rounded_rectangle([cx - 72, cy + 10, cx + 67, cy + 22], radius=4,
                           fill=(255, 255, 255), outline=(220, 220, 220), width=1)
    # 鞋面
    pts = [(cx - 70, cy + 12), (cx - 65, cy - 30), (cx - 30, cy - 50),
           (cx + 20, cy - 45), (cx + 55, cy - 25), (cx + 65, cy + 12)]
    draw.polygon(pts, fill=c, outline=dc, width=2)
    # 鞋舌
    draw.polygon([(cx - 25, cy - 48), (cx - 15, cy - 70),
                  (cx + 5, cy - 68), (cx + 10, cy - 44)],
                 fill=lighten(c, 0.25), outline=dc, width=1)
    # 鞋带区域
    for i in range(4):
        lx = cx - 20 + i * 12
        ly = cy - 42 + i * 3
        draw.line([(lx, ly), (lx + 8, ly - 6)], fill=dc, width=2)
    # swoosh 形装饰弧线
    draw.arc([cx - 50, cy - 30, cx + 40, cy + 30], 330, 150,
             fill=accent, width=3)


def draw_hoodie(draw, img, color, accent):
    """卫衣/帽衫"""
    cx, cy = 200, 158
    c = color
    dc = darken(c, 0.15)
    # 身体
    draw.rounded_rectangle([cx - 55, cy - 50, cx + 55, cy + 65], radius=6,
                           fill=c, outline=dc, width=2)
    # 帽子
    draw.arc([cx - 40, cy - 85, cx + 40, cy - 35], 180, 0, fill=dc, width=6)
    draw.rounded_rectangle([cx - 35, cy - 62, cx + 35, cy - 48], radius=4,
                           fill=lighten(c, 0.15))
    # 袖子
    for s in [-1, 1]:
        draw.polygon([(cx + s * 55, cy - 40), (cx + s * 90, cy + 5),
                      (cx + s * 82, cy + 12), (cx + s * 55, cy - 15)],
                     fill=lighten(c, 0.12), outline=dc, width=1)
    # 口袋
    draw.rounded_rectangle([cx - 30, cy + 20, cx + 30, cy + 45], radius=4,
                           outline=dc, width=1)
    # 抽绳
    draw.line([(cx - 8, cy - 48), (cx - 12, cy - 35)], fill=dc, width=1)
    draw.line([(cx + 8, cy - 48), (cx + 12, cy - 35)], fill=dc, width=1)


def draw_pants(draw, img, color, accent):
    """牛仔裤"""
    cx, cy = 200, 150
    c = color
    dc = darken(c, 0.2)
    # 腰带
    draw.rounded_rectangle([cx - 45, cy - 75, cx + 45, cy - 62], radius=3,
                           fill=darken(c, 0.3), outline=darken(c, 0.4), width=1)
    # 裤身（上部）
    draw.polygon([(cx - 45, cy - 62), (cx + 45, cy - 62),
                  (cx + 50, cy + 10), (cx - 50, cy + 10)],
                 fill=c, outline=dc, width=1)
    # 左腿
    draw.polygon([(cx - 50, cy + 10), (cx - 2, cy + 10),
                  (cx - 5, cy + 80), (cx - 48, cy + 80)],
                 fill=c, outline=dc, width=1)
    # 右腿
    draw.polygon([(cx + 2, cy + 10), (cx + 50, cy + 10),
                  (cx + 48, cy + 80), (cx + 5, cy + 80)],
                 fill=lighten(c, 0.08), outline=dc, width=1)
    # 缝线
    draw.line([(cx, cy - 62), (cx, cy + 10)], fill=dc, width=1)
    # 口袋
    draw.polygon([(cx - 40, cy - 58), (cx - 25, cy - 58),
                  (cx - 22, cy - 40), (cx - 42, cy - 45)],
                 outline=dc, width=1)
    draw.polygon([(cx + 40, cy - 58), (cx + 25, cy - 58),
                  (cx + 22, cy - 40), (cx + 42, cy - 45)],
                 outline=dc, width=1)
    # 纽扣
    draw.ellipse([cx - 4, cy - 72, cx + 4, cy - 64], fill=darken(c, 0.35))


def draw_bottle(draw, img, color, accent):
    """水瓶/饮料瓶"""
    cx, cy = 200, 150
    c = color
    dc = darken(c, 0.2)
    lc = lighten(c, 0.3)
    # 瓶身阴影
    draw.rounded_rectangle([cx - 28 + 4, cy - 50 + 5, cx + 28 + 4, cy + 70 + 5],
                           radius=14, fill=lighten(c, 0.7))
    # 瓶身
    draw.rounded_rectangle([cx - 28, cy - 50, cx + 28, cy + 70], radius=14,
                           fill=c, outline=dc, width=2)
    # 标签区域
    draw.rounded_rectangle([cx - 26, cy - 20, cx + 26, cy + 35], radius=4,
                           fill=(255, 255, 255), outline=lighten(c, 0.5), width=1)
    # 标签装饰条
    draw.rectangle([cx - 26, cy - 5, cx + 26, cy + 5], fill=accent)
    # 瓶颈
    draw.rounded_rectangle([cx - 14, cy - 75, cx + 14, cy - 48], radius=6,
                           fill=lighten(c, 0.15), outline=dc, width=1)
    # 瓶盖
    draw.rounded_rectangle([cx - 16, cy - 90, cx + 16, cy - 73], radius=5,
                           fill=accent, outline=darken(accent, 0.2), width=1)
    # 高光
    draw.line([(cx - 15, cy - 45), (cx - 15, cy + 65)],
             fill=lighten(c, 0.4), width=3)


def draw_package(draw, img, color, accent):
    """包装盒/礼包"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 盒身（3D 效果）
    # 正面
    draw.rectangle([cx - 55, cy - 45, cx + 35, cy + 55], fill=c, outline=dc, width=2)
    # 顶面
    draw.polygon([(cx - 55, cy - 45), (cx - 25, cy - 65),
                  (cx + 65, cy - 65), (cx + 35, cy - 45)],
                 fill=lighten(c, 0.25), outline=dc, width=1)
    # 右侧面
    draw.polygon([(cx + 35, cy - 45), (cx + 65, cy - 65),
                  (cx + 65, cy + 35), (cx + 35, cy + 55)],
                 fill=darken(c, 0.1), outline=dc, width=1)
    # 标签
    draw.rounded_rectangle([cx - 45, cy - 25, cx + 25, cy + 20], radius=4,
                           fill=(255, 255, 255, 200))
    # 装饰线
    draw.rectangle([cx - 45, cy - 8, cx + 25, cy + 2], fill=accent)
    # 品牌圆点
    draw.ellipse([cx - 15, cy + 8, cx + 5, cy + 18],
                 fill=accent, outline=darken(accent, 0.2))


def draw_coffee(draw, img, color, accent):
    """咖啡挂耳包"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 咖啡杯
    draw.rounded_rectangle([cx - 35, cy - 30, cx + 35, cy + 50], radius=8,
                           fill=(255, 255, 255), outline=(180, 180, 180), width=2)
    # 杯身装饰
    draw.rounded_rectangle([cx - 32, cy - 10, cx + 32, cy + 25], radius=3,
                           fill=c)
    # 品牌标识
    draw.ellipse([cx - 12, cy, cx + 12, cy + 15],
                 fill=(255, 255, 255))
    # 杯把手
    draw.arc([cx + 33, cy - 5, cx + 55, cy + 30], 280, 80,
             fill=(180, 180, 180), width=4)
    # 蒸汽
    for i, ox in enumerate([-8, 2, 12]):
        start_y = cy - 40 - i * 3
        draw.arc([cx + ox - 6, start_y - 15, cx + ox + 6, start_y],
                 180, 0, fill=(200, 200, 200), width=2)


def draw_lamp(draw, img, color, accent):
    """台灯"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 灯光晕（底层）
    for r in range(60, 0, -2):
        opacity = 0.03 * (1 - r / 60)
        glow = alpha_blend(accent, (255, 255, 255), opacity)
        draw.ellipse([cx - 20 - r, cy - 70 - r // 2,
                      cx + 40 + r, cy - 30 + r // 2], fill=glow)
    # 底座
    draw.ellipse([cx - 35, cy + 50, cx + 35, cy + 70],
                 fill=darken(c, 0.1), outline=dc, width=2)
    # 灯臂
    draw.line([(cx, cy + 55), (cx - 5, cy - 10)], fill=c, width=5)
    draw.line([(cx - 5, cy - 10), (cx + 10, cy - 50)], fill=c, width=5)
    # 关节
    draw.ellipse([cx - 8, cy - 14, cx + 2, cy - 6], fill=dc)
    # 灯头
    draw.polygon([(cx - 10, cy - 55), (cx + 40, cy - 55),
                  (cx + 35, cy - 40), (cx - 5, cy - 40)],
                 fill=c, outline=dc, width=2)
    # 灯泡光
    draw.ellipse([cx + 5, cy - 50, cx + 25, cy - 42],
                 fill=lighten(accent, 0.6))


def draw_sofa(draw, img, color, accent):
    """懒人沙发/豆袋"""
    cx, cy = 200, 160
    c = color
    dc = darken(c, 0.15)
    # 阴影
    draw.ellipse([cx - 62, cy + 35, cx + 62, cy + 60],
                 fill=lighten(c, 0.65))
    # 主体（豆袋形状）
    draw.ellipse([cx - 60, cy - 50, cx + 60, cy + 45],
                 fill=c, outline=dc, width=2)
    # 顶部褶皱
    draw.arc([cx - 30, cy - 55, cx + 30, cy - 25], 180, 0,
             fill=dc, width=2)
    # 面料纹理线
    for i in range(-2, 3):
        draw.arc([cx - 40 + i * 5, cy - 30, cx + 40 + i * 5, cy + 30],
                 200, 340, fill=lighten(c, 0.15), width=1)
    # 高光
    draw.ellipse([cx - 25, cy - 35, cx + 15, cy - 5],
                 fill=lighten(c, 0.2))


def draw_vacuum(draw, img, color, accent):
    """吸尘器（手持式）"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 主体管
    draw.rounded_rectangle([cx - 12, cy - 80, cx + 12, cy + 40], radius=6,
                           fill=c, outline=dc, width=2)
    # 集尘杯（透明）
    draw.rounded_rectangle([cx - 18, cy - 30, cx + 18, cy + 15], radius=8,
                           fill=lighten(accent, 0.7), outline=dc, width=2)
    # 内部旋风纹
    draw.arc([cx - 12, cy - 25, cx + 12, cy + 10], 0, 270,
             fill=accent, width=2)
    # 手柄
    draw.rounded_rectangle([cx - 8, cy - 80, cx + 8, cy - 55], radius=4,
                           fill=darken(c, 0.1))
    draw.rounded_rectangle([cx + 8, cy - 75, cx + 30, cy - 60], radius=4,
                           fill=accent, outline=darken(accent, 0.2), width=1)
    # 地刷头
    draw.rounded_rectangle([cx - 40, cy + 38, cx + 40, cy + 55], radius=6,
                           fill=darken(c, 0.1), outline=dc, width=2)
    # LED 灯条
    draw.rectangle([cx - 38, cy + 40, cx + 38, cy + 44],
                   fill=lighten(accent, 0.5))
    # 连接管
    draw.line([(cx, cy + 40), (cx, cy + 38)], fill=dc, width=4)


def draw_bedding(draw, img, color, accent):
    """床品四件套（折叠展示）"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.15)
    lc = lighten(c, 0.2)
    # 底层被子（折叠）
    draw.rounded_rectangle([cx - 65, cy - 25, cx + 65, cy + 55], radius=8,
                           fill=c, outline=dc, width=2)
    # 折叠纹理
    draw.line([(cx - 60, cy + 10), (cx + 60, cy + 10)], fill=dc, width=1)
    draw.line([(cx - 60, cy + 30), (cx + 60, cy + 30)], fill=dc, width=1)
    # 枕头
    draw.rounded_rectangle([cx - 50, cy - 60, cx + 50, cy - 20], radius=16,
                           fill=lc, outline=dc, width=2)
    # 枕头高光
    draw.ellipse([cx - 30, cy - 52, cx + 20, cy - 30],
                 fill=lighten(c, 0.35))
    # 装饰花纹
    for i in range(3):
        px = cx - 30 + i * 30
        draw.ellipse([px - 4, cy + 5, px + 4, cy + 13],
                     outline=accent, width=1)


def draw_book(draw, img, color, accent):
    """书籍（三册叠放）"""
    cx, cy = 200, 155
    colors = [color, darken(color, 0.15), lighten(color, 0.2)]
    # 三本书叠放
    for i, bc in enumerate(reversed(colors)):
        ox = (2 - i) * 8
        oy = (2 - i) * 12
        x0, y0 = cx - 45 + ox, cy - 55 + oy
        x1, y1 = cx + 50 + ox, cy + 50 + oy
        dc = darken(bc, 0.2)
        # 书脊
        draw.rectangle([x0, y0, x0 + 12, y1], fill=dc)
        # 封面
        draw.rectangle([x0 + 12, y0, x1, y1], fill=bc, outline=dc, width=1)
        # 封面装饰
        draw.rectangle([x0 + 18, y0 + 8, x1 - 6, y0 + 12], fill=accent)
        # 页面效果（底部）
        draw.line([(x0 + 12, y1 - 2), (x1, y1 - 2)],
                  fill=lighten(bc, 0.4), width=2)


def draw_notebook(draw, img, color, accent):
    """笔记本"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.25)
    # 封面
    x0, y0 = cx - 50, cy - 65
    x1, y1 = cx + 50, cy + 65
    # 阴影
    draw.rounded_rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], radius=4,
                           fill=lighten(c, 0.6))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=c,
                           outline=dc, width=2)
    # 松紧带
    draw.line([(cx + 20, y0), (cx + 20, y1)], fill=accent, width=3)
    # 封面压印方框
    draw.rounded_rectangle([x0 + 12, y0 + 15, x1 - 12, cy - 5], radius=2,
                           outline=lighten(c, 0.2), width=1)
    # 书签带
    draw.line([(cx - 10, y1), (cx - 10, y1 + 12)], fill=accent, width=2)
    draw.polygon([(cx - 13, y1 + 12), (cx - 10, y1 + 8), (cx - 7, y1 + 12)],
                 fill=accent)
    # 页边
    draw.line([(x1 - 3, y0 + 3), (x1 - 3, y1 - 3)],
             fill=lighten(c, 0.4), width=2)


def draw_pen(draw, img, color, accent):
    """中性笔组"""
    cx, cy = 200, 155
    pens = [(cx - 30, color), (cx - 10, darken(color, 0.3)),
            (cx + 10, accent), (cx + 30, darken(accent, 0.2))]
    for px, pc in pens:
        dc = darken(pc, 0.2)
        # 笔身
        draw.rounded_rectangle([px - 4, cy - 70, px + 4, cy + 40], radius=3,
                               fill=pc, outline=dc, width=1)
        # 笔帽
        draw.rounded_rectangle([px - 5, cy - 75, px + 5, cy - 60], radius=3,
                               fill=darken(pc, 0.15), outline=dc, width=1)
        # 笔夹
        draw.line([(px + 5, cy - 73), (px + 5, cy - 55)], fill=dc, width=2)
        # 笔尖
        draw.polygon([(px - 3, cy + 40), (px + 3, cy + 40), (px, cy + 52)],
                     fill=(180, 180, 180))
        # 握胶区
        draw.rounded_rectangle([px - 5, cy + 15, px + 5, cy + 35], radius=2,
                               fill=lighten(pc, 0.3), outline=dc, width=1)


def draw_treadmill(draw, img, color, accent):
    """跑步机"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 跑带
    draw.polygon([(cx - 60, cy + 30), (cx + 60, cy + 30),
                  (cx + 50, cy + 60), (cx - 50, cy + 60)],
                 fill=(60, 60, 60), outline=(40, 40, 40), width=2)
    # 跑带纹理
    for i in range(6):
        y = cy + 34 + i * 5
        draw.line([(cx - 55 + i, y), (cx + 55 - i, y)],
                  fill=(80, 80, 80), width=1)
    # 立柱
    draw.line([(cx - 40, cy + 30), (cx - 30, cy - 60)], fill=c, width=6)
    draw.line([(cx + 40, cy + 30), (cx + 30, cy - 60)], fill=c, width=6)
    # 扶手横杆
    draw.line([(cx - 30, cy - 60), (cx + 30, cy - 60)], fill=c, width=5)
    # 显示屏
    draw.rounded_rectangle([cx - 22, cy - 58, cx + 22, cy - 38], radius=4,
                           fill=(30, 30, 30), outline=dc, width=2)
    # 屏幕内容
    draw.rounded_rectangle([cx - 18, cy - 55, cx + 18, cy - 41], radius=2,
                           fill=lighten(accent, 0.6))
    # 扶手
    draw.rounded_rectangle([cx - 45, cy - 15, cx - 35, cy + 5], radius=3,
                           fill=darken(c, 0.1), outline=dc, width=1)
    draw.rounded_rectangle([cx + 35, cy - 15, cx + 45, cy + 5], radius=3,
                           fill=darken(c, 0.1), outline=dc, width=1)


def draw_racket(draw, img, color, accent):
    """羽毛球拍"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 拍头（椭圆）
    draw.ellipse([cx - 40, cy - 75, cx + 40, cy + 5],
                 outline=c, width=4)
    # 拍头内圈
    draw.ellipse([cx - 35, cy - 70, cx + 35, cy + 0],
                 outline=lighten(c, 0.3), width=2)
    # 网线（横）
    for i in range(7):
        y = cy - 65 + i * 10
        x_off = int(30 * math.sin(math.acos(max(-1, min(1, (y - (cy - 35)) / 38)))))
        if abs(y - (cy - 35)) <= 38:
            draw.line([(cx - x_off, y), (cx + x_off, y)],
                      fill=lighten(c, 0.5), width=1)
    # 网线（纵）
    for i in range(6):
        x = cx - 25 + i * 10
        draw.line([(x, cy - 65), (x, cy - 5)], fill=lighten(c, 0.5), width=1)
    # T 形连接
    draw.rounded_rectangle([cx - 8, cy + 2, cx + 8, cy + 18], radius=3,
                           fill=c, outline=dc, width=1)
    # 手柄
    draw.rounded_rectangle([cx - 6, cy + 18, cx + 6, cy + 75], radius=4,
                           fill=darken(c, 0.1), outline=dc, width=2)
    # 握把缠绕纹理
    for i in range(8):
        y = cy + 22 + i * 7
        draw.line([(cx - 5, y), (cx + 5, y + 3)], fill=accent, width=1)
    # 底盖
    draw.rounded_rectangle([cx - 7, cy + 72, cx + 7, cy + 78], radius=2,
                           fill=accent)


def draw_serum(draw, img, color, accent):
    """精华液瓶（滴管瓶）"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 瓶身阴影
    draw.rounded_rectangle([cx - 22 + 3, cy - 30 + 4, cx + 22 + 3, cy + 65 + 4],
                           radius=10, fill=lighten(c, 0.65))
    # 瓶身
    draw.rounded_rectangle([cx - 22, cy - 30, cx + 22, cy + 65], radius=10,
                           fill=c, outline=dc, width=2)
    # 标签
    draw.rounded_rectangle([cx - 19, cy - 10, cx + 19, cy + 40], radius=3,
                           fill=(255, 255, 255))
    draw.rectangle([cx - 19, cy + 5, cx + 19, cy + 15], fill=accent)
    # 瓶肩
    draw.polygon([(cx - 22, cy - 30), (cx - 12, cy - 50),
                  (cx + 12, cy - 50), (cx + 22, cy - 30)],
                 fill=c, outline=dc, width=1)
    # 滴管帽
    draw.rounded_rectangle([cx - 10, cy - 72, cx + 10, cy - 48], radius=5,
                           fill=accent, outline=darken(accent, 0.2), width=1)
    # 橡胶头
    draw.ellipse([cx - 8, cy - 80, cx + 8, cy - 68], fill=darken(accent, 0.1))
    # 高光
    draw.line([(cx - 12, cy - 25), (cx - 12, cy + 60)],
             fill=lighten(c, 0.35), width=2)


def draw_tube(draw, img, color, accent):
    """洁面乳管状包装"""
    cx, cy = 200, 155
    c = color
    dc = darken(c, 0.2)
    # 管身阴影
    draw.rounded_rectangle([cx - 25 + 3, cy - 45 + 4, cx + 25 + 3, cy + 55 + 4],
                           radius=12, fill=lighten(c, 0.65))
    # 管身
    draw.rounded_rectangle([cx - 25, cy - 45, cx + 25, cy + 55], radius=12,
                           fill=(255, 255, 255), outline=(200, 200, 200), width=2)
    # 标签
    draw.rounded_rectangle([cx - 22, cy - 30, cx + 22, cy + 30], radius=4,
                           fill=c)
    # 标签文字装饰
    draw.rectangle([cx - 18, cy - 10, cx + 18, cy], fill=accent)
    draw.ellipse([cx - 10, cy + 5, cx + 10, cy + 15],
                 fill=(255, 255, 255))
    # 管盖
    draw.rounded_rectangle([cx - 14, cy - 65, cx + 14, cy - 43], radius=6,
                           fill=accent, outline=darken(accent, 0.2), width=2)
    # 管盖翻盖
    draw.rounded_rectangle([cx - 8, cy - 72, cx + 8, cy - 63], radius=3,
                           fill=darken(accent, 0.1))
    # 高光
    draw.line([(cx - 14, cy - 40), (cx - 14, cy + 50)],
             fill=lighten(c, 0.4) if c != (255, 255, 255) else (240, 240, 240),
             width=2)


# ════════════════════════════════════════════
# 分类 / 品牌配色
# ════════════════════════════════════════════

CATEGORY_STYLE = {
    1: ("#1E3A5F", "电子产品"),
    2: ("#6B2D5B", "服装鞋帽"),
    3: ("#8B4513", "食品饮料"),
    4: ("#2E6B4F", "家居用品"),
    5: ("#2B4570", "图书文具"),
    6: ("#8B2500", "运动户外"),
    7: ("#8B1A6B", "美妆个护"),
    8: ("#6B3FA0", "母婴用品"),
}

BRAND_COLORS = {
    "Apple": "#333333", "Sony": "#000000", "Xiaomi": "#FF6700",
    "Nike": "#111111", "Levi's": "#C41230", "adidas": "#000000",
    "UNIQLO": "#FF0000", "BOSIDENG": "#1A1A6C",
    "三只松鼠": "#E74C3C", "农夫山泉": "#E74C3C", "Luckin": "#1A6FD5",
    "良品铺子": "#C0392B", "元气森林": "#00B894",
    "MUJI": "#8B7355", "Dyson": "#6C6C6C", "南极人": "#E74C3C",
    "刘慈欣": "#1A1A2E", "得力": "#0066CC", "Moleskine": "#1A1A1A",
    "DECATHLON": "#0066CC", "LI-NING": "#E74C3C", "CAMEL": "#8B6914",
    "Lancôme": "#1A1A1A", "L'Oréal": "#1A1A1A", "SK-II": "#C41230",
}

# ════════════════════════════════════════════
# 商品清单: (文件名, 商品名, 分类ID, 品牌, 绘制函数)
# ════════════════════════════════════════════

PRODUCTS = [
    # ── 电子产品 (1) ──
    ("product_01.png", "iPhone 16 Pro Max 256GB", 1, "Apple", draw_phone),
    ("product_02.png", "MacBook Pro 14英寸 M4", 1, "Apple", draw_laptop),
    ("product_03.png", "AirPods Pro 3", 1, "Apple", draw_earbuds),
    ("product_04.png", "iPad Air 6 11英寸", 1, "Apple", draw_tablet),
    ("product_05.png", "Sony WH-1000XM6 头戴耳机", 1, "Sony", draw_headphones),
    ("product_06.png", "小米14 Ultra", 1, "Xiaomi", draw_phone),

    # ── 服装鞋帽 (2) ──
    ("product_07.png", "优衣库轻薄羽绒服", 2, "UNIQLO", draw_jacket),
    ("product_08.png", "Nike Air Force 1 白色", 2, "Nike", draw_shoe),
    ("product_09.png", "Levi's 501 经典直筒牛仔裤", 2, "Levi's", draw_pants),
    ("product_10.png", "阿迪达斯三叶草卫衣", 2, "adidas", draw_hoodie),
    ("product_11.png", "波司登极寒系列羽绒服", 2, "BOSIDENG", draw_jacket),

    # ── 食品饮料 (3) ──
    ("product_12.png", "三只松鼠坚果大礼包", 3, "三只松鼠", draw_package),
    ("product_13.png", "农夫山泉矿泉水 550ml×24瓶", 3, "农夫山泉", draw_bottle),
    ("product_14.png", "瑞幸咖啡挂耳包 精品系列", 3, "Luckin", draw_coffee),
    ("product_15.png", "良品铺子猪肉脯 200g", 3, "良品铺子", draw_package),
    ("product_16.png", "元气森林气泡水 480ml×15瓶", 3, "元气森林", draw_bottle),

    # ── 家居用品 (4) ──
    ("product_17.png", "小米智能台灯 Pro", 4, "Xiaomi", draw_lamp),
    ("product_18.png", "无印良品懒人沙发", 4, "MUJI", draw_sofa),
    ("product_19.png", "戴森V15吸尘器", 4, "Dyson", draw_vacuum),
    ("product_20.png", "南极人四件套纯棉床品", 4, "南极人", draw_bedding),

    # ── 图书文具 (5) ──
    ("product_21.png", "三体（全三册）", 5, "刘慈欣", draw_book),
    ("product_22.png", "得力中性笔 0.5mm 黑色 12支", 5, "得力", draw_pen),
    ("product_23.png", "Moleskine经典笔记本", 5, "Moleskine", draw_notebook),

    # ── 运动户外 (6) ──
    ("product_24.png", "迪卡侬跑步机 T520B", 6, "DECATHLON", draw_treadmill),
    ("product_25.png", "李宁羽毛球拍 风刃900", 6, "LI-NING", draw_racket),
    ("product_26.png", "骆驼户外冲锋衣", 6, "CAMEL", draw_jacket),

    # ── 美妆个护 (7) ──
    ("product_27.png", "兰蔻小黑瓶精华 50ml", 7, "Lancôme", draw_serum),
    ("product_28.png", "欧莱雅男士洁面乳", 7, "L'Oréal", draw_tube),
    ("product_29.png", "SK-II神仙水 230ml", 7, "SK-II", draw_serum),
]


# ════════════════════════════════════════════
# 生成逻辑
# ════════════════════════════════════════════

def generate_product_image(filename, name, cat_id, brand, draw_func):
    """为一个商品生成插画风格展示图"""
    cat_hex, cat_name = CATEGORY_STYLE.get(cat_id, ("#555555", "其他"))
    cat_color = hex2rgb(cat_hex)
    brand_color = hex2rgb(BRAND_COLORS.get(brand, cat_hex))

    img, draw = new_canvas(cat_color)

    # 绘制产品插画
    accent = lighten(brand_color, 0.3)
    draw_func(draw, img, brand_color, accent)

    # 添加文字信息
    add_text(draw, name, brand, brand_color, cat_name, cat_color)

    filepath = os.path.join(UPLOAD_DIR, filename)
    img.save(filepath, "PNG", optimize=True)


def main():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    version_path = os.path.join(UPLOAD_DIR, VERSION_FILE)
    if not FORCE and os.path.exists(version_path):
        all_exist = all(
            os.path.exists(os.path.join(UPLOAD_DIR, p[0]))
            for p in PRODUCTS
        )
        if all_exist:
            print(f"商品图片已是 {VERSION}，跳过生成")
            return

    print(f"生成商品图片到 {UPLOAD_DIR} ...")
    count = 0

    for filename, name, cat_id, brand, draw_func in PRODUCTS:
        print(f"  ⊕ {filename} — {name}")
        generate_product_image(filename, name, cat_id, brand, draw_func)
        count += 1

    # 写入版本标记
    with open(version_path, "w") as f:
        f.write(f"{VERSION}\ngenerated={count}\n")

    # 清理旧版本标记
    for old in [".generated_v1", ".generated_v2", ".generated_v3"]:
        old_path = os.path.join(UPLOAD_DIR, old)
        if os.path.exists(old_path):
            os.remove(old_path)

    print(f"\n完成！共生成 {count} 张商品图片")


if __name__ == "__main__":
    main()
