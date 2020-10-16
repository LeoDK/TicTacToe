import client

c1 = client.Client('Client1')

try:
    c1.startGame()

except Exception as e:
    c1.quit()
    raise e

except KeyboardInterrupt:
    print("Aborting")
    c1.quit()

c1.quit()
