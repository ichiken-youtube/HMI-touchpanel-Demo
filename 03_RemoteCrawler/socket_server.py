import cv2
import socket
import struct

PACKET_SIZE_LIMIT = 800
FRAME_WIDTH =120
FRAME_HEIGHT =90
GRID_X = 0
GRID_Y = 0
grid = 3

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


def send_frame(frame, client_socket):
  image_bytes = frame.tobytes()
  size = len(image_bytes)
  grid = 0
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
  ret,frame = cap.read()
  if not ret:
    print("フレームをキャプチャできませんでした。")
    cap.release()
    exit()
  return frame

def main():
  # Webカメラのキャプチャ
  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("カメラを開くことができませんでした。")
    exit()
  # ソケット設定
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind(('0.0.0.0', 8000))
  server_socket.listen(1)
  print('サーバーはポート8000で待機中...')
  
  client_socket, client_address = server_socket.accept()
  print(f'クライアント {client_address} と接続されました')
  client_socket.settimeout(300)
  frame=shot(cap)

  try:
    while True:
      # クライアントからの送信要求を待つ
      print('送信要求待ち')
      request = client_socket.recv(12)
      print(request)
      if request[:4] == b'RQST':
        grid = struct.unpack(">I",request[4:8])[0]

        #resized_frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        resized_frame = split_image(GRID_X, GRID_Y, grid, frame)

        # OpenCVのBGRからRGBに変換
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2BGRA)
        # フレームを送信
        send_frame(rgb_frame, client_socket)
      elif request[:4] == b'SHOT':
        print('撮影要求受諾')
        params = struct.unpack(">II",request[4:12])
        GRID_X = params[0]
        GRID_Y = params[1]
        print(GRID_X,GRID_Y)
        frame=shot(cap)
  except Exception as e:
    print(f'エラーが発生しました: {e}')
  finally:
    cap.release()
    client_socket.close()
    server_socket.close()

if __name__ == '__main__':
  main()
