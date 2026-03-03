class Counter:
    def __init__(self, func):
        self.count = 0
        self.func = func
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)
    