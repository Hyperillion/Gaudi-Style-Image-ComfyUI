runningState = True
count = 0
while runningState:
    print(count)
    count += 1
    if count == 100:
        runningState = False