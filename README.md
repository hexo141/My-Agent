# My-Agent

My-Agent 是一个基于 Python 的语音识别和文件处理工具包，支持录音、语音转文本（STT）、文件下载和解压等功能。

## 功能介绍

- 录音：支持音频录制并保存为文件。
- 语音识别（STT）：将录制的音频转换为文本。
- 文件下载：支持从指定 URL 下载文件。
- 文件解压：支持 ZIP 文件的解压缩。

## 安装方法

1. 克隆项目仓库：

```bash
git clone https://github.com/hexo141/My-Agent.git
cd My-Agent
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 录音

```bash
python record.py
```

### 语音识别

```bash
python stt.py
```

### 下载文件

```bash
python dl_file.py
```

### 下载语音识别模型

```bash
python dl_stt_model.py
```

### 解压文件

```bash
python unzip.py
```

## 配置

请根据 `config.toml` 文件进行相关参数配置。

## 许可证

本项目采用 GPL-3.0 许可证，详见 LICENSE 文件。
