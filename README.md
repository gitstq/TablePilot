<p align="center">
  <h1 align="center">📊 TablePilot</h1>
  <p align="center">
    <strong>Lightweight Tabular Data Intelligent Analysis Engine CLI</strong><br>
    轻量级表格数据智能分析引擎CLI工具
  </p>
  <p align="center">
    <a href="#-简体中文">简体中文</a> ·
    <a href="#-繁體中文">繁體中文</a> ·
    <a href="#-english">English</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
    <img src="https://img.shields.io/badge/Dependencies-Zero-success.svg" alt="Zero Dependencies">
    <img src="https://img.shields.io/badge/Tests-55%20Passed-brightgreen.svg" alt="Tests">
  </p>
</p>

---

## 🇨🇳 简体中文

### 🎉 项目介绍

**TablePilot** 是一款轻量级的表格数据智能分析引擎CLI工具，**零外部依赖**，纯Python标准库实现。它为数据科学家、分析师和开发者提供了一站式的数据探索、统计分析、数据清洗、终端可视化和多格式报告生成能力。

灵感来源于对表格数据基础模型（如TabPFN）领域的关注，TablePilot专注于提供**开箱即用的数据分析体验**，无需安装pandas、numpy等重型依赖，一行命令即可完成从数据加载到深度分析的全流程。

#### 💡 自研差异化亮点

- 🚀 **零依赖**：纯Python标准库实现，无需安装任何第三方包
- 📊 **全面统计**：描述性统计、相关性分析、异常值检测、分布分析
- 🧹 **智能清洗**：缺失值处理、去重、标准化、异常值移除
- 📈 **终端可视化**：柱状图、直方图、箱线图、散点图、热力图
- 📝 **多格式报告**：Markdown、HTML、JSON三种报告格式
- 🔍 **交互模式**：支持交互式数据探索，实时查询分析
- 🌐 **多格式支持**：CSV、TSV、JSON、JSONL自动检测加载

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **数据概览** | 自动检测文件格式，展示数据形状、类型分布、质量评分 |
| 📐 **描述性统计** | 均值、中位数、标准差、偏度、峰度、百分位数、IQR等 |
| 🔗 **相关性分析** | Pearson相关系数矩阵，支持数值列两两关联分析 |
| 📊 **终端图表** | 柱状图、直方图、箱线图、散点图、热力图，纯ASCII渲染 |
| 🧹 **数据清洗** | 缺失值填充（均值/中位数/众数/前向/后向）、去重、标准化 |
| 🔎 **异常值检测** | IQR方法和Z-Score方法双重检测 |
| 📝 **报告生成** | Markdown/HTML/JSON多格式，含自动化洞察 |
| 🔄 **数据对比** | 两个数据文件的形状、统计量、分布对比 |
| 🎮 **交互模式** | 实时数据浏览、搜索、统计查询 |
| ⚡ **高性能** | 惰性计算、列缓存、流式处理大数据集 |

### 🚀 快速开始

#### 环境要求

- **Python** 3.8 或更高版本
- 无需任何第三方依赖

#### 安装

```bash
# 方式一：从源码安装
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
pip install .

# 方式二：直接运行（无需安装）
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
python -m tablepilot --help
```

#### 基本使用

```bash
# 全面分析CSV文件
python -m tablepilot analyze data.csv

# 快速数据概览
python -m tablepilot profile data.json

# 生成HTML报告
python -m tablepilot report data.csv --format html

# 数据清洗
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o cleaned.csv

# 终端可视化
python -m tablepilot visualize data.csv --chart bar --column sales
python -m tablepilot visualize data.csv --chart box --column age
python -m tablepilot visualize data.csv --chart heatmap

# 交互式探索
python -m tablepilot interactive data.csv

# 对比两个文件
python -m tablepilot compare file1.csv file2.csv
```

### 📖 详细使用指南

#### 1. 数据分析（analyze）

```bash
# 基础分析
python -m tablepilot analyze employees.csv

# 含相关性和异常值检测的完整分析
python -m tablepilot analyze employees.csv --correlation --outliers

# 指定列和行数限制
python -m tablepilot analyze data.csv -c "name,age,salary" -r 1000

# 导出分析报告
python -m tablepilot analyze data.csv --format html -o report.html
```

#### 2. 数据概览（profile）

```bash
# 快速数据质量评估
python -m tablepilot profile data.csv

# JSON格式输出（便于程序处理）
python -m tablepilot profile data.csv --format json
```

