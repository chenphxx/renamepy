import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ----------------- 配置 -----------------
FONT_FAMILY = "Microsoft YaHei" if os.name == "nt" else "Arial"
WINDOW_TITLE = "批量重命名工具 - 秋白"
WINDOW_SIZE = "1100x780"

# 支持的文件列表（无需图片依赖）
# ------------------------------------------------

class FolderBlock:
    """表示一个文件夹行块：路径、筛选下拉框、计数、文件列表、删除按钮"""
    def __init__(self, parent, app, idx):
        self.parent = parent
        self.app = app
        self.idx = idx

        self.folder_path = ""
        self.files = []           # 文件名列表（仅名称）
        self.filtered_files = []  # 筛选后的文件名列表

        # 此文件夹控件的容器框（标签框样式）
        self.frame_outer = ttk.LabelFrame(self.parent, text=f"文件夹 {idx+1}", padding=(8,6))
        self.frame_outer.pack(fill="x", padx=8, pady=(8,4))

        # 顶部行：选择按钮、路径显示、筛选下拉框、计数标签、删除按钮
        top_row = ttk.Frame(self.frame_outer)
        top_row.pack(fill="x", pady=(0,6))

        self.btn_select = ttk.Button(top_row, text="选择文件夹", width=14, command=self.select_folder)
        self.btn_select.pack(side="left")

        self.entry_path = ttk.Entry(top_row)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(8,8))

        ttk.Label(top_row, text="筛选:").pack(side="left")
        self.combo_filter = ttk.Combobox(top_row, state="readonly", width=12)
        self.combo_filter.pack(side="left", padx=(6,8))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        self.lbl_counts = ttk.Label(top_row, text="总数: 0 | 筛选: 0", width=20, anchor="center")
        self.lbl_counts.pack(side="left", padx=(8,8))

        self.btn_delete = ttk.Button(top_row, text="删除", width=8, command=self.delete_block)
        self.btn_delete.pack(side="left")

        # 用于显示文件的treeview
        columns = ("name", "ext")
        self.tree = ttk.Treeview(self.frame_outer, columns=columns, show="headings", height=6)
        self.tree.heading("name", text="文件名")
        self.tree.heading("ext", text="后缀")
        self.tree.column("name", width=700, anchor="w")
        self.tree.column("ext", width=120, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(0,6))

        # 为treeview添加垂直滚动条
        self.tree_scroll = ttk.Scrollbar(self.frame_outer, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side="left", fill="y")

        # 右键菜单（打开文件/打开文件夹）
        self.menu = tk.Menu(self.tree, tearoff=0)
        self.menu.add_command(label="打开文件", command=self.open_selected_file)
        self.menu.add_command(label="打开所在文件夹", command=self.open_file_location)

        # 绑定事件
        self.tree.bind("<Double-1>", lambda e: self.open_selected_file())
        self.tree.bind("<Button-3>", self._on_right_click)

    # ---------------- 操作 ----------------
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
        self.combo_filter['values'] = values
        self.combo_filter.set("全部")
        self.apply_filter()

    def apply_filter(self):
        sel = self.combo_filter.get()
        if sel == "全部" or not sel:
            self.filtered_files = list(self.files)
        else:
            self.filtered_files = [n for n in self.files if n.lower().endswith(sel)]
        # 刷新treeview
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, name in enumerate(self.filtered_files):
            ext = os.path.splitext(name)[1].lower()
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            self.tree.insert("", "end", values=(name, ext), tags=(tag,))
        # 更新计数
        self.lbl_counts.config(text=f"总数: {len(self.files)} | 筛选: {len(self.filtered_files)}")
        self.app.refresh_overall_counts()

    def delete_block(self):
        # 按要求直接删除，不提示
        self.frame_outer.destroy()
        # 从app中移除
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
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")

    def open_file_location(self):
        path = self.get_selected_tree_path()
        if not path:
            return
        folder = os.path.dirname(path)
        try:
            if os.name == "nt":
                subprocess.Popen(f'explorer /select,"{path}"')
            elif sys.platform == "darwin":
                subprocess.call(["open", folder])
            else:
                subprocess.call(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开所在文件夹: {e}")

# ----------------- 主程序 -----------------
class RenameApp:
    def __init__(self, root):
        self.root = root
        root.title(WINDOW_TITLE)
        root.geometry(WINDOW_SIZE)

        self.folder_blocks = []
        self.global_action = None  # None / "overwrite" / "skip"
        self.cancel_flag = False

        # ---- 样式 ----
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass
        default_font = (FONT_FAMILY, 10)
        self.style.configure("TLabel", font=default_font)
        self.style.configure("TButton", font=default_font, padding=6)
        self.style.configure("TEntry", font=default_font)
        self.style.configure("TCombobox", font=default_font)
        self.style.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"))
        self.style.configure("Status.TLabel", foreground="#333")

        # Treeview行标签
        # 注意：tag_configure 必须在每个tree实例上设置，创建treeview后再配置

        # ---- 顶部控制区 ----
        top_frame = ttk.Frame(root, padding=(8,8))
        top_frame.pack(side="top", fill="x")

        self.btn_add_folder = ttk.Button(top_frame, text="多文件夹处理", command=self.add_folder)
        self.btn_add_folder.pack(side="left")

        ttk.Label(top_frame, text="文件名前缀:").pack(side="left", padx=(12,4))
        self.entry_prefix = ttk.Entry(top_frame, width=24)
        self.entry_prefix.pack(side="left")
        ttk.Label(top_frame, text="起始数字:").pack(side="left", padx=(12,4))
        self.entry_start = ttk.Entry(top_frame, width=10)
        self.entry_start.insert(0, "1")
        self.entry_start.pack(side="left")

        self.btn_rename = ttk.Button(top_frame, text="重命名并保存文件", command=self.rename_and_save)
        self.btn_rename.pack(side="left", padx=(12,6))

        self.btn_cancel = ttk.Button(top_frame, text="取消处理", command=self.cancel_process)
        self.btn_cancel.pack(side="left")

        # ---- 中间可滚动区域（文件夹块） ----
        container = ttk.Frame(root)
        container.pack(side="top", fill="both", expand=True, padx=8, pady=(0,6))

        # canvas + 垂直滚动条用于放置文件夹块
        self.canvas = tk.Canvas(container)
        self.v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")

        self.blocks_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0,0), window=self.blocks_frame, anchor="nw")
        self.blocks_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # 鼠标滚轮绑定（仅内容高于canvas时滚动）
        self._bind_mousewheel(self.canvas)

        # ---- 底部状态区 ----
        bottom = ttk.Frame(root, padding=(6,6))
        bottom.pack(side="bottom", fill="x")

        self.progress = ttk.Progressbar(bottom, orient="horizontal", mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0,8))

        self.lbl_percent = ttk.Label(bottom, text="0%", width=6)
        self.lbl_percent.pack(side="left", padx=(0,8))

        self.lbl_count = ttk.Label(bottom, text="已处理 0 / 0", width=18)
        self.lbl_count.pack(side="left")

        # 初始化时添加一个文件夹块
        self.add_folder()

    # ---------------- UI辅助 ----------------
    def add_folder(self):
        idx = len(self.folder_blocks) + 1
        block = FolderBlock(self.blocks_frame, self, idx)
        # 配置treeview行颜色
        block.tree.tag_configure("oddrow", background="#f8f8f8")
        block.tree.tag_configure("evenrow", background="#ffffff")
        self.folder_blocks.append(block)
        # 稍后更新滚动区域
        self.root.after(50, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def remove_folder(self, block):
        if block in self.folder_blocks:
            self.folder_blocks.remove(block)
        # 重新编号剩余的labelframe（可选）
        for i, b in enumerate(self.folder_blocks, start=1):
            b.frame_outer.config(text=f"文件夹 {i}")
        self.refresh_overall_counts()
        self.root.after(50, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def _bind_mousewheel(self, widget):
        # 使用平台相关的绑定，仅内容高于canvas时滚动
        def on_mousewheel(event):
            bbox = widget.bbox("all")
            if bbox is None:
                return
            canvas_h = widget.winfo_height()
            content_h = bbox[3] - bbox[1]
            if content_h <= canvas_h:
                return
            if os.name == "nt":  # Windows
                widget.yview_scroll(-1 * (event.delta // 120), "units")
            elif os.name == "mac":  # macOS可能是'darwin'，tkinter事件delta不同，尝试兼容
                widget.yview_scroll(-1 * event.delta, "units")
            else:
                # Linux等X11系统，鼠标滚轮可能用Button-4/Button-5
                pass

        if os.name == "nt" or os.name == "mac" or True:
            widget.bind_all("<MouseWheel>", on_mousewheel)
            widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
            widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))

    def refresh_overall_counts(self):
        total = sum(len(b.filtered_files) for b in self.folder_blocks if b.folder_path)
        # 当前已处理为0（进度条在处理时显示）
        self.lbl_count.config(text=f"已处理 0 / {total}")

    # ---------------- 取消处理 ----------------
    def cancel_process(self):
        self.cancel_flag = True

    # ---------------- 核心处理 ----------------
    def rename_and_save(self):
        prefix = self.entry_prefix.get().strip()
        if not prefix:
            messagebox.showwarning("警告", "请输入文件名前缀")
            return
        try:
            start_num = int(self.entry_start.get())
        except ValueError:
            messagebox.showwarning("警告", "起始数字必须为整数")
            return

        # 收集所有块中的文件
        items = []
        for b in self.folder_blocks:
            if b.folder_path:
                for name in b.filtered_files:
                    items.append((b.folder_path, name))
        if not items:
            messagebox.showwarning("警告", "没有可处理的文件")
            return

        save_folder = filedialog.askdirectory(title="选择保存目标文件夹")
        if not save_folder:
            return

        # 询问是否清空目标文件夹或新增（是=清空，否=新增，取消=终止）
        choice = messagebox.askyesnocancel("保存模式选择", "请选择目标文件夹操作方式：\n\n是 = 清空文件夹\n否 = 在文件夹内新增\n取消 = 终止操作")
        if choice is None:
            return
        if choice:
            # 只清空文件（不清空文件夹）
            try:
                for f in os.listdir(save_folder):
                    fp = os.path.join(save_folder, f)
                    if os.path.isfile(fp):
                        os.remove(fp)
            except Exception as e:
                messagebox.showerror("错误", f"清空目标文件夹失败: {e}")
                return

        # 重置标志
        self.cancel_flag = False
        self.global_action = None

        total = len(items)
        processed = 0
        cur_num = start_num

        # 初始化进度条UI
        self.progress["maximum"] = 100
        self.progress["value"] = 0
        self.lbl_percent.config(text="0%")
        self.lbl_count.config(text=f"已处理 0 / {total}")
        self.root.update_idletasks()

        for idx, (folder, fname) in enumerate(items, start=1):
            if self.cancel_flag:
                messagebox.showinfo("已取消", "操作已取消")
                self._finalize_progress(processed, total)
                return

            src = os.path.join(folder, fname)
            ext = os.path.splitext(fname)[1]
            new_name = f"{prefix}{cur_num}{ext}"
            dst = os.path.join(save_folder, new_name)

            # 处理冲突
            if os.path.exists(dst):
                action = self._conflict_dialog(new_name)
                if action == "cancel":
                    messagebox.showinfo("已取消", "操作已取消")
                    self._finalize_progress(processed, total)
                    return
                elif action == "skip":
                    cur_num += 1
                    processed += 1
                    self._update_progress(processed, total)
                    continue
                # 覆盖 => 继续复制

            try:
                shutil.copy2(src, dst)
            except Exception as e:
                messagebox.showerror("错误", f"复制失败: {src}\n{e}")
                self._finalize_progress(processed, total)
                return

            cur_num += 1
            processed += 1
            self._update_progress(processed, total)

        # 处理完成
        self._finalize_progress(processed, total)
        if messagebox.askyesno("完成", "文件处理完成，是否现在打开目标文件夹？"):
            try:
                if os.name == "nt":
                    os.startfile(save_folder)
                elif sys.platform == "darwin":
                    subprocess.call(["open", save_folder])
                else:
                    subprocess.call(["xdg-open", save_folder])
            except:
                pass

    def _conflict_dialog(self, filename):
        """返回 'overwrite'、'skip' 或 'cancel'。支持全局应用。"""
        if self.global_action == "overwrite":
            return "overwrite"
        if self.global_action == "skip":
            return "skip"

        choice = messagebox.askyesnocancel("文件已存在", f"{filename} 已存在。\n\n是 = 覆盖\n否 = 跳过\n取消 = 终止操作")
        if choice is None:
            return "cancel"
        elif choice:
            apply_all = messagebox.askyesno("应用到全部", "是否对后续冲突文件全部覆盖？")
            if apply_all:
                self.global_action = "overwrite"
            return "overwrite"
        else:
            apply_all = messagebox.askyesno("应用到全部", "是否对后续冲突文件全部跳过？")
            if apply_all:
                self.global_action = "skip"
            return "skip"

    def _update_progress(self, processed, total):
        percent = int((processed / total) * 100) if total else 0
        self.progress["value"] = percent
        self.lbl_percent.config(text=f"{percent}%")
        self.lbl_count.config(text=f"已处理 {processed} / {total}")
        self.root.update_idletasks()

    def _finalize_progress(self, processed, total):
        percent = int((processed / total) * 100) if total else 0
        self.progress["value"] = percent
        self.lbl_percent.config(text=f"{percent}%")
        self.lbl_count.config(text=f"已处理 {processed} / {total}")
        self.root.update_idletasks()

# ----------------- 程序入口 -----------------
if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()
    