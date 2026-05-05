#!/usr/bin/env python3
"""
24点计算器 - 24-Point Card Game Calculator
===========================================
一个带GUI界面的24点计算程序。
功能：
  1. 用户输入4个1-13之间的整数
  2. 程序遍历所有可能的四则运算组合，找出结果为24且过程中不出现小数的表达式
  3. 支持提交、重置操作

算法说明：
  对于4个数字，共有 4! = 24 种排列方式、
  4³ = 64 种运算符组合（+, -, *, /）、
  5 种括号结构（即4个数字的5种不同二叉树形态），
  总搜索空间为 24 × 64 × 5 = 7680 种可能性。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import itertools
from typing import List, Tuple, Optional


# ============================================================
# 数学运算函数
# 使用严格整数运算，除法仅当能整除时才返回结果，
# 从而确保整个计算过程中不会出现小数。
# ============================================================

def op_add(a: int, b: int) -> Optional[int]:
    """整数加法"""
    return a + b


def op_sub(a: int, b: int) -> Optional[int]:
    """整数减法"""
    return a - b


def op_mul(a: int, b: int) -> Optional[int]:
    """整数乘法"""
    return a * b


def op_div(a: int, b: int) -> Optional[int]:
    """
    整数除法 -- 仅当满足以下条件时才返回结果:
      1. 除数不为零
      2. 能够整除（即商为整数，不会产生小数）
    若任一条件不满足，返回 None 表示此运算路径无效。
    """
    if b == 0:
        return None
    if a % b != 0:
        return None
    return a // b


# 运算符字符 → 运算函数的映射
OPERATOR_MAP = {
    '+': op_add,
    '-': op_sub,
    '*': op_mul,
    '/': op_div,
}

# 所有可用的运算符列表
ALL_OPERATORS = list(OPERATOR_MAP.keys())


# ============================================================
# 括号结构计算函数
# 4个数字 a, b, c, d 可构成5种不同的二叉树结构（即5种加括号方式）。
# 每个函数接收数字排列和运算符组合，返回 (计算结果, 表达式字符串)。
# 若中间某步出现小数，则返回 (None, "") 并提前终止。
# ============================================================

def eval_pattern_1(nums: Tuple[int, ...], ops: Tuple[str, ...]) -> Tuple[Optional[int], str]:
    """
    括号结构1: ((a ○₁ b) ○₂ c) ○₃ d
    先计算前两个数，再与第三个数运算，最后与第四个数运算。
    示例: ((1 + 2) × 3) - 4
    """
    a, b, c, d = nums
    op1, op2, op3 = ops

    # 第一步: a ○₁ b
    v1 = OPERATOR_MAP[op1](a, b)
    if v1 is None:
        return None, ""
    inner1 = f"({a} {op1} {b})"

    # 第二步: (a ○₁ b) ○₂ c
    v2 = OPERATOR_MAP[op2](v1, c)
    if v2 is None:
        return None, ""
    inner2 = f"({inner1} {op2} {c})"

    # 第三步: ((a ○₁ b) ○₂ c) ○₃ d
    v3 = OPERATOR_MAP[op3](v2, d)
    if v3 is None:
        return None, ""
    expr = f"{inner2} {op3} {d}"

    return v3, expr


def eval_pattern_2(nums: Tuple[int, ...], ops: Tuple[str, ...]) -> Tuple[Optional[int], str]:
    """
    括号结构2: (a ○₁ (b ○₂ c)) ○₃ d
    先计算中间两个数，再与第一个数运算，最后与第四个数运算。
    示例: (1 + (2 × 3)) + 4
    """
    a, b, c, d = nums
    op1, op2, op3 = ops

    # 第一步: b ○₂ c
    v1 = OPERATOR_MAP[op2](b, c)
    if v1 is None:
        return None, ""
    inner1 = f"({b} {op2} {c})"

    # 第二步: a ○₁ (b ○₂ c)
    v2 = OPERATOR_MAP[op1](a, v1)
    if v2 is None:
        return None, ""

    # 第三步: (a ○₁ (b ○₂ c)) ○₃ d
    v3 = OPERATOR_MAP[op3](v2, d)
    if v3 is None:
        return None, ""
    expr = f"({a} {op1} {inner1}) {op3} {d}"

    return v3, expr


def eval_pattern_3(nums: Tuple[int, ...], ops: Tuple[str, ...]) -> Tuple[Optional[int], str]:
    """
    括号结构3: a ○₁ ((b ○₂ c) ○₃ d)
    先计算中间两个数，再与第四个数运算，最后与第一个数运算。
    示例: 1 + ((2 × 3) - 4)
    """
    a, b, c, d = nums
    op1, op2, op3 = ops

    # 第一步: b ○₂ c
    v1 = OPERATOR_MAP[op2](b, c)
    if v1 is None:
        return None, ""
    inner1 = f"({b} {op2} {c})"

    # 第二步: (b ○₂ c) ○₃ d
    v2 = OPERATOR_MAP[op3](v1, d)
    if v2 is None:
        return None, ""

    # 第三步: a ○₁ ((b ○₂ c) ○₃ d)
    v3 = OPERATOR_MAP[op1](a, v2)
    if v3 is None:
        return None, ""
    expr = f"{a} {op1} ({inner1} {op3} {d})"

    return v3, expr


def eval_pattern_4(nums: Tuple[int, ...], ops: Tuple[str, ...]) -> Tuple[Optional[int], str]:
    """
    括号结构4: a ○₁ (b ○₂ (c ○₃ d))
    先计算最后两个数，再与第二个数运算，最后与第一个数运算。
    示例: 1 + (2 × (3 + 4))
    """
    a, b, c, d = nums
    op1, op2, op3 = ops

    # 第一步: c ○₃ d
    v1 = OPERATOR_MAP[op3](c, d)
    if v1 is None:
        return None, ""
    inner1 = f"({c} {op3} {d})"

    # 第二步: b ○₂ (c ○₃ d)
    v2 = OPERATOR_MAP[op2](b, v1)
    if v2 is None:
        return None, ""

    # 第三步: a ○₁ (b ○₂ (c ○₃ d))
    v3 = OPERATOR_MAP[op1](a, v2)
    if v3 is None:
        return None, ""
    expr = f"{a} {op1} ({b} {op2} {inner1})"

    return v3, expr


def eval_pattern_5(nums: Tuple[int, ...], ops: Tuple[str, ...]) -> Tuple[Optional[int], str]:
    """
    括号结构5: (a ○₁ b) ○₂ (c ○₃ d)
    先分别计算前两个数和后两个数，然后将两个中间结果做运算。
    示例: (1 + 2) × (3 + 4)
    """
    a, b, c, d = nums
    op1, op2, op3 = ops

    # 第一步(左): a ○₁ b
    v1 = OPERATOR_MAP[op1](a, b)
    if v1 is None:
        return None, ""
    left = f"({a} {op1} {b})"

    # 第一步(右): c ○₃ d
    v2 = OPERATOR_MAP[op3](c, d)
    if v2 is None:
        return None, ""
    right = f"({c} {op3} {d})"

    # 第二步: (a ○₁ b) ○₂ (c ○₃ d)
    v3 = OPERATOR_MAP[op2](v1, v2)
    if v3 is None:
        return None, ""
    expr = f"{left} {op2} {right}"

    return v3, expr


# 将所有括号结构函数汇入列表，方便遍历
ALL_PATTERNS = [
    eval_pattern_1,
    eval_pattern_2,
    eval_pattern_3,
    eval_pattern_4,
    eval_pattern_5,
]


# ============================================================
# 24点求解核心函数
# ============================================================

def solve_24(numbers: List[int]) -> List[str]:
    """
    求解24点问题的核心算法。

    遍历所有:
      - 数字排列（对4个数字去重排列，处理用户输入重复数字的情况）
      - 运算符组合（3个位置，每个位置4种选择 = 64种）
      - 括号结构（5种二叉树形态）

    合计最多 24 × 64 × 5 = 7680 次尝试，对现代计算机来说瞬间完成。

    参数:
        numbers: 包含4个 [1, 13] 范围内整数的列表

    返回:
        去重后排序的表达式字符串列表，每个表达式计算结果为24
    """
    result_set = set()  # 使用集合自动去除重复表达式

    # 对输入数字生成所有唯一排列（处理重复数字的情况）
    unique_permutations = set(itertools.permutations(numbers))

    # 三层嵌套遍历: 数字排列 × 运算符组合 × 括号结构
    for num_perm in unique_permutations:
        for op_combo in itertools.product(ALL_OPERATORS, repeat=3):
            for pattern_func in ALL_PATTERNS:
                value, expression = pattern_func(num_perm, op_combo)
                if value == 24:
                    result_set.add(expression)

    # 返回排序后的结果列表
    return sorted(result_set)


# ============================================================
# GUI 界面类
# ============================================================

class TwentyFourGameApp:
    """
    24点计算器主窗口应用程序。

    界面布局（从上到下）:
      1. 标题栏 - 程序名称
      2. 说明文字 - 使用提示
      3. 输入框区域 - 4个数字输入框
      4. 按钮区域 - 计算、重置按钮
      5. 结果展示区域 - 带滚动条的文本显示区
    """

    # 输入框统一尺寸
    ENTRY_WIDTH = 5          # 5个字符宽，容纳两位数绰绰有余，4个框完全一致

    # 颜色定义
    COLOR_INPUT_FG = '#D4380D'      # 输入字体颜色：深红
    COLOR_INPUT_BG = '#FFF2F0'      # 输入框背景色：浅红
    COLOR_INPUT_BORDER = '#FFA39E'  # 输入框边框色：淡红
    COLOR_OUTPUT_FG = '#0958D9'     # 输出字体颜色：深蓝
    COLOR_OUTPUT_BG = '#F0F5FF'     # 输出区背景色：浅蓝

    # 窗口默认尺寸
    WINDOW_WIDTH = 620
    WINDOW_HEIGHT = 680

    def __init__(self, root: tk.Tk):
        """
        初始化应用程序窗口。

        参数:
            root: tkinter 根窗口对象
        """
        self.root = root
        self.root.title("24点计算器")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(True, True)

        # 设置窗口最小尺寸，防止界面被缩得过小
        self.root.minsize(520, 580)

        # 配置主题样式
        self._setup_styles()

        # 构建界面组件
        self._build_ui()

    def _setup_styles(self):
        """配置 ttk 组件的自定义样式"""
        style = ttk.Style()
        # 尝试使用 'clam' 主题，在不同平台上提供一致的外观
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')

        # 自定义按钮样式
        style.configure('Submit.TButton', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Reset.TButton', font=('Microsoft YaHei', 12))

        # 自定义标签框样式
        style.configure('Card.TLabelframe', relief=tk.RIDGE, borderwidth=2)
        style.configure('Card.TLabelframe.Label', font=('Microsoft YaHei', 11, 'bold'))

    def _build_ui(self):
        """构建完整的用户界面布局"""
        # ---- 顶层主框架，提供页面边距 ----
        main_frame = ttk.Frame(self.root, padding="25 20 25 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- 1. 标题 ----
        self._create_title(main_frame)

        # ---- 2. 使用说明 ----
        self._create_description(main_frame)

        # ---- 3. 数字输入区域 ----
        self._create_input_area(main_frame)

        # ---- 4. 按钮区域 ----
        self._create_button_area(main_frame)

        # ---- 5. 结果展示区域 ----
        self._create_result_area(main_frame)

        # ---- 绑定键盘事件：回车键等同于点击"计算" ----
        self.root.bind('<Return>', lambda _event: self._handle_submit())

        # ---- 将焦点设置到第一个输入框 ----
        self.entries[0].focus_set()

    def _create_title(self, parent: ttk.Frame):
        """创建标题标签"""
        title = ttk.Label(
            parent,
            text="🃏 24点计算器",
            font=('Microsoft YaHei', 22, 'bold')
        )
        title.pack(pady=(0, 8))

    def _create_description(self, parent: ttk.Frame):
        """创建说明文字"""
        desc = ttk.Label(
            parent,
            text="请输入4个 1~13 之间的整数，点击「计算」查看所有能得到24的四则运算表达式。\n"
                 "计算过程中不出现小数，确保每一步都是整数运算。",
            font=('Microsoft YaHei', 10),
            justify=tk.CENTER
        )
        desc.pack(pady=(0, 20))

    def _create_input_area(self, parent: ttk.Frame):
        """创建数字输入区域，包含4个输入框"""
        card_frame = ttk.LabelFrame(
            parent,
            text="输入数字",
            padding="20 15",
            style='Card.TLabelframe'
        )
        card_frame.pack(fill=tk.X, pady=(0, 15))

        # 输入框居中容器
        entries_container = ttk.Frame(card_frame)
        entries_container.pack()

        self.entries: List[tk.Entry] = []

        for i in range(4):
            # 使用 tk.Entry 以便精确控制前景色/背景色和边框样式
            entry = tk.Entry(
                entries_container,
                width=self.ENTRY_WIDTH,
                font=('Arial Rounded MT Bold', 30),
                justify='center',
                relief=tk.SOLID,
                borderwidth=2,
                fg=self.COLOR_INPUT_FG,                   # 输入字体颜色：红色
                bg=self.COLOR_INPUT_BG,                   # 输入框背景：浅红色
                insertbackground=self.COLOR_INPUT_FG,     # 光标颜色：与字体同色
                highlightthickness=1,
                highlightcolor=self.COLOR_INPUT_BORDER,
                highlightbackground='#D9D9D9',
            )
            # 统一使用 place 风格的固定高度来保证大小一致
            entry.pack(side=tk.LEFT, padx=12, ipady=6)

            # 绑定输入验证（仅允许数字字符）
            entry.bind('<KeyRelease>', self._validate_input)

            self.entries.append(entry)

        # 输入框之间的分隔标记（+ 号装饰）
        # 在第1、2个和第2、3个以及第3、4个输入框之间... 不，使用简单的标签提示

    def _create_button_area(self, parent: ttk.Frame):
        """创建按钮区域"""
        btn_container = ttk.Frame(parent)
        btn_container.pack(pady=(5, 18))

        # 计算按钮
        self.btn_submit = ttk.Button(
            btn_container,
            text="  计  算  ",
            command=self._handle_submit,
            style='Submit.TButton'
        )
        self.btn_submit.pack(side=tk.LEFT, padx=15)

        # 重置按钮
        self.btn_reset = ttk.Button(
            btn_container,
            text="  重  置  ",
            command=self._handle_reset,
            style='Reset.TButton'
        )
        self.btn_reset.pack(side=tk.LEFT, padx=15)

    def _create_result_area(self, parent: ttk.Frame):
        """创建结果展示区域"""
        result_frame = ttk.LabelFrame(
            parent,
            text="计算结果",
            padding="10 8",
            style='Card.TLabelframe'
        )
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 带滚动条的文本显示区域
        self.result_text = tk.Text(
            result_frame,
            font=('Consolas', 12),
            wrap=tk.WORD,
            relief=tk.SUNKEN,
            borderwidth=1,
            bg=self.COLOR_OUTPUT_BG,         # 输出区背景：浅蓝色
            fg=self.COLOR_OUTPUT_FG,          # 输出字体颜色：蓝色
            state=tk.DISABLED,                 # 初始为只读状态
            padx=10,
            pady=8,
        )

        # 垂直滚动条
        scrollbar = ttk.Scrollbar(
            result_frame,
            orient=tk.VERTICAL,
            command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=scrollbar.set)

        # 布局：文本区域（左）+ 滚动条（右）
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置文本标签样式
        self.result_text.tag_configure(
            'header',
            font=('Microsoft YaHei', 12, 'bold'),
            foreground='#003EB3'              # 深蓝标题
        )
        self.result_text.tag_configure(
            'no_solution',
            font=('Microsoft YaHei', 14, 'bold'),
            foreground='#CF1322'              # 无解提示：红色突出显示
        )
        self.result_text.tag_configure(
            'count',
            font=('Microsoft YaHei', 11, 'bold'),
            foreground='#135200'              # 解法数量：绿色
        )
        self.result_text.tag_configure(
            'separator',
            foreground='#ADC6FF'              # 分隔线：浅蓝
        )

    # ---- 输入验证 ----

    def _validate_input(self, event: tk.Event):
        """
        实时验证用户输入 -- 仅允许数字字符。
        当检测到非法字符时自动删除。
        """
        widget: tk.Entry = event.widget
        current_text = widget.get()
        # 过滤掉非数字字符
        filtered = ''.join(ch for ch in current_text if ch.isdigit())
        if filtered != current_text:
            # 保存光标位置
            cursor_pos = widget.index(tk.INSERT)
            widget.delete(0, tk.END)
            widget.insert(0, filtered)
            # 尽量恢复光标位置
            new_cursor = min(cursor_pos, len(filtered))
            widget.icursor(new_cursor)

    # ---- 事件处理 ----

    def _handle_submit(self):
        """
        处理「计算」按钮点击事件。

        执行流程:
          1. 读取并校验4个输入框的值
          2. 调用 solve_24() 进行求解
          3. 将结果格式化输出到结果区域
        """
        # 第一步: 收集并校验输入
        numbers = self._collect_and_validate_inputs()
        if numbers is None:
            return  # 校验失败，_collect_and_validate_inputs 内部已弹出错误提示

        # 第二步: 执行计算
        expressions = solve_24(numbers)

        # 第三步: 展示结果
        self._show_results(numbers, expressions)

    def _collect_and_validate_inputs(self) -> Optional[List[int]]:
        """
        从输入框收集数字并进行校验。

        校验规则:
          - 不能为空
          - 必须是整数
          - 必须在 1~13 范围内

        返回:
            校验通过时返回包含4个整数的列表，否则返回 None
        """
        numbers = []

        for idx, entry in enumerate(self.entries):
            raw_value = entry.get().strip()

            # 检查是否为空
            if not raw_value:
                messagebox.showwarning(
                    title="输入不完整",
                    message=f"第 {idx + 1} 个数字尚未填写，请输入一个 1~13 之间的整数。"
                )
                entry.focus_set()
                return None

            # 检查是否为有效整数
            try:
                num = int(raw_value)
            except ValueError:
                messagebox.showwarning(
                    title="格式错误",
                    message=f"「{raw_value}」不是有效的整数，请重新输入第 {idx + 1} 个数字。"
                )
                # 选中错误内容方便用户直接修改
                entry.select_range(0, tk.END)
                entry.focus_set()
                return None

            # 检查数值范围
            if num < 1 or num > 13:
                messagebox.showwarning(
                    title="范围错误",
                    message=f"数字「{num}」不在 1~13 的范围内，请重新输入第 {idx + 1} 个数字。"
                )
                entry.select_range(0, tk.END)
                entry.focus_set()
                return None

            numbers.append(num)

        return numbers

    def _show_results(self, numbers: List[int], expressions: List[str]):
        """
        将计算结果格式化输出到结果展示区域。

        参数:
            numbers: 用户输入的4个数字
            expressions: 求解得到的所有表达式列表
        """
        # 启用文本区域的编辑功能
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)  # 清空旧内容

        # 第一部分: 输入回显
        self.result_text.insert(tk.END, "📥 输入数字: ", 'header')
        self.result_text.insert(tk.END, f"{', '.join(map(str, numbers))}\n")
        self.result_text.insert(tk.END, "─" * 55 + "\n\n", 'separator')

        # 第二部分: 计算结果
        if not expressions:
            # 无解的情况
            self.result_text.insert(
                tk.END,
                "❌ 这4个数字无法得到24。\n\n"
                "   请尝试更换其他数字组合。\n",
                'no_solution'
            )
        else:
            # 有解的情况
            self.result_text.insert(
                tk.END,
                f"✅ 共找到 {len(expressions)} 种解法:\n\n",
                'count'
            )
            for i, expr in enumerate(expressions, 1):
                # 序号 + 表达式 + 结果
                line = f"  {i:3d}.  {expr} = 24\n"
                self.result_text.insert(tk.END, line)

        # 恢复只读状态
        self.result_text.configure(state=tk.DISABLED)

        # 滚动到顶部
        self.result_text.see(1.0)

    def _handle_reset(self):
        """
        处理「重置」按钮点击事件。

        清空所有输入框内容、清除计算结果，
        并将输入焦点移回第一个输入框。
        """
        # 清空4个输入框
        for entry in self.entries:
            entry.delete(0, tk.END)

        # 清空结果展示区域
        self.result_text.configure(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.configure(state=tk.DISABLED)

        # 焦点回到第一个输入框
        self.entries[0].focus_set()


# ============================================================
# 程序入口
# ============================================================

def main():
    """启动24点计算器应用程序"""
    root = tk.Tk()
    TwentyFourGameApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
