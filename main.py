#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学习通自动学习助手
开发者：丁辉
版权所有 © 2026 丁辉。保留所有权利。
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import queue
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 应用目录：源码运行 = 脚本目录；PyInstaller 打包后 = exe 所在目录。
# 配置、日志、截图、随包浏览器都以它为基准，保证解压即用。
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

# 打包版随包分发 Playwright 浏览器（exe 旁的 ms-playwright 目录）
_BUNDLED_BROWSERS = os.path.join(APP_DIR, "ms-playwright")
if os.path.isdir(_BUNDLED_BROWSERS):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = _BUNDLED_BROWSERS

# ---- 开发者信息（集中定义，便于后续修改） ----
ABOUT_LINES = (
    "软件开发者：大学在读生 丁辉",
    "版权所有 © 2026 丁辉。保留所有权利。",
    "本软件的代码、界面设计、名称及相关内容未经许可不得复制、修改、传播或用于商业用途。",
)


class XueXiTongLearner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("学习通自动学习助手")
        self.root.geometry("1000x830")
        self.root.configure(bg="#0A0D12")
        
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        # Playwright sync API objects are bound to their creating thread.  All
        # browser work therefore runs through this one long-lived worker.
        self._browser_jobs = queue.Queue()
        self._browser_thread = None
        self._browser_ready = threading.Event()
        self._close_requested = threading.Event()
        self._browser_launching = False
        self._closing = False
        # AI 专属无头浏览器（独立线程/实例，用于过 Cloudflare，与刷课浏览器互不干扰）
        self._ai_jobs = queue.Queue()
        self._ai_browser_ready = threading.Event()
        self._ai_worker_started = False
        self._ai_playwright = None
        self._ai_browser = None
        self._ai_context = None
        self._ai_page = None
        
        self.is_running = False
        self.is_paused = False
        self.current_course = None
        self.courses = []
        self.ai_config = self._load_ai_config()
        self._log_path = os.path.join(APP_DIR, "learning.log")
        
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """配置主题样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 深色主题配色
        bg_primary = "#0A0D12"
        bg_secondary = "#161D2B"
        bg_tertiary = "#1E2636"
        accent = "#6EE7B7"
        text_primary = "#F4F4F5"
        text_secondary = "#A1A1AA"
        
        # Frame样式
        style.configure("Dark.TFrame", background=bg_primary)
        style.configure("Card.TFrame", background=bg_secondary, relief="flat")
        
        # Label样式
        style.configure("Title.TLabel", 
                       background=bg_primary, 
                       foreground=text_primary,
                       font=("Microsoft YaHei UI", 20, "bold"))
        style.configure("Dark.TLabel", 
                       background=bg_primary, 
                       foreground=text_primary)
        style.configure("Card.TLabel", 
                       background=bg_secondary, 
                       foreground=text_primary)
        style.configure("Muted.TLabel", 
                       background=bg_secondary, 
                       foreground=text_secondary,
                       font=("Microsoft YaHei UI", 9))
        
        # Button样式
        style.configure("Accent.TButton",
                       background=accent,
                       foreground=bg_primary,
                       borderwidth=0,
                       font=("Microsoft YaHei UI", 10, "bold"),
                       padding=(20, 10))
        style.map("Accent.TButton",
                 background=[("active", "#34D399"), ("disabled", "#334155")])
        
        style.configure("Secondary.TButton",
                       background=bg_tertiary,
                       foreground=text_primary,
                       borderwidth=0,
                       font=("Microsoft YaHei UI", 9),
                       padding=(16, 8))
        style.map("Secondary.TButton",
                 background=[("active", "#2D3748")])
        
        # Treeview样式
        style.configure("Dark.Treeview",
                       background=bg_secondary,
                       foreground=text_primary,
                       fieldbackground=bg_secondary,
                       borderwidth=0,
                       font=("Microsoft YaHei UI", 10))
        style.configure("Dark.Treeview.Heading",
                       background=bg_tertiary,
                       foreground=text_primary,
                       borderwidth=0,
                       font=("Microsoft YaHei UI", 10, "bold"))
        style.map("Dark.Treeview",
                 background=[("selected", accent)],
                 foreground=[("selected", bg_primary)])
        
    def setup_ui(self):
        """构建用户界面"""
        # 主容器
        main_container = ttk.Frame(self.root, style="Dark.TFrame", padding="24")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 头部区域
        header_frame = ttk.Frame(main_container, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="学习通自动学习助手", 
                               style="Title.TLabel")
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                   text="自动播放视频 · 智能答题 · 连续学习",
                                   style="Dark.TLabel",
                                   font=("Microsoft YaHei UI", 11))
        subtitle_label.pack(anchor=tk.W, pady=(4, 0))
        
        # 控制卡片
        control_card = ttk.Frame(main_container, style="Card.TFrame", padding="20")
        control_card.pack(fill=tk.X, pady=(0, 16))
        
        control_label = ttk.Label(control_card, text="启动设置", 
                                 style="Card.TLabel",
                                 font=("Microsoft YaHei UI", 12, "bold"))
        control_label.pack(anchor=tk.W, pady=(0, 12))
        
        btn_frame = ttk.Frame(control_card, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)
        
        self.launch_btn = ttk.Button(btn_frame, text="启动浏览器并登录", 
                                     style="Accent.TButton",
                                     command=self.start_browser)
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.fetch_btn = ttk.Button(btn_frame, text="获取课程列表",
                                     style="Secondary.TButton",
                                     command=self.fetch_courses)
        self.fetch_btn.pack(side=tk.LEFT)

        self.ai_btn = ttk.Button(btn_frame, text="AI 答题设置",
                                  style="Secondary.TButton",
                                  command=self._open_ai_settings)
        self.ai_btn.pack(side=tk.LEFT, padx=(12, 0))
        
        # 关于区域（side=BOTTOM 反向锚定，优先分配空间，永远贴底可见；
        # 文案统一取自 ABOUT_LINES 常量，便于修改）
        about_card = ttk.Frame(main_container, style="Card.TFrame", padding="10")
        about_card.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))

        about_title = ttk.Label(about_card, text="关于本软件",
                               style="Card.TLabel",
                               font=("Microsoft YaHei UI", 10, "bold"))
        about_title.pack(anchor=tk.W, pady=(0, 6))

        for line in ABOUT_LINES:
            info = ttk.Label(about_card, text=line, style="Muted.TLabel", wraplength=900)
            info.pack(anchor=tk.W, pady=(0, 3))

        # 日志区域
        log_card = ttk.Frame(main_container, style="Card.TFrame", padding="20")
        log_card.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))  # 底部锚定，空间不足时压缩课程列表
        
        log_label = ttk.Label(log_card, text="运行日志", 
                             style="Card.TLabel",
                             font=("Microsoft YaHei UI", 11, "bold"))
        log_label.pack(anchor=tk.W, pady=(0, 8))
        
        self.log_text = scrolledtext.ScrolledText(
            log_card, 
            height=5,
            wrap=tk.WORD, 
            state=tk.DISABLED,
            bg="#161D2B",
            fg="#F4F4F5",
            font=("Consolas", 9),
            borderwidth=0,
            insertbackground="#6EE7B7"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 操作按钮区
        action_card = ttk.Frame(main_container, style="Card.TFrame", padding="16")
        action_card.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 8))
        
        self.start_btn = ttk.Button(action_card, text="开始学习", 
                                    style="Accent.TButton",
                                    command=self.start_learning, 
                                    state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.pause_btn = ttk.Button(action_card, text="暂停", 
                                    style="Secondary.TButton",
                                    command=self.pause_learning, 
                                    state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        self.stop_btn = ttk.Button(action_card, text="停止", 
                                   style="Secondary.TButton",
                                   command=self.stop_learning, 
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # 课程列表卡片
        course_card = ttk.Frame(main_container, style="Card.TFrame", padding="20")
        course_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        course_header = ttk.Frame(course_card, style="Card.TFrame")
        course_header.pack(fill=tk.X, pady=(0, 12))
        
        course_label = ttk.Label(course_header, text="我的课程", 
                                style="Card.TLabel",
                                font=("Microsoft YaHei UI", 12, "bold"))
        course_label.pack(side=tk.LEFT)
        
        self.course_count_label = ttk.Label(course_header, text="", 
                                           style="Muted.TLabel")
        self.course_count_label.pack(side=tk.LEFT, padx=(12, 0))
        
        # Treeview
        tree_frame = ttk.Frame(course_card, style="Card.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("name", "progress", "status")
        self.course_tree = ttk.Treeview(tree_frame, columns=columns, 
                                        show="tree headings", 
                                        style="Dark.Treeview",
                                        selectmode="browse")
        self.course_tree.heading("#0", text="序号")
        self.course_tree.heading("name", text="课程名称")
        self.course_tree.heading("progress", text="学习进度")
        self.course_tree.heading("status", text="状态")
        
        self.course_tree.column("#0", width=60, anchor=tk.CENTER)
        self.course_tree.column("name", width=500)
        self.course_tree.column("progress", width=120, anchor=tk.CENTER)
        self.course_tree.column("status", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=scrollbar.set)
        
        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        

        

        
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(self.root, 
                             textvariable=self.status_var,
                             bg="#0F131C",
                             fg="#A1A1AA",
                             font=("Microsoft YaHei UI", 9),
                             anchor=tk.W,
                             padx=24,
                             pady=8)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message):
        """输出日志（线程安全，同时写入 learning.log 文件）"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(log_message)
        except Exception:
            pass

        def _write_log():
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)
        
        if not self._post_to_ui(_write_log):
            # 窗口已经关闭时仍保留最后的诊断信息。
            print(log_message.strip())

    def _post_to_ui(self, callback, allow_when_closing=False):
        """将 UI 操作交回 Tk 主线程。"""
        if self._closing and not allow_when_closing:
            return False

        def run_callback():
            if self._closing and not allow_when_closing:
                return
            try:
                callback()
            except tk.TclError:
                pass

        try:
            self.root.after(0, run_callback)
            return True
        except tk.TclError:
            return False

    def _browser_worker(self):
        """唯一持有 Playwright 同步 API 对象的线程。"""
        while True:
            job = self._browser_jobs.get()
            try:
                if job is None:
                    return
                job()
            except Exception as error:
                self.log(f"✗ 浏览器任务意外失败：{error}")
            finally:
                self._browser_jobs.task_done()

    def _ensure_browser_worker(self):
        if self._browser_thread and self._browser_thread.is_alive():
            return
        self._browser_thread = threading.Thread(
            target=self._browser_worker,
            name="PlaywrightWorker",
            daemon=True,
        )
        self._browser_thread.start()

    def _submit_browser_job(self, job):
        """从 Tk 线程向浏览器工作线程提交任务。"""
        if self._closing:
            return False
        self._ensure_browser_worker()
        self._browser_jobs.put(job)
        return True

    def _cleanup_browser_resources(self):
        """仅由浏览器工作线程调用，避免跨线程关闭 Playwright。"""
        self._browser_ready.clear()

        if self.context:
            try:
                self.context.close()
            except Exception:
                pass
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    def _start_browser_job(self):
        """启动浏览器并等待登录；在浏览器工作线程中执行。"""
        try:
            if self._close_requested.is_set():
                return

            self.log("正在启动浏览器...")
            self._post_to_ui(lambda: self.status_var.set("正在启动..."))

            # 允许在上一次启动失败或超时后重新启动。
            self._cleanup_browser_resources()
            self.playwright = sync_playwright().start()
            # 允许视频无用户手势自动播放（仅本机浏览器策略，不影响学习通服务端记录）
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=["--autoplay-policy=no-user-gesture-required"]
            )
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            self.page = self.context.new_page()

            self.log("浏览器已启动，正在打开学习通...")
            self.page.goto("https://i.chaoxing.com/")
            self.log("请在浏览器中完成登录...")
            self._post_to_ui(lambda: self.status_var.set("等待用户登录中..."))

            # 以短超时轮询登录状态，窗口关闭时可以及时回收浏览器。
            # 学习通登录后的落地 URL 不固定，不能用 "**/space/**" 判断，
            # 改为检测当前 URL 是否已离开登录页（passport/login）。
            deadline = time.monotonic() + 300
            while not self._close_requested.is_set() and time.monotonic() < deadline:
                time.sleep(1)
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=1000)
                except PlaywrightTimeout:
                    pass

                current_url = self.page.url.lower()
                if "login" not in current_url and "passport" not in current_url:
                    self._browser_ready.set()
                    self.log("✓ 登录成功！")

                    def on_login_success():
                        self._browser_launching = False
                        self.status_var.set("已登录")
                        self.launch_btn.configure(state=tk.NORMAL)
                        self.fetch_btn.configure(state=tk.NORMAL)
                        messagebox.showinfo("提示", "登录成功！现在可以获取课程列表了")

                    self._post_to_ui(on_login_success)
                    return

            if self._close_requested.is_set():
                self._cleanup_browser_resources()
                return

            self.log("✗ 登录超时，请重新启动")
            self._cleanup_browser_resources()

            def on_timeout():
                self._browser_launching = False
                self.status_var.set("登录超时")
                self.launch_btn.configure(state=tk.NORMAL)

            self._post_to_ui(on_timeout)

        except Exception as error:
            error_msg = str(error)
            self.log(f"✗ 启动浏览器失败：{error_msg}")
            self._cleanup_browser_resources()

            def show_error():
                self._browser_launching = False
                self.launch_btn.configure(state=tk.NORMAL)
                self.fetch_btn.configure(state=tk.DISABLED)
                self.status_var.set("启动失败")
                messagebox.showerror("错误", f"启动失败：{error_msg}")

            self._post_to_ui(show_error)

    def start_browser(self):
        """启动浏览器并等待用户登录"""
        if self._browser_ready.is_set():
            messagebox.showinfo("提示", "浏览器已登录，可以直接获取课程列表")
            return
        if self._browser_launching:
            messagebox.showinfo("提示", "浏览器正在启动，请在打开的窗口中完成登录")
            return

        self._close_requested.clear()
        self._browser_launching = True
        self.launch_btn.configure(state=tk.DISABLED)
        self.fetch_btn.configure(state=tk.DISABLED)
        self._submit_browser_job(self._start_browser_job)
        
    def fetch_courses(self):
        """获取课程列表"""
        if not self.page:
            messagebox.showwarning("警告", "请先点击“启动浏览器并登录”，并完成登录")
            return

        self.fetch_btn.configure(state=tk.DISABLED)

        def _fetch():
            try:
                if self._close_requested.is_set():
                    return

                self.log("正在获取课程列表...")
                
                def update_status_fetching():
                    self.status_var.set("获取课程中...")
                self._post_to_ui(update_status_fetching)
                
                # 先尝试个人空间首页
                self.log("正在访问个人空间...")
                self.page.goto("https://i.chaoxing.com/")
                time.sleep(3)
                
                # 获取当前 URL，判断是否跳转
                current_url = self.page.url
                self.log(f"当前页面：{current_url}")
                
                # 尝试多种方式找到课程列表
                # 方案1：直接访问课程页面
                self.log("尝试访问课程页面...")
                try:
                    self.page.goto("https://mooc1.chaoxing.com/visit/interaction", timeout=15000)
                    time.sleep(3)
                except:
                    self.log("方案1失败，尝试其他路径...")
                
                # 方案2：查找页面上的课程链接
                self.log("正在页面中查找课程元素...")
                
                # 先截图帮助调试
                try:
                    screenshot_path = os.path.join(APP_DIR, "debug_screenshot.png")
                    self.page.screenshot(path=screenshot_path)
                    self.log(f"已保存调试截图到：{screenshot_path}")
                except:
                    pass
                
                # 提取课程信息（增强版）
                courses_data = self.page.evaluate("""
                    () => {
                        const courses = [];
                        
                        // 调试信息
                        console.log('开始查找课程...');
                        
                        // 方案1：查找标准课程列表
                        let courseElements = document.querySelectorAll(
                            'ul.clearfix li, .course-item, .course-list li, ' +
                            '[class*="courselist"] li, [class*="course-card"]'
                        );
                        console.log('方案1找到元素数:', courseElements.length);
                        
                        // 方案2：查找所有包含课程链接的元素
                        if (courseElements.length === 0) {
                            courseElements = document.querySelectorAll(
                                'a[href*="mycourse"], a[href*="course/"]'
                            );
                            console.log('方案2找到元素数:', courseElements.length);
                        }
                        
                        courseElements.forEach((el, index) => {
                            // 尝试多种选择器查找课程名称
                            let nameEl = el.querySelector(
                                '.course-name, .coursetitle, .course_title, ' +
                                'h3, h4, .title, [class*="title"]'
                            );
                            
                            // 如果是链接元素本身
                            if (!nameEl && el.tagName === 'A') {
                                nameEl = el;
                            }
                            
                            // 查找链接
                            let linkEl = el.querySelector('a[href*="course"]');
                            if (!linkEl && el.tagName === 'A') {
                                linkEl = el;
                            }
                            
                            if (nameEl && linkEl && linkEl.href) {
                                const courseName = nameEl.innerText.trim();
                                // 过滤掉空名称或过短的名称
                                if (courseName && courseName.length > 1) {
                                    // 卡片上若带真实进度（如"学习进度 80%"）就取用，否则显示 --
                                    const pm = el.innerText.match(/(\d+(\.\d+)?)\s*%/);
                                    courses.push({
                                        id: index,
                                        name: courseName,
                                        progress: pm ? pm[1] + '%' : '--',
                                        url: linkEl.href
                                    });
                                    console.log('找到课程:', courseName);
                                }
                            }
                        });
                        
                        console.log('最终找到课程数:', courses.length);
                        return courses;
                    }
                """)
                
                self.log(f"页面解析完成，找到 {len(courses_data)} 个课程元素")
                
                if not courses_data:
                    self.log("✗ 未检测到课程")
                    self.log("提示：请确保：")
                    self.log("  1. 已经成功登录学习通")
                    self.log("  2. 账号中有已加入的课程")
                    self.log("  3. 可以尝试手动在浏览器中点击【我的课程】")
                    
                    def show_no_course_warning():
                        messagebox.showwarning(
                            "提示", 
                            "未找到课程。\n\n请确认：\n1. 已成功登录\n2. 账号中有课程\n3. 可手动点击浏览器中的【我的课程】"
                        )
                    self._post_to_ui(show_no_course_warning)
                    return
                
                self.courses = courses_data
                self.log(f"✓ 成功获取 {len(self.courses)} 门课程")
                
                # 更新UI（所有UI操作都通过 after 调度到主线程）
                def update_ui():
                    self._update_course_list()
                    self.start_btn.configure(state=tk.NORMAL)
                    self.status_var.set(f"已加载 {len(self.courses)} 门课程")
                
                self._post_to_ui(update_ui)
                
            except Exception as e:
                self.log(f"✗ 获取课程失败：{str(e)}")
                import traceback
                error_detail = traceback.format_exc()
                self.log(f"详细错误：{error_detail}")
                
                # 立即捕获错误信息
                error_msg = str(e)
                def show_fetch_error():
                    messagebox.showerror(
                        "错误", f"获取课程失败：{error_msg}\n\n请查看日志了解详情"
                    )
                self._post_to_ui(show_fetch_error)
            finally:
                def finish_fetch():
                    if self._browser_ready.is_set() and not self._closing:
                        self.fetch_btn.configure(state=tk.NORMAL)

                self._post_to_ui(finish_fetch)

        self._submit_browser_job(_fetch)
        
    def _update_course_list(self):
        """更新课程列表UI"""
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        
        for idx, course in enumerate(self.courses, 1):
            self.course_tree.insert("", tk.END, text=str(idx),
                                   values=(course["name"], 
                                          course["progress"], 
                                          "待开始"))
        
        self.course_count_label.configure(
            text=f"共 {len(self.courses)} 门课程"
        )
    
    def start_learning(self):
        """开始学习选中的课程"""
        if not self.page:
            messagebox.showwarning("警告", "请先点击“启动浏览器并登录”，并完成登录")
            return

        selection = self.course_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一门课程")
            return
        
        item = selection[0]
        course_idx = int(self.course_tree.item(item, "text")) - 1
        self.current_course = self.courses[course_idx]
        
        self.is_running = True
        self.is_paused = False
        self.start_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.NORMAL)
        
        self.log(f"▶ 开始学习课程：{self.current_course['name']}")
        self.status_var.set("学习中...")
        
        # 更新选中课程状态
        self.course_tree.set(item, "status", "学习中")
        
        self._submit_browser_job(lambda selected_item=item: self._learn_course(selected_item))
    
    # ---------- 页面内执行的 JS 片段 ----------
    # 学习通的章节列表、视频、弹题都在多层 iframe 里，
    # 因此所有操作都基于 frame 遍历，不假设固定层级。

    JS_VIDEO_INFO = r"""
    () => {
        const v = document.querySelector('video');
        if (!v) return null;
        const r = v.getBoundingClientRect();
        if (r.width < 50 || r.height < 40) return null;
        return {
            ended: !!v.ended,
            paused: !!v.paused,
            time: v.currentTime || 0,
            duration: v.duration || 0
        };
    }
    """

    JS_PLAY = r"""
    () => {
        const v = document.querySelector('video');
        if (!v) return false;
        const big = document.querySelector('.vjs-big-play-button');
        if (big && v.paused && (v.currentTime || 0) < 0.3) { big.click(); return true; }
        if (v.paused) {
            const p = v.play();
            if (p && p.catch) p.catch(() => {});
        }
        return true;
    }
    """

    JS_RESUME = r"""
    () => {
        const v = document.querySelector('video');
        if (v && v.paused) {
            const p = v.play();
            if (p && p.catch) p.catch(() => {});
            return true;
        }
        return false;
    }
    """

    JS_FIND_QUESTION = r"""
    () => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2 && getComputedStyle(el).visibility !== 'hidden';
        }
        // 输入框型选项（radio/checkbox）
        const inputs = Array.from(document.querySelectorAll('input[type=radio],input[type=checkbox]')).filter(vis);
        if (inputs.length >= 2) {
            let container = inputs[0].closest('li,ul,form,div') || inputs[0].parentElement;
            for (let i = 0; i < 8 && container && container.parentElement; i++) {
                if ((container.innerText || '').trim().length >= 30) break;
                if (container.parentElement === document.body) break;
                container = container.parentElement;
            }
            const options = inputs.map(r => {
                const lab = r.closest('label') || r.parentElement;
                return ((lab && lab.innerText) || '').trim().replace(/\s+/g, ' ').slice(0, 150);
            });
            const q = ((container && container.innerText) || '').trim().replace(/\s+/g, ' ').slice(0, 400);
            if (!q || q.length < 8) return null;
            return { question: q, options: options };
        }
        // div 列表型选项（新版播放器弹题）
        const sels = '.answerItem,.optionItem,.qtItem,ul[class*=answer] li,ul[class*=option] li,[class*=quiz] li,[class*=question] li';
        for (const sel of sels.split(',')) {
            try {
                const items = Array.from(document.querySelectorAll(sel)).filter(vis)
                    .filter(el => (el.innerText || '').trim().length > 0);
                if (items.length >= 2 && items.length <= 8) {
                    let container = items[0].parentElement;
                    for (let i = 0; i < 4 && container && container.parentElement; i++) {
                        if ((container.innerText || '').trim().length >= 30) break;
                        if (container.parentElement === document.body) break;
                        container = container.parentElement;
                    }
                    const q = ((container && container.innerText) || '').trim().replace(/\s+/g, ' ').slice(0, 400);
                    if (!q || q.length < 8) continue;
                    return { question: q, options: items.map(el => (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 150)) };
                }
            } catch (e) {}
        }
        return null;
    }
    """

    JS_CLICK_OPTION = r"""
    (idx) => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2;
        }
        const inputs = Array.from(document.querySelectorAll('input[type=radio],input[type=checkbox]')).filter(vis);
        if (idx < 0 || idx >= inputs.length) return false;
        inputs[idx].click();
        return true;
    }
    """

    JS_CLICK_DIV_OPTION = r"""
    (idx) => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2;
        }
        const sels = '.answerItem,.optionItem,.qtItem,ul[class*=answer] li,ul[class*=option] li,[class*=quiz] li,[class*=question] li';
        for (const sel of sels.split(',')) {
            const items = Array.from(document.querySelectorAll(sel)).filter(vis)
                .filter(el => (el.innerText || '').trim().length > 0);
            if (items.length >= 2) {
                items[Math.min(Math.max(idx, 0), items.length - 1)].click();
                return true;
            }
        }
        return false;
    }
    """

    JS_CLICK_BTN = r"""
    (re) => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2;
        }
        const reg = new RegExp(re);
        const groups = [
            'button', 'a', 'input[type=button]', 'input[type=submit]',
            '[class*=btn]', '[class*=submit]', '[class*=confirm]',
            'div', 'span', 'li', 'p'
        ];
        for (const sel of groups) {
            for (const el of Array.from(document.querySelectorAll(sel)).filter(vis)) {
                const t = ((el.innerText || el.value || '') + '').trim();
                if (t && t.length <= 10 && reg.test(t)) { el.click(); return t; }
            }
        }
        return null;
    }
    """


    # 识别填空题/简答题（input text、textarea）
    JS_FIND_TEXT_QUESTION = r"""
    () => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2 && getComputedStyle(el).visibility !== 'hidden';
        }
        
        const textInputs = Array.from(document.querySelectorAll('input[type=text], textarea'))
            .filter(vis)
            .filter(el => !el.disabled && !el.readOnly);
        
        if (textInputs.length === 0) return null;
        
        let container = textInputs[0].closest('form,div[class*=question],div[class*=quiz],li,ul') || textInputs[0].parentElement;
        for (let i = 0; i < 8 && container && container.parentElement; i++) {
            const text = (container.innerText || '').trim();
            if (text.length >= 20) break;
            if (container.parentElement === document.body) break;
            container = container.parentElement;
        }
        
        let questionText = '';
        if (container) {
            const clone = container.cloneNode(true);
            clone.querySelectorAll('input, textarea, button').forEach(el => el.remove());
            questionText = (clone.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 600);
        }
        
        if (!questionText || questionText.length < 5) return null;
        
        return {
            question: questionText,
            inputCount: textInputs.length,
            inputType: textInputs[0].tagName.toLowerCase() === 'textarea' ? 'textarea' : 'text'
        };
    }
    """
    
    JS_FILL_TEXT_ANSWER = r"""
    (answers) => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2 && getComputedStyle(el).visibility !== 'hidden';
        }
        
        const textInputs = Array.from(document.querySelectorAll('input[type=text], textarea'))
            .filter(vis)
            .filter(el => !el.disabled && !el.readOnly);
        
        if (!Array.isArray(answers)) answers = [answers];
        
        let filled = 0;
        for (let i = 0; i < Math.min(textInputs.length, answers.length); i++) {
            const input = textInputs[i];
            const answer = String(answers[i] || '').trim();
            input.value = answer;
            ['input', 'change', 'blur'].forEach(eventType => {
                input.dispatchEvent(new Event(eventType, { bubbles: true }));
            });
            filled++;
        }
        return filled;
    }
    """
    
    JS_CHECK_TEXT_ERROR = r"""
    () => {
        const errorKeywords = ['错误', '不正确', '答错', 'wrong', 'incorrect', 'error'];
        const errorSelectors = [
            '[class*=error]', '[class*=wrong]', '[class*=incorrect]',
            '.tip', '.hint', '.message', '.feedback'
        ];
        
        for (const sel of errorSelectors) {
            const elements = Array.from(document.querySelectorAll(sel));
            for (const el of elements) {
                const text = (el.innerText || '').toLowerCase();
                if (errorKeywords.some(kw => text.includes(kw))) {
                    return true;
                }
            }
        }
        return false;
    }
    """

    JS_NEXT_SECTION = r"""
    () => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 5 && r.height > 3;
        }
        const reg = /^(下一节|下一章|下一个)\s*>?\s*$/;
        for (const el of Array.from(document.querySelectorAll('a,button,div,span,li')).filter(vis)) {
            const t = (el.innerText || '').trim();
            if (t && reg.test(t)) { el.click(); return true; }
        }
        return false;
    }
    """

    JS_ENTER_CHAPTER = r"""
    () => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2;
        }
        const links = Array.from(document.querySelectorAll('a')).filter(vis);
        for (const a of links) {
            const href = a.getAttribute('href') || '';
            if (href.indexOf('nodeId') >= 0) {
                const name = (a.innerText || '').trim().slice(0, 60) || '章节';
                a.click();
                return name;
            }
        }
        const re = /^第[一二三四五六七八九十0-9０-９]{1,4}[章节讲单元]/;
        for (const a of links) {
            const t = (a.innerText || '').trim();
            if (re.test(t)) { a.click(); return t.slice(0, 60); }
        }
        return null;
    }
    """

    def _live_frames(self):
        """返回当前所有存活的 frame（含主文档）。"""
        frames = []
        for frame in list(self.page.frames):
            try:
                frame.evaluate("1")
                frames.append(frame)
            except Exception:
                continue
        return frames

    def _dump_frames_info(self, reason):
        """打印当前所有 frame 的诊断信息（video 有无与地址）。"""
        try:
            self.log(f"[诊断] {reason}，当前共 {len(self.page.frames)} 个 frame：")
            for i, frame in enumerate(list(self.page.frames)):
                tag = "主文档" if frame == self.page.main_frame else "iframe"
                try:
                    has_video = frame.evaluate("() => !!document.querySelector('video')")
                except Exception:
                    has_video = "?"
                url = (frame.url or "")[:110]
                self.log(f"[诊断]   #{i} {tag} video={has_video} {url}")
        except Exception:
            pass

    def _try_close_masks(self):
        """尝试关闭新手引导/提示遮罩。"""
        for frame in self._live_frames():
            try:
                frame.evaluate(self.JS_CLICK_BTN, "^(我知道了|知道了|下次再说|关闭|×)$")
            except Exception:
                pass

    def _learn_course(self, tree_item):
        """执行课程学习流程：逐节播放视频，播完点官方“下一节”推进。"""
        try:
            if self._close_requested.is_set():
                return

            self.log("正在打开课程页面...")
            self.page.goto(self.current_course["url"])
            time.sleep(3)
            self._try_close_masks()

            if not self._enter_first_chapter():
                self.log("未能自动进入章节，请在打开的浏览器中点开任意一节课（60 秒内）")
                if not self._wait_manual_entry(60):
                    self.log("✗ 仍未检测到课程视频，停止学习")
                    return

            section_no = 0
            while self.is_running:
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                if not self.is_running:
                    break

                section_no += 1
                self.log(f"—— 开始学习第 {section_no} 节 ——")
                self._play_section_videos()
                if not self.is_running:
                    break

                self.log(f"第 {section_no} 节完成，检查是否有课后题目...")
                self._handle_non_video_questions()
                
                self.log(f"正在跳到下一节...")
                self._post_to_ui(lambda s=tree_item, n=section_no:
                                 self.course_tree.set(s, "status", f"已完成 {n} 节"))
                if not self._goto_next_section():
                    self._dump_frames_info("找不到官方“下一节”按钮")
                    self.log("✓ 已经是最后一节，本课程学习完成！")
                    break

            if self.is_running:
                self.log("✓ 课程学习完成！")
                course_name = self.current_course["name"]
                item = tree_item

                def mark_complete():
                    self.course_tree.set(item, "status", "已完成")
                    messagebox.showinfo("完成", f'课程"{course_name}"已学习完成')

                self._post_to_ui(mark_complete)

        except Exception as e:
            self.log(f"✗ 学习过程出错：{str(e)}")
        finally:
            self.is_running = False
            self._post_to_ui(self._reset_buttons)

    def _enter_first_chapter(self):
        """进入课程第一章；页面若已停在上次学到的地方（有视频）则直接续播。"""
        if self._find_video_frame(set()):
            self.log("页面已定位到视频位置，直接续播")
            return True
        for frame in self._live_frames():
            try:
                name = frame.evaluate(self.JS_ENTER_CHAPTER)
            except Exception:
                continue
            if name:
                self.log(f"已点击章节：{name}")
                time.sleep(3)
                return True
        self._dump_frames_info("未能自动进入章节")
        return False

    def _wait_manual_entry(self, seconds):
        """等待用户在浏览器里手动打开某节课；检测到视频返回 True。"""
        deadline = time.monotonic() + seconds
        while self.is_running and time.monotonic() < deadline:
            if self._find_video_frame(set()):
                self.log("检测到课程视频，继续自动学习")
                return True
            time.sleep(2)
        return False

    def _play_section_videos(self):
        """播放当前节内的视频（同一节可能有多个视频卡片，逐个播完）。"""
        finished = set()
        found_any = False
        while self.is_running and not self.is_paused:
            if self._close_requested.is_set():
                return
            frame = self._find_video_frame(finished)
            if frame is None:
                if not found_any:
                    time.sleep(2)
                    frame = self._find_video_frame(finished)
                    if frame is None:
                        self._dump_frames_info("本节未找到视频")
                        self.log("本节没有检测到视频，跳到下一节")
                        return
                else:
                    return
            found_any = True
            try:
                self._play_one_video(frame)
            except Exception as e:
                self.log(f"播放监控异常：{e}")
            finished.add(frame.url)

    def _find_video_frame(self, excluded):
        """在所有 frame 中找一个尚未播完的视频。"""
        for frame in self._live_frames():
            if frame.url in excluded:
                continue
            try:
                info = frame.evaluate(self.JS_VIDEO_INFO)
            except Exception:
                continue
            if info and not info["ended"]:
                return frame
        return None

    def _play_one_video(self, frame):
        """在指定 frame 内播放视频直到结束；期间自动处理弹题与意外暂停。"""
        self.log("检测到视频，开始播放...")
        try:
            frame.evaluate(self.JS_PLAY)
        except Exception:
            pass
        time.sleep(2)

        last_report = time.monotonic()
        deadline = time.monotonic() + 4 * 3600
        while self.is_running and not self.is_paused:
            if self._close_requested.is_set():
                return
            if time.monotonic() > deadline:
                self.log("✗ 单个视频监控超时，跳过")
                return

            try:
                info = frame.evaluate(self.JS_VIDEO_INFO)
            except Exception:
                self.log("视频页面已切换，进入下一节")
                return
            if info is None:
                self.log("视频元素消失，进入下一节")
                return

            if info["ended"] or (info["duration"] > 0 and info["time"] >= info["duration"] - 0.6):
                self.log("✓ 视频播放完成")
                return

            if self._handle_popup_questions():
                time.sleep(1)
                try:
                    frame.evaluate(self.JS_RESUME)
                except Exception:
                    pass
            elif self._handle_text_questions():
                time.sleep(1)
                try:
                    frame.evaluate(self.JS_RESUME)
                except Exception:
                    pass
            elif info["paused"]:
                # 可能有防挂机确认框挡住播放，先尝试点掉它再恢复播放
                self._try_close_masks()
                try:
                    frame.evaluate(self.JS_CLICK_BTN, "^(确定|继续观看|继续学习|继续)$")
                except Exception:
                    pass
                try:
                    frame.evaluate(self.JS_RESUME)
                except Exception:
                    pass

            now = time.monotonic()
            if now - last_report > 60:
                last_report = now
                total = int(info["duration"]) if info["duration"] else 0
                self.log(f"   播放中：{int(info['time'])}/{total} 秒")
            time.sleep(2)

    def _handle_non_video_questions(self):
        """处理视频外的题目（课后作业、章节测试等）。"""
        if not self.is_running or self.is_paused:
            return
        
        time.sleep(2)
        
        attempt_count = 0
        max_attempts = 5
        
        while attempt_count < max_attempts and self.is_running and not self.is_paused:
            if self._close_requested.is_set():
                return
            
            found_choice = self._handle_popup_questions()
            found_text = self._handle_text_questions()
            
            if not found_choice and not found_text:
                if attempt_count == 0:
                    self.log("未检测到课后题目")
                break
            
            attempt_count += 1
            time.sleep(1)
        
        if attempt_count >= max_attempts:
            self.log(f"已处理 {attempt_count} 道题目，继续下一节")

    def _goto_next_section(self):
        """点击官方“下一节”按钮推进到下一节；找不到视为课程结束。"""
        for attempt in range(3):
            for frame in self._live_frames():
                try:
                    if frame.evaluate(self.JS_NEXT_SECTION):
                        self.log("已点击官方“下一节”按钮")
                        time.sleep(3)
                        for f2 in self._live_frames():
                            try:
                                f2.evaluate(self.JS_CLICK_BTN, "^(确定|是|继续学习|继续)$")
                            except Exception:
                                pass
                        return True
                except Exception:
                    continue
            time.sleep(2)
        return False

    # ---------- AI 接口通用工具（移植自 zsb-study-helper src/services/ai.ts） ----------

    DEFAULT_AI_PROXY_URL = "https://shandong-zsb-study-helper.vercel.app/api/ai/proxy"

    JS_READ_RESULT = r"""
    () => {
        function vis(el) {
            const r = el.getBoundingClientRect();
            return r.width > 2 && r.height > 2 && getComputedStyle(el).visibility !== 'hidden';
        }
        const sels = '[class*="tips"],[class*="Tips"],[class*="result"],[class*="Result"],[class*="score"],[class*="Score"],[class*="judge"],[class*="Judge"],[class*="correct"],[class*="wrong"],[class*="notice"],[class*="toast"]';
        const parts = [];
        for (const el of Array.from(document.querySelectorAll(sels)).filter(vis)) {
            const t = (el.innerText || '').trim();
            if (t && t.length < 120) parts.push(t);
        }
        return parts.join(' | ').slice(0, 300);
    }
    """

    def _handle_popup_questions(self):
        """扫描所有 frame，处理视频弹题。

        答错时自动换下一个未试过的选项重答，直到答对让视频继续；
        所有选项都错时尝试关闭弹窗（由老师设置决定能否继续观看）。
        """
        for frame in self._live_frames():
            if self._close_requested.is_set():
                return False
            try:
                data = frame.evaluate(self.JS_FIND_QUESTION)
            except Exception:
                continue
            if not data or len(data.get("options") or []) < 2:
                continue

            options = data["options"]
            question = data.get("question") or ""
            self.log(f"检测到题目弹窗（{len(options)} 个选项）：{question[:60]}")

            tried = set()
            max_try = min(len(options), 6)
            for attempt in range(max_try):
                choice = self._pick_answer(question, options, tried)
                if choice is None:
                    break
                tried.add(choice)
                label = options[choice][:30] if 0 <= choice < len(options) else "?"
                self.log(f"尝试作答：第 {choice + 1} 项（{label}）")

                picked = False
                try:
                    picked = frame.evaluate(self.JS_CLICK_OPTION, choice)
                except Exception:
                    picked = False
                if not picked:
                    try:
                        picked = frame.evaluate(self.JS_CLICK_DIV_OPTION, choice)
                    except Exception:
                        picked = False

                time.sleep(0.5)
                try:
                    frame.evaluate(self.JS_CLICK_BTN, "^(提交|提交答案|确定|继续)$")
                except Exception:
                    pass
                time.sleep(1.5)

                result = ""
                try:
                    result = frame.evaluate(self.JS_READ_RESULT)
                except Exception:
                    pass

                if self._result_is_wrong(result):
                    self.log(f"✗ 第 {choice + 1} 项答错，自动换下一个选项重试")
                    continue

                if self._result_is_right(result):
                    self.log(f"✓ 答对了（第 {choice + 1} 项：{label}），继续播放")
                    self._click_after_answer(frame)
                    return True

                # 没有明确结果提示：题目还在说明没提交成功，重试；弹窗消失视为已通过
                still_visible = False
                try:
                    still_visible = bool(frame.evaluate(self.JS_FIND_QUESTION))
                except Exception:
                    still_visible = False
                if still_visible and attempt < max_try - 1:
                    continue
                self.log(f"✓ 已作答（第 {choice + 1} 项：{label}），弹窗已消失，继续播放")
                self._click_after_answer(frame)
                return True

            self.log("✗ 所有选项都试过仍未答对，尝试关闭弹窗继续播放")
            self._click_after_answer(frame)
            return True
        return False

    def _handle_text_questions(self):
        """扫描所有 frame，处理填空题和简答题。"""
        for frame in self._live_frames():
            if self._close_requested.is_set():
                return False
            
            try:
                data = frame.evaluate(self.JS_FIND_TEXT_QUESTION)
            except Exception:
                continue
            
            if not data or not data.get("question"):
                continue
            
            question = data.get("question", "")
            input_count = data.get("inputCount", 1)
            input_type = data.get("inputType", "text")
            
            type_name = "简答题" if input_type == "textarea" else "填空题"
            self.log(f"检测到{type_name}（{input_count} 个输入框）：{question[:60]}")
            
            attempt = 0
            while True:
                if self._close_requested.is_set():
                    return False
                
                attempt += 1
                answer = self._generate_text_answer(question, input_count, input_type, attempt - 1)
                
                if not answer:
                    self.log(f"AI 生成答案失败（第 {attempt} 次尝试），1秒后重试...")
                    time.sleep(1)
                    continue
                
                if isinstance(answer, list):
                    for i, ans in enumerate(answer):
                        self.log(f"AI 生成答案 [{i+1}]（第 {attempt} 次尝试）：{ans[:100]}")
                else:
                    self.log(f"AI 生成答案（第 {attempt} 次尝试）：{answer[:100]}")
                
                try:
                    filled = frame.evaluate(self.JS_FILL_TEXT_ANSWER, answer)
                    if filled > 0:
                        self.log(f"已填写 {filled} 个输入框")
                    else:
                        self.log("填写失败")
                        continue
                except Exception as e:
                    self.log(f"填写答案时出错：{e}")
                    continue
                
                time.sleep(0.8)
                
                try:
                    frame.evaluate(self.JS_CLICK_BTN, "^(提交|提交答案|确定|继续|下一题)$")
                    self.log("已点击提交按钮")
                except Exception:
                    pass
                
                time.sleep(2)
                
                is_wrong = False
                try:
                    is_wrong = frame.evaluate(self.JS_CHECK_TEXT_ERROR)
                except Exception:
                    pass
                
                if is_wrong:
                    self.log(f"✗ 第 {attempt} 次作答错误，重新生成答案...")
                    time.sleep(1)
                    continue
                else:
                    self.log(f"✓ 文本题已作答（尝试 {attempt} 次后成功）")
                    try:
                        frame.evaluate(self.JS_CLICK_BTN, "^(继续|关闭|确定|知道了)$")
                    except Exception:
                        pass
                    return True
        
        return False

    def _click_after_answer(self, frame):
        """点掉答题结果/关闭类按钮。"""
        try:
            frame.evaluate(self.JS_CLICK_BTN, "^(关闭|确定|继续|我知道了|知道了|完成)$")
        except Exception:
            pass

    @staticmethod
    def _result_is_wrong(text):
        if not text:
            return False
        return bool(re.search(r"不正确|回答错误|答案错误|答错", text))

    @staticmethod
    def _result_is_right(text):
        if not text:
            return False
        if re.search(r"不正确|回答错误|答案错误|答错", text):
            return False
        return bool(re.search(r"回答正确|答案正确|答对了|正确|满分", text))

    def _pick_answer(self, question, options, tried):
        """选择答案：启用 AI 时问接口，失败或重复时按顺序试剩余选项。"""
        cfg = self.ai_config or {}
        if cfg.get("enabled") and cfg.get("api_key"):
            try:
                idx = self._ai_pick_option(question, options)
                if idx is not None and 0 <= idx < len(options) and idx not in tried:
                    self.log(f"AI 选择：第 {idx + 1} 项")
                    return idx
                self.log("AI 未给出有效答案，按顺序尝试剩余选项")
            except Exception as e:
                self.log(f"AI 调用失败（{e}），按顺序尝试剩余选项")
        for i in range(len(options)):
            if i not in tried:
                return i
        return None

    def _ai_pick_option(self, question, options):
        """调用 OpenAI 兼容接口挑选答案，返回选项下标。"""
        cfg = self.ai_config or {}
        if (cfg.get("reasoning") or "中") == "高":
            system_prompt = ("你是答题助手。根据题目从给定选项中选出最可能的正确答案。"
                             "可用不超过一行文字简述理由，最后一行只写选项序号。")
        else:
            system_prompt = ("你是答题助手。根据题目从给定选项中选出最可能的正确答案。"
                             "只回复选项序号（1、2、3……），不要任何其他文字。")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "题目：" + (question or "") + "\n选项：\n" + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(options))}
        ]
        endpoint = "/responses" if (self.ai_config.get("api_mode") or "chat") == "responses" else "/chat/completions"
        data, _ = self._ai_send(endpoint, payload=self._build_chat_payload(messages))
        content = ""
        try:
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        except Exception:
            pass
        nums = re.findall(r"\d+", content or "")
        if not nums:
            return None
        return int(nums[-1]) - 1

    def _generate_text_answer(self, question, input_count=1, input_type="text", retry_attempt=0):
        """调用 AI 生成填空题/简答题的文本答案。"""
        cfg = self.ai_config or {}
        
        if not cfg.get("enabled") or not cfg.get("api_key"):
            return None
        
        try:
            if input_type == "textarea":
                system_prompt = "你是答题助手。请根据题目要求给出准确、完整的答案。简答题需要完整表述，字数在50-200字之间。直接给出答案内容，不要添加前缀。"
                if retry_attempt > 0:
                    system_prompt += f"\n这是第{retry_attempt + 1}次尝试，请换一个角度或更详细地回答。"
            else:
                if input_count == 1:
                    system_prompt = "你是答题助手。请根据题目要求给出准确的填空答案。答案要简洁精确，通常是一个词、短语或数字。直接给出答案，不要添加任何说明或标点。"
                else:
                    system_prompt = f"你是答题助手。这道题有{input_count}个空需要填写。请给出{input_count}个答案，每行一个答案，不要编号。答案要简洁精确。"
                if retry_attempt > 0:
                    system_prompt += f"\n这是第{retry_attempt + 1}次尝试，之前的答案不正确，请重新思考。"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            endpoint = "/responses" if (cfg.get("api_mode") or "chat") == "responses" else "/chat/completions"
            data, _ = self._ai_send(endpoint, payload=self._build_chat_payload(messages))
            
            content = ""
            try:
                content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
            except Exception:
                return None
            
            if not content or not content.strip():
                return None
            
            content = content.strip()
            
            if input_count > 1:
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                cleaned_lines = []
                for line in lines:
                    line = re.sub(r'^\d+[.、\s]+', '', line)
                    if line:
                        cleaned_lines.append(line)
                
                if len(cleaned_lines) >= input_count:
                    return cleaned_lines[:input_count]
                elif len(cleaned_lines) > 0:
                    while len(cleaned_lines) < input_count:
                        cleaned_lines.append(cleaned_lines[0])
                    return cleaned_lines
                else:
                    parts = re.split(r'[,，;；]', content)
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) >= input_count:
                        return parts[:input_count]
                    else:
                        return content
            
            return content
            
        except Exception as e:
            self.log(f"AI 生成答案出错：{e}")
            return None

    @staticmethod
    def _normalize_ai_base_url(base_url):
        """规范化接口地址：补协议头、去尾部斜杠；OpenAI 官方域名不带路径时补 /v1。

        缺少协议头时自动补全（公网域名用 https://，本机/内网地址用 http://），
        与专升本助手行为对齐，避免地址被当作本地文件路径。
        """
        trimmed = (base_url or "").strip().rstrip("/")
        if not trimmed:
            return ""
        if "://" not in trimmed:
            low = trimmed.lower()
            is_local = (low.startswith("localhost") or low.startswith("127.") or low.startswith("192.168.")
                        or low.startswith("10.") or low.startswith("169.254.") or low.startswith("[::1]")
                        or bool(re.match(r"^172\.(1[6-9]|2\d|3[01])\.", low)))
            trimmed = ("http://" if is_local else "https://") + trimmed
        if "api.openai.com" in trimmed and "/" not in trimmed.split("//", 1)[1]:
            trimmed += "/v1"
        return trimmed

    @staticmethod
    def _is_local_ai_target(target):
        """判断是否本机/内网/非 HTTPS 地址（这类地址不能交给公网应用中转）。"""
        try:
            parsed = urllib.parse.urlparse(target)
            host = (parsed.hostname or "").lower()
            if parsed.scheme != "https":
                return True
            if host in ("localhost", "::1", "0.0.0.0") or host.endswith(".localhost") or host.endswith(".local"):
                return True
            parts = host.split(".")
            if len(parts) == 4 and all(p.isdigit() for p in parts):
                n = [int(p) for p in parts]
                return (n[0] in (10, 127)
                        or (n[0] == 192 and n[1] == 168)
                        or (n[0] == 172 and 16 <= n[1] <= 31)
                        or (n[0] == 169 and n[1] == 254))
            return False
        except Exception:
            return False

    @staticmethod
    def _network_error_hint(url, error):
        """把网络层错误翻译成可操作的中文提示。"""
        reason = str(error)
        if "No such file or directory" in reason:
            return (f"接口地址格式不正确：'{url}' 被当作本地文件路径处理。"
                    f"请检查是否缺少 https:// 前缀，例如 https://api.example.com/v1")
        if "10061" in reason or "积极拒绝" in reason:
            return f"连接被拒绝（{url}）：目标端口上没有服务在监听，请确认接口地址和端口是否正确"
        if "getaddrinfo failed" in reason or "name or service not known" in reason.lower():
            return f"域名解析失败（{url}）：请检查域名拼写和网络连接"
        if "timed out" in reason.lower() or "超时" in reason:
            return f"连接超时（{url}）：请检查网络，或在设置中增大请求超时时间"
        return f"网络请求失败（{url}）：{reason}"

    def _ai_endpoint_candidates(self, base_url, endpoint):
        """由 Base URL 生成请求端点：严格按用户填写的地址，不自动加 /v1。

        只做两件事：把 Base URL 与端点路径（/chat/completions、/models 等）拼接；
        若填的已是完整端点则不重复拼接。缺协议头仍会自动补全（否则无法发请求）。
        """
        base = self._normalize_ai_base_url(base_url)
        if not base:
            return [endpoint]
        known = ("/chat/completions", "/responses", "/models")
        path = urllib.parse.urlparse(base).path.rstrip("/")
        for item in known:
            if path.endswith(item):
                base = base[: len(base) - len(item)]
                break
        return [base.rstrip("/") + endpoint]

    def _ai_headers(self):
        """组装请求头：自定义头 + Bearer Key（已被自定义头覆盖时不重复添加）。"""
        headers = {"Content-Type": "application/json"}
        custom = self.ai_config.get("custom_headers")
        if isinstance(custom, dict):
            for k, v in custom.items():
                name = str(k).strip()
                if name and name.lower() not in ("content-length", "host", "cookie"):
                    headers[name] = str(v)
        api_key = (self.ai_config.get("api_key") or "").strip()
        if api_key and not any(h.lower() in ("authorization", "api-key", "x-api-key") for h in headers):
            headers["Authorization"] = "Bearer " + api_key
        return headers

    def _proxy_endpoint(self):
        """规范化应用中转地址（移植 proxyEndpoint：根地址 / /api/ai / /models 均可）。"""
        configured = self._normalize_ai_base_url((self.ai_config.get("proxy_url") or "").strip())
        if not configured:
            configured = self.DEFAULT_AI_PROXY_URL
        try:
            parsed = urllib.parse.urlparse(configured)
            path = parsed.path.rstrip("/")
            if not path or path == "/":
                path = "/api/ai/proxy"
            elif path.endswith("/models"):
                path = path[: -len("/models")] + "/proxy"
            elif path.endswith("/api/ai"):
                path = path + "/proxy"
            elif not path.endswith("/proxy"):
                path = path + "/api/ai/proxy"
            return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))
        except Exception:
            return self.DEFAULT_AI_PROXY_URL

    @staticmethod
    def _ai_error_message(status, body=""):
        """把 HTTP 状态码翻译成可操作的中文提示。"""
        if status in (401, 403):
            return f"请求失败（HTTP {status}）：API Key 无效或没有该模型权限，请检查 Key"
        if status == 404:
            return "请求失败（HTTP 404）：接口地址或模型名不正确，请检查地址（Base URL 一般需要包含 /v1）"
        if status == 402:
            return "请求失败（HTTP 402）：账户余额或套餐额度不足"
        if status in (408, 429):
            return f"请求失败（HTTP {status}）：请求超时或触发限流，请稍后重试"
        if status >= 500:
            return f"请求失败（HTTP {status}）：服务商临时故障，请稍后重试"
        detail = (body or "").strip().replace("\n", " ")[:120]
        return f"请求失败（HTTP {status}）" + (f"：{detail}" if detail else "")

    @staticmethod
    def _safe_error_body(e):
        try:
            return e.read().decode("utf-8", "ignore")
        except Exception:
            return ""

    def _parse_ai_response(self, raw):
        """解析响应：JSON / SSE 流式文本统一转成 {choices:[{message:{content}}]}。"""
        raw = (raw or "").strip()
        if not raw:
            raise RuntimeError("接口返回了空内容")
        if raw.startswith("data:") or "\ndata:" in raw[:200]:
            text = self._parse_sse_text(raw)
            return {"choices": [{"message": {"content": text}}]}
        try:
            return json.loads(raw)
        except Exception:
            compact = raw.replace("\n", " ")[:120]
            head = raw[:20].lower()
            if head.startswith("<!doctype") or head.startswith("<html"):
                raise RuntimeError("接口返回了网页而不是 JSON，请检查接口地址是否正确")
            raise RuntimeError("接口返回了非 JSON 内容：" + compact)

    @staticmethod
    def _parse_sse_text(raw):
        """解析 OpenAI 兼容 SSE 的 data 行，拼接增量文本。"""
        full = ""
        for line in (raw or "").splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                j = json.loads(payload)
            except Exception:
                continue
            try:
                choice = j.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                piece = delta.get("content")
                if piece is None:
                    piece = choice.get("message", {}).get("content")
            except Exception:
                piece = None
            if isinstance(piece, str):
                full += piece
            elif isinstance(piece, list):
                for part in piece:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        full += part["text"]
        return full

    def _ai_opener(self):
        """AI 请求专用 opener。

        - 不走系统代理：本机代理软件经常未运行，urllib 默认读取系统代理会直接"积极拒绝"。
        - 用 certifi 的 CA 证书：Windows 的 Python 没有系统证书库，默认验证会报
          [Errno 2] No such file or directory。上游（豆包/DeepSeek/千问）国内均可直连。
        """
        cached = getattr(self, "_ai_opener_cache", None)
        if cached is not None:
            return cached
        try:
            import certifi
            ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ssl_ctx = ssl.create_default_context()
        handlers = [urllib.request.ProxyHandler({}),
                    urllib.request.HTTPSHandler(context=ssl_ctx)]
        cached = urllib.request.build_opener(*handlers)
        self._ai_opener_cache = cached
        return cached

    def _ai_direct(self, url, method, payload, headers, timeout):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with self._ai_opener().open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "ignore")
        return self._parse_ai_response(raw)

    def _ai_via_proxy(self, target_url, headers, payload, timeout):
        """经应用中转转发：POST {target, headers, payload}，密钥仅随单次请求转发。"""
        proxy = self._proxy_endpoint()
        body = {"target": target_url, "headers": dict(headers)}
        if payload is not None:
            body["payload"] = payload
        req = urllib.request.Request(
            proxy,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with self._ai_opener().open(req, timeout=timeout + 10) as resp:
            raw = resp.read().decode("utf-8", "ignore")
        return self._parse_ai_response(raw)

    def _ai_send(self, endpoint, payload=None, timeout=20):
        """按配置的请求方式发送请求，返回 (解析后的json, 实际上游地址)。

        - 浏览器直连：直接请求接口（桌面程序无跨域限制）
        - 应用中转：经中转地址转发（接口被拦截/屏蔽或只允许 HTTPS 白名单时使用）
        - 经内置浏览器：通过 AI 专属无头 Chromium 发请求（真实浏览器指纹，可过
          Cloudflare 等对非浏览器客户端的指纹拦截，例如"error code: 1010"；
          首次使用自动启动，与刷课浏览器互不干扰）
        - 自动：先按候选顺序直连；被 Cloudflare 拦截（403）时自动改走 AI 浏览器
          通道；候选挂起超时自动换下一个；全部候选超时也走浏览器通道兜底
        403/404/405 自动尝试下一个端点候选（根地址补 /v1）。
        """
        method = "POST" if payload is not None else "GET"
        headers = self._ai_headers()
        transport = (self.ai_config.get("transport") or "auto").strip() or "auto"
        candidates = self._ai_endpoint_candidates(self.ai_config.get("api_url"), endpoint)
        errors = []  # 记录每个候选的失败原因，最终汇总给用户


        for idx, url in enumerate(candidates):
            has_next = idx < len(candidates) - 1
            if transport == "browser":
                return self._ai_via_browser(url, headers, payload, timeout), url
            if transport == "proxy":
                if self._is_local_ai_target(url):
                    raise RuntimeError("本机、内网或 HTTP 接口不能走应用中转，请把请求方式切换为“浏览器直连”")
                try:
                    return self._ai_via_proxy(url, headers, payload, timeout), url
                except urllib.error.HTTPError as e:
                    body = self._safe_error_body(e)
                    last_error = self._ai_error_message(e.code, body)
                    if e.code == 403 and self._looks_like_cloudflare(body):
                        try:
                            return self._ai_via_browser(url, headers, payload, timeout), url
                        except Exception:
                            pass
                    if e.code in (403, 404, 405) and has_next:
                        # 403 也换候选：部分网关根地址返回 403，真正端点在 /v1 下
                        continue
                    raise RuntimeError(f"{last_error}（请求：{url}｜方式：应用中转）")
                except (urllib.error.URLError, OSError) as e:
                    raise RuntimeError(self._network_error_hint(self._proxy_endpoint(), e))
            try:
                return self._ai_direct(url, method, payload, headers, timeout), url
            except urllib.error.HTTPError as e:
                body = self._safe_error_body(e)
                last_error = self._ai_error_message(e.code, body)
                if e.code == 403 and self._looks_like_cloudflare(body):
                    # Cloudflare 指纹拦截：Python/中转都过不去，只有真浏览器能过
                    try:
                        return self._ai_via_browser(url, headers, payload, timeout), url
                    except Exception as be:
                        errors.append(f"{url} 被Cloudflare拦截，浏览器通道也未成功：{be}")
                        last_error = errors[-1]
                else:
                    errors.append(f"{url} → {last_error}")
                if e.code in (403, 404, 405) and has_next:
                    continue
                raise RuntimeError(f"{last_error}（请求：{url}｜方式：直连）")
            except (urllib.error.URLError, OSError) as e:
                direct_hint = self._network_error_hint(url, e)
                timed_out = ("timed out" in str(e).lower() or "10060" in str(e)
                             or "超时" in str(e) or "timed out" in direct_hint)
                if timed_out:
                    # 当前候选挂起超时（部分网关的非标准路径是黑洞路由），换下一个候选；
                    # 全部候选都超时时在循环后走浏览器兜底
                    errors.append(direct_hint)
                    continue
                if transport == "direct":
                    raise RuntimeError(direct_hint)
                if self._is_local_ai_target(url):
                    # 本机/内网地址无法交给公网中转，直接给出直连诊断
                    raise RuntimeError(direct_hint)
                try:
                    return self._ai_via_proxy(url, headers, payload, timeout), url
                except Exception as pe:
                    raise RuntimeError(f"直连与应用中转均失败。直连：{direct_hint}；中转：{pe}")

        # 收尾：全部候选都挂起超时（如 Cloudflare 对非浏览器请求黑洞处理），
        # 用 AI 专属浏览器通道逐个候选兜底（通道会自动启动，无需先点启动浏览器）
        for url in candidates:
            try:
                return self._ai_via_browser(url, headers, payload, timeout), url
            except Exception:
                continue
        detail = "；".join(errors) if errors else "未知错误"
        cf_guide = ""
        if not browser_alive:
            cf_guide = ("\n提示：该接口可能开启了 Cloudflare 浏览器验证，不开浏览器是无法连通的。"
                        "请先点击“启动浏览器并登录”打开浏览器，AI 请求会自动改从浏览器发出。")
        raise RuntimeError(f"所有候选地址均连接超时：{detail}{cf_guide}")

    @staticmethod
    def _looks_like_cloudflare(body):
        """识别 Cloudflare 指纹拦截类响应（error 1010/1020、Access denied 等）。"""
        low = (body or "").lower()
        return ("error code: 1010" in low or "error code: 1020" in low
                or "cloudflare" in low or "just a moment" in low
                or ("access denied" in low and "cloudflare" in low))

    def _browser_fetch(self, url, headers, payload, timeout):
        """在 AI 浏览器线程内：用 AI 专用页面同源 fetch 发请求。

        页面由真实 Chromium 加载，TLS/浏览器指纹可过 Cloudflare 的客户端校验；
        同源请求不受 CORS 限制。仅可在 AI 浏览器线程调用（Playwright 对象线程绑定）。
        """
        ai_page = getattr(self, "_ai_page", None)
        if ai_page is None or ai_page.is_closed():
            raise RuntimeError("AI 浏览器通道未就绪")
        page = ai_page
        parsed = urllib.parse.urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if not page.url.startswith(origin):
            page.goto(origin + "/", timeout=max(timeout, 20) * 1000, wait_until="domcontentloaded")
            time.sleep(1)  # 留给 Cloudflare 质询脚本执行
        result = page.evaluate("""
            async ([url, headers, payload]) => {
                try {
                    const resp = await fetch(url, {
                        method: payload ? 'POST' : 'GET',
                        headers: headers,
                        body: payload ? JSON.stringify(payload) : undefined
                    });
                    const text = await resp.text();
                    return { status: resp.status, text: text.slice(0, 500000) };
                } catch (e) {
                    return { status: 0, text: 'fetch error: ' + String(e) };
                }
            }
        """, [url, headers, payload])
        if result.get("status") == 0:
            raise RuntimeError("浏览器通道请求失败：" + str(result.get("text"))[:150])
        raw = result.get("text") or ""
        if result.get("status") == 403 and self._looks_like_cloudflare(raw):
            # 可能撞上质询页：等它跑完再试一次
            time.sleep(3)
            retry = page.evaluate("""
                async ([url, headers, payload]) => {
                    try {
                        const resp = await fetch(url, {
                            method: payload ? 'POST' : 'GET',
                            headers: headers,
                            body: payload ? JSON.stringify(payload) : undefined
                        });
                        const text = await resp.text();
                        return { status: resp.status, text: text.slice(0, 500000) };
                    } catch (e) {
                        return { status: 0, text: 'fetch error: ' + String(e) };
                    }
                }
            """, [url, headers, payload])
            if retry.get("status") == 0:
                raise RuntimeError("浏览器通道请求失败：" + str(retry.get("text"))[:150])
            if retry.get("status") >= 400:
                raise RuntimeError(f"HTTP {retry['status']}（浏览器通道）：{(retry.get('text') or '')[:120]}")
            return self._parse_ai_response(retry.get("text"))
        if result.get("status") >= 400:
            raise RuntimeError(f"HTTP {result['status']}（浏览器通道）：{(result.get('text') or '')[:120]}")
        return self._parse_ai_response(raw)

    def _ensure_ai_browser(self):
        """确保 AI 专属无头浏览器已启动（首次调用时自动启动，与刷课浏览器互不干扰）。"""
        if self._ai_browser_ready.is_set():
            return True
        if getattr(self, "_ai_worker_started", False):
            # 已在启动中，等它就绪
            return self._ai_browser_ready.wait(45)
        self._ai_worker_started = True
        self.log("正在启动 AI 浏览器通道（独立无头浏览器，用于过 Cloudflare 防护）...")
        threading.Thread(target=self._ai_browser_worker, daemon=True,
                         name="ai-browser-worker").start()
        ok = self._ai_browser_ready.wait(45)
        if ok:
            self.log("✓ AI 浏览器通道已就绪")
        else:
            self.log("✗ AI 浏览器通道启动超时")
        return ok

    def _ai_browser_worker(self):
        """AI 专属浏览器线程：独立无头 Chromium，串行处理 AI 请求队列。

        与刷课用的浏览器完全分离，因此登录等待、刷课过程中 AI 请求随时可用。
        """
        try:
            self._ai_playwright = sync_playwright().start()
            self._ai_browser = self._ai_playwright.chromium.launch(
                headless=True,
                args=["--autoplay-policy=no-user-gesture-required",
                      "--no-first-run", "--no-default-browser-check"]
            )
            self._ai_context = self._ai_browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            self._ai_page = self._ai_context.new_page()
            self._ai_browser_ready.set()
        except Exception as e:
            self.log(f"✗ AI 浏览器通道启动失败：{e}")
            self._ai_worker_started = False
            return
        while True:
            job = self._ai_jobs.get()
            if job is None:
                break
            try:
                job()
            except Exception as e:
                self.log(f"AI 浏览器通道任务异常：{e}")

    def _ai_via_browser(self, url, headers, payload, timeout):
        """经 AI 专属浏览器发请求。任意线程可调；请求排队由 AI 线程串行执行。"""
        if not self._ensure_ai_browser():
            raise RuntimeError("AI 浏览器通道未就绪，请稍后重试")
        box = {}
        done = threading.Event()

        def job():
            try:
                box["data"] = self._browser_fetch(url, headers, payload, timeout)
            except Exception as e:
                box["error"] = e
            finally:
                done.set()

        self._ai_jobs.put(job)
        if not done.wait(timeout + 30):
            raise RuntimeError("浏览器通道请求超时")
        if "error" in box:
            raise box["error"]
        return box["data"]

    def _build_chat_payload(self, messages):
        """按接口协议（对话补全 / Responses）与高级配置构造请求体。"""
        cfg = self.ai_config
        model = (cfg.get("model") or "").strip()
        mode = (cfg.get("api_mode") or "chat").strip() or "chat"
        try:
            max_tokens = int(cfg.get("max_tokens")) if str(cfg.get("max_tokens") or "").strip() else None
        except (TypeError, ValueError):
            max_tokens = None
        try:
            temperature = float(cfg.get("temperature")) if str(cfg.get("temperature") or "").strip() else 0.2
        except (TypeError, ValueError):
            temperature = 0.2
        # 推理模型通常不接受 temperature（与原项目 isReasoningModel 规则一致）
        is_reasoning = bool(re.search(r"(?:^|[-_/.])(?:o1|o3|o4|gpt-5)(?:[-_/.]|$)", model.lower()))
        payload = {"model": model, "stream": bool(cfg.get("stream"))}
        if mode == "responses":
            payload["input"] = [
                {"role": m["role"], "content": [{"type": "input_text", "text": m["content"]}]}
                for m in messages
            ]
            if not is_reasoning:
                payload["temperature"] = temperature
            if max_tokens:
                payload["max_output_tokens"] = max_tokens
        else:
            payload["messages"] = messages
            if not is_reasoning:
                payload["temperature"] = temperature
            if max_tokens:
                payload["max_tokens"] = max_tokens
        return payload

    def _fetch_ai_models(self):
        """GET /models 拉取模型列表（兼容 OpenAI data 与常见网关 models/items 格式）。"""
        if not (self.ai_config.get("api_url") or "").strip():
            raise RuntimeError("读取模型列表需要先填写接口地址")
        if not (self.ai_config.get("api_key") or "").strip():
            raise RuntimeError("读取模型列表需要先填写 API Key")
        try:
            data, used_url = self._ai_send("/models", timeout=25)
        except RuntimeError as e:
            if "HTTP 403" in str(e) or "HTTP 401" in str(e):
                raise RuntimeError(
                    "模型列表接口被拒绝（" + str(e).split("（")[0].strip() + "）。"
                    "很多中转站不开放 /models 列表接口，这不影响 AI 答题："
                    "请直接手动输入模型名（中转站后台可查），然后点「测试连接」验证。"
                )
            raise
        self.log(f"[AI] 模型列表来自：{used_url}")
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = None
            for key in ("data", "models", "items"):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break
        else:
            items = None
        if not items:
            raise RuntimeError("上游返回了空模型列表，请确认接口支持 GET /models")
        names = []
        for item in items:
            if isinstance(item, str) and item.strip():
                names.append(item.strip())
            elif isinstance(item, dict):
                for key in ("id", "model", "model_id", "modelId", "slug", "name"):
                    if isinstance(item.get(key), str) and item[key].strip():
                        names.append(item[key].strip())
                        break
        unique = []
        seen = set()
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        if not unique:
            raise RuntimeError("未能从接口响应中解析出模型名")
        return unique

    def _test_ai_connection(self):
        """连接测试：发一条极短消息验证地址、Key、模型三者都可用。"""
        if not (self.ai_config.get("model") or "").strip():
            raise RuntimeError("请先填写或拉取模型名称")
        try:
            timeout = float(self.ai_config.get("timeout_s") or 60)
        except (TypeError, ValueError):
            timeout = 60.0
        endpoint = "/responses" if (self.ai_config.get("api_mode") or "chat") == "responses" else "/chat/completions"
        data, used_url = self._ai_send(
            endpoint,
            payload=self._build_chat_payload([{"role": "user", "content": "请回复:连接成功"}]),
            timeout=max(timeout, 20.0)
        )
        text = ""
        try:
            text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        except Exception:
            pass
        return used_url, (text or "").strip()

    def _load_ai_config(self):
        """从脚本目录 config.json 读取 AI 答题配置（缺省关闭）。"""
        path = os.path.join(APP_DIR, "config.json")
        default = {
            "enabled": False,
            "api_url": "",
            "api_key": "",
            "model": "",
            "transport": "auto",
            "proxy_url": self.DEFAULT_AI_PROXY_URL,
            "api_mode": "chat",
            "timeout_s": "60",
            "max_tokens": "2048",
            "temperature": "0.2",
            "stream": False,
            "custom_headers": {},
            "reasoning": "中"
        }
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k in list(default.keys()):
                    if k in data:
                        default[k] = data[k]
        except Exception:
            pass
        if isinstance(default.get("custom_headers"), str):
            try:
                parsed = json.loads(default["custom_headers"])
                default["custom_headers"] = parsed if isinstance(parsed, dict) else {}
            except Exception:
                default["custom_headers"] = {}
        return default

    def _save_ai_config(self):
        path = os.path.join(APP_DIR, "config.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.ai_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"✗ 保存配置失败：{e}")

    def _open_ai_settings(self):
        """AI 答题设置对话框：完整配置 + 拉取模型列表 + 测试连接 + 保存。"""
        cfg = self.ai_config or {}
        win = tk.Toplevel(self.root)
        win.title("AI 答题设置")
        win.geometry("700x660")
        win.configure(bg="#161D2B")
        win.transient(self.root)
        win.grab_set()

        outer = tk.Frame(win, bg="#161D2B")
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, bg="#161D2B", highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg="#161D2B")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw", width=660)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        def on_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>") if e.widget is win else None)

        tip = tk.Label(
            body, bg="#161D2B", fg="#A1A1AA", justify="left",
            text=("视频弹题默认使用本地策略：自动选一个选项提交，答错会自动换选项重答，直到答对。\n"
                  "开启 AI 后把题干和选项发给所填接口挑选答案；调用失败自动回退本地策略。")
        )
        tip.pack(anchor="w", padx=20, pady=(12, 4))

        var_enabled = tk.BooleanVar(value=bool(cfg.get("enabled")))
        tk.Checkbutton(body, text="启用 AI 答题（未启用时使用本地策略）", variable=var_enabled,
                       bg="#161D2B", fg="#F4F4F5", selectcolor="#1E2636",
                       activebackground="#161D2B", activeforeground="#F4F4F5").pack(anchor="w", padx=20, pady=4)

        entries = {}

        def add_field(label, key, show="", width=66):
            tk.Label(body, text=label, bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
            e = tk.Entry(body, width=width, bg="#1E2636", fg="#F4F4F5",
                         insertbackground="#F4F4F5", show=show)
            e.insert(0, str(cfg.get(key, "") if cfg.get(key) is not None else ""))
            e.pack(fill=tk.X, padx=20, pady=2)
            entries[key] = e
            return e

        # 服务商预设（与专升本学习助手一致）：选预设自动填接口地址和模型
        AI_PROVIDERS = [
            ("豆包(火山方舟)", "https://ark.cn-beijing.volces.com/api/v3", "doubao-1-5-lite-32k-250115"),
            ("DeepSeek", "https://api.deepseek.com/v1", "deepseek-chat"),
            ("通义千问(阿里云百炼)", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
            ("自定义(OpenAI 兼容网关)", "", ""),
        ]
        current_url = str(cfg.get("api_url") or "").strip().rstrip("/")
        preset_idx = len(AI_PROVIDERS) - 1
        for i, (_, base, _) in enumerate(AI_PROVIDERS[:-1]):
            if current_url == base:
                preset_idx = i
                break
        tk.Label(body, text="服务商（选择后自动填入接口地址和模型；自定义则手动填写网关地址）",
                 bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
        provider_var = tk.StringVar(value=AI_PROVIDERS[preset_idx][0])
        provider_box = ttk.Combobox(body, textvariable=provider_var, width=40,
                                    values=[p[0] for p in AI_PROVIDERS], state="readonly")
        provider_box.pack(anchor="w", padx=20, pady=2)

        def on_provider_change(event=None):
            name = provider_var.get()
            for pname, pbase, pmodel in AI_PROVIDERS:
                if pname == name and pbase:
                    entries["api_url"].delete(0, tk.END)
                    entries["api_url"].insert(0, pbase)
                    try:
                        model_var.set(pmodel)
                    except Exception:
                        pass
                    break
        provider_box.bind("<<ComboboxSelected>>", on_provider_change)

        add_field("接口地址 Base URL（填到 /v1 为止，例如 https://756777.xyz/v1）", "api_url")

        preview_var = tk.StringVar(value="")
        preview_label = tk.Label(body, textvariable=preview_var, bg="#161D2B", fg="#6EE7B7",
                                 justify="left", wraplength=640)
        preview_label.pack(anchor="w", padx=20, pady=(2, 0))

        def update_preview(*_):
            base = entries["api_url"].get().strip()
            if not base:
                preview_var.set("")
                return
            try:
                cands = self._ai_endpoint_candidates(base, "/chat/completions")
                text = "将请求：" + cands[0]
                if len(cands) > 1:
                    text += "（不通时自动重试 " + cands[1] + "）"
                preview_var.set(text)
            except Exception:
                preview_var.set("")

        entries["api_url"].bind("<KeyRelease>", update_preview)
        update_preview()

        add_field("API Key", "api_key", show="*")

        tk.Label(body, text="模型（可手动输入，或点“拉取模型列表”从接口读取）",
                 bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
        model_row = tk.Frame(body, bg="#161D2B")
        model_row.pack(fill=tk.X, padx=20, pady=2)
        model_var = tk.StringVar(value=str(cfg.get("model", "") or ""))
        model_box = ttk.Combobox(model_row, textvariable=model_var, width=50)
        model_box.pack(side=tk.LEFT)

        # 请求方式 / 应用中转
        tk.Label(body, text="请求方式", bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
        var_transport = tk.StringVar(value=str(cfg.get("transport") or "auto"))
        transport_row = tk.Frame(body, bg="#161D2B")
        transport_row.pack(anchor="w", padx=20)
        for text, value in [("自动（推荐）", "auto"), ("浏览器直连", "direct"),
                            ("应用中转", "proxy"), ("经内置浏览器", "browser")]:
            tk.Radiobutton(transport_row, text=text, value=value, variable=var_transport,
                           bg="#161D2B", fg="#F4F4F5", selectcolor="#1E2636",
                           activebackground="#161D2B", activeforeground="#F4F4F5").pack(side=tk.LEFT)
        tk.Label(body, text="应用中转地址（自动/应用中转时使用；密钥仅随单次请求转发）",
                 bg="#161D2B", fg="#A1A1AA").pack(anchor="w", padx=20, pady=(4, 0))
        entry_proxy = tk.Entry(body, width=66, bg="#1E2636", fg="#F4F4F5", insertbackground="#F4F4F5")
        entry_proxy.insert(0, str(cfg.get("proxy_url") or self.DEFAULT_AI_PROXY_URL))
        entry_proxy.pack(fill=tk.X, padx=20, pady=2)

        # 接口协议
        tk.Label(body, text="接口协议（大多数中转使用对话补全接口）",
                 bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
        var_mode = tk.StringVar(value=str(cfg.get("api_mode") or "chat"))
        mode_row = tk.Frame(body, bg="#161D2B")
        mode_row.pack(anchor="w", padx=20)
        for text, value in [("对话补全接口", "chat"), ("Responses API", "responses")]:
            tk.Radiobutton(mode_row, text=text, value=value, variable=var_mode,
                           bg="#161D2B", fg="#F4F4F5", selectcolor="#1E2636",
                           activebackground="#161D2B", activeforeground="#F4F4F5").pack(side=tk.LEFT)

        # 高级参数
        tk.Label(body, text="请求超时（秒）／ 最大输出 Token ／ 温度",
                 bg="#161D2B", fg="#F4F4F5").pack(anchor="w", padx=20, pady=(8, 0))
        adv_row = tk.Frame(body, bg="#161D2B")
        adv_row.pack(fill=tk.X, padx=20)
        entry_timeout = tk.Entry(adv_row, width=10, bg="#1E2636", fg="#F4F4F5", insertbackground="#F4F4F5")
        entry_timeout.insert(0, str(cfg.get("timeout_s", "60")))
        entry_maxtok = tk.Entry(adv_row, width=10, bg="#1E2636", fg="#F4F4F5", insertbackground="#F4F4F5")
        entry_maxtok.insert(0, str(cfg.get("max_tokens", "2048")))
        entry_temp = tk.Entry(adv_row, width=10, bg="#1E2636", fg="#F4F4F5", insertbackground="#F4F4F5")
        entry_temp.insert(0, str(cfg.get("temperature", "0.2")))
        entry_timeout.pack(side=tk.LEFT)
        entry_maxtok.pack(side=tk.LEFT, padx=(12, 0))
        entry_temp.pack(side=tk.LEFT, padx=(12, 0))

        # 流式输出 / 思考程度
        opt_row = tk.Frame(body, bg="#161D2B")
        opt_row.pack(anchor="w", padx=20, pady=(8, 0))
        var_stream = tk.BooleanVar(value=bool(cfg.get("stream")))
        tk.Checkbutton(opt_row, text="启用流式输出", variable=var_stream,
                       bg="#161D2B", fg="#F4F4F5", selectcolor="#1E2636",
                       activebackground="#161D2B", activeforeground="#F4F4F5").pack(side=tk.LEFT)
        tk.Label(opt_row, text="    思考程度：", bg="#161D2B", fg="#F4F4F5").pack(side=tk.LEFT)
        var_reason = tk.StringVar(value=str(cfg.get("reasoning") or "中"))
        for text in ("低", "中", "高"):
            tk.Radiobutton(opt_row, text=text, value=text, variable=var_reason,
                           bg="#161D2B", fg="#F4F4F5", selectcolor="#1E2636",
                           activebackground="#161D2B", activeforeground="#F4F4F5").pack(side=tk.LEFT)

        # 自定义请求头
        tk.Label(body, text="自定义请求(JSON)，例如 {\"X-Channel\":\"codex\"}；需要 x-api-key 时在此填写，不要把密钥写进代码",
                 bg="#161D2B", fg="#A1A1AA").pack(anchor="w", padx=20, pady=(8, 0))
        text_headers = tk.Text(body, height=3, bg="#1E2636", fg="#F4F4F5",
                               insertbackground="#F4F4F5", relief="flat")
        try:
            ch = cfg.get("custom_headers") or {}
            if isinstance(ch, dict) and ch:
                text_headers.insert("1.0", json.dumps(ch, ensure_ascii=False, indent=2))
        except Exception:
            pass
        text_headers.pack(fill=tk.X, padx=20, pady=2)

        status_var = tk.StringVar(value="")
        status_label = tk.Label(body, textvariable=status_var, bg="#161D2B",
                                fg="#6EE7B7", justify="left", wraplength=640)
        status_label.pack(anchor="w", padx=20, pady=(10, 0))

        busy = {"flag": False}

        def apply_inputs():
            headers_raw = text_headers.get("1.0", "end").strip()
            headers = {}
            if headers_raw:
                try:
                    parsed = json.loads(headers_raw)
                    if isinstance(parsed, dict):
                        headers = {str(k): str(v) for k, v in parsed.items()}
                    else:
                        status_var.set("✗ 自定义请求头必须是 JSON 对象，已忽略")
                except Exception:
                    status_var.set("✗ 自定义请求头不是有效 JSON，已忽略")
            self.ai_config = {
                "enabled": bool(var_enabled.get()),
                "api_url": entries["api_url"].get().strip(),
                "api_key": entries["api_key"].get().strip(),
                "model": model_var.get().strip(),
                "transport": var_transport.get(),
                "proxy_url": entry_proxy.get().strip(),
                "api_mode": var_mode.get(),
                "timeout_s": entry_timeout.get().strip() or "60",
                "max_tokens": entry_maxtok.get().strip() or "2048",
                "temperature": entry_temp.get().strip() or "0.2",
                "stream": bool(var_stream.get()),
                "custom_headers": headers,
                "reasoning": var_reason.get()
            }

        def run_bg(task, on_done):
            def worker():
                try:
                    result = task()
                    error = None
                except Exception as e:
                    result, error = None, str(e)

                def deliver():
                    busy["flag"] = False
                    on_done(result, error)

                self._post_to_ui(deliver)
            threading.Thread(target=worker, daemon=True).start()

        def fetch_models():
            if busy["flag"]:
                return
            apply_inputs()
            if not self.ai_config["api_url"]:
                status_var.set("✗ 请先填写接口地址")
                status_label.configure(fg="#F87171")
                return
            busy["flag"] = True
            status_var.set("正在拉取模型列表…")
            status_label.configure(fg="#A1A1AA")

            def on_done(models, error):
                if error:
                    status_var.set(f"✗ {error}")
                    status_label.configure(fg="#F87171")
                    self.log(f"[AI] 拉取模型列表失败：{error}")
                    return
                model_box.configure(values=tuple(models))
                if models and not model_var.get().strip():
                    model_var.set(models[0])
                status_var.set(f"✓ 已拉取 {len(models)} 个模型，请在下拉框中选择")
                status_label.configure(fg="#6EE7B7")

            run_bg(self._fetch_ai_models, on_done)

        def test_connection():
            if busy["flag"]:
                return
            apply_inputs()
            busy["flag"] = True
            status_var.set("正在测试连接…")
            status_label.configure(fg="#A1A1AA")

            def on_done(result, error):
                if error:
                    status_var.set(f"✗ {error}")
                    status_label.configure(fg="#F87171")
                    self.log(f"[AI] 测试连接失败：{error}")
                    return
                used_url, reply = result
                short = reply[:40] + ("…" if len(reply) > 40 else "")
                status_var.set(f"✓ 连接成功（{used_url}）\n模型回复：{short}")
                status_label.configure(fg="#6EE7B7")
                self.log(f"[AI] 测试连接成功：{used_url}")

            run_bg(self._test_ai_connection, on_done)

        def save():
            apply_inputs()
            self._save_ai_config()
            state = "已启用" if self.ai_config["enabled"] else "已关闭（本地策略）"
            self.log(f"AI 答题设置已保存：{state}（请求方式：{self.ai_config['transport']}）")
            win.destroy()

        fetch_btn = tk.Button(model_row, text="拉取模型列表", command=fetch_models,
                              bg="#1E2636", fg="#F4F4F5", relief="flat", padx=10)
        fetch_btn.pack(side=tk.LEFT, padx=(8, 0))

        btn_row = tk.Frame(body, bg="#161D2B")
        btn_row.pack(pady=14)
        tk.Button(btn_row, text="测试连接", command=test_connection,
                  bg="#1E2636", fg="#F4F4F5", relief="flat",
                  font=("Microsoft YaHei UI", 10), padx=16, pady=3).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_row, text="保存配置", command=save,
                  bg="#6EE7B7", fg="#0A0D12", relief="flat",
                  font=("Microsoft YaHei UI", 10, "bold"), padx=18, pady=3).pack(side=tk.LEFT, padx=8)

        # 关于本软件（设置页底部信息区，文案取自 ABOUT_LINES，不影响上方设置操作）
        tk.Label(body, text="— 关于本软件 —", bg="#161D2B", fg="#A1A1AA",
                 font=("Microsoft YaHei UI", 9, "bold")).pack(pady=(18, 4))
        for line in ABOUT_LINES:
            tk.Label(body, text=line, bg="#161D2B", fg="#8B93A5",
                     justify="left", wraplength=620).pack(fill=tk.X, padx=20, pady=1)

    def pause_learning(self):
        """暂停/继续学习"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="继续")
            self.log("⏸ 已暂停")
            self.status_var.set("已暂停")
        else:
            self.pause_btn.configure(text="暂停")
            self.log("▶ 继续学习")
            self.status_var.set("学习中...")
    
    def stop_learning(self):
        """停止学习"""
        self.is_running = False
        self.is_paused = False
        self.log("⏹ 学习已停止")
        self._reset_buttons()
    
    def _reset_buttons(self):
        """重置按钮状态"""
        self.start_btn.configure(state=tk.NORMAL)
        self.pause_btn.configure(state=tk.DISABLED, text="暂停")
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("就绪")
    
    def run(self):
        """启动应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def _shutdown_browser_worker(self):
        """在拥有 Playwright 的线程中清理资源并结束工作线程。"""
        self._cleanup_browser_resources()
        self._browser_jobs.put(None)
        self._post_to_ui(self.root.destroy, allow_when_closing=True)

    def on_closing(self):
        """关闭窗口时清理资源"""
        if self._closing:
            return

        self._closing = True
        self._close_requested.set()
        self.is_running = False
        self.is_paused = False
        self._browser_ready.clear()

        # The worker may be waiting for login or learning.  Its loops observe
        # _close_requested, then this queued task closes Playwright on the
        # same thread that created it.
        if self._browser_thread and self._browser_thread.is_alive():
            self._browser_jobs.put(self._shutdown_browser_worker)
        else:
            self.root.destroy()


if __name__ == "__main__":
    app = XueXiTongLearner()
    app.run()
