import requests

class ControlLED:
    def __init__(self):
        self.arduino_ip = '192.168.0.86'  # 아두이노의 IP 주소
        self.port = 80
        self.url_on = f'http://{self.arduino_ip}:{self.port}/H'
        self.url_off = f'http://{self.arduino_ip}:{self.port}/L'
        self.current_state = 'off'  # 현재 LED 상태를 추적

    def request_on(self):
        if self.current_state != 'on':  # LED가 이미 켜져 있는지 확인
            try:
                requests.get(self.url_on)
                self.current_state = 'on'
            except requests.RequestException as e:
                print(f"An error occurred: {e}")

    def request_off(self):
        if self.current_state != 'off':  # LED가 이미 꺼져 있는지 확인
            try:
                requests.get(self.url_off)
                self.current_state = 'off'
            except requests.RequestException as e:
                print(f"An error occurred: {e}")

