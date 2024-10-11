from datetime import datetime

def get_elapsed_time(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00min 00sec), without miliseconds"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.minute // 60}min {time_elapsed.second:02}sec"

def get_elapsed_time_ms(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00min 00sec 000ms), with miliseconds"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.minute // 60}min {time_elapsed.second:02}sec {time_elapsed.microsecond // 1000}ms"

def get_elapsed_time_smal(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00sec 000ms)"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.second:02}sec {time_elapsed.microsecond // 1000:03}ms"