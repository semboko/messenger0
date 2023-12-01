from threading import Thread

def thread1():
    for i in range(40):
        print("Hello 1")
        

def thread2():
    for i in range(40):
        print("Hello 2")
        
t1 = Thread(target=thread1)
t2 = Thread(target=thread2)
t1.start()
t2.start()