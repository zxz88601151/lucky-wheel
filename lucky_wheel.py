# -*- coding: utf-8 -*-
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
90后童年回忆抽奖大转盘 - PySide6 实现
==========================================
参考复古街机抽奖机设计：木质边框、铆钉、霓虹灯、拉杆、
20 种童年怀旧奖品，点击拉杆摇动触发转盘旋转。
"""

import sys
import math
import random
from datetime import datetime

from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF, QRectF,
    Signal, Property
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient,
    QPainterPath, QFontMetrics, QPixmap, QImage
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QDialog, QFrame, QScrollArea
)


# ============================================================
#  奖品数据 (23 种，按梯度分类)
# ============================================================
# 普惠零食（高频易中, rate 9-10）
PRIZES = [
    {"name": "瓜子仁",       "display_name": "瓜子",     "rate": 10, "group": "普惠", "color": "#D64535", "icon": "seed"},
    {"name": "小小酥",       "display_name": "小小酥",   "rate": 10, "group": "普惠", "color": "#F4B934", "icon": "crisp"},
    {"name": "水晶果冻",     "display_name": "果冻",     "rate": 10, "group": "普惠", "color": "#2A7FB8", "icon": "jelly"},
    {"name": "跳跳糖干脆面", "display_name": "跳跳糖",   "rate": 9, "group": "普惠", "color": "#F5E6C8", "icon": "pop"},
    {"name": "干脆面",       "display_name": "干脆面",   "rate": 9, "group": "普惠", "color": "#1A9E8C", "icon": "noodle"},
    {"name": "橡皮尺子套装", "display_name": "橡皮尺",   "rate": 9, "group": "普惠", "color": "#9B59B6", "icon": "eraser"},
    {"name": "卡通贴纸",     "display_name": "卡通贴纸", "rate": 9, "group": "普惠", "color": "#E67E22", "icon": "sticker"},
    {"name": "无花果丝",     "display_name": "无花果",   "rate": 9, "group": "普惠", "color": "#D64535", "icon": "strip"},
    {"name": "大大泡泡糖",   "display_name": "泡泡糖",   "rate": 9, "group": "普惠", "color": "#F4B934", "icon": "gum"},
    {"name": "大大卷",       "display_name": "大大卷",   "rate": 9, "group": "普惠", "color": "#2A7FB8", "icon": "tape"},
    {"name": "咪咪虾条",     "display_name": "虾条",     "rate": 9, "group": "普惠", "color": "#F5E6C8", "icon": "shrimp"},
    {"name": "华华丹",       "display_name": "华华丹",   "rate": 9, "group": "普惠", "color": "#27AE60", "icon": "again"},
    # 怀旧文具 & 普通玩具（中等概率, rate 7-8）
    {"name": "陀螺",         "display_name": "陀螺",     "rate": 8, "group": "怀旧", "color": "#1A9E8C", "icon": "top"},
    {"name": "泡泡水",       "display_name": "泡泡水",   "rate": 8, "group": "怀旧", "color": "#9B59B6", "icon": "bubble"},
    {"name": "陀螺玩具",     "display_name": "陀螺玩具", "rate": 8, "group": "怀旧", "color": "#E67E22", "icon": "top"},
    {"name": "彩色铅笔",     "display_name": "彩色铅笔", "rate": 7, "group": "怀旧", "color": "#D64535", "icon": "pencil"},
    {"name": "卡通万花筒",   "display_name": "万花筒",   "rate": 7, "group": "怀旧", "color": "#F4B934", "icon": "scope"},
    {"name": "玻璃弹珠",     "display_name": "玻璃弹珠", "rate": 7, "group": "怀旧", "color": "#2A7FB8", "icon": "marble"},
    {"name": "沙包",         "display_name": "沙包",     "rate": 7, "group": "怀旧", "color": "#F5E6C8", "icon": "sack"},
    {"name": "彩色翻花绳",   "display_name": "翻花绳",   "rate": 7, "group": "怀旧", "color": "#1A9E8C", "icon": "string"},
    {"name": "泡泡水套装",   "display_name": "泡泡水",   "rate": 8, "group": "怀旧", "color": "#9B59B6", "icon": "bubble"},
    # 珍藏稀有童年好物（低概率, rate 3-4）
    {"name": "小霸王游戏机", "display_name": "小霸王",   "rate": 3, "group": "稀有", "color": "#D64535", "icon": "game"},
    {"name": "铁皮青蛙玩具", "display_name": "铁皮蛙",   "rate": 4, "group": "稀有", "color": "#27AE60", "icon": "frog"},
    # 幸运特殊奖励（最低概率, rate=2）
    {"name": "再来一次",     "display_name": "再来一次", "rate": 2, "group": "特殊", "color": "#7F8C8D", "icon": "again"},
]

NUM_PRIZES = len(PRIZES)
STEP_ANGLE = 360.0 / NUM_PRIZES  # 18 度


def _polar_point(cx, cy, r, deg_from_top):
    """从 12 点方向顺时针 deg_from_top 度的点坐标。"""
    rad = math.radians(deg_from_top)
    return cx + r * math.sin(rad), cy - r * math.cos(rad)




# ============================================================
#  转盘绘制 Widget
# ============================================================
class WheelWidget(QWidget):
    """自定义绘制的抽奖转盘。"""

    spin_finished = Signal()
    spin_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self._spinning = False
        self.setFixedSize(560, 560)

        self._animation = QPropertyAnimation(self, b"angle")
        self._animation.setDuration(5000)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    # ---------- 属性: angle ----------
    def get_angle(self):
        return self._angle

    def set_angle(self, value):
        self._angle = value
        self.update()

    angle = Property(float, get_angle, set_angle)

    def is_spinning(self):
        return self._spinning

    # ---------- 开始抽奖 ----------
    def spin(self):
        """按 rate 权重随机选中奖品并旋转到对应位置。"""
        if self._spinning:
            return None

        # 加权随机选择: 权重 = rate
        weights = [p["rate"] for p in PRIZES]
        total = sum(weights)
        pick = random.uniform(0, total)
        cumulative = 0
        prize_index = 0
        for i, w in enumerate(weights):
            cumulative += w
            if pick <= cumulative:
                prize_index = i
                break

        mid_angle = prize_index * STEP_ANGLE + STEP_ANGLE / 2
        final_pos = (360 - mid_angle) % 360

        current_pos = self._angle % 360
        delta = final_pos - current_pos
        if delta <= 0:
            delta += 360

        target = self._angle + 360 * 6 + delta

        self._spinning = True
        self._animation.setStartValue(self._angle)
        self._animation.setEndValue(target)
        self._animation.start()
        self._animation.finished.connect(self._on_finished)

        return prize_index

    def _on_finished(self):
        self._spinning = False
        try:
            self._animation.finished.disconnect(self._on_finished)
        except RuntimeError:
            pass
        self.spin_finished.emit()

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        outer_r = min(w, h) / 2 - 8

        # 1. 木质外框
        self._draw_wood_frame(painter, cx, cy, outer_r)

        # 2. 铆钉
        self._draw_rivets(painter, cx, cy, outer_r - 18)

        # 3. 转盘主体
        wheel_r = outer_r - 32
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        self._draw_wheel(painter, wheel_r)
        painter.restore()

        # 4. 中心旋钮
        self._draw_center_knob(painter, cx, cy)

        # 5. 指针
        self._draw_pointer(painter, cx, cy, wheel_r)

    # ---------- 绘制: 木质外框 ----------
    def _draw_wood_frame(self, painter, cx, cy, r):
        # 深木色外环
        grad = QRadialGradient(cx, cy, r)
        grad.setColorAt(0, QColor("#5D3A1A"))
        grad.setColorAt(0.8, QColor("#3D2610"))
        grad.setColorAt(1, QColor("#2A1808"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#1A0F05"), 2))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # 木纹线条 (仅在外圈, 不覆盖扇区)
        painter.setPen(QPen(QColor("#4A2C14"), 1))
        for i in range(0, 360, 20):
            x1, y1 = _polar_point(cx, cy, r - 5, i)
            x2, y2 = _polar_point(cx, cy, r - 18, i)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 内圈浅色
        inner_r = r - 20
        painter.setBrush(QBrush(QColor("#2A1808")))
        painter.setPen(QPen(QColor("#6B4226"), 2))
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

    # ---------- 绘制: 铆钉 ----------
    def _draw_rivets(self, painter, cx, cy, r):
        n = 24
        for i in range(n):
            deg = i * 360 / n
            x, y = _polar_point(cx, cy, r, deg)
            # 金属铆钉
            grad = QRadialGradient(x - 2, y - 2, 5)
            grad.setColorAt(0, QColor("#FFF"))
            grad.setColorAt(1, QColor("#7F8C8D"))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor("#5D6D7E"), 1))
            painter.drawEllipse(QPointF(x, y), 5, 5)

    # ---------- 绘制: 转盘扇形/文字/图标 ----------
    def _draw_wheel(self, painter, r):
        for i in range(NUM_PRIZES):
            prize = PRIZES[i]
            start_deg = i * STEP_ANGLE
            mid_deg = start_deg + STEP_ANGLE / 2

            qt_start = int((90 - start_deg) * 16)
            qt_span = int(-STEP_ANGLE * 16)

            base_color = QColor(prize["color"])
            grad = QRadialGradient(0, 0, r)
            grad.setColorAt(0.0, base_color.lighter(120))
            grad.setColorAt(1.0, base_color.darker(110))
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor("#3D2610"), 1.5))
            painter.drawPie(QRectF(-r, -r, r * 2, r * 2), qt_start, qt_span)

            # 文字
            display_name = prize.get("display_name", prize["name"])
            self._draw_prize_text(painter, display_name, mid_deg, r, prize["color"])

    LIGHT_COLORS = {'#F5E6C8', '#F4B934'}

    # ---------- 绘制: 文字(随扇形旋转, 字符屏幕正立) ----------
    def _draw_prize_text(self, painter, text, mid_deg, r, prize_color):
        """文字中心随扇形旋转，字符本身保持屏幕正立，字号自适应。"""
        painter.save()
        is_light = prize_color in self.LIGHT_COLORS
        painter.setPen(QPen(QColor("#2C3E50") if is_light else QColor("#FFFFFF")))

        # 字号按显示文字长度微调，半径 0.88r，文字尽量居中不溢出
        n = len(text)
        if n <= 2:
            font_size = 17
        elif n == 3:
            font_size = 14
        else:
            font_size = 11
        painter.setFont(QFont("Microsoft YaHei", font_size, QFont.Bold))

        text_r = r * 0.88
        x = text_r * math.sin(math.radians(mid_deg))
        y = -text_r * math.cos(math.radians(mid_deg))

        # 平移到文字中心，再反向旋转当前角度，使字符在屏幕上正立
        painter.translate(x, y)
        painter.rotate(-self._angle)

        # 用 QFontMetrics 精确居中
        metrics = QFontMetrics(painter.font())
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        rect = QRectF(-text_width / 2, -text_height / 2, text_width, text_height)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()

    # ---------- 绘制: 中心旋钮 ----------
    def _draw_center_knob(self, painter, cx, cy):
        r = 45
        # 外圈金属
        grad = QRadialGradient(cx - 5, cy - 5, r)
        grad.setColorAt(0, QColor("#D4A017"))
        grad.setColorAt(1, QColor("#8B6914"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#5D3A1A"), 2))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # 内圈红色
        r2 = 32
        red_grad = QRadialGradient(cx - 3, cy - 3, r2)
        red_grad.setColorAt(0, QColor("#C0392B"))
        red_grad.setColorAt(1, QColor("#7B241C"))
        painter.setBrush(QBrush(red_grad))
        painter.setPen(QPen(QColor("#5D3A1A"), 1))
        painter.drawEllipse(QPointF(cx, cy), r2, r2)

        # 中心金属点
        painter.setBrush(QBrush(QColor("#D4A017")))
        painter.setPen(QPen(QColor("#6B4E00"), 1))
        painter.drawEllipse(QPointF(cx, cy), 8, 8)

    # ---------- 绘制: 指针 ----------
    def _draw_pointer(self, painter, cx, cy, wheel_r):
        painter.save()
        tip_y = cy - wheel_r + 10
        base_y = cy - wheel_r - 32
        half_w = 18

        path = QPainterPath()
        path.moveTo(cx, tip_y)
        path.lineTo(cx - half_w, base_y)
        path.lineTo(cx - half_w + 5, base_y - 5)
        path.lineTo(cx + half_w - 5, base_y - 5)
        path.lineTo(cx + half_w, base_y)
        path.closeSubpath()

        grad = QLinearGradient(cx - half_w, 0, cx + half_w, 0)
        grad.setColorAt(0, QColor("#D4A017"))
        grad.setColorAt(0.5, QColor("#FFF3B0"))
        grad.setColorAt(1, QColor("#8B6914"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#5D3A1A"), 2))
        painter.drawPath(path)

        painter.setBrush(QBrush(QColor("#C0392B")))
        painter.setPen(QPen(QColor("#7B241C"), 1))
        painter.drawEllipse(QPointF(cx, base_y - 12), 7, 7)
        painter.restore()


# ============================================================
#  拉杆 Widget
# ============================================================
class LeverWidget(QWidget):
    """可拖动的复古拉杆，拉到底释放后触发旋转。"""

    pulled = Signal()  # 拉到底释放时发出

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 280)
        self._pos = 0.0      # 0 = 顶部, 1 = 底部
        self._dragging = False
        self._threshold = 0.75

        self._animation = QPropertyAnimation(self, b"lever_pos")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.OutBounce)

    def get_pos(self):
        return self._pos

    def set_pos(self, value):
        self._pos = max(0.0, min(1.0, value))
        self.update()

    lever_pos = Property(float, get_pos, set_pos)

    # ---------- 鼠标事件 ----------
    def mousePressEvent(self, event):
        self._dragging = True
        self._set_from_y(event.position().y())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._set_from_y(event.position().y())

    def mouseReleaseEvent(self, event):
        if not self._dragging:
            return
        self._dragging = False
        if self._pos >= self._threshold:
            self.pulled.emit()
        self._animation.setStartValue(self._pos)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _set_from_y(self, y):
        # 0 -> 顶部, height -> 底部
        h = self.height()
        knob_h = 36
        track_h = h - knob_h
        self.set_pos((y - knob_h / 2) / track_h)

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w / 2
        track_w = 12
        track_x = cx - track_w / 2
        knob_h = 36

        # 轨道槽
        painter.setBrush(QBrush(QColor("#2A1808")))
        painter.setPen(QPen(QColor("#5D3A1A"), 2))
        painter.drawRoundedRect(track_x, 8, track_w, h - 16, 6, 6)

        # 轨道内部金属
        painter.setBrush(QBrush(QColor("#7F8C8D")))
        painter.drawRoundedRect(track_x + 3, 12, track_w - 6, h - 24, 3, 3)

        # 把手位置
        track_h = h - 16 - knob_h
        ky = 8 + self._pos * track_h

        # 红色把手
        grad = QRadialGradient(cx - 3, ky + knob_h/2 - 3, knob_h/2)
        grad.setColorAt(0, QColor("#FF6B6B"))
        grad.setColorAt(1, QColor("#C0392B"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#5D3A1A"), 2))
        painter.drawRoundedRect(cx - 22, ky, 44, knob_h, 8, 8)

        # 把手高光线
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawLine(cx - 12, ky + 8, cx + 12, ky + 8)

        # 底部触发区提示
        if self._pos >= self._threshold:
            painter.setPen(QPen(QColor("#FFD700"), 2))
            painter.drawText(QRectF(0, h - 25, w, 20), Qt.AlignCenter, "松手!")


# ============================================================
#  霓虹灯牌
# ============================================================
class NeonSignWidget(QWidget):
    """右侧霓虹灯牌装饰。"""

    def __init__(self, text="幸运", parent=None):
        super().__init__(parent)
        self._text = text
        self.setFixedSize(80, 120)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # 背景板
        painter.setBrush(QBrush(QColor("#1A0F05")))
        painter.setPen(QPen(QColor("#D4A017"), 2))
        painter.drawRoundedRect(2, 2, w - 4, h - 4, 8, 8)

        # 霓虹文字
        font = QFont("Microsoft YaHei", 22, QFont.Bold)
        painter.setFont(font)

        # 闪烁效果
        glow = 200 if self._timer.isActive() else 100
        for color, offset in [(QColor(255, 50, 50, glow), 0), (QColor(255, 150, 150, 120), 2)]:
            painter.setPen(QPen(color, 3))
            painter.drawText(QRectF(offset, offset, w - offset*2, h - offset*2),
                             Qt.AlignCenter, self._text)

        # 底部小字
        painter.setPen(QPen(QColor("#F5D061")))
        painter.setFont(QFont("Microsoft YaHei", 9))
        painter.drawText(QRectF(0, h - 25, w, 20), Qt.AlignCenter, "LUCKY")


# ============================================================
#  复古海报
# ============================================================
class PosterWidget(QWidget):
    """左侧复古海报装饰。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(110, 180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # 泛黄纸张
        painter.setBrush(QBrush(QColor("#F5E6C8")))
        painter.setPen(QPen(QColor("#D4A017"), 2))
        painter.drawRect(0, 0, w, h)

        # 装饰图: 小孩剪影
        painter.setBrush(QBrush(QColor("#E74C3C")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(w*0.5, h*0.32), 18, 18)
        painter.drawRect(int(w*0.5 - 16), int(h*0.42), 32, 45)
        painter.drawRect(int(w*0.5 - 24), int(h*0.45), 12, 32)
        painter.drawRect(int(w*0.5 + 12), int(h*0.45), 12, 32)
        painter.drawRect(int(w*0.5 - 10), int(h*0.72), 10, 30)
        painter.drawRect(int(w*0.5), int(h*0.72), 10, 30)

        # 文字
        painter.setPen(QPen(QColor("#2C3E50")))
        painter.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        painter.drawText(QRectF(0, 10, w, 20), Qt.AlignCenter, "童年回忆")
        painter.setFont(QFont("Microsoft YaHei", 8))
        painter.drawText(QRectF(5, h - 30, w - 10, 20), Qt.AlignCenter, "奖券多多\n快乐无限")


# ============================================================
#  中奖弹窗
# ============================================================
class PrizeDialog(QDialog):
    """复古中奖结果弹窗。"""

    def __init__(self, prize_name, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedSize(400, 420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._prize_name = prize_name
        self._is_again = (prize_name == "再来一次")
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("prizeDialog")
        self.setStyleSheet("""
            #prizeDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C1810, stop:1 #4A2818);
                border: 3px solid #D4A017;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("再来一次!" if self._is_again else "恭喜中奖!")
        title.setStyleSheet("""
            color: #FFD700; font-size: 30px; font-weight: bold;
            font-family: 'Microsoft YaHei';
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #D4A017; max-height: 2px; border: none;")
        line.setFixedHeight(2)
        layout.addWidget(line)

        prize = QLabel(self._prize_name)
        color = "#BDC3C7" if self._is_again else "#FF6B6B"
        prize.setStyleSheet(f"""
            color: {color}; font-size: 36px; font-weight: bold;
            font-family: 'Microsoft YaHei';
        """)
        prize.setAlignment(Qt.AlignCenter)
        layout.addWidget(prize)

        msg = QLabel("拉杆再来一次!" if self._is_again else "请到兑奖处领取!")
        msg.setStyleSheet("color: #F5D061; font-size: 14px;")
        msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg)

        # 奖品图片
        self._setup_image(layout)

        btn = QPushButton("确定")
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF6B6B, stop:1 #C0392B);
                color: white; font-size: 16px; font-weight: bold;
                border: 2px solid #D4A017; border-radius: 20px;
            }
            QPushButton:hover { background: #E74C3C; }
        """)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    def _setup_image(self, layout):
        """根据奖品名称加载图片，不存在则显示占位提示。"""
        import os

        image_label = QLabel()
        image_label.setFixedSize(220, 160)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("""
            border: 2px dashed #D4A017;
            border-radius: 12px;
            background: #2C1810;
        """)

        if self._is_again:
            image_label.setText("♻ 再来一次")
            image_label.setStyleSheet(image_label.styleSheet() + "color: #BDC3C7; font-size: 18px;")
        else:
            # 图片文件名：奖品名.png（去除文件系统不友好字符）
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_dir = os.path.join(base_dir, "images")
            img_path = os.path.join(img_dir, f"{self._prize_name}.png")

            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(220, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled)
                    image_label.setStyleSheet("border: 2px solid #D4A017; border-radius: 12px; background: #2C1810;")
                else:
                    image_label.setText(f"图片加载失败\n{self._prize_name}")
                    image_label.setStyleSheet(image_label.styleSheet() + "color: #95A5A6; font-size: 12px;")
            else:
                image_label.setText(f"暂无图片\n{self._prize_name}")
                image_label.setStyleSheet(image_label.styleSheet() + "color: #7F8C8D; font-size: 12px;")

        layout.addWidget(image_label, alignment=Qt.AlignCenter)

    def mousePressEvent(self, event):
        pass


# ============================================================
#  历史记录面板
# ============================================================
class HistoryPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPanel")
        self.setFixedWidth(180)
        self.setStyleSheet("""
            #historyPanel {
                background: rgba(44, 24, 16, 220);
                border: 2px solid #D4A017;
                border-radius: 15px;
            }
            QLabel { color: #F5D061; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel("抽奖记录")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self._stats_label = QLabel("已抽 0 次")
        self._stats_label.setStyleSheet("color: #BDC3C7; font-size: 11px;")
        self._stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._stats_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #D4A017; max-height: 1px; border: none;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }"
                             "QScrollBar:vertical { width: 5px; background: transparent; }"
                             "QScrollBar::handle:vertical { background: #D4A017; border-radius: 2px; }")

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(3)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

        self._count = 0

    def add_record(self, prize_name, is_again=False):
        self._count += 1
        self._stats_label.setText(f"已抽 {self._count} 次")
        time_str = datetime.now().strftime("%H:%M:%S")
        color = "#95A5A6" if is_again else "#FF6B6B"
        item = QLabel(f"#{self._count} {prize_name}\n   {time_str}")
        item.setStyleSheet(f"""
            color: {color}; font-size: 11px; padding: 3px 6px;
            background: rgba(0,0,0,40); border-radius: 5px;
        """)
        item.setWordWrap(True)
        self._list_layout.insertWidget(self._list_layout.count() - 1, item)
        if self._list_layout.count() > 52:
            old = self._list_layout.takeAt(0)
            if old.widget():
                old.widget().deleteLater()


# ============================================================
#  主窗口
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("90后童年回忆抽奖大转盘")
        self.setFixedSize(1000, 720)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(16, 12, 16, 12)
        main.setSpacing(8)

        # 顶部标题牌
        self.title = QLabel("90 后 童 年 回 忆")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            color: #F5D061; font-size: 34px; font-weight: bold;
            font-family: 'Microsoft YaHei';
            letter-spacing: 10px;
            background: #A52A2A;
            border: 3px solid #D4A017;
            border-radius: 12px;
            padding: 6px 20px;
        """)
        main.addWidget(self.title, alignment=Qt.AlignCenter)

        # 中间区域
        mid = QHBoxLayout()
        mid.setSpacing(10)

        # 左侧: 海报
        left = QVBoxLayout()
        left.addWidget(PosterWidget())
        left.addStretch()
        mid.addLayout(left)

        # 中间: 转盘
        self.wheel = WheelWidget()
        mid.addWidget(self.wheel, alignment=Qt.AlignCenter)

        # 右侧: 拉杆 + 霓虹灯
        right = QVBoxLayout()
        right.setSpacing(8)
        right.addWidget(NeonSignWidget("幸运"))
        self.lever = LeverWidget()
        right.addWidget(self.lever, alignment=Qt.AlignCenter)
        mid.addLayout(right)

        # 右侧: 历史记录
        self.history = HistoryPanel()
        mid.addWidget(self.history)

        main.addLayout(mid)

        # 底部提示牌
        bottom = QLabel("幸运奖 再来一次")
        bottom.setAlignment(Qt.AlignCenter)
        bottom.setFixedSize(160, 50)
        bottom.setStyleSheet("""
            color: #A52A2A; font-size: 15px; font-weight: bold;
            background: #F5D061; border: 2px solid #A52A2A;
            border-radius: 8px;
        """)
        main.addWidget(bottom, alignment=Qt.AlignRight)

        # 信号
        self.wheel.spin_finished.connect(self._on_finished)
        self.lever.pulled.connect(self._on_spin)

        self._current_prize_index = None

    def _on_spin(self):
        if self.wheel.is_spinning() or self.lever.get_pos() < self.lever._threshold:
            return
        prize_index = self.wheel.spin()
        if prize_index is not None:
            self._current_prize_index = prize_index

    def _on_finished(self):
        if self._current_prize_index is not None:
            prize = PRIZES[self._current_prize_index]
            is_again = (prize["name"] == "再来一次")
            self.history.add_record(prize["name"], is_again)
            dialog = PrizeDialog(prize["name"], self)
            dialog.exec()
            self._current_prize_index = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


# ============================================================
#  程序入口
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
