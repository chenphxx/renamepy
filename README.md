# renamepy

一款用于重命名文件夹内的文件的脚本软件 

1. 点击`选择文件夹`添加文件, 可用`筛选`只看特定扩展名 
2. 填写文件名前缀与起始数字, 点击`开始处理` 
3. 保存位置选原文件夹 = 原地重命名; 选其他文件夹 = 复制并改名 
4. 点击文件列表中的文件, 可在预览内容 

## 快速开始

> Python 3.10及以上 

```bash
python -m venv .venv 
.venv\Scripts\activate 
pip install -r requirements.txt 
python main.py 
```

## 打包为`.exe`文件 

```bash
pyinstaller --onefile --noconsole --name renamepy main.py
```
