import sqlite3
import base64
from datetime import datetime
from PIL import Image
import io

class ImageDatabase:
    def __init__(self, db_path='image_database.db'):
        # 데이터베이스 연결 (데이터베이스 파일이 없으면 자동으로 생성됨)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        # 커서 객체 생성
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # 테이블 생성 SQL
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            dimensions TEXT NOT NULL,
            image_blob BLOB NOT NULL,
            status INTEGER NOT NULL
        )
        '''
        # 테이블 생성 실행
        self.cur.execute(create_table_query)
        self.conn.commit()

    def save_image(self, image_bytes, status):
        # 이미지 바이트로부터 이미지 객체 생성
        img = Image.open(io.BytesIO(image_bytes))
        
        # 이미지 차원 얻기
        dimensions = f"{img.width}x{img.height}"
        
        # 이미지 Base64 인코딩
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 현재 시간 (밀리초 단위)
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # 데이터 삽입 SQL
        insert_data_query = '''
        INSERT INTO images (timestamp, dimensions, image_blob, status)
        VALUES (?, ?, ?, ?)
        '''
        
        # 데이터 삽입
        self.cur.execute(insert_data_query, (timestamp, dimensions, image_base64, status))
        self.conn.commit()

    def update_image_status(self, image_id, status):
        # 이미지 상태 업데이트 SQL
        update_status_query = '''
        UPDATE images
        SET status = ?
        WHERE id = ?
        '''
        # 상태 업데이트
        self.cur.execute(update_status_query, (status, image_id))
        self.conn.commit()

    def fetch_images(self):
        # 이미지 데이터 가져오기 SQL
        fetch_images_query = '''
        SELECT id, timestamp, dimensions, image_blob, status
        FROM images
        '''
        self.cur.execute(fetch_images_query)
        rows = self.cur.fetchall()
        images = []
        for row in rows:
            image = {
                'id': row[0],
                'timestamp': row[1],
                'dimensions': row[2],
                'image_blob': row[3],
                'status': row[4]
            }
            images.append(image)
        return images

    def close_db(self):
        # 커서와 연결 종료
        self.cur.close()
        self.conn.close()
