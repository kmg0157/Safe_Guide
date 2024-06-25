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
            Sequence INT PRIMARY KEY AUTOINCREMENT,
            Timestamp INT NOT NULL,
            Filename BLOB NOT NULL,
            Height INT NOT NULL,
            Width INT NOT NULL,
            Channel INT NOT NULL,
            Status INT NOT NULL
        )
        '''
        self.cur.execute(create_table_query)
        self.conn.commit()

    #수정필요
    def save_image(self, image_bytes, status):
        # 이미지 바이트로부터 이미지 객체 생성
        img = Image.open(io.BytesIO(image_bytes))
        
        width, height=img.size
        channel=len(img.getbands())

        
        # 현재 시간 (밀리초 단위)
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # 데이터 삽입 SQL
        insert_data_query = '''
        INSERT INTO images (Timestamp, Filename, Height, Width, Channel, Status)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        # 데이터 삽입
        self.cur.execute(insert_data_query, (timestamp, width, height, channel, status))
        self.conn.commit()


    def close_db(self):
        self.cur.close()
        self.conn.close()
