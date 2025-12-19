x = 10          # Global x = 10

def outer():
    x = 20      # Local x = 20
    
    def inner():
        global x
        x = 30  # Should modify global x to 30
        print(x)  # Should print 30
    
    inner()
    print(x)    # Prints 20 (local unchanged)

outer()
print(x)        # Should print 30 (global changed)
