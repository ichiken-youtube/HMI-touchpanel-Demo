import cv2
import socket
import struct
import numpy as np
import time

PACKET_SIZE_LIMIT = 800
FRAME_WIDTH = 0
FRAME_HEIGHT = 0
GRID_X = 2
GRID_Y = 2
grid = 0

def receive_frame(server_socket):
  # フレームサイズを受信
  header = b''
  while len(header) < 16:
    header += server_socket.recv(16 - len(header))
  FRAME_WIDTH, FRAME_HEIGHT, grid, size = struct.unpack(">LLLL", header)

  # フレームデータを受信
  frame_data = b''
  while len(frame_data) < size:
    remaining = size - len(frame_data)
    frame_data += server_socket.recv(min(PACKET_SIZE_LIMIT, remaining))

  # 受信したデータを画像に変換
  frame = np.frombuffer(frame_data, dtype=np.uint8)
  frame = frame.reshape((FRAME_HEIGHT, FRAME_WIDTH, 4))

  return frame

def main():
  # ソケット設定
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect(('127.0.0.1', 8000))
  print('サーバーに接続しました')

  try:
    while True:
      request = b'SHOT' + struct.pack(">II", GRID_X, GRID_Y)
      client_socket.sendall(request)
      print('撮影要求')
      for i in range(1,GRID_X*GRID_Y):
        request = b'RQST' + struct.pack(">II", i,0)
        client_socket.sendall(request)
        print('画像要求')
        #client_socket.sendall(struct.pack('>L', i))
        # フレームを受信して表示
        frame = receive_frame(client_socket)
        cv2.imshow('Received Frame', frame)

      # 'q'を押すと終了
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
      time.sleep(1)
  except Exception as e:
    print(f'エラーが発生しました: {e}')
  finally:
    client_socket.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
