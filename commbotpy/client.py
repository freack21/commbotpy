import serial
import json
import time

class CommBotClient:
  def __init__(self, port, baudrate=115200, heartbeat_interval=1.0):
    self.ser = serial.Serial(port, baudrate, timeout=0.1)
    self.heartbeat_interval = heartbeat_interval
    self.last_heartbeat = time.time()
    self.connected = False
    self.callbacks = {}
    self._handshake_sent = False
    self._last_hello = 0

  def _publish(self, data):
    self.ser.write((json.dumps(data) + "\n").encode())

  def publish(self, topic, payload):
    if not isinstance(payload, dict):
      payload = {"data": payload}
    payload["topic"] = topic
    payload["id"] = str(int(time.time() * 1000))
    self._publish(payload)

  def on(self, topic, callback):
    self.callbacks[topic] = callback

  def _handle_message(self, msg):
    if "handshake" in msg:
      if msg["handshake"] == "hello_ack":
        self.connected = True
        print("[CommBotPy] Handshake done!")
      return

    if "heartbeat" in msg:
      return

    if "topic" in msg:
      topic = msg["topic"]
      if topic in self.callbacks:
        self.callbacks[topic](msg)

    if "id" in msg:
      self._publish({"ack": msg["id"]})

  def spin_once(self):
    line = self.ser.readline().decode().strip()
    if line:
      try:
        msg = json.loads(line)
        self._handle_message(msg)
      except json.JSONDecodeError:
        print("[CommBotPy] JSON Error:", line)

    if time.time() - self.last_heartbeat >= self.heartbeat_interval:
      self._publish({"heartbeat": True})
      self.last_heartbeat = time.time()

  def spin(self, delay=0.01):
    while True:
      self.spin_once()
      time.sleep(delay)
