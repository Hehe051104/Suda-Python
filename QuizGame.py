import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as sc
import tkinter.messagebox as mb
import openpyxl as px
import sys
import datetime
import time
import pygame # 导入pygame
from Exam import *


# --- 主题颜色定义 ---
LIGHT_THEME = {
    "app_bg": "#ECECEC",
    "frame_bg": "#ECECEC",
    "text_fg": "#000000",
    "button_bg": "#F0F0F0",
    "button_fg": "#000000",
    "entry_bg": "#FFFFFF",
    "text_widget_bg": "#FFFFFF",
    "notebook_bg": "#ECECEC",
    "tab_bg": "#DCDCDC",
    "tab_fg": "#000000",
    "tab_selected_bg": "#FFFFFF",
    "disabled_fg": "#A3A3A3",
}

DARK_THEME = {
    "app_bg": "#2E2E2E",
    "frame_bg": "#2E2E2E",
    "text_fg": "#EAEAEA",
    "button_bg": "#555555",
    "button_fg": "#EAEAEA",
    "entry_bg": "#3C3C3C",
    "text_widget_bg": "#3C3C3C",
    "notebook_bg": "#2E2E2E",
    "tab_bg": "#4A4A4A",
    "tab_fg": "#EAEAEA",
    "tab_selected_bg": "#5A5A5A",
    "disabled_fg": "#777777",
}


