def timestr(tick) -> str:
	millisecond = int((tick - int(tick)) * 1000)
	tick = int(tick)
	second = tick % 60
	tick //= 60
	minute = tick % 60
	hour = tick // 60
	return f'{hour}:{minute}:{second} (+{millisecond}ms)'