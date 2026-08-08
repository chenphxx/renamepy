# renamepy

## 关于

一款用于重命名文件夹内的文件的脚本软件 

1. 点击「选择文件夹」添加文件, 可用「筛选」只看特定扩展名 
2. 填写文件名前缀与起始数字, 点击「开始处理」
3. 保存位置选原文件夹 = 原地重命名; 选其他文件夹 = 复制并改名 
4. 点击文件列表中的文件, 可在下方预览内容 

## 依赖库

- Python 3.8+（仅标准库即可运行）
- Pillow: 图片预览（`pip install pillow`）
- openpyxl: Excel 表格预览（`pip install openpyxl`）
- PyInstaller: 打包（`pip install pyinstaller`）

## 打包命令

```bash
pyinstaller --noconfirm --clean renamepy.spec
# 或
pyinstaller --onefile --noconsole --name renamepy main.py
```
