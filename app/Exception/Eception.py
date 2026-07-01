class PDFParseError(Exception):
    """PDF文件解析失败"""
    pass
class InvalidJSON(Exception):
    """JSON格式错误(大模型返回数据异常)"""
    pass
class LLMCalledFailed(Exception):
    """大模型调用异常"""
    pass
class LLMParseError(Exception):
    """简历解析失败(代码逻辑或者语法错误)"""
    pass
class InsertException(Exception):
    """数据写入失败"""
    pass