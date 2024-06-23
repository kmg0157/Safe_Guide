from client import FileReceiver
from db_manage import ImageDatabase

def main():
    client = FileReceiver()
    imagedb=ImageDatabase()
    try:
        client.run()
        client._set_routes()
        imagedb.save_image()
        imagedb.close_db()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