#### 3. 数据清洗（clean）

```bash
# 删除空值和重复行
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o clean.csv

# 用均值填充空值
python -m tablepilot clean data.csv --fill-na mean -o filled.csv

# 标准化数值列
python -m tablepilot clean data.csv --normalize minmax -o normalized.csv

# 组合操作
python -m tablepilot clean data.csv --strip-whitespace --fill-na median --drop-duplicates -o result.csv
```

#### 4. 终端可视化（visualize）

```bash
# 柱状图（分类数据频率）
python -m tablepilot visualize data.csv --chart bar --column department

# 直方图（数值数据分布）
python -m tablepilot visualize data.csv --chart hist --column salary

# 箱线图（数值数据分布与异常值）
python -m tablepilot visualize data.csv --chart box --column age

# 散点图（两个数值变量的关系）
python -m tablepilot visualize data.csv --chart scatter --columns salary,experience

# 相关性热力图
python -m tablepilot visualize data.csv --chart heatmap
```

#### 5. 报告生成（report）

```bash
# Markdown报告
python -m tablepilot report data.csv --format markdown

# HTML报告（带暗色主题样式）
python -m tablepilot report data.csv --format html -o analysis.html

# 自定义标题
python -m tablepilot report data.csv --title "Q4销售数据分析"
```

#### 6. 交互模式（interactive）

```bash
python -m tablepilot interactive data.csv
```

交互模式支持的命令：

| 命令 | 说明 |
|------|------|
| `head [n]` | 显示前n行 |
| `tail [n]` | 显示后n行 |
| `sample [n]` | 随机采样n行 |
| `stats [col]` | 显示列统计信息 |
| `hist [col]` | 显示直方图 |
| `box [col]` | 显示箱线图 |
| `corr` | 显示相关性矩阵 |
| `search <col> <val>` | 搜索数据 |
| `columns` | 列出所有列 |
| `shape` | 显示数据形状 |
| `help` | 显示帮助 |

### 💡 设计思路与迭代规划

#### 设计理念

TablePilot的设计遵循以下原则：

1. **零依赖哲学**：不依赖pandas、numpy等重型库，确保在任何Python环境中都能运行
2. **CLI优先**：所有功能通过命令行暴露，便于集成到自动化流水线
3. **渐进式分析**：从概览到深入分析，用户可按需选择分析深度
4. **终端原生**：可视化直接在终端渲染，无需打开额外窗口

#### 技术选型

- **纯Python标准库**：csv、json、math、statistics、collections
- **DataTable结构**：自研轻量级内存数据表，支持列式和行式访问
- **惰性计算**：列数据按需计算并缓存，避免不必要的内存开销

#### 后续迭代计划

- [ ] 📊 新增饼图和折线图可视化
- [ ] 🔄 支持Excel (.xlsx) 文件读取
- [ ] 📋 新增SQL查询接口
- [ ] 🧪 新增数据质量规则引擎
- [ ] 🌐 新增Web仪表盘模式
- [ ] 📦 支持pip直接安装

### 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交Pull Request

**提交规范**：遵循Angular提交规范
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具变更

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

## 🇹🇼 繁體中文

### 🎉 專案介紹

**TablePilot** 是一款輕量級的表格資料智慧分析引擎CLI工具，**零外部依賴**，純Python標準函式庫實作。它為資料科學家、分析師和開發者提供了一站式的資料探索、統計分析、資料清洗、終端視覺化和多格式報告生成能力。

靈感來自於對表格資料基礎模型（如TabPFN）領域的關注，TablePilot專注於提供**開箱即用的資料分析體驗**，無需安裝pandas、numpy等重型依賴，一行指令即可完成從資料載入到深度分析的全流程。

#### 💡 自研差異化亮點

