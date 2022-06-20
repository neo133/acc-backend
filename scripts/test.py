import time

count = 0
while count < 5:
    print(count)
    try:
        count += 1
        time.sleep(1)
    except:
        continue
