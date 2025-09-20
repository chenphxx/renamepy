import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform
import subprocess

# -----------------------------------
# Folder row block
# -----------------------------------
class FolderFrame:
    def __init__(self, parent_frame, app, index):
        self.parent_frame = parent_frame
        self.app = app
        self.index = index

        self.folder_path = ""
        self.files = []
        self.filtered_files = []

        # horizontal frame for controls
        self.row_frame = tk.Frame(self.parent_frame)
        self.row_frame.pack(fill=tk.X, pady=(5, 0), padx=5)

        # Select folder button
        self.btn_select = tk.Button(self.row_frame, text="选择文件夹", width=12, command=self.select_folder)
        self.btn_select.pack(side=tk.LEFT, padx=(0,5))

        # Path display
        self.entry_path = tk.Entry(self.row_frame, width=45, state="readonly")
        self.entry_path.pack(side=tk.LEFT, padx=(0,5), fill=tk.X, expand=True)

        # Filter dropdown
        self.file_types = ["全部"]
        self.selected_type = tk.StringVar(value="全部")
        self.option_menu = tk.OptionMenu(self.row_frame, self.selected_type, *self.file_types, command=self.filter_files)
        self.option_menu.config(width=8)
        self.option_menu.pack(side=tk.LEFT, padx=(0,5))

        # Delete button
        self.btn_delete = tk.Button(self.row_frame, text="删除", width=8, command=self.delete)
        self.btn_delete.pack(side=tk.LEFT, padx=(0,5))

        # Count label
        self.count_label = tk.Label(self.parent_frame, text="总数: 0 | 筛选: 0")
        self.count_label.pack(padx=5, pady=(0,2))

        # Listbox
        self.listbox = tk.Listbox(self.parent_frame, width=110, height=6)
        self.listbox.pack(padx=5, pady=(0,8))

        # Right-click menu
        self.listbox.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.listbox, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_file)
        self.context_menu.add_command(label="打开所在文件夹", command=self.open_folder)

    # ---------------- folder functions ----------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.entry_path.config(state="normal")
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, self.folder_path)
            self.entry_path.config(state="readonly")
            self.load_files()
            self.app.refresh_overall_counts()

    def load_files(self):
        self.files = []
        self.listbox.delete(0, tk.END)
        try:
            for f in os.listdir(self.folder_path):
                fp = os.path.join(self.folder_path, f)
                if os.path.isfile(fp):
                    self.files.append(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件夹失败: {e}")
            return

        extensions = sorted(set([os.path.splitext(f)[1] for f in self.files if "." in f]))
        self.file_types = ["全部"] + extensions

        # update dropdown
        menu = self.option_menu["menu"]
        menu.delete(0, "end")
        for ext in self.file_types:
            menu.add_command(label=ext, command=lambda e=ext: self.set_file_type(e))
        self.set_file_type("全部")

    def set_file_type(self, file_type):
        self.selected_type.set(file_type)
        self.filter_files()

    def filter_files(self, *_args):
        self.listbox.delete(0, tk.END)
        sel = self.selected_type.get()
        if sel == "全部" or not sel:
            self.filtered_files = list(self.files)
        else:
            self.filtered_files = [f for f in self.files if f.endswith(sel)]
        for f in self.filtered_files:
            self.listbox.insert(tk.END, f)
        # 更新计数显示
        self.count_label.config(text=f"总数: {len(self.files)} | 筛选: {len(self.filtered_files)}")
        self.app.refresh_overall_counts()

    def delete(self):
        # 直接删除，不提示
        self.row_frame.destroy()
        self.listbox.destroy()
        self.count_label.destroy()
        self.app.remove_folder_frame(self)

    # ---------------- right-click menu ----------------
    def show_context_menu(self, event):
        try:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def open_file(self):
        sel = self.listbox.curselection()
        if sel and self.folder_path:
            fname = self.listbox.get(sel[0])
            fpath = os.path.join(self.folder_path, fname)
            if os.path.exists(fpath):
                try:
                    if platform.system() == "Windows":
                        os.startfile(fpath)
                    elif platform.system() == "Darwin":
                        subprocess.call(["open", fpath])
                    else:
                        subprocess.call(["xdg-open", fpath])
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开文件: {e}")

    def open_folder(self):
        sel = self.listbox.curselection()
        if sel and self.folder_path:
            fname = self.listbox.get(sel[0])
            fpath = os.path.join(self.folder_path, fname)
            folder = os.path.dirname(fpath)
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer /select,"{fpath}"')
                elif platform.system() == "Darwin":
                    subprocess.call(["open", folder])
                else:
                    subprocess.call(["xdg-open", folder])
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件夹: {e}")

# -----------------------------------
# Main app
# -----------------------------------
class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        root.title("多文件夹文件重命名工具")
        root.geometry("980x740")

        self.folder_frames = []
        self.global_action = None
        self.cancel_flag = False

        # Top controls
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, pady=6, padx=6)

        self.btn_add = tk.Button(top_frame, text="多文件夹处理", command=self.add_folder_frame)
        self.btn_add.pack(side=tk.LEFT, padx=(0,8))

        tk.Label(top_frame, text="文件名前缀:").pack(side=tk.LEFT)
        self.entry_prefix = tk.Entry(top_frame, width=20)
        self.entry_prefix.pack(side=tk.LEFT, padx=(4,12))

        tk.Label(top_frame, text="起始数字:").pack(side=tk.LEFT)
        self.entry_start = tk.Entry(top_frame, width=10)
        self.entry_start.insert(0, "1")
        self.entry_start.pack(side=tk.LEFT, padx=(4,12))

        self.btn_rename = tk.Button(top_frame, text="重命名并保存文件", command=self.rename_and_save)
        self.btn_rename.pack(side=tk.LEFT, padx=(8, 4))

        self.btn_cancel = tk.Button(top_frame, text="取消处理", command=self.cancel_processing)
        self.btn_cancel.pack(side=tk.LEFT)

        # Middle scrollable area
        container = tk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))

        self.canvas = tk.Canvas(container)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._bind_mousewheel(self.canvas)

        # Bottom progress
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill=tk.X, pady=(0,8), padx=6)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0,8))

        self.progress_label = tk.Label(bottom_frame, text="0%")
        self.progress_label.pack(side=tk.LEFT, padx=(0,10))

        self.count_label = tk.Label(bottom_frame, text="已处理 0 / 0")
        self.count_label.pack(side=tk.LEFT)

        self.add_folder_frame()

    # ---------------- UI helpers ----------------
    def add_folder_frame(self):
        idx = len(self.folder_frames)
        ff = FolderFrame(self.inner_frame, self, idx)
        self.folder_frames.append(ff)
        self.root.after(50, self._update_scrollregion)

    def remove_folder_frame(self, ff):
        if ff in self.folder_frames:
            self.folder_frames.remove(ff)
        self.refresh_overall_counts()
        self.root.after(50, self._update_scrollregion)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mousewheel(self, widget):
        def _on_mousewheel(event):
            bbox = widget.bbox("all")
            if bbox:
                canvas_height = widget.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height <= canvas_height:
                    return
            if platform.system() == "Windows":
                widget.yview_scroll(-1*(event.delta//120), "units")
            elif platform.system() == "Darwin":
                widget.yview_scroll(-1*event.delta, "units")
        if platform.system() in ["Windows", "Darwin"]:
            widget.bind_all("<MouseWheel>", _on_mousewheel)
        else:
            widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
            widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))

    def refresh_overall_counts(self):
        total = sum(len(ff.filtered_files) for ff in self.folder_frames if ff.folder_path)
        self.count_label.config(text=f"已处理 0 / {total}")

    def cancel_processing(self):
        self.cancel_flag = True

    # ---------------- Core processing ----------------
    def rename_and_save(self):
        prefix = self.entry_prefix.get()
        try:
            start_num = int(self.entry_start.get())
        except ValueError:
            messagebox.showerror("错误", "起始数字必须为整数")
            return

        # select save folder
        save_folder = filedialog.askdirectory(title="选择保存目标文件夹")
        if not save_folder:
            return

        # 提示用户选择操作模式
        choice = messagebox.askyesnocancel(
            "保存模式选择",
            "请选择目标文件夹操作方式：\n\n是 = 清空文件夹\n否 = 在文件夹内新增\n取消 = 终止操作"
        )
        if choice is None:
            return  # 取消操作
        elif choice:
            # 清空目标文件夹
            for f in os.listdir(save_folder):
                fp = os.path.join(save_folder, f)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                except Exception as e:
                    messagebox.showerror("错误", f"无法删除文件: {fp}\n{e}")
                    return

        self.cancel_flag = False
        self.global_action = None

        all_files = []
        for ff in self.folder_frames:
            if ff.folder_path:
                all_files.extend([(ff.folder_path, f) for f in ff.filtered_files])

        total = len(all_files)
        processed_count = 0
        current_num = start_num

        for folder, fname in all_files:
            if self.cancel_flag:
                messagebox.showinfo("已取消", "操作已取消。")
                self._finalize_progress(processed_count, total)
                return

            src = os.path.join(folder, fname)
            ext = os.path.splitext(fname)[1]
            new_name = f"{prefix}{current_num}{ext}"
            dst = os.path.join(save_folder, new_name)

            # conflict handling
            while os.path.exists(dst):
                action = self._handle_conflict_dialog(new_name)
                if action == "cancel":
                    messagebox.showinfo("已取消", "操作已取消。")
                    self._finalize_progress(processed_count, total)
                    return
                elif action == "skip":
                    current_num += 1
                    processed_count += 1
                    self._update_progress(processed_count, total)
                    break
                elif action == "overwrite":
                    break

            if os.path.exists(dst) and self.global_action != "skip":
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    messagebox.showerror("错误", f"复制文件出错: {e}\n文件: {src}")
                    self._finalize_progress(processed_count, total)
                    return
            elif not os.path.exists(dst):
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    messagebox.showerror("错误", f"复制文件出错: {e}\n文件: {src}")
                    self._finalize_progress(processed_count, total)
                    return

            current_num += 1
            processed_count += 1
            self._update_progress(processed_count, total)

        self._finalize_progress(processed_count, total)
        if messagebox.askyesno("完成", "文件处理完成，是否现在打开目标文件夹？"):
            try:
                if platform.system() == "Windows":
                    os.startfile(save_folder)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", save_folder])
                else:
                    subprocess.call(["xdg-open", save_folder])
            except:
                pass

    # ---------------- Conflict handling ----------------
    def _handle_conflict_dialog(self, filename):
        if self.global_action == "overwrite":
            return "overwrite"
        if self.global_action == "skip":
            return "skip"

        choice = messagebox.askyesnocancel(
            "文件已存在",
            f"{filename} 已存在。\n\n是 = 覆盖\n否 = 跳过\n取消 = 终止操作"
        )
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

    # ---------------- Progress ----------------
    def _update_progress(self, processed, total):
        percent = (processed / total) * 100 if total else 0
        self.progress_var.set(percent)
        self.progress_label.config(text=f"{int(percent)}%")
        self.count_label.config(text=f"已处理 {processed} / {total}")
        self.root.update_idletasks()

    def _finalize_progress(self, processed, total):
        percent = int((processed / total) * 100) if total else 0
        self.progress_var.set(percent)
        self.progress_label.config(text=f"{percent}%")
        self.count_label.config(text=f"已处理 {processed} / {total}")
        self.root.update_idletasks()


# -----------------------------------
# Run
# -----------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