- 🚀 **零依賴**：純Python標準函式庫實作，無需安裝任何第三方套件
- 📊 **全面統計**：描述性統計、相關性分析、異常值檢測、分佈分析
- 🧹 **智慧清洗**：缺失值處理、去重、標準化、異常值移除
- 📈 **終端視覺化**：柱狀圖、直方圖、箱線圖、散點圖、熱力圖
- 📝 **多格式報告**：Markdown、HTML、JSON三種報告格式
- 🔍 **互動模式**：支援互動式資料探索，即時查詢分析
- 🌐 **多格式支援**：CSV、TSV、JSON、JSONL自動偵測載入

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **資料概覽** | 自動偵測檔案格式，展示資料形狀、型別分佈、品質評分 |
| 📐 **描述性統計** | 平均值、中位數、標準差、偏度、峰度、百分位數、IQR等 |
| 🔗 **相關性分析** | Pearson相關係數矩陣，支援數值欄位兩兩關聯分析 |
| 📊 **終端圖表** | 柱狀圖、直方圖、箱線圖、散點圖、熱力圖，純ASCII渲染 |
| 🧹 **資料清洗** | 缺失值填充（均值/中位數/眾數/前向/後向）、去重、標準化 |
| 🔎 **異常值檢測** | IQR方法和Z-Score方法雙重檢測 |
| 📝 **報告生成** | Markdown/HTML/JSON多格式，含自動化洞察 |
| 🔄 **資料對比** | 兩個資料檔案的形狀、統計量、分佈對比 |
| 🎮 **互動模式** | 即時資料瀏覽、搜尋、統計查詢 |
| ⚡ **高效能** | 惰性計算、欄位快取、串流處理大型資料集 |

### 🚀 快速開始

#### 環境需求

- **Python** 3.8 或更高版本
- 無需任何第三方依賴

#### 安裝

```bash
# 方式一：從原始碼安裝
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
pip install .

# 方式二：直接執行（無需安裝）
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
python -m tablepilot --help
```

#### 基本使用

```bash
# 全面分析CSV檔案
python -m tablepilot analyze data.csv

# 快速資料概覽
python -m tablepilot profile data.json

# 生成HTML報告
python -m tablepilot report data.csv --format html

# 資料清洗
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o cleaned.csv

# 終端視覺化
python -m tablepilot visualize data.csv --chart bar --column sales
python -m tablepilot visualize data.csv --chart box --column age
python -m tablepilot visualize data.csv --chart heatmap

# 互動式探索
python -m tablepilot interactive data.csv

# 對比兩個檔案
python -m tablepilot compare file1.csv file2.csv
```

### 📖 詳細使用指南

#### 1. 資料分析（analyze）

```bash
# 基礎分析
python -m tablepilot analyze employees.csv

# 含相關性和異常值檢測的完整分析
python -m tablepilot analyze employees.csv --correlation --outliers

# 指定欄位和行數限制
python -m tablepilot analyze data.csv -c "name,age,salary" -r 1000

# 匯出分析報告
python -m tablepilot analyze data.csv --format html -o report.html
```

#### 2. 資料概覽（profile）

```bash
# 快速資料品質評估
python -m tablepilot profile data.csv

# JSON格式輸出（便於程式處理）
python -m tablepilot profile data.csv --format json
```

#### 3. 資料清洗（clean）

```bash
# 刪除空值和重複行
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o clean.csv

# 用均值填充空值
python -m tablepilot clean data.csv --fill-na mean -o filled.csv

# 標準化數值欄位
python -m tablepilot clean data.csv --normalize minmax -o normalized.csv

# 組合操作
python -m tablepilot clean data.csv --strip-whitespace --fill-na median --drop-duplicates -o result.csv
```

#### 4. 終端視覺化（visualize）

```bash
# 柱狀圖（分類資料頻率）
python -m tablepilot visualize data.csv --chart bar --column department

# 直方圖（數值資料分佈）
python -m tablepilot visualize data.csv --chart hist --column salary

# 箱線圖（數值資料分佈與異常值）
python -m tablepilot visualize data.csv --chart box --column age

# 散點圖（兩個數值變數的關係）
python -m tablepilot visualize data.csv --chart scatter --columns salary,experience

# 相關性熱力圖
python -m tablepilot visualize data.csv --chart heatmap
```

#### 5. 報告生成（report）

```bash
# Markdown報告
python -m tablepilot report data.csv --format markdown

# HTML報告（帶暗色主題樣式）
python -m tablepilot report data.csv --format html -o analysis.html

# 自訂標題
python -m tablepilot report data.csv --title "Q4銷售資料分析"
```

#### 6. 互動模式（interactive）

```bash
python -m tablepilot interactive data.csv
```

互動模式支援的命令：