class QuizApp:
    def __init__(self, master):
        self.master = master
        self.qusAndAns = QusAndAns()
        self.logstate = 0
        self.totalScore = 0
        self.indexofselect = 0
        self.indexofblank = 0
        self.indexofjudge = 0 # 新增判断题索引

        self.question_start_time = None
        self.question_timer_id = None

        self.current_theme = 'light'
        self.style = ttk.Style(self.master)

        self.setup_audio()
        self.setup_data()
        self.setup_ui()
        self.start_timer()
        self.apply_theme() # 应用初始主题

    def setup_audio(self):
        try:
            pygame.mixer.init()
            self.correct_sound = pygame.mixer.Sound("correct.wav")
            self.incorrect_sound = pygame.mixer.Sound("incorrect.wav")
            self.warning_sound = None # 暂时禁用警告音
            self.sound_enabled = True
        except Exception as e:
            self.sound_enabled = False
            error_msg = f"无法加载音效！程序将静音运行。\n\n" \
                        f"请确保：\n" \
                        f"1. Pygame已正确安装。\n" \
                        f"2. correct.wav 和 incorrect.wav 文件在程序目录中。\n\n" \
                        f"错误详情: {e}"
            mb.showwarning("音频加载失败", error_msg)

    def setup_data(self):
        # 获取题目数据
        self.qus_select = self.qusAndAns.getQusOfSelect()
        self.ans_select = self.qusAndAns.getAnsOfSelect()
        self.analyze_select = self.qusAndAns.getAnalyzeOfSelect()
        self.rand_select = self.qusAndAns.getRandQusOfSelect()
        self.totalSelect, self.iselectScore = self.qusAndAns.getTotalAndiScore()

        self.qus_blank = self.qusAndAns.getQusOfBlank()
        self.ans_blank = self.qusAndAns.getAnsOfBlank()
        self.analyze_blank = self.qusAndAns.getAnalyzeOfblank()
        self.rand_blank = self.qusAndAns.getRandQusOfBlank()
        self.totalblank, self.iblankScore = self.qusAndAns.getTotalAndiScore1()

        # 新增：获取判断题数据
        self.qus_judge = self.qusAndAns.getQusOfJudge()
        self.ans_judge = self.qusAndAns.getAnsOfJudge()
        self.analyze_judge = self.qusAndAns.getAnalyzeOfJudge()
        self.rand_judge = self.qusAndAns.getRandQusOfJudge()
        self.totalJudge, self.ijudgeScore = self.qusAndAns.getTotalAndiScore2()
        
        self.eName, self.eTime = self.qusAndAns.getEnameAndEtime()

    def setup_ui(self):
        # 窗口设置
        x = (self.master.winfo_screenwidth() - 800) // 2
        y = (self.master.winfo_screenheight() - 600) // 2
        self.master.geometry(f'800x600+{x}+{y}')
        self.master.resizable(width=False, height=False)
        self.master.title(f'QuizGame{" "*50}测验名称: {self.eName}{" "*10}测试时长(分)：{self.eTime}')

        # 将选项卡控件放在主区域
        self.note = ttk.Notebook(self.master)
        
        # 底部信息栏
        self.bottom_frame = ttk.Frame(self.master)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))

        self.L_info = ttk.Label(self.bottom_frame, text='剩余时间：')
        self.L_info.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.theme_button = ttk.Button(self.bottom_frame, text="切换深色模式", command=self.toggle_theme)
        self.theme_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 选项卡控件置于底部栏之上
        self.note.pack(fill='both', expand=True, padx=5, pady=5)
        self.note.bind('<Button-1>', self.click_tab)

        # 创建各个选项卡
        self.create_login_tab()
        self.create_select_tab()
        self.create_blank_tab()
        self.create_judge_tab() # 新增：创建判断题选项卡

    def start_timer(self):
        # 设置固定的30分钟倒计时
        self.timer = myTimer(self.master, self.L_info, 30 * 60, self)
        # 登录成功后再启动计时器
    
    # --- 登录页面 ---
    def create_login_tab(self):
        frml = ttk.Frame(self.note)
        self.note.add(frml, text='登录')

        text1 = sc.ScrolledText(frml, wrap=tk.WORD)
        text1.pack(padx=20, pady=10, fill='both', expand=True)
        try:
            game_info = TxtFile.getGameInfo()
            text1.insert('0.0', '\n\n' + 'QuizGame游戏说明'.center(90) + '\n\n\n\n' + game_info)
        except Exception as e:
            text1.insert('0.0', f'加载游戏说明失败: {e}')
        text1.config(state='disabled')

        login_area_frame = ttk.Frame(frml)
        login_area_frame.pack(pady=10)

        lno = ttk.Label(login_area_frame, text='学号:')
        self.tno = ttk.Entry(login_area_frame)
        lname = ttk.Label(login_area_frame, text='姓名:')
        self.tname = ttk.Entry(login_area_frame)
        self.blogin = ttk.Button(login_area_frame, text='登录', command=self.login)

        lno.grid(column=0, row=0, padx=2, pady=5, sticky=tk.E)
        self.tno.grid(column=1, row=0, padx=2, pady=5, sticky=tk.W)
        lname.grid(column=0, row=1, padx=2, pady=5, sticky=tk.E)
        self.tname.grid(column=1, row=1, padx=2, pady=5, sticky=tk.W)
        self.blogin.grid(column=0, row=2, columnspan=2, pady=5)

    def login(self):
        sno = self.tno.get().strip()
        sname = self.tname.get().strip()
        stu = Stu()
        stu_info = stu.getStu()

        if (sno, sname) in stu_info:
            self.logstate = 1
            mb.showinfo('QuizGame', '登录成功，开始游戏!')
            
            # 解锁第一个题型选项卡
            if self.qus_select:
                self.note.tab(1, state='normal')
                self.note.select(1)
            elif self.qus_blank:
                self.note.tab(2, state='normal')
                self.note.select(2)
            elif self.qus_judge:
                self.note.tab(3, state='normal')
                self.note.select(3)
            else:
                self.game_over() # 没有题目
            
            self.tno.config(state='disabled')
            self.tname.config(state='disabled')
            self.blogin.config(state='disabled')
            self.timer.start() # 启动计时器
        else:
            mb.showerror('QuizGame', '学号或姓名错误，请重新输入!')

    def click_tab(self, event):
        if self.logstate == 0 and self.note.identify(event.x, event.y) != 'TNotebook.Tab':
            is_on_login_tab = self.note.index(self.note.select()) == 0
            if not is_on_login_tab:
                mb.showinfo('QuizGame', '请先登录后开始测验游戏！')

    # --- 选择题页面 ---
    def create_select_tab(self):
        self.frm_select = ttk.Frame(self.note)
        self.note.add(self.frm_select, text='选择题', state='disabled')
        
        self.Lqus_select = ttk.Label(self.frm_select, text='题目:')
        self.L_qtime_select = ttk.Label(self.frm_select, text='本题用时: 0s', font=('Arial', 10))
        self.tqus_select = sc.ScrolledText(self.frm_select, height=15, width=80, wrap=tk.WORD)
        self.Lans_select = ttk.Label(self.frm_select, text='解析:')
        self.tans_select = sc.ScrolledText(self.frm_select, height=15, width=20, wrap=tk.WORD)
        self.Lresult_select = ttk.Label(self.frm_select, font=('楷体', 14))
        self.bconfirm_select = ttk.Button(self.frm_select, text='确认', command=lambda: self.check_answer('select'))
        self.bnext_select = ttk.Button(self.frm_select, text='下一题', command=lambda: self.next_question('select'), state='disabled')

        # 布局
        self.Lqus_select.grid(column=0, row=0, padx=20, pady=10, sticky=tk.W)
        self.L_qtime_select.grid(column=0, row=0, padx=(100, 0), pady=10)
        self.Lans_select.grid(column=1, row=0, padx=5, pady=10, sticky=tk.W)
        self.tqus_select.grid(column=0, row=1, rowspan=10, padx=20, pady=5, sticky='nsew')
        self.tans_select.grid(column=1, row=1, rowspan=10, padx=5, pady=5, sticky='nsew')
        
        radio_frame = ttk.Frame(self.frm_select)
        radio_frame.grid(column=0, row=11, pady=10)
        
        self.v_select = tk.StringVar(value=None)
        self.rb_a = ttk.Radiobutton(radio_frame, text='A', variable=self.v_select, value='A')
        self.rb_b = ttk.Radiobutton(radio_frame, text='B', variable=self.v_select, value='B')
        self.rb_c = ttk.Radiobutton(radio_frame, text='C', variable=self.v_select, value='C')
        self.rb_d = ttk.Radiobutton(radio_frame, text='D', variable=self.v_select, value='D')
        self.rb_a.pack(side=tk.LEFT, padx=10)
        self.rb_b.pack(side=tk.LEFT, padx=10)
        self.rb_c.pack(side=tk.LEFT, padx=10)
        self.rb_d.pack(side=tk.LEFT, padx=10)
        
        self.Lresult_select.grid(column=0, row=12, pady=5)
        self.bconfirm_select.grid(column=0, row=13, pady=5)
        self.bnext_select.grid(column=0, row=14, pady=5)
        
        self.frm_select.grid_rowconfigure(1, weight=1)
        self.frm_select.grid_columnconfigure(0, weight=4)
        self.frm_select.grid_columnconfigure(1, weight=1)

        self.frm_select.bind('<Visibility>', lambda e: self.load_question('select'))
        
    def load_question(self, q_type):
        if q_type == 'select':
            if not self.qus_select: return
            # 清空上一题内容
            self.tqus_select.config(state='normal')
            self.tans_select.config(state='normal')
            self.tqus_select.delete('1.0', 'end')
            self.tans_select.delete('1.0', 'end')
            self.Lresult_select.config(text='')
            self.v_select.set(None)

            # 加载新题目
            q_index = self.rand_select[self.indexofselect]
            question_text = f"{self.indexofselect + 1}{self.qus_select[q_index]}"
            self.tqus_select.insert('1.0', question_text)
            self.tqus_select.config(state='disabled')
            self.tans_select.config(state='disabled')

            # 重置按钮状态
            for rb in [self.rb_a, self.rb_b, self.rb_c, self.rb_d]:
                rb.config(state='normal')
            self.bconfirm_select.config(state='normal')
            self.bnext_select.config(state='disabled')

        elif q_type == 'blank':
            if not self.qus_blank: return
            self.tqus_blank.config(state='normal')
            self.tans_blank.config(state='normal')
            self.tqus_blank.delete('1.0', 'end')
            self.tans_blank.delete('1.0', 'end')
            self.entry_blank.delete(0, 'end')
            self.Lresult_blank.config(text='')

            q_index = self.rand_blank[self.indexofblank]
            question_text = f"{self.indexofblank + 1}{self.qus_blank[q_index]}"
            self.tqus_blank.insert('1.0', question_text)
            self.tqus_blank.config(state='disabled')
            self.tans_blank.config(state='disabled')

            self.bconfirm_blank.config(state='normal')
            self.bnext_blank.config(state='disabled')

        elif q_type == 'judge':
            if not self.qus_judge: return
            self.tqus_judge.config(state='normal')
            self.tans_judge.config(state='normal')
            self.tqus_judge.delete('1.0', 'end')
            self.tans_judge.delete('1.0', 'end')
            self.Lresult_judge.config(text='')
            self.v_judge.set(None)

            q_index = self.rand_judge[self.indexofjudge]
            question_text = f"{self.indexofjudge + 1}{self.qus_judge[q_index]}"
            self.tqus_judge.insert('1.0', question_text)
            self.tqus_judge.config(state='disabled')
            self.tans_judge.config(state='disabled')

            for btn in [self.rb_true, self.rb_false]:
                btn.config(state='normal')
            self.bconfirm_judge.config(state='normal')
            self.bnext_judge.config(state='disabled')
        
        self.start_question_timer()

    def check_answer(self, q_type):
        correct = False
        if q_type == 'select':
            user_ans = self.v_select.get()
            if not user_ans:
                mb.showwarning("提示", "请选择一个选项！")
                return
            
            self.stop_question_timer()
            correct_ans_index = self.rand_select[self.indexofselect]
            correct_ans = self.ans_select[correct_ans_index]
            
            if user_ans == correct_ans:
                self.totalScore += self.iselectScore
                self.Lresult_select.config(text='回答正确！', foreground='green')
                if self.sound_enabled: self.correct_sound.play()
                correct = True
            else:
                self.Lresult_select.config(text=f'回答错误！正确答案: {correct_ans}', foreground='red')
                if self.sound_enabled: self.incorrect_sound.play()
            
            # 显示解析
            self.tans_select.config(state='normal')
            self.tans_select.delete('1.0', 'end')
            self.tans_select.insert('1.0', self.analyze_select[correct_ans_index])
            self.tans_select.config(state='disabled')

            for rb in [self.rb_a, self.rb_b, self.rb_c, self.rb_d]:
                rb.config(state='disabled')
            self.bconfirm_select.config(state='disabled')
            self.bnext_select.config(state='normal')

        elif q_type == 'blank':
            user_ans = self.entry_blank.get().strip()
            if not user_ans:
                mb.showwarning("提示", "请输入答案！")
                return
            
            self.stop_question_timer()
            correct_ans_index = self.rand_blank[self.indexofblank]
            correct_ans = self.ans_blank[correct_ans_index]

            if user_ans == correct_ans:
                self.totalScore += self.iblankScore
                self.Lresult_blank.config(text='回答正确！', foreground='green')
                if self.sound_enabled: self.correct_sound.play()
                correct = True
            else:
                self.Lresult_blank.config(text=f'回答错误！', foreground='red')
                if self.sound_enabled: self.incorrect_sound.play()

            self.tans_blank.config(state='normal')
            self.tans_blank.delete('1.0', 'end')
            self.tans_blank.insert('1.0', f"正确答案: {correct_ans}\n\n解析:\n{self.analyze_blank[correct_ans_index]}")
            self.tans_blank.config(state='disabled')
            
            self.bconfirm_blank.config(state='disabled')
            self.bnext_blank.config(state='normal')
        
        elif q_type == 'judge':
            user_ans = self.v_judge.get()
            if not user_ans:
                mb.showwarning("提示", "请选择答案！")
                return

            self.stop_question_timer()
            correct_ans_index = self.rand_judge[self.indexofjudge]
            correct_ans = self.ans_judge[correct_ans_index]

            if user_ans == correct_ans:
                self.totalScore += self.ijudgeScore
                self.Lresult_judge.config(text='回答正确！', foreground='green')
                if self.sound_enabled: self.correct_sound.play()
                correct = True
            else:
                self.Lresult_judge.config(text=f'回答错误！正确答案: {"正确" if correct_ans == "T" else "错误"}', foreground='red')
                if self.sound_enabled: self.incorrect_sound.play()

            self.tans_judge.config(state='normal')
            self.tans_judge.delete('1.0', 'end')
            self.tans_judge.insert('1.0', self.analyze_judge[correct_ans_index])
            self.tans_judge.config(state='disabled')

            for btn in [self.rb_true, self.rb_false]:
                btn.config(state='disabled')
            self.bconfirm_judge.config(state='disabled')
            self.bnext_judge.config(state='normal')
        
        # 回答正确自动跳转
        if correct:
            self.master.after(1000, lambda: self.next_question(q_type))

    def next_question(self, q_type):
        if q_type == 'select':
            self.indexofselect += 1
            if self.indexofselect < len(self.rand_select):
                self.load_question('select')
            else:
                mb.showinfo("提示", "选择题已全部完成！")
                self.bnext_select.config(state='disabled')
                self.bconfirm_select.config(state='disabled')
                # 切换到下一题型
                if self.qus_blank:
                    self.note.tab(2, state='normal')
                    self.note.select(2)
                elif self.qus_judge:
                    self.note.tab(3, state='normal')
                    self.note.select(3)
                else:
                    self.game_over()
        
        elif q_type == 'blank':
            self.indexofblank += 1
            if self.indexofblank < len(self.rand_blank):
                self.load_question('blank')
            else:
                mb.showinfo("提示", "填空题已全部完成！")
                self.bnext_blank.config(state='disabled')
                self.bconfirm_blank.config(state='disabled')
                if self.qus_judge:
                    self.note.tab(3, state='normal')
                    self.note.select(3)
                else:
                    self.game_over()

        elif q_type == 'judge':
            self.indexofjudge += 1
            if self.indexofjudge < len(self.rand_judge):
                self.load_question('judge')
            else:
                mb.showinfo("提示", "所有题目已全部完成！")
                self.bnext_judge.config(state='disabled')
                self.bconfirm_judge.config(state='disabled')
                self.game_over()

    # --- 填空题页面 ---
    def create_blank_tab(self):
        self.frm_blank = ttk.Frame(self.note)
        self.note.add(self.frm_blank, text='填空题', state='disabled')
        
        self.Lqus_blank = ttk.Label(self.frm_blank, text='题目:')
        self.L_qtime_blank = ttk.Label(self.frm_blank, text='本题用时: 0s', font=('Arial', 10))
        self.tqus_blank = sc.ScrolledText(self.frm_blank, height=15, width=80, wrap=tk.WORD)
        self.Lans_blank = ttk.Label(self.frm_blank, text='解析:')
        self.tans_blank = sc.ScrolledText(self.frm_blank, height=15, width=20, wrap=tk.WORD)
        
        self.entry_blank = ttk.Entry(self.frm_blank, width=40)
        
        self.Lresult_blank = ttk.Label(self.frm_blank, font=('楷体', 14))
        self.bconfirm_blank = ttk.Button(self.frm_blank, text='确认', command=lambda: self.check_answer('blank'))
        self.bnext_blank = ttk.Button(self.frm_blank, text='下一题', command=lambda: self.next_question('blank'), state='disabled')

        self.Lqus_blank.grid(column=0, row=0, padx=20, pady=10, sticky=tk.W)
        self.L_qtime_blank.grid(column=0, row=0, padx=(100, 0), pady=10)
        self.Lans_blank.grid(column=1, row=0, padx=5, pady=10, sticky=tk.W)
        self.tqus_blank.grid(column=0, row=1, rowspan=10, padx=20, pady=5, sticky='nsew')
        self.tans_blank.grid(column=1, row=1, rowspan=10, padx=5, pady=5, sticky='nsew')
        
        self.entry_blank.grid(column=0, row=11, pady=10)
        self.Lresult_blank.grid(column=0, row=12, pady=5)
        self.bconfirm_blank.grid(column=0, row=13, pady=5)
        self.bnext_blank.grid(column=0, row=14, pady=5)
        
        self.frm_blank.grid_rowconfigure(1, weight=1)
        self.frm_blank.grid_columnconfigure(0, weight=4)
        self.frm_blank.grid_columnconfigure(1, weight=1)

        self.frm_blank.bind('<Visibility>', lambda e: self.load_question('blank'))
        
    # --- 判断题页面 ---
    def create_judge_tab(self):
        self.frm_judge = ttk.Frame(self.note)
        self.note.add(self.frm_judge, text='判断题', state='disabled')

        self.Lqus_judge = ttk.Label(self.frm_judge, text='题目:')
        self.L_qtime_judge = ttk.Label(self.frm_judge, text='本题用时: 0s', font=('Arial', 10))
        self.tqus_judge = sc.ScrolledText(self.frm_judge, height=15, width=80, wrap=tk.WORD)
        self.Lans_judge = ttk.Label(self.frm_judge, text='解析:')
        self.tans_judge = sc.ScrolledText(self.frm_judge, height=15, width=20, wrap=tk.WORD)
        self.Lresult_judge = ttk.Label(self.frm_judge, font=('楷体', 14))
        self.bconfirm_judge = ttk.Button(self.frm_judge, text='确认', command=lambda: self.check_answer('judge'))
        self.bnext_judge = ttk.Button(self.frm_judge, text='下一题', command=lambda: self.next_question('judge'), state='disabled')
        
        self.Lqus_judge.grid(column=0, row=0, padx=20, pady=10, sticky=tk.W)
        self.L_qtime_judge.grid(column=0, row=0, padx=(100, 0), pady=10)
        self.Lans_judge.grid(column=1, row=0, padx=5, pady=10, sticky=tk.W)
        self.tqus_judge.grid(column=0, row=1, rowspan=10, padx=20, pady=5, sticky='nsew')
        self.tans_judge.grid(column=1, row=1, rowspan=10, padx=5, pady=5, sticky='nsew')
        
        judge_frame = ttk.Frame(self.frm_judge)
        judge_frame.grid(column=0, row=11, pady=10)

        self.v_judge = tk.StringVar(value=None)
        self.rb_true = ttk.Radiobutton(judge_frame, text='正确 (T)', variable=self.v_judge, value='T')
        self.rb_false = ttk.Radiobutton(judge_frame, text='错误 (F)', variable=self.v_judge, value='F')
        self.rb_true.pack(side=tk.LEFT, padx=10)
        self.rb_false.pack(side=tk.LEFT, padx=10)
        
        self.Lresult_judge.grid(column=0, row=12, pady=5)
        self.bconfirm_judge.grid(column=0, row=13, pady=5)
        self.bnext_judge.grid(column=0, row=14, pady=5)
        
        self.frm_judge.grid_rowconfigure(1, weight=1)
        self.frm_judge.grid_columnconfigure(0, weight=4)
        self.frm_judge.grid_columnconfigure(1, weight=1)

        self.frm_judge.bind('<Visibility>', lambda e: self.load_question('judge'))

    def _find_widgets(self, parent, widget_class):
        """Recursively find all widgets of a given class."""
        widgets = []
        for child in parent.winfo_children():
            if isinstance(child, widget_class):
                widgets.append(child)
            widgets.extend(self._find_widgets(child, widget_class))
        return widgets

    def start_question_timer(self):
        self.stop_question_timer()  # Stop any previous timer
        self.question_start_time = time.time()
        self.update_question_timer()

    def stop_question_timer(self):
        if self.question_timer_id:
            self.master.after_cancel(self.question_timer_id)
            self.question_timer_id = None

    def update_question_timer(self):
        if self.question_start_time is None:
            return

        elapsed_seconds = int(time.time() - self.question_start_time)
        time_str = f"本题用时: {elapsed_seconds}s"

        # Update the correct label based on the current tab
        current_tab_index = self.note.index(self.note.select())
        if current_tab_index == 1:  # Select
            if hasattr(self, 'L_qtime_select'):
                self.L_qtime_select.config(text=time_str)
        elif current_tab_index == 2:  # Blank
            if hasattr(self, 'L_qtime_blank'):
                self.L_qtime_blank.config(text=time_str)
        elif current_tab_index == 3:  # Judge
            if hasattr(self, 'L_qtime_judge'):
                self.L_qtime_judge.config(text=time_str)

        self.question_timer_id = self.master.after(1000, self.update_question_timer)

    def update_info_label(self, remaining_time_str, is_warning=False):
        sno = self.tno.get()
        sname = self.tname.get()
        text = f'学号: {sno}    姓名: {sname}    剩余时间: {remaining_time_str}       总得分：{self.totalScore}'
        self.L_info.config(text=text)
        if is_warning:
            self.L_info.config(foreground='red')
        else:
            theme = LIGHT_THEME if self.current_theme == 'light' else DARK_THEME
            self.L_info.config(foreground=theme['text_fg'])

    def game_over(self):
        if self.timer: self.timer.stop()
        
        sno = self.tno.get()
        sname = self.tname.get()
        
        # 简化的得分报告
        total_possible_score = self.totalSelect + self.totalblank + self.totalJudge
        msg = f"测验结束！\n\n"
        msg += f"考生: {sname} ({sno})\n"
        msg += f"最终得分: {self.totalScore} / {total_possible_score}\n\n"

        result = TxtFile.getMaxScore()
        if result == -1 or self.totalScore > result:
            msg += "恭喜你，创造了新的最高分记录！"
            TxtFile.setNewRecord(sno, sname, self.totalScore)
        else:
            msg += f"继续努力！当前最高记录为: {result}"

        mb.showinfo('QuizGame - 最终得分', msg)
        self.master.destroy()

    def toggle_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.theme_button.config(text="切换浅色模式")
        else:
            self.current_theme = 'light'
            self.theme_button.config(text="切换深色模式")
        self.apply_theme()

    def apply_theme(self):
        theme = LIGHT_THEME if self.current_theme == 'light' else DARK_THEME
        
        # 1. 配置根窗口
        self.master.config(bg=theme['app_bg'])

        # 2. 配置 ttk 样式
        self.style.theme_use('default')
        self.style.configure('.', background=theme['app_bg'], foreground=theme['text_fg'])
        self.style.configure('TFrame', background=theme['frame_bg'])
        self.style.configure('TLabel', background=theme['frame_bg'], foreground=theme['text_fg'])
        self.style.configure('TButton', background=theme['button_bg'], foreground=theme['button_fg'], borderwidth=1, focusthickness=3, focuscolor='none')
        self.style.map('TButton', background=[('active', theme['entry_bg'])])
        self.style.configure('TRadiobutton', background=theme['frame_bg'], foreground=theme['text_fg'])
        self.style.map('TRadiobutton', background=[('active', theme['entry_bg'])])
        self.style.configure('TNotebook', background=theme['notebook_bg'])
        self.style.configure('TNotebook.Tab', background=theme['tab_bg'], foreground=theme['tab_fg'], padding=[5, 2])
        self.style.map('TNotebook.Tab', background=[('selected', theme['tab_selected_bg'])])
        self.style.map('TEntry',
                       fieldbackground=[('!disabled', theme['entry_bg'])],
                       foreground=[('!disabled', theme['text_fg'])],
                       background=[('disabled', theme['frame_bg'])])

        # 3. 手动配置非 ttk 或复杂控件
        # 获取所有 ScrolledText 控件
        scrolled_texts = [
            getattr(self, name) for name in dir(self) 
            if isinstance(getattr(self, name, None), sc.ScrolledText)
        ]
        # 登录页面的特殊 ScrolledText
        try:
            login_tab_frame = self.note.tabs()[0]
            login_sc_text = self.master.nametowidget(login_tab_frame).winfo_children()[0]
            if isinstance(login_sc_text, sc.ScrolledText):
                scrolled_texts.append(login_sc_text)
        except (IndexError, tk.TclError):
            pass # 登录页面可能还没完全创建

        for widget in scrolled_texts:
            widget.config(bg=theme['text_widget_bg'], fg=theme['text_fg'], 
                          insertbackground=theme['text_fg'])
            

        # 更新禁用状态下的文本颜色
        for entry in [self.tno, self.tname]:
             if entry.cget('state') == 'disabled':
                 self.style.map('TEntry', foreground=[('disabled', theme['disabled_fg'])])

