import cv2
import socket
import struct
from threading import Thread
from picamera2 import Picamera2
import random

PACKET_SIZE_LIMIT = 800
FRAME_WIDTH =120
FRAME_HEIGHT =90
GRID_X = 1
GRID_Y = 1
#grid = 1
latest_grid_flag = 0
grid_flag_mask = 0

def split_image(grid_x, grid_y, grid_number, frame):
  # 画像の高さと幅を取得
  height, width, _ = frame.shape

  # 各グリッドの高さと幅を計算
  grid_height = height // grid_x
  grid_width = width // grid_y

  # グリッドの行と列を計算
  grid_row = (grid_number - 1) // grid_y
  grid_col = (grid_number - 1) % grid_y

  # 指定されたグリッドの位置を計算
  start_y = grid_row * grid_height
  start_x = grid_col * grid_width
  end_y = start_y + grid_height
  end_x = start_x + grid_width

  # 指定されたグリッドの画像を取得
  grid_image = frame[start_y:end_y, start_x:end_x]
  return cv2.resize(grid_image, (FRAME_WIDTH, FRAME_HEIGHT))


def send_frame(frame, grid, client_socket):
  image_bytes = frame.tobytes()
  size = len(image_bytes)
  # フレームサイズを送信
  header = struct.pack(">LLLL", FRAME_WIDTH, FRAME_HEIGHT, grid, size)
  print(FRAME_WIDTH, FRAME_HEIGHT, grid, size)
  client_socket.sendall(header)
  #client_socket.sendall(struct.pack('>L', size))
  print('size:'+str(size))
  # フレームデータを送信
  for i in range(0, size, PACKET_SIZE_LIMIT):
    #print('chunk:'+str(i)+'-'+str(min(i + PACKET_SIZE_LIMIT,size)))
    chunk = image_bytes[i:min(i + PACKET_SIZE_LIMIT,size)]
    #print(len(chunk))
    client_socket.sendall(chunk)
    #time.sleep(0.01)

def shot(cap):
  frame = cap.capture_array()
  #ret,frame = cap.read()
  #if not ret:
  if len(frame)==0:
    print("フレームをキャプチャできませんでした。")
    cap.close()
    exit()
  return frame

def main(client_socket):
  global grid_flag_mask
  global latest_grid_flag
  # Webカメラのキャプチャ
  '''cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("カメラを開くことができませんでした。")
    exit()'''
  cap = Picamera2()
  cap.start()
  #cap.set_controls({'AfMode': controls.AfModeEnum.Continuous})
  frame=shot(cap)

  try:
    while True:
      # クライアントからの送信要求を待つ
      #print('送信要求待ち')
      request = client_socket.recv(12)
      if len(request) > 0:
        print(request)
      if request[:4] == b'RQST':
        grid = struct.unpack(">I",request[4:8])[0]
        if grid==0 :
          if latest_grid_flag == grid_flag_mask:
            latest_grid_flag=0
            grid = 1
          elif latest_grid_flag>0:
            for i in range(GRID_X*GRID_Y):
              if (latest_grid_flag >> i) & 0b1 == 0b00 :
                grid = i+1
                break
          else:
            grid = 1
          
        #print('latest_grid_flag:'+bin(latest_grid_flag))
        latest_grid_flag = ((0b1<<(grid-1))|latest_grid_flag) & grid_flag_mask
        print('latest_grid_flag:'+bin(latest_grid_flag))
        print('grid:'+str(grid))
        resized_frame = split_image(GRID_X, GRID_Y, grid, frame)

        # OpenCVのBGRからRGBに変換
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGBA)
        # フレームを送信
        send_frame(rgb_frame, grid, client_socket)
        print('送信完了')
      elif request[:4] == b'SHOT':
        #print('撮影要求受諾')
        params = struct.unpack(">II",request[4:12])
        GRID_X = params[0]
        GRID_Y = params[1]
        print(GRID_X,GRID_Y)
        if grid_flag_mask == 0b0 or None:
          #print('grid_flag_mask初期化')
          for i in range(GRID_X*GRID_Y):
            #print(i)
            grid_flag_mask = (1 << i) | grid_flag_mask
          print('grid_flag_mask:'+bin(grid_flag_mask))
        #latest_grid_flag = 0b0
        frame=shot(cap)
      else:
        pass
  except Exception as e:
    print(f'エラーが発生しました: {e}')
  finally:
    cap.close()
    client_socket.close()

if __name__ == '__main__':
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 5)
  server_socket.bind(('0.0.0.0', 8000))
  server_socket.listen(5)
  try:
    while True:
      print("接続待機中...")
      client_socket, client_address = server_socket.accept()
      # ソケット設定
      client_socket.settimeout(60)
      print(f'クライアント {client_address} と接続されました')
      thread = Thread(target = main,args=(client_socket,), daemon= True)
      thread.start()
  except KeyboardInterrupt:
    print("\nサーバーを停止します")
  finally:
    server_socket.close()

