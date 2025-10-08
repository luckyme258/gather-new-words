import os
import re

def split_book(input_file, words_per_part=3000):
    """
    将英文书籍分割成指定词汇量的多个文件，序号在前
    
    参数:
        input_file: 输入的英文书籍txt文件路径
        words_per_part: 每个分割文件的目标词汇量，默认7000
    """
    # 读取书籍内容
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取文件名（不含扩展名）用于生成分割文件
    base_name = os.path.splitext(input_file)[0]
    
    # 按段落分割内容（以空行作为段落分隔符）
    paragraphs = re.split(r'\n\s*\n', content.strip())
    total_paragraphs = len(paragraphs)
    print(f"检测到 {total_paragraphs} 个段落，开始处理...")
    
    current_part = []
    current_word_count = 0
    part_number = 1
    processed_paragraphs = 0
    
    for para in paragraphs:
        # 计算当前段落的单词数（按空格分割）
        para_word_count = len(para.split())
        
        # 如果添加当前段落会超过目标词汇量
        if current_word_count + para_word_count > words_per_part:
            # 保存当前部分，序号在前
            output_file = f"part_{part_number}_{base_name}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(current_part))
            
            print(f"已创建: {output_file}, 词汇量: {current_word_count}")
            
            # 开始新的部分
            current_part = [para]
            current_word_count = para_word_count
            part_number += 1
        
        else:
            # 添加到当前部分
            current_part.append(para)
            current_word_count += para_word_count
        
        # 更新进度
        processed_paragraphs += 1
        progress = (processed_paragraphs / total_paragraphs) * 100
        # 每处理10%的段落显示一次进度
        if progress % 10 < (1 / total_paragraphs * 100) or processed_paragraphs == total_paragraphs:
            print(f"处理进度: {progress:.1f}% ({processed_paragraphs}/{total_paragraphs} 段落)")
    
    # 处理最后一部分
    if current_part:
        output_file = f"part_{part_number}_{base_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(current_part))
        print(f"已创建: {output_file}, 词汇量: {current_word_count}")
    
    print(f"分割完成，共生成 {part_number} 个文件")

if __name__ == "__main__":
    # 获取当前目录下的txt文件
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt') and os.path.isfile(f)]
    
    if len(txt_files) == 0:
        print("当前目录下没有找到txt文件")
    else:
        # 取第一个txt文件（假设只有一个）
        book_file = txt_files[0]
        print(f"找到书籍文件: {book_file}")
        split_book(book_file)
    