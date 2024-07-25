import sqlite3
import numpy as np
from datetime import datetime
from PIL import Image
import io

class ImageDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('image_database.db', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS images (
            Sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp INTEGER NOT NULL,
            Filename TEXT NOT NULL,
            Height INTEGER NOT NULL,
            Width INTEGER NOT NULL,
            Channel INTEGER NOT NULL,
            Status INTEGER NOT NULL
        )
        '''
        self.cur.execute(create_table_query)
        self.conn.commit()
    
    def save_image(self, image_bytes, filename, status):
        # 이미지 바이트로부터 이미지 객체 생성
        img = Image.open(io.BytesIO(image_bytes))
        
        img_array = np.array(img)
        height, width, channel = img_array.shape

        # 현재 시간 (밀리초 단위)
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # 데이터 삽입 SQL
        insert_data_query = '''
        INSERT INTO images (Timestamp, Filename, Height, Width, Channel, Status)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        # 데이터 삽입
        self.cur.execute(insert_data_query, (timestamp, filename, height, width, channel, status))
        self.conn.commit()

    def close_db(self):
        self.cur.close()
        self.conn.close()
