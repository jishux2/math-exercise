# Math Exercise Generator

一个基于Python的数学练习题生成器，支持加减乘除四则运算，提供灵活的题目生成策略和评分机制。

## 功能特点

- 支持加减乘除四则运算题目生成
- 灵活的难度设置和数字范围控制
- 多种评分策略（计时得分、准确率得分等）
- 观察者模式实现练习状态通知
- 工厂模式实现题目生成
- 策略模式实现灵活的评分机制
- 可选的AI点评功能（需要额外安装poe_api_wrapper包）

## 安装

1. 克隆仓库
   ```bash
   git clone https://github.com/jishux2/math-exercise.git
   cd math-exercise
   ```
   
2. 创建虚拟环境
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```
   
3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. （可选）安装AI点评相关依赖
   ```bash
   python install_poe.py
   ```
   
   > 注意：AI点评功能需要代理支持
   > - 默认配置支持v2rayN（端口10809）
   > - 如果使用clash，需要手动修改`poe_api_wrapper`依赖中的以下文件中的端口设置：
   >   - `poe_api_wrapper/__init__.py`
   >   - `poe_api_wrapper/proxies.py`

## 项目结构

```
math_exercise/
│
├── src/                    # 源代码目录
│   ├── models/            # 数据模型
│   ├── factories/         # 工厂模式实现
│   ├── strategies/        # 策略模式实现
│   ├── observers/         # 观察者模式实现
│   ├── core/             # 核心功能实现
│   └── ui/               # 用户界面实现
│
├── examples/              # 示例代码
│   ├── main.py           # 命令行版本
│   └── main_gui.py       # 图形界面版本
│
├── screenshots/           # 界面截图
├── requirements.txt       # 项目依赖
└── README.md             # 项目说明
```

## 运行方式

### 图形界面版本
```bash
python -m examples.main_gui
```

### 命令行版本
```bash
python -m examples.main
```
