from collections.abc import Callable
import sys
from typing import Generic, TypeVar


MT = TypeVar('MT')
RT = TypeVar('RT')

class classproperty(Generic[MT, RT]):
	"""
	之前写的小玩意，太好用了，搬过来。

	简单来说就是允许一个类函数被以属性的方式调用，并且你可以从类本身调用，也可以从类的任何实例进行调用。

	缺点是不支持set/delete，但多数情况下这类属性本来也不应该能被修改。
	"""
	def __init__(self, fget: Callable[[type[MT]], RT], /) -> None:
		self.fget = classmethod(fget)

	def __get__(self, instance: MT | None, objtype: type[MT]) -> RT:
		
		if instance is not None:
			if sys.version_info >= (3, 10):
				attr_name = self.fget.__name__
			else:
				attr_name = self.fget.__func__.__name__ # pyright: ignore[reportFunctionMemberAccess]
		return self.fget.__get__(instance, objtype)()