# =================================================================================
class myTimer:
    def __init__(self, window, label, seconds, app_instance):
        self.window = window
        self.label = label
        self.duration = seconds
        self.app = app_instance
        self.is_running = False
        self.start_time = None
        self.last_two_minutes_warning_played = False

    def format_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def play_warning(self):
        """Plays a warning sound (if available) and shows a message box."""
        if self.app.sound_enabled and self.app.warning_sound:
            self.app.warning_sound.play()
        mb.showinfo("时间提醒", "测验剩余时间不足两分钟！")

    def update_time(self):
        if self.is_running:
            elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
            remaining_time = self.duration - elapsed
            if remaining_time <= 0:
                self.is_running = False
                self.label.config(text='剩余时间： 00:00:00')
                self.app.game_over()
            else:
                is_warning = remaining_time < 120
                if is_warning and not self.last_two_minutes_warning_played:
                    self.play_warning()
                    self.last_two_minutes_warning_played = True

                time_str = self.format_time(int(remaining_time))
                self.app.update_info_label(time_str, is_warning=is_warning)
                self.window.after(1000, self.update_time)

    def start(self):
        if not self.is_running:
            self.start_time = datetime.datetime.now()
            self.is_running = True
        self.update_time()

    def stop(self):
        self.is_running = False

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()