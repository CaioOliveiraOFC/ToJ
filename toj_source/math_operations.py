# this module is dedicated to the creation of math functions 
def percentage(percent, whole, remainder=True):
    # Calculate the percentage of a whole number
    if remainder:
        operation = (percent * whole) / 100
    else:
        operation = (percent * whole) // 100
    return operation

if __name__ == "__main__":
    pass 
