# -*- coding: utf-8 -*-
"""文件系统操作：打开文件/文件夹、定位文件、清空目录、原位重命名辅助。"""

import os
import subprocess
import sys
import uuid


def open_file(path):
    """使用系统默认程序打开文件。"""
    if os.name == "nt":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


def open_folder(path):
    """在系统文件管理器中打开文件夹。"""
    if os.name == "nt":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


def reveal_file(path):
    """打开文件所在文件夹，并在文件管理器中选中该文件。"""
    folder = os.path.dirname(path)
    if os.name == "nt":
        # explorer 的 /select 参数必须作为单个参数传入，路径含空格也能正常工作
        subprocess.Popen(["explorer", f"/select,{path}"])
    else:
        open_folder(folder)


def clear_files_in_folder(folder):
    """删除文件夹内的所有文件（不递归，保留子文件夹）。

    返回被删除文件的完整路径列表，便于调用方统计。
    """
    removed = []
    for name in os.listdir(folder):
        full = os.path.join(folder, name)
        if os.path.isfile(full):
            os.remove(full)
            removed.append(full)
    return removed


# ---------------- 原位重命名辅助 ----------------

def prepare_inplace_temps(folder, jobs):
    """将目标名与其他待处理源文件同名的文件先移到临时名，防止互相覆盖。

    jobs: [(源文件名, 目标文件名), ...]，均位于 folder 内。
    返回 {源文件名: 临时完整路径}；中途出错时自动还原已移动的文件并抛出异常。
    """
    moved = {}
    try:
        target_names = {new_name for _, new_name in jobs}
        for src_name, new_name in jobs:
            if src_name == new_name or src_name not in target_names:
                continue
            tmp = os.path.join(folder, f".{src_name}.renamepy_tmp_{uuid.uuid4().hex}")
            os.rename(os.path.join(folder, src_name), tmp)
            moved[src_name] = tmp
    except Exception:
        restore_inplace_temps(folder, moved)
        raise
    return moved


def restore_inplace_temp(folder, src_name, tmp):
    """把单个临时文件还原为原名（仅当原名尚不存在时）。"""
    original = os.path.join(folder, src_name)
    if os.path.exists(tmp) and not os.path.exists(original):
        try:
            os.rename(tmp, original)
        except OSError:
            pass


def restore_inplace_temps(folder, moved):
    """还原所有仍处于临时名的文件。"""
    for src_name, tmp in list(moved.items()):
        restore_inplace_temp(folder, src_name, tmp)
