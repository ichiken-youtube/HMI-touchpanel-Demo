import cv2
import socket
import struct
from threading import Thread
from picamera2 import Picamera2
import motor

PACKET_SIZE_LIMIT = 800
FRAME_WIDTH =120
FRAME_HEIGHT =90
GRID_X = 1
GRID_Y = 1
REQUEST_PACKET_SIZE = 12
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
  print('size:'+str(size))
  # フレームデータを送信
  for i in range(0, size, PACKET_SIZE_LIMIT):
    chunk = image_bytes[i:min(i + PACKET_SIZE_LIMIT,size)]
    client_socket.sendall(chunk)

def shot(cap):
  frame = cv2.rotate(cap.capture_array(), cv2.ROTATE_180)
  #ret,frame = cap.read()
  #if not ret:
  if len(frame)==0:
    raise Exception("フレームをキャプチャできませんでした。")
    #exit()
  return frame

def main(client_socket,cap):
  global grid_flag_mask
  global latest_grid_flag
  
  # ソケット設定
  client_socket.settimeout(60)
  # Webカメラのキャプチャ
  '''cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("カメラを開くことができませんでした。")
    exit()'''
  #cap.set_controls({'AfMode': controls.AfModeEnum.Continuous})
  frame=shot(cap)

  try:
    while True:
      # クライアントからのrequestを待つ
      request = b''
      params=b''
      while len(request) < REQUEST_PACKET_SIZE:
        request += client_socket.recv(min(REQUEST_PACKET_SIZE-len(request), REQUEST_PACKET_SIZE))

      if len(request) != REQUEST_PACKET_SIZE :
        continue

      print(request)
      params = struct.unpack(">II",request[4:12])
      if request[:4] == b'RQST':
        grid = params[0]
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
        GRID_X = params[0]
        GRID_Y = params[1]
        print(GRID_X,GRID_Y)
        if grid_flag_mask == 0b0 or None:
          #print('grid_flag_mask初期化')
          for i in range(GRID_X*GRID_Y):
            grid_flag_mask = (1 << i) | grid_flag_mask
          print('grid_flag_mask:'+bin(grid_flag_mask))
        frame=shot(cap)

      elif request[:4] == b'COMM':
        motor.motor(params[0],params[1])

      elif request[:4] == b'PING':
        client_socket.sendall(b'PONG')
        
      else:
        pass
  except Exception as e:
    print(f'エラーが発生しました: {e}')
  finally:
    client_socket.close()

if __name__ == '__main__':
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 5)
  server_socket.bind(('0.0.0.0', 8000))
  server_socket.listen(5)
  
  cap = Picamera2()
  cap.start()

  try:
    while True:
      print("接続待機中...")
      client_socket, client_address = server_socket.accept()
      print(f'クライアント {client_address} と接続されました')
      thread = Thread(target = main,args=(client_socket,cap), daemon= True)
      thread.start()
  except KeyboardInterrupt:
    print("\nサーバーを停止します")
    cap.close()
  finally:
    server_socket.close()

