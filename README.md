# 简历 ReAct 双 Agent

一个 Vue + FastAPI 的简历优化 MVP。用户可以上传 PDF/DOCX 简历，也可以直接粘贴简历文本；输入目标公司、岗位和 JD 后，后端调用 DeepSeek，并通过 `DecisionAgent` 与 `ActionAgent` 完成折中版 ReAct 优化。

## 本地运行

### 后端

建议使用 Python 3.12：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
uvicorn backend.react_resume.app:app --reload --host 127.0.0.1 --port 8000
```
后端启动命令---.\.venv\Scripts\python.exe -m uvicorn backend.react_resume.app:app --reload --host 127.0.0.1 --port 8000

健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 前端

```powershell
cd frontend
npm install
npm run dev
```

打开：

```text
http://localhost:5173
```

## 第一版能力

- 上传 PDF/DOCX 简历，或直接粘贴简历文本。
- 输入目标公司、目标岗位和 JD。
- 调用 DeepSeek 运行双 Agent ReAct 优化流程，当前折中版一次请求使用 2 次模型调用。
- 以对话形式展示诊断、Agent 思考摘要、行动轨迹、优化后简历和面试预测问题。

## 测试

后端：

```powershell
.\.venv\Scripts\python -m pytest tests\backend -v
```

前端：

```powershell
cd frontend
npm run test
npm run build
```
