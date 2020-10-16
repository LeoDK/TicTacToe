import server
s = server.Server()
try:
    s.startGame()

except Exception as e:
    s.quit()
    raise e

except KeyboardInterrupt:
    print("Aborting")
    s.quit()
s.quit()
