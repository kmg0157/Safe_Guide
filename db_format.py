import sqlite3
import base64
from datetime import datetime
from PIL import Image
import io

# 데이터베이스 연결 (데이터베이스 파일이 없으면 자동으로 생성됨)
conn = sqlite3.connect('image_database.db')

# 커서 객체 생성
cur = conn.cursor()

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
cur.execute(create_table_query)
conn.commit()


def save_image_to_db(image_path, status):
    # 이미지 열기
    with Image.open(image_path) as img:
        # 이미지 차원 얻기
        dimensions = f"{img.width}x{img.height}"
        
        # 이미지 바이트로 변환
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        
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
        cur.execute(insert_data_query, (timestamp, dimensions, image_base64, status))
        conn.commit()

# 예제 이미지 저장 (처리되지 않음 상태로 저장)
save_image_to_db('example_image.png', 0)


def update_image_status(image_id, new_status):
    # 상태 업데이트 SQL
    update_status_query = '''
    UPDATE images
    SET status = ?
    WHERE id = ?
    '''
    
    # 상태 업데이트 실행
    cur.execute(update_status_query, (new_status, image_id))
    conn.commit()

# 예제: ID가 1인 이미지의 상태를 1로 업데이트
update_image_status(1, 1)


def fetch_images():
    # 데이터 조회 SQL
    select_query = '''
    SELECT id, timestamp, dimensions, status
    FROM images
    '''
    
    # 데이터 조회 실행
    cur.execute(select_query)
    rows = cur.fetchall()
    
    # 결과 출력
    for row in rows:
        print(f"ID: {row[0]}, Timestamp: {row[1]}, Dimensions: {row[2]}, Status: {row[3]}")

# 예제: 저장된 이미지 조회
fetch_images()


# 커서와 연결 종료
cur.close()
conn.close()
