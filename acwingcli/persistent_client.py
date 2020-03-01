from multiprocessing.connection import Client

address = ('localhost', 6001)
conn = Client(address, authkey=b'1234')
msg = conn.recv()
print(msg)

while True:
    msg = str(input())
    conn.send(msg)
    response = conn.recv()
    print(response)
# can also send arbitrary objects:
# conn.send(['a', 2.5, None, int, sum])
# conn.close()
 
