import  hashlib

def Encode(password):
    # 用md5加密的方式（md5加密后无法解密），创建一个md5的对象
    E = hashlib.md5()
    # 转换成bytes函数，要加上encoding='utf-8'
    E.update(bytes(password, encoding='utf-8'))
    # 16进制格式的加密后的字符串
    en_password=E.hexdigest()
    return en_password