# Абстрактный класс python
# __next__ реализация генераторов python
# 

class ISource:
    def __init__(path: str):
        path = path,
    __next__: str
        

class PhoneReader:
    pass

# вместо AbstractUnqiueSource может быть или Google, или файл
# phone_reader = PhoneReader(AbstractUnqiueSource)
# 
# for phone in phone_reader:
#   do_phone()

__all__ = [
    'PhoneReader'
]
