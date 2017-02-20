import socket
import ssl


def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        u = url

    # 检查路径
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 默认端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    port = port_dict[protocol]

    # 检查端口
    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    return protocol, host, port, path


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    size = 1024
    while True:
        r = s.recv(size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(r):
    """
    解析 response 返回 (status_code headers body)
    status_code 是 int
    headers 是 dict
    body 是 str
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)
    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)
    s = socket_by_protocol(protocol)
    s.connect((host, port))
    request = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))
    response = response_by_socket(s)
    r = response.decode(encoding)
    status_code, headers, body = parsed_response(r)
    if status_code == 301:
        url = headers['Location']
        get(url)
    return status_code, headers, body


def main():
    url = 'https://movie.douban.com/top250'
    status_code, headers, body = get(url)
    print(status_code, headers, body)


if __name__ == '__main__':
    main()