| 指令 | 說明 |
|------|------|
| `head [n]` | 顯示前n行 |
| `tail [n]` | 顯示後n行 |
| `sample [n]` | 隨機取樣n行 |
| `stats [col]` | 顯示欄位統計資訊 |
| `hist [col]` | 顯示直方圖 |
| `box [col]` | 顯示箱線圖 |
| `corr` | 顯示相關性矩陣 |
| `search <col> <val>` | 搜尋資料 |
| `columns` | 列出所有欄位 |
| `shape` | 顯示資料形狀 |
| `help` | 顯示說明 |

### 💡 設計思路與迭代規劃

#### 設計理念

TablePilot的設計遵循以下原則：

1. **零依賴哲學**：不依賴pandas、numpy等重型函式庫，確保在任何Python環境中都能執行
2. **CLI優先**：所有功能透過命令列暴露，便於整合到自動化流水線
3. **漸進式分析**：從概覽到深入分析，使用者可按需選擇分析深度
4. **終端原生**：視覺化直接在終端渲染，無需開啟額外視窗

#### 技術選型

- **純Python標準函式庫**：csv、json、math、statistics、collections
- **DataTable結構**：自研輕量級記憶體資料表，支援欄位式和行式存取
- **惰性計算**：欄位資料按需計算並快取，避免不必要的記憶體開銷

#### 後續迭代計畫

- [ ] 📊 新增圓餅圖和折線圖視覺化
- [ ] 🔄 支援Excel (.xlsx) 檔案讀取
- [ ] 📋 新增SQL查詢介面
- [ ] 🧪 新增資料品質規則引擎
- [ ] 🌐 新增Web儀表板模式
- [ ] 📦 支援pip直接安裝

### 🤝 貢獻指南

歡迎貢獻程式碼！請遵循以下步驟：

1. Fork本倉庫
2. 建立功能分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交Pull Request

**提交規範**：遵循Angular提交規範
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具變更

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

## 🇬🇧 English

### 🎉 Introduction

**TablePilot** is a lightweight tabular data intelligent analysis engine CLI tool with **zero external dependencies**, built entirely with Python's standard library. It provides data scientists, analysts, and developers with an all-in-one solution for data exploration, statistical analysis, data cleaning, terminal visualization, and multi-format report generation.

Inspired by the tabular data foundation model field (such as TabPFN), TablePilot focuses on delivering an **out-of-the-box data analysis experience** without requiring heavy dependencies like pandas or numpy. A single command takes you from data loading to in-depth analysis.

#### 💡 Differentiation Highlights

- 🚀 **Zero Dependencies**: Pure Python standard library — no third-party packages needed
- 📊 **Comprehensive Statistics**: Descriptive stats, correlation analysis, outlier detection, distribution analysis
- 🧹 **Smart Data Cleaning**: Missing value handling, deduplication, normalization, outlier removal
- 📈 **Terminal Visualization**: Bar charts, histograms, box plots, scatter plots, heatmaps
- 📝 **Multi-format Reports**: Markdown, HTML, and JSON report formats
- 🔍 **Interactive Mode**: Interactive data exploration with real-time query and analysis
- 🌐 **Multi-format Support**: Auto-detection for CSV, TSV, JSON, and JSONL files

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Data Overview** | Auto-detect file format, display shape, type distribution, quality score |
| 📐 **Descriptive Statistics** | Mean, median, std dev, skewness, kurtosis, percentiles, IQR, and more |
| 🔗 **Correlation Analysis** | Pearson correlation matrix for pairwise numeric column analysis |
| 📊 **Terminal Charts** | Bar, histogram, box plot, scatter, heatmap — all rendered in pure ASCII |
| 🧹 **Data Cleaning** | Fill missing values (mean/median/mode/forward/backward), dedup, normalize |
| 🔎 **Outlier Detection** | Dual detection with IQR and Z-Score methods |
| 📝 **Report Generation** | Markdown/HTML/JSON formats with automated insights |
| 🔄 **Data Comparison** | Compare shape, statistics, and distribution between two data files |
| 🎮 **Interactive Mode** | Real-time data browsing, search, and statistical queries |
| ⚡ **High Performance** | Lazy evaluation, column caching, streaming for large datasets |

### 🚀 Quick Start

#### Requirements

- **Python** 3.8 or higher
- No third-party dependencies required

#### Installation

```bash
# Option 1: Install from source
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
pip install .

# Option 2: Run directly (no installation needed)
git clone https://github.com/gitstq/TablePilot.git
cd TablePilot
python -m tablepilot --help
```

#### Basic Usage

