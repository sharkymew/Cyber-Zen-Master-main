import os
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

from analyze_agent import AnalyzeAgent
from debator_agent import DebatorAgent
from express_agent import ExpressAgent

def sanitize_folder_name(text):
    sanitized = text.replace('/', 'vs')
    sanitized = re.sub(r'[\\/*?:"<>|]', '', sanitized)
    sanitized = '_'.join(sanitized.split())
    return sanitized

def setup_output_dirs(base_dir):
    stages = ['stage1', 'stage2', 'stage3']
    dirs = {}
    for stage in stages:
        stage_dir = os.path.join(base_dir, stage)
        os.makedirs(stage_dir, exist_ok=True)
        dirs[stage] = stage_dir
    return dirs

def run_answer_anything_system(full_topic):
    base_output_dir = os.path.join('output', sanitize_folder_name(full_topic))
    output_dirs = setup_output_dirs(base_output_dir)
    
    # 第一阶段：分析
    print(f"\nStage 1: 分析阶段 ({full_topic})")
    analyzer = AnalyzeAgent()
    analyzer.OUTPUT_DIR = output_dirs['stage1']
    
    print("联想分析:")
    analyzer.opposite_opinion_association(full_topic)
    print("\n批判性分析:")
    analyzer.analyze_critique()
    print("\n现实意义分析:")
    analyzer.analyze_significance(full_topic)
    
    # 第二阶段：辩论
    print(f"\nStage 2: 立论阶段 ({full_topic})")
    debater = DebatorAgent()
    debater.STAGE1_DIR = output_dirs['stage1']
    debater.OUTPUT_DIR = output_dirs['stage2']
    
    print("开始生成观点")
    debater.generate_argument(full_topic)
    
    # 第三阶段：表达
    print(f"\nStage 3: 表达阶段 ({full_topic})")
    expresser = ExpressAgent()
    expresser.STAGE1_DIR = output_dirs['stage1']
    expresser.STAGE2_DIR = output_dirs['stage2']
    expresser.OUTPUT_DIR = output_dirs['stage3']
    
    print("开始生成金句")
    expresser.build_golden_sentence(full_topic)
    print("\n开始生成自我表达")
    expresser.build_self_expression(full_topic)
    
    # 读取最终回答并返回
    response_file = os.path.join(output_dirs['stage3'], "self_expression.txt")
    if os.path.exists(response_file):
        with open(response_file, "r", encoding="utf-8") as f:
            response = f.read().strip()
    else:
        response = "无回答"
    final_answer_path = os.path.join(base_output_dir, "final_answer.txt")
    with open(final_answer_path, "w", encoding="utf-8") as f:
        f.write(response)
    
    return full_topic, response
def run_answer_anything_system_gui(full_topic, append_log, on_stream):
    base_output_dir = os.path.join("output", sanitize_folder_name(full_topic))
    output_dirs = setup_output_dirs(base_output_dir)
    append_log(f"\nStage 1: 分析阶段 ({full_topic})\n")
    analyzer = AnalyzeAgent()
    analyzer.OUTPUT_DIR = output_dirs["stage1"]
    analyzer.opposite_opinion_association(full_topic, stream=True, on_chunk=on_stream, print_stream=False)
    append_log("\n")
    analyzer.analyze_critique(stream=True, on_chunk=on_stream, print_stream=False)
    append_log("\n")
    analyzer.analyze_significance(full_topic, stream=True, on_chunk=on_stream, print_stream=False)
    append_log(f"\n\nStage 2: 立论阶段 ({full_topic})\n")
    debater = DebatorAgent()
    debater.STAGE1_DIR = output_dirs["stage1"]
    debater.OUTPUT_DIR = output_dirs["stage2"]
    debater.generate_argument(full_topic, stream=True, on_chunk=on_stream, print_stream=False)
    append_log(f"\n\nStage 3: 表达阶段 ({full_topic})\n")
    expresser = ExpressAgent()
    expresser.STAGE1_DIR = output_dirs["stage1"]
    expresser.STAGE2_DIR = output_dirs["stage2"]
    expresser.OUTPUT_DIR = output_dirs["stage3"]
    expresser.build_golden_sentence(full_topic, stream=True, on_chunk=on_stream, print_stream=False)
    append_log("\n开始生成自我表达(流式)\n")
    expresser.build_self_expression(full_topic, stream=True, on_chunk=on_stream, print_stream=False)
    response_file = os.path.join(output_dirs["stage3"], "self_expression.txt")
    if os.path.exists(response_file):
        with open(response_file, "r", encoding="utf-8") as f:
            response = f.read().strip()
    else:
        response = "无回答"
    final_answer_path = os.path.join(base_output_dir, "final_answer.txt")
    with open(final_answer_path, "w", encoding="utf-8") as f:
        f.write(response)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_path = os.path.join(base_output_dir, f"final_answer_{ts}.txt")
    with open(history_path, "w", encoding="utf-8") as f:
        f.write(response)
    return response

def start_gui():
    root = tk.Tk()
    root.title("赛博禅师")
    root.geometry("800x600")
    input_frame = tk.Frame(root)
    input_frame.pack(fill=tk.X, padx=10, pady=10)
    tk.Label(input_frame, text="请输入问题（每行一个）:").pack(anchor="w")
    questions_text = scrolledtext.ScrolledText(input_frame, height=5)
    questions_text.pack(fill=tk.X)
    output_frame = tk.Frame(root)
    output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    tk.Label(output_frame, text="输出:").pack(anchor="w")
    output_text = scrolledtext.ScrolledText(output_frame)
    output_text.pack(fill=tk.BOTH, expand=True)
    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    start_button = tk.Button(button_frame, text="开始生成")
    start_button.pack(side=tk.LEFT)
    def append_log(text):
        def inner():
            output_text.insert(tk.END, text)
            output_text.see(tk.END)
        root.after(0, inner)
    def append_stream(text):
        def inner():
            output_text.insert(tk.END, text)
            output_text.see(tk.END)
        root.after(0, inner)
    def run_questions():
        lines = questions_text.get("1.0", tk.END).splitlines()
        topics = [line.strip() for line in lines if line.strip()]
        if not topics:
            append_log("未输入问题\n")
            root.after(0, lambda: start_button.config(state=tk.NORMAL))
            return
        os.makedirs("output", exist_ok=True)
        for topic in topics:
            append_log(f"\n==============================\n问题: {topic}\n")
            answer = run_answer_anything_system_gui(topic, append_log, append_stream)
            append_log("\n\n最终答案:\n")
            append_log(answer + "\n")
        root.after(0, lambda: start_button.config(state=tk.NORMAL))
    def on_start():
        output_text.delete("1.0", tk.END)
        start_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=run_questions, daemon=True)
        thread.start()
    start_button.config(command=on_start)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
