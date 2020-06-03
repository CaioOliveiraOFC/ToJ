def percentage(percent, whole, remainder=True):
    if remainder:
        operation = (percent * whole) / 100
    else:
        operation = (percent * whole) // 100
    return operation
