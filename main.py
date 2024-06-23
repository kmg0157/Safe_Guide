from client import FlaskClient

def main():
    client = FlaskClient()
    try:
        client.run()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == '__main__':
    main()
