# -*- coding: utf-8 -*-
"""全局配置：窗口、界面常量与主题配色（Discord 风格深色 / 浅色）。"""

import os

FONT_FAMILY = "Microsoft YaHei" if os.name == "nt" else "Arial"
WINDOW_TITLE = "renamepy"
WINDOW_SIZE = "1150x860"
WINDOW_MIN_SIZE = (980, 700)

# Discord 风格深色主题
DARK = {
    "bg": "#36393F",                  # 主背景（聊天区）
    "card": "#2F3136",                # 卡片 / 面板
    "card_border": "#26272B",         # 卡片边框
    "header": "#313338",              # 顶栏
    "header_border": "#232428",
    "text": "#DBDEE1",                # 主文字
    "text_secondary": "#949BA4",      # 次要文字
    "accent": "#5865F2",              # Discord 紫蓝
    "accent_hover": "#4752C4",
    "accent_selected": "#40444B",     # 选中行
    "accent_selected_fg": "#FFFFFF",
    "danger": "#ED4245",              # 危险操作（删除）
    "danger_hover": "#3A3D42",        # 危险操作悬停背景
    "button_secondary": "#4F545C",    # 灰色次要按钮
    "button_secondary_hover": "#686D73",
    "button_text": "#FFFFFF",
    "input": "#40444B",               # 输入框背景
    "input_border": "#202225",        # 输入框边框
    "row_alt": "#36393F",             # 表格隔行背景
    "heading_bg": "#2B2D31",          # 表头背景
    "heading_hover": "#36393F",       # 表头悬停
    "progress_trough": "#40444B",
    "progress_bar": "#5865F2",
    "preview_bg": "#1E1F22",          # 预览内容区（代码块底色）
    "menu_bg": "#18191C",             # 右键菜单背景
    "menu_hover": "#393C41",          # 右键菜单悬停
    "scrollbar": "#202225",
}

# Discord 风格浅色主题
LIGHT = {
    "bg": "#F2F3F5",
    "card": "#FFFFFF",
    "card_border": "#DADDE1",
    "header": "#E3E5E8",
    "header_border": "#D4D7DC",
    "text": "#2E3338",
    "text_secondary": "#747F8D",
    "accent": "#5865F2",
    "accent_hover": "#4752C4",
    "accent_selected": "#DCDEE0",
    "accent_selected_fg": "#2E3338",
    "danger": "#ED4245",
    "danger_hover": "#E8E8EA",
    "button_secondary": "#E3E5E8",
    "button_secondary_hover": "#D4D7DC",
    "button_text": "#4E5058",
    "input": "#EBEDEF",
    "input_border": "#D4D7DC",
    "row_alt": "#F2F3F5",
    "heading_bg": "#E3E5E8",
    "heading_hover": "#D4D7DC",
    "progress_trough": "#E3E5E8",
    "progress_bar": "#5865F2",
    "preview_bg": "#EDEFF2",
    "menu_bg": "#F6F7F9",
    "menu_hover": "#E4E7EB",
    "scrollbar": "#C7CCD1",
}

# 当前激活的主题（切换时原地更新，保持各模块引用一致）
COLORS = dict(DARK)
