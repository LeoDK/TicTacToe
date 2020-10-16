import client

c2 = client.Client('Client2', port=50003)

try:
    c2.startGame()

except Exception as e:
    c2.quit()
    raise e

except KeyboardInterrupt:
    print("Aborting...")
    c2.quit()

c2.quit()
