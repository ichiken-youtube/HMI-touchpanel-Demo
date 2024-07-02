import cv2
import socket
import struct
import numpy as np
import time
import settings

SERVER_IP = settings.SERVER_IP
PACKET_SIZE_LIMIT = 800
FRAME_WIDTH = 0
FRAME_HEIGHT = 0
GRID_X = 2
GRID_Y = 2
grid = 0

def receive_frame(server_socket):
  global FRAME_HEIGHT, FRAME_WIDTH
  # フレームサイズを受信
  header = b''
  while len(header) < 16:
    header += server_socket.recv(16 - len(header))
  FRAME_WIDTH, FRAME_HEIGHT, grid, size = struct.unpack(">LLLL", header)
  print(FRAME_WIDTH, FRAME_HEIGHT, grid, size)

  # フレームデータを受信
  frame_data = b''
  while len(frame_data) < size:
    remaining = size - len(frame_data)
    frame_data += server_socket.recv(min(PACKET_SIZE_LIMIT, remaining))

  # 受信したデータを画像に変換
  frame = np.frombuffer(frame_data, dtype=np.uint8)
  frame = frame.reshape((FRAME_HEIGHT, FRAME_WIDTH, 4))

  return frame,grid

def main():
  # ソケット設定
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.settimeout(10)
  client_socket.connect((SERVER_IP, 8000))
  print('サーバーに接続しました')
  
  request = b'SETG' + struct.pack(">II", GRID_X,GRID_Y)
  client_socket.sendall(request)
  request = b'SETF' + struct.pack(">II", FRAME_WIDTH,FRAME_HEIGHT)
  client_socket.sendall(request)
  full_frame = np.zeros((90*2, 120*2, 4), dtype=np.uint8)
  grid = 0

  try:
    while True:
      for y in range(GRID_Y):
        for x in range(GRID_X):
          print('撮影要求')
          request = b'SHOT' + struct.pack(">II", GRID_X, GRID_Y)
          client_socket.sendall(request)
          request = b'RQST' + struct.pack(">II", 0,0)
          client_socket.sendall(request)
          print('画像要求')
          #client_socket.sendall(struct.pack('>L', i))
          # フレームを受信して表示
          frame,grid = receive_frame(client_socket)
          print(int((grid-1)/GRID_X))
          print((grid-1)%GRID_X)
          #full_frame[y*FRAME_HEIGHT:(y+1)*FRAME_HEIGHT, x*FRAME_WIDTH:(x+1)*FRAME_WIDTH] = frame
          full_frame[int((grid-1)/GRID_X)*FRAME_HEIGHT:(int((grid-1)/GRID_X)+1)*FRAME_HEIGHT, ((grid-1)%GRID_X)*FRAME_WIDTH:((grid-1)%GRID_X+1)*FRAME_WIDTH] = frame
          cv2.imshow('Received Frame', full_frame)
          time.sleep(0.5)

      # 'q'を押すと終了
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  except Exception as e:
    print(f'エラーが発生しました: {e}')
  finally:
    client_socket.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
  main()
