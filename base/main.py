from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def check_connection():
    return {
        "message": "Đã kết nối tới API thành công!"
    }