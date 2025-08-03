import serial
import json
import time

class CommBotClient:
  def __init__(self, port, baudrate=115200, heartbeat_interval=1.0):
    self.ser = serial.Serial(port, baudrate, timeout=0.1)
    self.heartbeat_interval = heartbeat_interval
    self.last_master_heartbeat = time.time()
    self.last_slave_heartbeat = time.time()
    self.max_heartbeat_loss_time = 10
    self.connected = False
    self.callbacks = {}

  def log(self, data, type="log"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    colors = {
      "log": "\033[0m",
      "info": "\033[94m",
      "warn": "\033[93m",
      "error": "\033[91m",
    }

    color = colors.get(type, "\033[0m")

    print(f"[{timestamp}] {color}{data}\033[0m")

  def publisher(self, topic):
    return lambda data: self.publish(topic, data)

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
      if msg["handshake"] == "slave":
        self.connected = True
        payload = {
          "handshake": "master"
        }
        self._publish(payload)

        self.last_slave_heartbeat = time.time()
        self.log("Handshake done!", "info")
      return

    if "heartbeat" in msg:
      if msg["heartbeat"] == "slave":
        self.last_slave_heartbeat = time.time()
      return

    if "log" in msg:
      self.log(msg['log'])
      return

    if not self.connected:
      return

    if "topic" in msg:
      topic = msg["topic"]
      if topic in self.callbacks:
        self.callbacks[topic](msg)

  def spin_once(self):
    line = self.ser.readline().decode().strip()
    if line:
      try:
        msg = json.loads(line)
        self._handle_message(msg)
      except json.JSONDecodeError:
        self.log(f"{line}", "error")

    if time.time() - self.last_master_heartbeat >= self.heartbeat_interval:
      self._publish({"heartbeat": "master"})
      self.last_master_heartbeat = time.time()

    now = time.time()
    if self.connected and now - self.last_slave_heartbeat >= self.max_heartbeat_loss_time:
      self.connected = False
      self.last_slave_heartbeat = time.time()
      self.log("Handshake loss!", "warn")

  def spin(self, delay=0.01):
    while True:
      self.spin_once()
      time.sleep(delay)
