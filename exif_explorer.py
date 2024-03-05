import tkinter
from tkinter import ttk, scrolledtext,filedialog
from tkinter import messagebox
import os
import glob
from PIL import Image, ImageTk
from PIL.ExifTags import Base,IFD,TAGS
from fractions import Fraction
import ctypes
#import subprocess
import webbrowser



PICTURE_SIZE = 200

WIDTH = 1280
HEIGHT = 720


class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        width = WIDTH
        height = HEIGHT
        self.master.geometry(str(width)+"x"+str(height)+"+"+str(int(self.screen_width/2-width/2))+"+"+str(int(self.screen_height/2-height/2)))  # centering     
        self.master.title("Exif Explorer")
        
        # frames
        self.input_frame = tkinter.Frame(self.master, width=WIDTH, height=100, bg='white')
        self.input_frame.grid(columnspan=2,column=0,row=0)
        self.output_frame = tkinter.Frame(self.master, width=(WIDTH-430), height=(HEIGHT-100), bg='white')
        self.output_frame.grid(column=0, row=1,rowspan=2)
        self.listbox_frame = tkinter.Frame(self.master, width=430,height=(HEIGHT-100)/2)
        self.listbox_frame.grid(column=1,row=1)
        self.filter_frame = tkinter.Frame(self.master, width=430,height=(HEIGHT-100)/2, bg='white')
        self.filter_frame.grid(column=1,row=2)
        
        
        # input_frame
        self.file_edit = ttk.Entry(self.input_frame, width=40, state='readonly')
        self.path_btn = ttk.Button(self.input_frame, text='Open', command=self.select_dir)
        self.file_edit.grid(column=0, row=0, sticky=tkinter.EW, padx=5)
        self.path_btn.grid(column=1, row=0, pady=10, padx=5)
        #self.path_btn.bind('<Button-1>', self.select_dir)


        # output_frame
        self.scroll_canvas = tkinter.Canvas(self.output_frame, width=(WIDTH-480), height=(HEIGHT-100), bg='white')
        self.scroll_canvas.grid(column=0, row=0)
        self.bar = tkinter.Scrollbar(self.output_frame, orient=tkinter.VERTICAL, repeatdelay=2000, repeatinterval=20)
        self.bar.grid(column=1, row=0, sticky='ns')
        self.bar.config(command=self.scroll_canvas.yview)
        self.scroll_canvas.config(yscrollcommand=self.bar.set)
        
        
        # listbox_frame
        ## check box
        ### model
        self.model_var = tkinter.BooleanVar()
        self.model_var.set(False)
        self.model_checkbox = tkinter.Checkbutton(self.listbox_frame, text="モデル", variable=self.model_var)
        self.model_checkbox.grid(column=0, row=0, columnspan=2, sticky=tkinter.W)
        ### lens
        self.lens_var = tkinter.BooleanVar()
        self.lens_var.set(False)
        self.lens_checkbox = tkinter.Checkbutton(self.listbox_frame, text="レンズ", variable=self.lens_var)
        self.lens_checkbox.grid(column=0, row=3, columnspan=2, sticky=tkinter.W)
        ## model_list_box
        self.scroll_model_y = tkinter.Scrollbar(self.listbox_frame, orient="vertical")
        self.scroll_model_x = tkinter.Scrollbar(self.listbox_frame, orient="horizontal")
        self.model_listbox = tkinter.Listbox(self.listbox_frame, height=5, width=48, selectmode="multiple", exportselection=False)
        self.model_listbox.grid(column=0,row=1)
        self.scroll_model_y.config(command=self.model_listbox.yview)
        self.scroll_model_x.config(command=self.model_listbox.xview)
        self.model_listbox.config(yscrollcommand=self.scroll_model_y.set, xscrollcommand=self.scroll_model_x.set)
        self.scroll_model_y.grid(column=1,row=1,sticky='ns')
        self.scroll_model_x.grid(column=0, row=2,sticky='we')
        ## lens_list_box
        self.scroll_lens_y = tkinter.Scrollbar(self.listbox_frame, orient="vertical")
        self.scroll_lens_x = tkinter.Scrollbar(self.listbox_frame, orient="horizontal")
        self.lens_listbox = tkinter.Listbox(self.listbox_frame, height=5, width=48, selectmode="multiple", exportselection=False)
        self.lens_listbox.grid(column=0,row=4)
        self.scroll_lens_y.config(command=self.lens_listbox.yview)
        self.scroll_lens_x.config(command=self.lens_listbox.xview)
        self.lens_listbox.config(yscrollcommand=self.scroll_lens_y.set, xscrollcommand=self.scroll_lens_x.set)
        self.scroll_lens_y.grid(column=1,row=4,sticky='ns')
        self.scroll_lens_x.grid(column=0, row=5,sticky='we')
        
        
        # filter_frame
        ## label text
        self.info_text = "ディレクトリ内の画像ファイル数：　\n・焦点距離：　～　 ・絞り値：　～　\n・露光時間：　～　　・ISO：　～　"
        self.info = tkinter.Label(self.filter_frame, text=self.info_text, bg="white")
        self.info.grid(column=0, row=0, columnspan=5, sticky=tkinter.W, padx=10, pady=5)
        ## check box
        self.param_var = []
        self.param_checkbox = []
        for i in range(4):
            var = tkinter.BooleanVar()
            var.set(False)
            self.param_checkbox.append(tkinter.Checkbutton(self.filter_frame, text="", variable=var))
            self.param_var.append(var)
        for index, p in enumerate(self.param_checkbox):
            p.grid(column=0, row=index+1,  pady=10, padx=5, sticky=tkinter.W)
        ### focus
        self.param_checkbox[0].configure(text="焦点距離")
        ### f number
        self.param_checkbox[1].configure(text="絞り値")
        ### speed
        self.param_checkbox[2].configure(text="露光時間")
        ### iso
        self.param_checkbox[3].configure(text="ISO")
        ## check boxes for range selection
        self.range_checkbox = []
        self.range_var = []
        for i in range(4):
            var = tkinter.BooleanVar()
            var.set(True)
            self.range_checkbox.append(tkinter.Checkbutton(self.filter_frame, text="範囲選択", variable=var, bg="white"))
            self.range_var.append(var)
        for index, r in enumerate(self.range_checkbox):
            r.grid(column=1, row=index+1,  pady=10, padx=5)
        ## entries(BOTTOM)
        self.edit_bottom = []
        for i in range(4):
            self.edit_bottom.append(ttk.Entry(self.filter_frame, width=8))
        for index, e in enumerate(self.edit_bottom):
            e.grid(column=2, row=index+1,  pady=10, padx=5)
        ## labels
        self.labels = []
        for i in range(4):
            self.labels.append(tkinter.Label(self.filter_frame, text=" ～ ", bg="white"))
        for index, l in enumerate(self.labels):
            l.grid(column=3, row=index+1,  pady=10, padx=5)
        ## entries(UP)
        self.edit_up= []
        for i in range(4):
            self.edit_up.append(ttk.Entry(self.filter_frame, width=8))
        for index, e in enumerate(self.edit_up):
            e.grid(column=4, row=index+1,  pady=10, padx=5)
        ## button
        self.readme_btn = ttk.Button(self.filter_frame, text='README', command=self.read_me)
        self.search_btn = ttk.Button(self.filter_frame, text='Search', command=self.search_images, state=tkinter.DISABLED)
        self.readme_btn.grid(column=0, row=5, pady=10, padx=5)
        self.search_btn.grid(column=1, row=5, pady=10, padx=5)
        
        
        # each global list
        self.img_list = []
        self.path_list = []
        self.filter_path_list = []
        
    # PICTURE_SIZE*PICTURE_SIZE内に画像を収める 
    def resize_image(self, file_name, orientation):
        img = Image.open(file_name)
        try:
            if(orientation == 8):
                img = img.rotate(90, expand=True)
            elif(orientation == 6):
                img = img.rotate(270, expand=True)
        except KeyError:
            pass
        img_width, img_height = img.size
        reducation_size =  img_width if img_width >= img_height else img_height
        return img.resize(( int( img_width * (PICTURE_SIZE/reducation_size)), int(img_height * (PICTURE_SIZE/reducation_size)) ))
        
    

    def select_dir(self):
        path = os.getcwd()
        
        dir_path=""
        dir_path = filedialog.askdirectory(initialdir=path)
        if(dir_path==""):
            print("haven't select file path")
            return 0
        
        self.file_edit.configure(state='normal')
        self.file_edit.delete(0, tkinter.END)
        self.file_edit.insert(0, dir_path)
        self.file_edit.configure(state='readonly')
        # only jpg or png files
        files = glob.glob(dir_path + "\\*.jpg")
        files.extend(glob.glob(dir_path + '\\*.png'))
        if len(files) == 0 :
            messagebox.showerror(title="エラー", message="対象ディレクトリに画像ファイルがありません。")
            return 0 
        
        # initialize
        for i in range(4):
            self.param_var[i].set(False)
            self.range_var[i].set(True)
            self.edit_bottom[i].delete(0, tkinter.END)
            self.edit_up[i].delete(0, tkinter.END)
        
        self.path_list = files
        index_list = list(range(len(files)))
        
        model_list = []
        lens_list = []
        focus_list = []
        fnum_list = []
        speed_list = []
        iso_list = []
        
        
        self.search_btn.configure(state=tkinter.DISABLED)
        
        for file in files:    
            with Image.open(file) as img:
                exif = img.getexif()
            exif_ifd = exif.get_ifd(IFD.Exif)
            try:
                model = exif[Base.Model]
                if (model not in model_list and model != ""):
                    model_list.append(model)
            except KeyError:
                pass
            try:
                lens = exif_ifd[Base.LensModel]
                if (lens not in lens_list and lens != ""):
                    lens_list.append(lens)
            except KeyError:
                pass
            try:
                focus_list.append(exif_ifd[Base.FocalLength])
            except KeyError:
                pass
            try:
                fnum_list.append(exif_ifd[Base.FNumber])
            except KeyError:
                pass
            try:
                speed_list.append(exif_ifd[Base.ExposureTime])
            except KeyError:
                pass
            try:
                iso_list.append(exif_ifd[Base.ISOSpeedRatings])
            except KeyError:
                pass
        
        param_list =[focus_list,fnum_list,speed_list,iso_list]

        model_value=tkinter.StringVar()
        model_value.set(model_list)
        self.model_listbox.configure(listvariable=model_value)
        lens_value=tkinter.StringVar()
        lens_value.set(lens_list)
        self.lens_listbox.configure(listvariable=lens_value)
            
        try:
            for i in range(4):
                if (i==2):
                    bottom_list = str((Fraction(min(param_list[i]))).limit_denominator()).split('/')
                    up_list = str((Fraction(max(param_list[i]))).limit_denominator()).split('/')
                    self.edit_bottom[i].insert(0,int(bottom_list[1]))
                    self.edit_up[i].insert(0,int(up_list[1]))
                else:
                    self.edit_bottom[i].insert(0,min(param_list[i]))
                    self.edit_up[i].insert(0,max(param_list[i]))
            
            update = "ディレクトリ内の画像ファイル数："+str(len(files))+"\n"
            update += "・焦点距離："+self.edit_bottom[0].get()+"～"+self.edit_up[0].get()
            update += " ・絞り値："+self.edit_bottom[1].get()+"～"+self.edit_up[1].get()+"\n"
            update += "・露光時間：1/"+self.edit_bottom[2].get()+"～1/"+self.edit_up[2].get()
            update += " ・ISO："+self.edit_bottom[3].get()+"～"+self.edit_up[3].get()
            self.info.configure(text=update)
            
            self.search_btn.configure(state="normal")
        except ValueError:
            print("[ValueError Exists] ")
            update = "ディレクトリ内の画像ファイル数："+str(len(files))+"\n"
            update += "・焦点距離：　～　 ・絞り値：　～　\n・露光時間：　～　 ・ISO：　～　"
            self.info.configure(text=update)
        
        self.show_images(self.scroll_canvas, index_list)
    
    def sub_window_delete(self):
        messagebox.showerror(title="Error", message="Image loading is in process!")

    def path_click(self, event, path):
        #subprocess.Popen(['explorer', path],shell=True)
        webbrowser.open_new(path)

    def show_images(self, canvas, path_index):
        canvas.delete('all')
        self.img_list.clear()
        
        sub_window = tkinter.Toplevel()
        width = 420
        height = 90
        sub_window.title('Loading')
        sub_window.geometry(str(width)+'x'+str(height)+'+'+str(int(self.screen_width/2-width/2))+"+"+str(int(self.screen_height/2-height/2)))
        sub_window.wm_protocol('WM_DELETE_WINDOW', self.sub_window_delete)
        sub_window.grid_rowconfigure((0, 1), weight=1)
        p = ttk.Progressbar(sub_window, length=400, mode="determinate", maximum=1)
        p.grid(row=0, padx=10)
        p.configure(value=0)
        l = ttk.Label(sub_window, text='')
        l.grid(row=1, padx=10)
        
        column_counts = int(self.scroll_canvas.winfo_width() / PICTURE_SIZE)
        height = int(len(path_index)/column_counts)*PICTURE_SIZE
        
        if (int(len(path_index)%column_counts) != 0):
            height = height + PICTURE_SIZE
        self.scroll_canvas.config(scrollregion=(0, 0, (WIDTH-480), height))
        self.bar.config(command=self.scroll_canvas.yview)
        self.scroll_canvas.config(yscrollcommand=self.bar.set)
        
        for index, file_index in enumerate(path_index):
            img = Image.open(self.path_list[file_index])
            exif = img.getexif()
            try:
                orientation = exif[Base.Orientation]
            except KeyError:
                orientation = 1
            img = self.resize_image(self.path_list[file_index], orientation)
            img = ImageTk.PhotoImage(image=img)
            row_no =  int(index / column_counts)
            column_no = int(index % column_counts)
            img_canvas = canvas.create_image(column_no * PICTURE_SIZE, row_no * PICTURE_SIZE, anchor='nw', image=img)
            
            canvas.tag_bind(img_canvas, "<Button-1>",lambda event, path=self.path_list[file_index]: self.path_click(event, path))
            self.img_list.append(img)
            l.configure(text=f'loading images... {index+1}/{len(path_index)}')
            p.configure(value=(index+1)/len(path_index))
            p.update()
            l.update()
            sub_window.lift()
        
        p.stop()
        sub_window.destroy()
    
    def search_images(self):
        self.filter_path_list.clear()
        
        
        error_incorrect_flag=False
        error_minmax_flag=False
        error_minmax = [False,False,False,False]
        error_incorrect = [False,False,False,False]
        for index, file_name in enumerate(self.path_list):
            flag = True
            
            img = Image.open(file_name)
            exif = img.getexif()
            exif_ifd = exif.get_ifd(IFD.Exif)
                
            if (self.model_var.get() and len(self.model_listbox.curselection()) != 0):
                model_list = []
                for i in self.model_listbox.curselection():
                    model_list.append(self.model_listbox.get(i))
                try:
                    if (exif[Base.Model] not in model_list):
                        flag = False
                except KeyError:
                    flag = False
                    pass
            
            if(self.lens_var.get() and len(self.lens_listbox.curselection()) != 0):
                lens_list = []
                for i in self.lens_listbox.curselection():
                    lens_list.append(self.lens_listbox.get(i))
                try:
                    if (exif_ifd[Base.LensModel] not in lens_list):
                        flag = False
                except KeyError:
                    flag = False
                    pass
            
 
            exif_use = [Base.FocalLength, Base.FNumber, Base.ExposureTime, Base.ISOSpeedRatings]
            
            i=0
            for var in self.param_var:
                if(var.get()):
                    valueerror_flag = False
                    
                    try:
                        if(self.range_var[i].get()):
                            if(i==2):
                                min = 1 / int(self.edit_bottom[i].get())
                                max = 1 / int(self.edit_up[i].get())
                            else:
                                min = float(self.edit_bottom[i].get())
                                max = float(self.edit_up[i].get())
                            if (min > max):
                                error_minmax_flag = True
                                error_minmax[i] = True
                                #print("Error: The maximum value is smaller than the minimum value.")
                                if (float(exif_ifd[exif_use[i]]) < min):
                                    flag = False
                            else:
                                if (float(exif_ifd[exif_use[i]]) < min or max < float(exif_ifd[exif_use[i]])):
                                    flag = False
                        else:
                            if(i==2):
                                if((1 / int(self.edit_bottom[i].get())) != float(exif_ifd[exif_use[i]])):
                                    flag = False
                            else:
                                if(float(self.edit_bottom[i].get()) != float(exif_ifd[exif_use[i]]) ):
                                    flag = False
                    except ValueError:
                        error_incorrect[i] = True
                        error_incorrect_flag = True
                        valueerror_flag = True
                        pass
                    except KeyError:
                        # image doesn't have the exif param
                        if(not valueerror_flag):
                            flag=False
                i+=1
            
                
            if (flag):
                self.filter_path_list.append(index)
        
        
        error_text = ""
        if(error_incorrect_flag):
            print(error_incorrect)
            # str([index+1 for index, e in error_minmax_flag if e])+
            error_text += str([index+1 for index, e in enumerate(error_incorrect) if e])+"：不正な値が入力されたため条件検索が正しく行えませんでした。\n"
        if(error_minmax_flag):
            error_text += str([index+1 for index, e in enumerate(error_minmax) if e])+"：左の入力値と右の入力値の大小関係が不整合であるため、左の入力値のみ考慮します。\n"
        if(error_minmax_flag or  error_incorrect_flag):
            error_text += "[1:焦点距離，2:絞り値，3:露光時間，4:ISO]\n"
            messagebox.showerror(title="エラー", message=error_text)
        
        if (len(self.filter_path_list)!=0):
            print(len(self.filter_path_list))
            self.show_images(self.scroll_canvas, self.filter_path_list)
        else:
            messagebox.showinfo("No Image files" , message="条件に合う画像ファイルはありませんでした。")
            
                
            
    
    def read_me(self):
        info = "Exif Exploreはフォルダ内の画像ファイルをメタデータで絞り込み検索を行うアプリケーションです。\n"
        info += "JPGファイルかPNGファイルの画像ファイルが対象です。\n"
        info += "使用したカメラのモデル名、レンズ名、焦点距離、絞り値、露光時間、ISOの情報を基に、フォルダ内の画像を検索し表示する事が出来ます。\n"
        info += "それぞれの項目にチェックを入れると、その項目で選択または入力した内容で条件検索する事が出来ます。\n"
        info += "「範囲選択」にチェックを入れると、２つの数値間の範囲で条件検索、チェックを外すと左の入力欄の数値に一致するもののみで条件検索します。\n"
        info += "数値の入力欄には、半角数字のみを使用して正しい値を入力してください。（ダメな例：4.2.0 ← 小数点を複数含む）\n"
        info += "露光時間の入力欄には、分母の値を整数で入力してください。(例：1/3200 →「3200」)\n"
        info += "それぞれの数値は左が小さい値、右が大きい値となり、その値の範囲を検索の条件とします。\n"
        info += "表示されている画像をクリックすると「フォト」アプリで画像を確認する事が出来ます。\n"
        messagebox.showinfo("READ ME" , message=info)

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass

    root = tkinter.Tk()
    app = Application(master = root)
    app.mainloop()
