from client import FileReceiver

def main():
    client = FileReceiver()
    try:
        client.run()
        client._set_routes()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
