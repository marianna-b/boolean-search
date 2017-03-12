from simple9 import Simple9

index = Simple9("lol")
index.add(0, 127)
index.add(0, 128)
index.add(0, 256)
index.add(0, 2421)
index.flush()
print index.get_next(0)
print index.get_next(0)
print index.get_next(0)
print index.get_next(0)
print index.get_next(0)