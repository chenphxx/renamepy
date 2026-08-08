# -*- coding: utf-8 -*-
"""单个文件夹处理块的界面控件（扁平化卡片样式）。"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import COLORS, FONT_FAMILY
from file_ops import open_file, reveal_file


class FolderBlock:
    """表示一个文件夹卡片：路径、筛选下拉框、计数、文件列表、删除按钮。"""

    def __init__(self, parent, app, idx):
        self.parent = parent
        self.app = app
        self.idx = idx

        self.folder_path = ""
        self.files = []           # 文件名列表（仅名称）
        self.filtered_files = []  # 筛选后的文件名列表

        # 卡片容器（白底 + 细边框）
        self.frame_outer = tk.Frame(
            self.parent,
            bg=COLORS["card"],
            highlightbackground=COLORS["card_border"],
            highlightthickness=1,
        )
        self.frame_outer.pack(fill="x", padx=2, pady=(0, 10))

        # 卡片头部：标题 + 删除按钮
        header = tk.Frame(self.frame_outer, bg=COLORS["card"])
        header.pack(fill="x", padx=14, pady=(10, 8))

        self.lbl_title = tk.Label(
            header,
            text=f"文件夹 {idx}",
            bg=COLORS["card"],
            fg=COLORS["accent"],
            font=(FONT_FAMILY, 11, "bold"),
        )
        self.lbl_title.pack(side="left")

        self.btn_delete = ttk.Button(header, text="删除", style="Danger.TButton", command=self.delete_block)
        self.btn_delete.pack(side="right")

        # 操作行：选择按钮、路径、筛选、计数
        row = tk.Frame(self.frame_outer, bg=COLORS["card"])
        row.pack(fill="x", padx=14, pady=(0, 8))

        self.btn_select = ttk.Button(row, text="选择文件夹", style="Ghost.TButton", command=self.select_folder)
        self.btn_select.pack(side="left")

        self.entry_path = ttk.Entry(row, font=(FONT_FAMILY, 10))
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(10, 10))

        ttk.Label(row, text="筛选", style="Card.TLabel").pack(side="left")
        self.combo_filter = ttk.Combobox(row, state="readonly", width=10)
        self.combo_filter.pack(side="left", padx=(6, 10))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        self.lbl_counts = ttk.Label(row, text="总数 0 · 筛选 0", style="CardMuted.TLabel", width=20, anchor="center")
        self.lbl_counts.pack(side="left")

        # 文件列表区域（固定高度，可通过下方拖拽手柄调整）
        self.tree_frame = tk.Frame(self.frame_outer, bg=COLORS["card"], height=180)
        self.tree_frame.pack_propagate(False)
        self.tree_frame.pack(fill="x", padx=14, pady=(0, 6))

        self.tree = ttk.Treeview(self.tree_frame, columns=("name", "ext"), show="headings", height=6)
        self.tree.heading("name", text="文件名")
        self.tree.heading("ext", text="后缀")
        self.tree.column("name", width=700, anchor="w")
        self.tree.column("ext", width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side="left", fill="y", padx=(8, 0))

        # 拖拽手柄：调整文件列表高度
        self.tree_drag = tk.Frame(self.frame_outer, bg=COLORS["card_border"], cursor="sb_v_double_arrow", height=5)
        self.tree_drag.pack(fill="x", padx=14, pady=(0, 10))
        self._tree_drag_y = None
        self._tree_drag_h = None
        self.tree_drag.bind("<Button-1>", self._tree_drag_press)
        self.tree_drag.bind("<B1-Motion>", self._tree_drag_motion)
        self.tree_drag.bind("<Enter>", lambda e: self.tree_drag.configure(bg=COLORS["accent"]))
        self.tree_drag.bind("<Leave>", lambda e: self.tree_drag.configure(bg=COLORS["card_border"]))

        # 右键菜单（打开文件/打开文件夹）
        self.menu = tk.Menu(
            self.tree,
            tearoff=0,
            bg=COLORS["menu_bg"],
            fg=COLORS["text"],
            activebackground=COLORS["menu_hover"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
        )
        self.menu.add_command(label="打开文件", command=self.open_selected_file)
        self.menu.add_command(label="打开所在文件夹", command=self.open_file_location)

        # 绑定事件
        self.tree.bind("<Double-1>", lambda e: self.open_selected_file())
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._on_tree_select())

    # ---------------- 操作 ----------------
    def _tree_drag_press(self, event):
        self._tree_drag_y = event.y_root
        self._tree_drag_h = self.tree_frame.winfo_height()

    def _tree_drag_motion(self, event):
        if self._tree_drag_y is None:
            return
        delta = event.y_root - self._tree_drag_y
        new_h = max(100, min(self._tree_drag_h + delta, 420))
        self.tree_frame.configure(height=new_h)
        self.app.root.update_idletasks()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.folder_path = folder
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, folder)
        self.load_files()
        self.app.refresh_overall_counts()

    def load_files(self):
        self.files = []
        self.filtered_files = []
        # 只列出文件夹下的文件（不递归）
        try:
            for name in os.listdir(self.folder_path):
                full = os.path.join(self.folder_path, name)
                if os.path.isfile(full):
                    self.files.append(name)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件夹失败: {e}")
            return

        # 计算扩展名
        exts = sorted({os.path.splitext(n)[1].lower() for n in self.files if os.path.splitext(n)[1]})
        values = ["全部"] + exts if exts else ["全部"]
        self.combo_filter["values"] = values
        self.combo_filter.set("全部")
        self.apply_filter()

    def apply_filter(self):
        sel = self.combo_filter.get()
        if sel == "全部" or not sel:
            self.filtered_files = list(self.files)
        else:
            self.filtered_files = [n for n in self.files if n.lower().endswith(sel)]
        # 刷新 treeview
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, name in enumerate(self.filtered_files):
            ext = os.path.splitext(name)[1].lower()
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            self.tree.insert("", "end", values=(name, ext), tags=(tag,))
        # 更新计数
        self.lbl_counts.config(text=f"总数 {len(self.files)} · 筛选 {len(self.filtered_files)}")
        self.app.refresh_overall_counts()
        # 列表内容变化后清空预览
        self.app.show_preview(None)

    def _on_tree_select(self):
        self.app.show_preview(self.get_selected_tree_path())

    def delete_block(self):
        # 按要求直接删除，不提示
        self.frame_outer.destroy()
        # 从 app 中移除
        self.app.remove_folder(self)

    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def get_selected_tree_path(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = sel[0]
        name = self.tree.item(item, "values")[0]
        if not self.folder_path:
            return None
        return os.path.join(self.folder_path, name)

    def open_selected_file(self):
        path = self.get_selected_tree_path()
        if not path:
            return
        try:
            open_file(path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")

    def open_file_location(self):
        path = self.get_selected_tree_path()
        if not path:
            return
        try:
            reveal_file(path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开所在文件夹: {e}")