```bash
# Full analysis of a CSV file
python -m tablepilot analyze data.csv

# Quick data profiling
python -m tablepilot profile data.json

# Generate HTML report
python -m tablepilot report data.csv --format html

# Data cleaning
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o cleaned.csv

# Terminal visualization
python -m tablepilot visualize data.csv --chart bar --column sales
python -m tablepilot visualize data.csv --chart box --column age
python -m tablepilot visualize data.csv --chart heatmap

# Interactive exploration
python -m tablepilot interactive data.csv

# Compare two files
python -m tablepilot compare file1.csv file2.csv
```

### 📖 Detailed Usage Guide

#### 1. Data Analysis (analyze)

```bash
# Basic analysis
python -m tablepilot analyze employees.csv

# Full analysis with correlation and outlier detection
python -m tablepilot analyze employees.csv --correlation --outliers

# Specify columns and row limit
python -m tablepilot analyze data.csv -c "name,age,salary" -r 1000

# Export analysis report
python -m tablepilot analyze data.csv --format html -o report.html
```

#### 2. Data Profiling (profile)

```bash
# Quick data quality assessment
python -m tablepilot profile data.csv

# JSON output for programmatic processing
python -m tablepilot profile data.csv --format json
```

#### 3. Data Cleaning (clean)

```bash
# Drop null values and duplicates
python -m tablepilot clean data.csv --drop-na --drop-duplicates -o clean.csv

# Fill null values with mean
python -m tablepilot clean data.csv --fill-na mean -o filled.csv

# Normalize numeric columns
python -m tablepilot clean data.csv --normalize minmax -o normalized.csv

# Combined operations
python -m tablepilot clean data.csv --strip-whitespace --fill-na median --drop-duplicates -o result.csv
```

#### 4. Terminal Visualization (visualize)

```bash
# Bar chart (categorical data frequency)
python -m tablepilot visualize data.csv --chart bar --column department

# Histogram (numeric data distribution)
python -m tablepilot visualize data.csv --chart hist --column salary

# Box plot (numeric data distribution and outliers)
python -m tablepilot visualize data.csv --chart box --column age

# Scatter plot (relationship between two numeric variables)
python -m tablepilot visualize data.csv --chart scatter --columns salary,experience

# Correlation heatmap
python -m tablepilot visualize data.csv --chart heatmap
```

#### 5. Report Generation (report)

```bash
# Markdown report
python -m tablepilot report data.csv --format markdown

# HTML report (with dark theme styling)
python -m tablepilot report data.csv --format html -o analysis.html

# Custom title
python -m tablepilot report data.csv --title "Q4 Sales Data Analysis"
```

#### 6. Interactive Mode (interactive)

```bash
python -m tablepilot interactive data.csv
```

Available interactive commands:

| Command | Description |
|---------|-------------|
| `head [n]` | Show first n rows |
| `tail [n]` | Show last n rows |
| `sample [n]` | Random sample of n rows |
| `stats [col]` | Show column statistics |
| `hist [col]` | Show histogram |
| `box [col]` | Show box plot |
| `corr` | Show correlation matrix |
| `search <col> <val>` | Search data |
| `columns` | List all columns |
| `shape` | Show data shape |
| `help` | Show help |

### 💡 Design Philosophy & Roadmap

#### Design Principles

TablePilot follows these core principles:

1. **Zero Dependency Philosophy**: No pandas, numpy, or heavy libraries — runs in any Python environment
2. **CLI-First**: All features exposed via command line for easy integration into automation pipelines
3. **Progressive Analysis**: From overview to deep analysis, users choose their desired depth
4. **Terminal-Native**: Visualizations render directly in the terminal — no extra windows needed

#### Tech Stack

- **Pure Python Standard Library**: csv, json, math, statistics, collections
- **DataTable Structure**: Custom lightweight in-memory data table with column and row access
- **Lazy Evaluation**: Column data computed on-demand and cached to minimize memory overhead

#### Roadmap

- [ ] 📊 Add pie chart and line chart visualizations
- [ ] 🔄 Support Excel (.xlsx) file reading
- [ ] 📋 Add SQL query interface
- [ ] 🧪 Add data quality rule engine
- [ ] 🌐 Add web dashboard mode
- [ ] 📦 Support direct pip installation

### 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a Pull Request

**Commit Convention**: Follow the Angular commit convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tooling changes

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <sub>Built with ❤️ by TablePilot Team · Powered by Pure Python</sub>
</p>
