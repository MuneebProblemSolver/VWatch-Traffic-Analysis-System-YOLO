from app.db.database import init_db
from app.ai.processor import process_video
from app.config import VIDEO_PATH

if __name__ == "__main__":
    init_db()
    process_video(VIDEO_PATH)
