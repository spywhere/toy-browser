import socket
import ssl

useragent = "toy-browser/0.1.0"

def request(url):
  scheme, url = url.split("://", 1)
  host, path = url.split("/", 1)
  path = "/" + path

  assert scheme in ["http", "https"], "Unknow scheme {}".format(scheme)
  port = 80

  s = socket.socket(
    family=socket.AF_INET,
    type=socket.SOCK_STREAM,
    proto=socket.IPPROTO_TCP
  )

  if scheme == "https":
    port = 443
    ctx = ssl.create_default_context()
    s = ctx.wrap_socket(s, server_hostname=host)

  s.connect((host, port))
  s.send(
      "GET {} HTTP/1.1\r\nHost: {}\r\nUser-Agent: {}\r\n\r\n".format(
        path, host, useragent
      ).encode("utf8")
  )

  response = s.makefile("r", encoding="utf8", newline="\r\n")

  statusline = response.readline()
  version, status, explanation = statusline.split(" ", 2)
  assert status == "200", "{}: {}".format(status, explanation)

  headers = {}
  while True:
    line = response.readline()
    if line == "\r\n":
      break
    header, value = line.split(":", 1)
    headers[header.lower()] = value.strip()

  body = response.read()
  s.close()

  return headers, body

def show(body):
  in_angle = False
  for c in body:
    if c == "<":
      in_angle = True
    elif c == ">":
      in_angle = False
    elif not in_angle:
      print(c, end="")

def load(url):
  headers, body = request(url)
  show(body)

if __name__ == "__main__":
  import sys
  load(sys.argv[1])

