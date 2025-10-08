import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import re
import os
from collections import defaultdict

class EnglishArticleTool:
    def __init__(self, root):
        self.root = root
        self.root.title("英文文章交互工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 预编译正则表达式，提升性能
        self.word_pattern = re.compile(r"\b[a-zA-Z]+\b")
        
        # 简单词汇集合，使用frozenset提升查找性能
        self.simple_words = frozenset({
            "a", "an", "the",
            "in", "on", "at", "by", "with", "for", "to", "of", "from", "about", "into", "onto",
            "i", "me", "my", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
            "it", "its", "we", "us", "our", "ours", "they", "them", "their", "theirs",
            "am", "is", "are", "was", "were", "be", "been", "being",
            "do", "does", "did", "have", "has", "had",
            "will", "would", "shall", "should", "can", "could", "may", "might", "must",
            "this", "that", "these", "those", "here", "there", "now", "then", "and", "or", "but", "so", "not", "no"
        })
        
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区（保留：打开文件、保存选中项、清除选中）
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="打开文件", command=self.open_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存选中项", command=self.save_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除选中", command=self.clear_selected).pack(side=tk.LEFT, padx=5)
        
        # 移除原有的PanedWindow（不再需要左右分割），直接创建文本框容器
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧文本框（保留，且占满整个剩余区域）
        self.text_widget = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            font=("Times New Roman", 18),
            padx=10, 
            pady=10
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 文本选中相关绑定（保留：开始选中、扩展选中、结束选中）
        self.text_widget.bind("<Button-1>", self.start_selection)
        self.text_widget.bind("<B1-Motion>", self.extend_selection)
        self.text_widget.bind("<ButtonRelease-1>", self.end_selection)
        
        # 保留必要的变量（删除右侧组件相关变量：如list_canvas、list_scrollbar等）
        self.current_file = None
        self.word_positions = []  # 单词位置缓存（用于选中定位）
        self.word_counts = defaultdict(int)  # 非简单词频缓存（用于计算出现次数）
        self.selected_items = []  # 选中项列表（用于保存）
        self.selected_items_set = set()  # 选中项去重集合
        self.highlight_tags = {}  # 高亮标签缓存（用于清除高亮）
        self.selection_in_progress = False  # 选中状态标记
        self.selection_start = None  # 选中起始位置
        self.line_lengths = []  # 行长度缓存（用于字符位置转文本索引）
        self.content = ""  # 文章内容缓存（避免重复从文本框读取）
        
        # 文本高亮标签配置（保留：临时选中高亮、最终选中高亮）
        self.text_widget.tag_config("highlight", background="#FFFACD")  # 最终选中：浅黄色
        self.text_widget.tag_config("temp_highlight", background="#E6E6FA")  # 临时选中：浅紫色
    
    def open_file(self):
        # 保留原功能：打开文本文件、清空文本框、预处理内容
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="选择英文文章"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.content = file.read()  # 缓存内容
                
                self.text_widget.delete(1.0, tk.END)
                self.clear_selected()  # 打开新文件时清除之前的选中状态
                
                self.text_widget.insert(tk.END, self.content)
                self.current_file = file_path
                
                self.preprocess_content()  # 预处理：提取单词位置、词频等
                
                self.root.title(f"英文文章交互工具 - {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")
    
    def preprocess_content(self):
        # 保留原功能：处理文章内容，缓存单词位置、词频、行长度（用于后续选中定位）
        self.word_positions = []
        self.word_counts.clear()
        self.line_lengths = []
        
        # 计算每行长度（用于字符位置转文本索引）
        lines = self.content.split('\n')
        for line in lines:
            self.line_lengths.append(len(line) + 1)  # +1 包含换行符
        
        # 提取所有单词，缓存位置和词频（仅非简单词）
        for match in self.word_pattern.finditer(self.content):
            word = match.group()
            start = match.start()
            end = match.end()
            self.word_positions.append((start, end, word))
            
            lower_word = word.lower()
            if lower_word not in self.simple_words:
                self.word_counts[lower_word] += 1
    
    def start_selection(self, event):
        # 保留原功能：标记选中开始，记录起始单词位置
        self.selection_in_progress = True
        self.selection_start = self.get_word_at_position(event)
    
    def extend_selection(self, event):
        # 保留原功能：扩展选中范围，显示临时高亮
        if not self.selection_in_progress or self.selection_start is None:
            return
        
        current_word = self.get_word_at_position(event)
        if current_word:
            # 移除之前的临时高亮
            self.text_widget.tag_remove("temp_highlight", 1.0, tk.END)
            
            # 计算临时选中的文本索引，添加新高亮
            start_idx = self.get_text_index(self.selection_start[0])
            end_idx = self.get_text_index(current_word[1])
            self.text_widget.tag_add("temp_highlight", start_idx, end_idx)
    
    def end_selection(self, event):
        # 核心修改：删除“添加到右侧列表”的逻辑，保留“过滤简单词、添加高亮、记录选中项”
        if not self.selection_in_progress or self.selection_start is None:
            return
        
        self.selection_in_progress = False
        self.text_widget.tag_remove("temp_highlight", 1.0, tk.END)  # 清除临时高亮
        
        current_word = self.get_word_at_position(event)
        if current_word:
            # 计算最终选中的文本范围（起始到结束位置）
            start_pos = min(self.selection_start[0], current_word[0])
            end_pos = max(self.selection_start[1], current_word[1])
            
            # 转换为文本框的索引（行.列），获取选中文本
            start_idx = self.get_text_index(start_pos)
            end_idx = self.get_text_index(end_pos)
            selected_text = self.text_widget.get(start_idx, end_idx).strip()
            
            # 过滤：空文本或已选中过的内容，不处理
            if not selected_text or selected_text in self.selected_items_set:
                return
            
            # 过滤简单词：仅保留包含非简单词的选中项
            selected_words = self.word_pattern.findall(selected_text.lower())
            if (len(selected_words) == 1 and selected_words[0] in self.simple_words) or \
               (all(word in self.simple_words for word in selected_words)):
                messagebox.showinfo("提示", f"“{selected_text}”是简单词汇，已自动排除")
                return
            
            # 记录选中项（用于后续保存）
            self.selected_items.append(selected_text)
            self.selected_items_set.add(selected_text)
            
            # 为选中内容添加永久高亮（保留原逻辑）
            self.highlight_selected_text(selected_text)
    
    def get_word_at_position(self, event):
        # 保留原功能：根据鼠标点击位置，找到对应的单词（二分查找优化）
        index = self.text_widget.index(f"@{event.x},{event.y}")
        line, column = map(int, index.split('.'))
        
        # 计算点击位置对应的全局字符索引
        char_pos = sum(self.line_lengths[:line-1]) + column
        
        # 二分查找单词位置列表，定位点击的单词
        left, right = 0, len(self.word_positions) - 1
        while left <= right:
            mid = (left + right) // 2
            start, end, word = self.word_positions[mid]
            
            if start <= char_pos < end:
                return (start, end, word)
            elif char_pos < start:
                right = mid - 1
            else:
                left = mid + 1
        
        return None
    
    def get_text_index(self, char_pos):
        # 保留原功能：将全局字符索引转换为文本框的“行.列”索引
        left, right = 0, len(self.line_lengths) - 1
        while left <= right:
            mid = (left + right) // 2
            line_total = sum(self.line_lengths[:mid+1])
            
            if line_total > char_pos:
                right = mid - 1
            else:
                left = mid + 1
        
        line = left + 1
        prev_total = sum(self.line_lengths[:left]) if left > 0 else 0
        column = char_pos - prev_total
        
        return f"{line}.{column}"
    
    def calculate_occurrences(self, text):
        # 保留原功能：计算选中文本在文章中的出现次数（用于保存时的逻辑，虽不显示但保留完整性）
        if self.word_pattern.fullmatch(text):
            # 单个单词：直接用预缓存的词频
            lower_text = text.lower()
            return self.word_counts.get(lower_text, 0)
        
        # 短语：遍历文章查找完整匹配
        count = 0
        start = 0
        text_len = len(text)
        content = self.content
        
        while True:
            pos = content.find(text, start)
            if pos == -1:
                break
            
            # 检查是否为完整匹配（前后非字母数字）
            prev_char = content[pos-1] if pos > 0 else ' '
            next_char = content[pos+text_len] if pos+text_len < len(content) else ' '
            
            if (not prev_char.isalnum() or pos == 0) and (not next_char.isalnum() or pos+text_len == len(content)):
                # 过滤仅包含简单词的短语
                match_words = self.word_pattern.findall(content[pos:pos+text_len].lower())
                if not all(word in self.simple_words for word in match_words):
                    count += 1
            
            start = pos + 1
        
        return count
    
    def highlight_selected_text(self, text):
        # 保留原功能：为选中内容添加永久高亮（浅黄色）
        tag = f"highlight_{len(self.highlight_tags)}"
        self.highlight_tags[text] = tag
        self.text_widget.tag_config(tag, background="#FFFACD")
        
        content = self.content
        start = 0
        text_len = len(text)
        
        while True:
            pos = content.find(text, start)
            if pos == -1:
                break
            
            # 检查完整匹配，避免部分匹配（如“cat”匹配“category”）
            prev_char = content[pos-1] if pos > 0 else ' '
            next_char = content[pos+text_len] if pos+text_len < len(content) else ' '
            
            if (not prev_char.isalnum() or pos == 0) and (not next_char.isalnum() or pos+text_len == len(content)):
                # 仅高亮包含非简单词的内容
                match_words = self.word_pattern.findall(content[pos:pos+text_len].lower())
                if not all(word in self.simple_words for word in match_words):
                    start_idx = self.get_text_index(pos)
                    end_idx = self.get_text_index(pos + text_len)
                    self.text_widget.tag_add(tag, start_idx, end_idx)
            
            start = pos + 1
    
    def save_selected(self):
        # 保留原功能：将选中项保存到文本文件
        if not self.selected_items:
            messagebox.showinfo("提示", "没有选中任何内容")
            return
        
        # 生成默认文件名（基于当前打开的文件）
        default_filename = "selected_words.txt"
        if self.current_file:
            base_name = os.path.splitext(os.path.basename(self.current_file))[0]
            default_filename = f"{base_name}_selected.txt"
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=default_filename,
            title="保存选中项"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(self.selected_items))  # 批量写入，更高效
                
                messagebox.showinfo("成功", f"已保存 {len(self.selected_items)} 项到文件\n{file_path}")
            
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def clear_selected(self):
        # 保留原功能：清除所有选中项的高亮和记录
        # 移除所有永久高亮标签
        for tag in self.highlight_tags.values():
            self.text_widget.tag_remove(tag, 1.0, tk.END)
        
        # 重置选中项相关变量
        self.selected_items = []
        self.selected_items_set = set()
        self.highlight_tags = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishArticleTool(root)
    root.mainloop()