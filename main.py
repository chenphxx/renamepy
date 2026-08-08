# -*- coding: utf-8 -*-
"""程序入口：启动批量重命名工具。"""

import tkinter as tk

from rename_app import RenameApp


def main():
    root = tk.Tk()
    RenameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
