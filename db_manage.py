import sqlite3
import base64
from datetime import datetime
from PIL import Image
import io
from client import FileReceiver

class ImageDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('image_database.db', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()
        self.image_data=FileReceiver()

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS images (
            timestamp INTEGER NOT NULL,
            filename BLOB NOT NULL,
            height INT NOT NULL,
            width INT NOT NULL,
            channel INT NOT NULL,
            status INTEGER NOT NULL
        )
        '''
        self.cur.execute(create_table_query)
        self.conn.commit()

    #수정필요
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


    def close_db(self):
        self.cur.close()
        self.conn.close()
