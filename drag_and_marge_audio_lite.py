import os
import sys
import subprocess
import threading
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import natsort

COLORS = {
    'bg': '#1E1E1E', 'card': '#252526', 'text': '#E0E0E0', 'sub': '#9E9E9E',
    'accent': '#4CC2FF', 'progress': '#00E676', 'prog_bg': '#333333',
    'drop_bg': '#2D2D2D', 'drop_border': '#404040', 'drop_busy': '#252526',
    'error': '#FF5252', 'success': '#69F0AE'
}

FONT_NAME = "NanumGothic"
FONTS = {
    'head': (FONT_NAME, 11, "bold"), 'body': (FONT_NAME, 10),
    'small': (FONT_NAME, 9), 'drop': (FONT_NAME, 16, "bold"),
    'mono': ("Consolas", 9)
}

TEXTS = {
    'ko': {
        'title': "Audio Merger Lite", 
        'batch': "배치 크기", 
        'lang': "English",
        'drop': "여기에 파일을 드래그하거나\n클릭해서 선택하세요", 
        'busy': "작업 진행 중...",
        'ready': "시스템 준비 완료 (Lite)", 
        'analyze': "메타데이터 분석 중...",
        'proc': "처리 중 [ {} / {} ]", 
        'done': "작업 완료",
        'cancel': "취소됨", 
        'err_dep': "FFmpeg를 찾을 수 없습니다.\n시스템에 설치하거나 같은 폴더에 넣어주세요.",
        'dial_title': "파일 선택"
    },
    'en': {
        'title': "Audio Merger Lite", 
        'batch': "BATCH SIZE", 
        'lang': "한국어",
        'drop': "Drop Files Here", 
        'busy': "PROCESSING...",
        'ready': "SYSTEM READY (Lite)", 
        'analyze': "ANALYZING...",
        'proc': "PROCESSING [ {} / {} ]", 
        'done': "COMPLETED",
        'cancel': "CANCELLED", 
        'err_dep': "FFmpeg not found.\nPlease install it or place in app folder.",
        'dial_title': "Select Files"
    }
}

class AudioMergerApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'ko'
        self.exts = ['*.mp3', '*.mp4', '*.m4a', '*.wav', '*.flac', '*.aac', '*.ogg', '*.wma']
        self.is_running = False
        
        self.ffmpeg_bin, self.ffprobe_bin = self.find_dependencies()
        
        self.config_window()
        self.config_style()
        self.build_ui()
        self.refresh_text()
        
        if not self.ffmpeg_bin or not self.ffprobe_bin:
            messagebox.showerror("Error", TEXTS[self.lang]['err_dep'])

    def find_dependencies(self):
        ffmpeg = shutil.which('ffmpeg')
        ffprobe = shutil.which('ffprobe')

        if not ffmpeg:
            local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
            if os.path.exists(local_ffmpeg): ffmpeg = local_ffmpeg
            
        if not ffprobe:
            local_ffprobe = os.path.join(os.getcwd(), 'ffprobe.exe')
            if os.path.exists(local_ffprobe): ffprobe = local_ffprobe
            
        return ffmpeg, ffprobe

    def config_window(self):
        self.root.title("Audio Merger Lite")
        self.root.geometry("500x680")
        self.root.configure(bg=COLORS['bg'])
        self.root.attributes('-toolwindow', True)

    def config_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Sleek.Horizontal.TProgressbar",
                        troughcolor=COLORS['prog_bg'], background=COLORS['progress'],
                        darkcolor=COLORS['progress'], lightcolor=COLORS['progress'],
                        bordercolor=COLORS['bg'], thickness=4)

    def build_ui(self):
        # (기존 UI 코드와 동일하여 생략, 필요한 경우 이전 코드의 build_ui 그대로 사용)
        top = tk.Frame(self.root, bg=COLORS['bg'])
        top.pack(fill='x', padx=25, pady=25)

        bf = tk.Frame(top, bg=COLORS['bg'])
        bf.pack(side='left')
        self.lbl_batch = tk.Label(bf, font=FONTS['head'], bg=COLORS['bg'], fg=COLORS['sub'])
        self.lbl_batch.pack(side='left', padx=(0, 10))
        self.ent_batch = tk.Entry(bf, width=4, font=FONTS['head'], justify='center',
                                  bg=COLORS['card'], fg=COLORS['accent'], relief='flat', bd=5)
        self.ent_batch.insert(0, "20")
        self.ent_batch.pack(side='left')

        self.btn_lang = tk.Button(top, font=FONTS['small'], bg=COLORS['card'], fg=COLORS['sub'],
                                  activebackground=COLORS['accent'], activeforeground='white',
                                  relief='flat', bd=0, padx=12, pady=4, cursor="hand2",
                                  command=self.toggle_lang)
        self.btn_lang.pack(side='right')

        cont = tk.Frame(self.root, bg=COLORS['bg'], padx=25)
        cont.pack(expand=True, fill='both')
        self.drop_fr = tk.Frame(cont, bg=COLORS['drop_bg'],
                                highlightbackground=COLORS['drop_border'],
                                highlightthickness=1)
        self.drop_fr.pack(expand=True, fill='both', pady=(0, 20))
        self.drop_fr.pack_propagate(False)

        self.drop_lbl = tk.Label(self.drop_fr, bg=COLORS['drop_bg'], fg=COLORS['sub'],
                                 font=FONTS['drop'], cursor="hand2")
        self.drop_lbl.pack(fill='both', expand=True)
        self.drop_lbl.drop_target_register(DND_FILES)
        self.drop_lbl.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_lbl.bind("<Button-1>", self.on_click)

        bot = tk.Frame(self.root, bg=COLORS['bg'])
        bot.pack(fill='x', padx=25, pady=(0, 25))
        self.pbar = ttk.Progressbar(bot, style="Sleek.Horizontal.TProgressbar", mode="determinate")
        self.lbl_stat = tk.Label(bot, font=FONTS['mono'], bg=COLORS['bg'], fg=COLORS['accent'])
        self.lbl_stat.pack(side='bottom', anchor='w')

    def get_startup_info(self):
        if sys.platform == 'win32':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return si
        return None

    def toggle_busy(self, busy):
        self.is_running = busy
        txt = TEXTS[self.lang]
        if busy:
            self.drop_lbl.unbind("<Button-1>")
            self.drop_lbl.dnd_bind('<<Drop>>', lambda e: None)
            self.drop_lbl.config(bg=COLORS['drop_busy'], fg=COLORS['sub'], text=txt['busy'], cursor="wait")
            self.drop_fr.config(highlightthickness=0)
            self.ent_batch.config(state='disabled')
            self.btn_lang.config(state='disabled')
            self.pbar.pack(fill='x', pady=(0, 10))
        else:
            self.drop_lbl.bind("<Button-1>", self.on_click)
            self.drop_lbl.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_lbl.config(bg=COLORS['drop_bg'], fg=COLORS['sub'], text=txt['drop'], cursor="hand2")
            self.drop_fr.config(highlightthickness=1)
            self.ent_batch.config(state='normal')
            self.btn_lang.config(state='normal')
            self.pbar.pack_forget()
            self.pbar['value'] = 0

    def toggle_lang(self):
        self.lang = 'en' if self.lang == 'ko' else 'ko'
        self.refresh_text()

    def refresh_text(self):
        t = TEXTS[self.lang]
        self.root.title(t['title'])
        self.lbl_batch.config(text=t['batch'])
        self.btn_lang.config(text=t['lang'])
        if not self.is_running:
            self.drop_lbl.config(text=t['drop'])
            self.lbl_stat.config(text=t['ready'])
        else:
            self.drop_lbl.config(text=t['busy'])

    def get_meta(self, path):
        if not self.ffmpeg_bin: return 0.0, 44100 # 의존성 없으면 패스
        
        si = self.get_startup_info()
        dur, rate = 0.0, 44100
        try:
            cmd_d = [self.ffprobe_bin, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path]
            dur = float(subprocess.check_output(cmd_d, startupinfo=si).decode().strip())
        except: pass
        try:
            cmd_r = [self.ffprobe_bin, '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=sample_rate', '-of', 'default=noprint_wrappers=1:nokey=1', path]
            rate = int(subprocess.check_output(cmd_r, startupinfo=si).decode().strip())
        except: pass
        return dur, rate
    
    def ffmpeg_convert(self, inp, out, rate):
        si = self.get_startup_info()
        # self.ffmpeg_bin 사용
        cmd = [self.ffmpeg_bin, '-y', '-i', inp, '-acodec', 'pcm_s24le', '-ar', str(rate), '-ac', '2', out, '-loglevel', 'error']
        subprocess.run(cmd, startupinfo=si)

    def ffmpeg_merge(self, inputs, output):
        si = self.get_startup_info()
        lst = "concat_list.txt"
        with open(lst, 'w', encoding='utf-8') as f:
            for i in inputs: f.write(f"file '{os.path.abspath(i).replace(os.sep, '/')}'\n")
        
        # self.ffmpeg_bin 사용
        cmd = [self.ffmpeg_bin, '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', output, '-loglevel', 'error']
        subprocess.run(cmd, startupinfo=si)
        if os.path.exists(lst): os.remove(lst)

    def parse_paths(self, data):
        if sys.platform != 'win32': return data.split()
        paths, buf, curly = [], "", False
        for c in data:
            if c == '{': curly = True
            elif c == '}': curly = False
            elif c == ' ' and not curly:
                if buf: paths.append(buf); buf = ""
            else: buf += c
        if buf: paths.append(buf)
        return paths

    def on_click(self, e=None):
        if self.is_running: return
        if not self.ffmpeg_bin: return messagebox.showerror("Error", TEXTS[self.lang]['err_dep'])

        try: bs = int(self.ent_batch.get()); bs = bs if bs >=2 else 2
        except: return messagebox.showerror("Error", "Number only")
        
        fs = filedialog.askopenfilenames(title=TEXTS[self.lang]['dial_title'], filetypes=[("Media", " ".join(self.exts)), ("All", "*.*")])
        if fs: threading.Thread(target=self.prepare, args=(natsort.natsorted(list(fs)), bs), daemon=True).start()

    def on_drop(self, e):
        if self.is_running: return
        if not self.ffmpeg_bin: return messagebox.showerror("Error", TEXTS[self.lang]['err_dep'])

        try: bs = int(self.ent_batch.get()); bs = bs if bs >=2 else 2
        except: return messagebox.showerror("Error", "Number only")
        
        fs = self.parse_paths(e.data)
        exts = tuple(x.replace('*','') for x in self.exts)
        valid = [f for f in fs if f.lower().endswith(exts)]
        if valid: threading.Thread(target=self.prepare, args=(natsort.natsorted(valid), bs), daemon=True).start()

    def prepare(self, files, batch_size):
        self.root.after(0, lambda: self.toggle_busy(True))
        self.root.after(0, lambda: self.lbl_stat.config(text=TEXTS[self.lang]['analyze'], fg=COLORS['text']))
        self.root.after(0, lambda: self.pbar.config(mode='indeterminate'))
        self.root.after(0, lambda: self.pbar.start(10))

        max_rate = 44100
        batches = (len(files) + batch_size - 1) // batch_size
        preview = []
        folder = os.path.basename(os.path.dirname(files[0]))

        for i in range(batches):
            sub = files[i*batch_size : (i+1)*batch_size]
            bdur = 0
            for f in sub:
                d, r = self.get_meta(f)
                if r > max_rate: max_rate = r
                bdur += d
            size = (max_rate * 24 * 2 * bdur) / 8388608
            preview.append("Group {:02d}: {} Files / ~{:.2f} MB".format(i+1, len(sub), size))

        self.root.after(0, lambda: self.confirm(files, max_rate, batch_size, preview, folder))

    def confirm(self, files, rate, bs, info, folder):
        self.pbar.stop()
        self.pbar.config(mode='determinate')
        t = TEXTS[self.lang]
        
        pop = tk.Toplevel(self.root)
        pop.title("Confirm")
        pop.geometry("480x600")
        pop.configure(bg=COLORS['bg'])
        pop.attributes('-toolwindow', True)
        pop.protocol("WM_DELETE_WINDOW", lambda: self.cancel(pop))

        tk.Label(pop, text=f"Total: {len(files)} / {rate}Hz", font=FONTS['head'], bg=COLORS['bg'], fg=COLORS['text']).pack(pady=20)
        
        fr = tk.Frame(pop, bg=COLORS['bg'], padx=20)
        fr.pack(fill='both', expand=True)
        lb = tk.Listbox(fr, font=FONTS['mono'], bg=COLORS['card'], fg=COLORS['text'], relief='flat')
        lb.pack(fill='both', expand=True)
        for i in info: lb.insert(tk.END, i)

        bf = tk.Frame(pop, bg=COLORS['bg'])
        bf.pack(pady=20)
        
        tk.Button(bf, text="START", command=lambda: [pop.destroy(), threading.Thread(target=self.process, args=(files, rate, bs, folder), daemon=True).start()], bg=COLORS['accent'], fg='black', relief='flat').pack(side='left', padx=10)
        tk.Button(bf, text="CANCEL", command=lambda: self.cancel(pop), bg=COLORS['card'], fg='white', relief='flat').pack(side='left', padx=10)

    def cancel(self, pop):
        pop.destroy()
        self.toggle_busy(False)
        self.lbl_stat.config(text=TEXTS[self.lang]['cancel'], fg=COLORS['error'])

    def process(self, files, rate, bs, folder):
        base = os.path.dirname(files[0])
        out_dir = os.path.join(base, f"{folder}_Merged")
        tmp_dir = os.path.join(base, "temp_lite")
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)

        try:
            batches = (len(files) + bs - 1) // bs
            self.root.after(0, lambda: self.pbar.config(maximum=batches, value=0))
            
            for i in range(batches):
                sub = files[i*bs : (i+1)*bs]
                self.root.after(0, lambda v=i+1: self.lbl_stat.config(text=f"Processing {v}/{batches}", fg=COLORS['accent']))
                
                tmp_wavs = []
                for idx, f in enumerate(sub):
                    out = os.path.join(tmp_dir, f"{idx}.wav")
                    self.ffmpeg_convert(f, out, rate)
                    tmp_wavs.append(out)
                
                final = os.path.join(out_dir, f"{folder}_{i+1:03d}.wav")
                self.ffmpeg_merge(tmp_wavs, final)
                self.root.after(0, lambda v=i+1: self.pbar.config(value=v))

            self.root.after(0, lambda: messagebox.showinfo("Done", f"Saved to {out_dir}"))
            self.root.after(0, lambda: self.lbl_stat.config(text="Done", fg=COLORS['success']))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            if os.path.exists(tmp_dir): shutil.rmtree(tmp_dir)
            self.root.after(0, lambda: self.toggle_busy(False))

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AudioMergerApp(root)
    root.mainloop()