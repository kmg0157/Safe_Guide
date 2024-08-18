import requests


class ControlLED:
    def __init__(self):
        
        # 아두이노의 IP 주소와 포트 번호
        self.arduino_ip = '192.168.0.86'  # 아두이노의 IP 주소
        self.port = 80                                                                                                                                          

        # 요청을 보낼 URL 설정
        self.url_on = f'http://{self.arduino_ip}:{self.port}/H'
        self.url_off = f'http://{self.arduino_ip}:{self.port}/L'

    #LED On
    def request_on(self):
        try:
            requests.get(self.url_on)
        except requests.RequestException as e:
            print(f"An error occurred: {e}")

    #LED Off
    def request_off(self):
        try:
            requests.get(self.url_off)
        except requests.RequestException as e:
            print(f"An error occurred: {e}")