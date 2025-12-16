# Age Key Generator (age-keygen GUI)

---
![ScreenShot](https://github.com/louischang38/age-keygen-gui/blob/main/screenshot/screenshot.png)

### Introduction

A simple, cross-platform graphical user interface (GUI) wrapper for the official `age-keygen` command-line tool. This application allows users to generate **age identity (private)** and **recipient (public)** key pairs easily without using the terminal.

The application is built with **Python** and **PySide6**, and automatically adapts to the system's dark or light theme using `darkdetect`.

---

### Features

- GUI-based key generation with a single click
- Automatic dark / light theme detection
- One-click copy and save buttons for public and private keys
- Real-time status and progress updates

---

### Prerequisites

- Python 3.13.11
- `age` command-line tool installed and available in system `PATH`

---

### Installation

Install required Python dependencies:

```bash
pip install PySide6 darkdetect
```

---

### Running the Application

1. Ensure `age` is correctly installed.
2. Save the source code as `age_keygen_gui.py`.
3. Run the application:

```bash
python age_keygen_gui.py
```

---

### Usage

1. Click **"Generate New Key Pair"**.
2. The application runs `age-keygen` in the background.
3. Generated keys will appear in the interface.

#### Private Key (Identity Key)

- Save securely using the **Save** button
- Recommended filename: `age_private.key`
- **Never share this file**

#### Public Key (Recipient Key)

- Copy to clipboard or save to file
- Share with others so they can encrypt files for you

---

### Security Notes

- Keys are never transmitted or uploaded
---




### 簡介

Age Key Generator 是一個簡單、跨平台的圖形化介面（GUI）工具，作為官方 `age-keygen` 指令列工具的前端，讓使用者不需要操作終端機即可產生 **age 私鑰（Identity Key）** 與 **公鑰（Recipient Key）**。

本程式使用 **Python** 與 **PySide6** 開發，並透過 `darkdetect` 自動偵測系統的深色或淺色主題。

---

### 功能特色

- 一鍵產生 age 金鑰對
- 自動支援深色 / 淺色系統主題
- 公鑰與私鑰支援一鍵複製與儲存
- 即時顯示金鑰產生狀態

---

### 系統需求

- Python 3.13.11 以上
- 系統需已安裝 `age` 指令工具，並可於命令列直接執行

---

### 安裝方式

安裝必要的 Python 套件：

```bash
pip install PySide6 darkdetect
```

---

### 執行方式

1. 確認 `age` 已正確安裝
2. 將程式碼儲存為 `age_keygen_gui.py`
3. 執行程式：

```bash
python age_keygen_gui.py
```

---

### 使用說明

1. 點擊 **「Generate New Key Pair」** 按鈕
2. 程式會在背景執行 `age-keygen`
3. 產生的金鑰會自動顯示於介面中

#### 私鑰（Identity Key）

- 使用 **Save** 按鈕安全儲存
- 建議檔名：`age_private.key`
- ⚠️ 請勿分享私鑰

#### 公鑰（Recipient Key）

- 可複製或另存成檔案
- 可自由分享給需要加密檔案給你的人

---

### 安全注意事項

- 本工具不會自動儲存或上傳任何金鑰

---

