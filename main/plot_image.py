import matplotlib.pyplot as plt
import sqlite3
import io

class FileOpener:
    def __init__(self):
        self.conn=sqlite3.connect('image_database.py')
        self.cur=self.conn.cursor()

    def file_open(self):
        self.cur.execute("SELECT Filename, Height, Width, Channel FROM images ORDER BY Sequence DESC LIMIT 1;")
        row=self.cur.fetchone()
        image_blob=row[0]
        h=row[1]
        w=row[2]
        c=row[3]

        image_stream=io.BytesIO(image_blob)
        image=plt.imread(image_stream)

        plt.imshow(image)
        plt.title(f"Image (Height:{h}, Width:{w}, Channel:{c})")
        plt.axis('off')
        plt.show()

        self.conn.close()
        self.cur.close()

def main():
    test=FileOpener()
    test.file_open()

if __name__ == '__main__':
    main()
