"""renamepy - 批量文件重命名工具 入口文件。"""

import tkinter as tk

from app.ui.main_window import RenameApp


def main():
    root = tk.Tk()
    RenameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
