import tkinter as tk
import numpy as np
from tkinter import filedialog, ttk
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import threading



class FitsPreviewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FITS Previewer")
        self.geometry("1000x800")

        self.fits_data = None

        # 设置UI
        self.setup_ui()
        
    def open_file_thread(self):
        threading.Thread(target=self.open_file).start()
            
    def setup_ui(self):
        # 文件打开按钮
        self.open_button = ttk.Button(self, text="Open FITS File", command=self.open_file_thread)
        self.open_button.pack(side=tk.TOP, padx=10, pady=10)

        # 创建带垂直滚动条的扩展按钮区域
        self.extensions_scroll_frame = ttk.Frame(self)
        self.extensions_canvas = tk.Canvas(self.extensions_scroll_frame)
        self.extensions_scrollbar = ttk.Scrollbar(self.extensions_scroll_frame, orient="vertical", command=self.extensions_canvas.yview)
        self.extensions_frame = ttk.Frame(self.extensions_canvas)
        
        self.extensions_canvas.create_window((0, 0), window=self.extensions_frame, anchor="nw")
        self.extensions_canvas.configure(yscrollcommand=self.extensions_scrollbar.set)

        self.extensions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.extensions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.extensions_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 更新canvas的滚动区域大小
        self.extensions_frame.bind("<Configure>", lambda e: self.extensions_canvas.configure(scrollregion=self.extensions_canvas.bbox("all")))

        # 数据展示区域
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("FITS files", "*.*")])
        if filename:
            self.fits_data = fits.open(filename, ignore_missing_simple=True)
            self.show_extensions()

    def show_extensions(self):
        # 清除现有的扩展按钮
        for widget in self.extensions_frame.winfo_children():
            widget.destroy()

        # 为每个扩展创建按钮
        # ext_label = tk.Label(self.data_frame, text="Extentions:", font=('Arial', 12, 'bold'))
        # ext_label.pack(fill=tk.BOTH, padx=10, pady=(5, 0))
        for i, hdu in enumerate(self.fits_data):
            btn = ttk.Button(
                self.extensions_frame, 
                text=f"Extension {i}: {hdu.name}", 
                command=lambda i=i: self.show_extension_data(i)
                )
            btn.pack(side=tk.TOP, padx=5, pady=5)


    def show_extension_data(self, index):
    # 清除旧的数据展示区域内容
        for widget in self.data_frame.winfo_children():
            widget.destroy()

        hdu = self.fits_data[index]

        # Header标题
        header_label = tk.Label(self.data_frame, text="Header Information", font=('Arial', 12, 'bold'))
        header_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))


        # 显示Header信息
        header_frame = ttk.Frame(self.data_frame)
        header_frame.pack(fill=tk.BOTH, padx=10, pady=5)

        # 显示Header信息的Text控件和垂直滚动条
        header_text = tk.Text(header_frame, height=10, wrap="word")
        header_scroll = ttk.Scrollbar(header_frame, orient="vertical", command=header_text.yview)
        header_text.configure(yscrollcommand=header_scroll.set)

        header_str = '\n'.join([f'{key}: {value}' for key, value in hdu.header.items()])
        header_text.insert(tk.END, header_str)

        header_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        header_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 判断是否为图像数据并显示
        if hdu.is_image:
            # 图像数据标题
            data_label = tk.Label(self.data_frame, text="Image Data", font=('Arial', 12, 'bold'))
            data_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))

            fig, ax = plt.subplots(figsize=(5, 4))
            if hdu.data is None:
                pass
            elif len(hdu.data.shape)==1:
                ax.imshow(np.reshape(hdu.data, newshape=(1, hdu.data.shape[0])), cmap='gray', origin='lower')
            else:
                ax.imshow(hdu.data, cmap='gray', origin='lower')
            ax.axis('off')
            canvas = FigureCanvasTkAgg(fig, master=self.data_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            canvas.draw()
        else:
            # 表格数据标题\
            data_label = tk.Label(self.data_frame, text="Table Data", font=('Arial', 12, 'bold'))
            data_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
            table_frame = ttk.Frame(self.data_frame)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            # 创建表格和滚动条
            table = ttk.Treeview(table_frame, show="headings")
            
            # 配置表格列
            data = hdu.data
            columns = data.names
            table["columns"] = columns
            for col in columns:
                table.heading(col, text=col)
                table.column(col, anchor="center", width=50)  # 设置默认列宽

            # 填充数据
            for row in data:
                table.insert('', tk.END, values=row)

            # 布局表格和滚动条
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
            hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
            table.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

            table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            hsb.pack(side=tk.BOTTOM, fill=tk.X)


if __name__ == "__main__":
    app = FitsPreviewer()
    app.mainloop()
