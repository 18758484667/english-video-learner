from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .database import engine, Base
from .init_db import init_database, seed_vocabulary_levels

# 创建FastAPI应用
app = FastAPI(
    title="English Video Learner API",
    description="API for English learning through video subtitles",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 启动时初始化数据库
@app.on_event("startup")
def startup_event():
    init_database()
    seed_vocabulary_levels()
    print("Server started successfully!")

# 健康检查端点
@app.get("/")
def read_root():
    return {"message": "English Video Learner API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 导入并注册路由
from .api import users, videos, vocabulary, tests

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(vocabulary.router, prefix="/api/vocabulary", tags=["vocabulary"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])

# 临时测试端点
@app.get("/api/test-reload")
def test_reload():
    return {"status": "main reloaded"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
