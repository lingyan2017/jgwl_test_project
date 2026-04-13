"""
AES 加密解密工具
"""
import base64
import json
import logging
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

logger = logging.getLogger("app.aes_cipher")


class AESCipher:
    """AES CBC 模式加密解密工具（使用 Hex 编码的 Key 和 IV）"""
    
    def __init__(self, key: str, iv: str):
        """
        初始化 AES 加密器，接收十六进制表示的密钥和 IV
        
        Args:
            key: AES 密钥（Hex 字符串，16/24/32 字节对应 32/48/64 个字符）
            iv: 初始化向量（Hex 字符串，16 字节对应 32 个字符）
        """
        self.key = self._hex_to_bytes(key)
        self.iv = self._hex_to_bytes(iv)
        
        logger.debug(f"AES Cipher 初始化成功 - Key长度: {len(self.key)} bytes, IV长度: {len(self.iv)} bytes")
    
    @staticmethod
    def _hex_to_bytes(hex_string: str) -> bytes:
        """
        将十六进制字符串转换为字节数组
        
        Args:
            hex_string: 十六进制字符串
            
        Returns:
            转换后的字节数组
        """
        if not hex_string:
            logger.error("Hex 字符串为空")
            raise ValueError("Hex 字符串不能为空")
        
        hex_string = hex_string.upper()
        length = len(hex_string) // 2
        result = bytearray(length)
        
        try:
            for i in range(length):
                pos = i * 2
                high = AESCipher._char_to_byte(hex_string[pos])
                low = AESCipher._char_to_byte(hex_string[pos + 1])
                result[i] = (high << 4) | low
            return bytes(result)
        except Exception as e:
            logger.error(f"十六进制转换错误: {e}")
            raise ValueError(f"无效的十六进制字符串: {hex_string}") from e
    
    @staticmethod
    def _char_to_byte(c: str) -> int:
        """
        将单个十六进制字符转换为对应的字节值
        
        Args:
            c: 十六进制字符
            
        Returns:
            对应的字节值
        """
        try:
            return int(c, 16)
        except ValueError as e:
            logger.error(f"字符转换错误: {c}")
            raise ValueError(f"无效的十六进制字符: {c}") from e
    
    def encrypt(self, data: str) -> str:
        """
        使用 AES/CBC/PKCS5Padding 加密数据，并进行 URL 编码
        
        Args:
            data: 待加密的字符串
            
        Returns:
            URL 编码的 Base64 加密数据
        """
        try:
            logger.debug(f"开始加密 - 原始数据长度: {len(data)} bytes")
            
            if not self.key or not self.iv:
                logger.error("加密密钥或 IV 为空")
                raise ValueError("加密密钥或 IV 为空")
            
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            padded_data = pad(data.encode('utf-8'), AES.block_size)
            logger.debug(f"数据填充后长度: {len(padded_data)} bytes")
            
            encrypted = cipher.encrypt(padded_data)
            encoded = base64.b64encode(encrypted).decode('utf-8')
            result = urllib.parse.quote(encoded)
            
            logger.debug(f"加密完成 - 加密数据长度: {len(result)} chars")
            return result
        except Exception as e:
            logger.error(f"AES 加密失败: {e}", exc_info=True)
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密 URL 编码的 Base64 字符串，返回原始明文
        
        Args:
            encrypted_data: URL 编码的 Base64 加密数据
            
        Returns:
            解密后的字符串
        """
        try:
            logger.debug(f"开始解密 - 加密数据长度: {len(encrypted_data)} chars")
            
            # 检查输入参数
            if not encrypted_data:
                logger.warning("解密输入数据为空字符串")
                return ""
            
            if not self.key or not self.iv:
                logger.error("解密密钥或 IV 为空")
                return ""
            
            # URL 解码
            decoded_data = urllib.parse.unquote(encrypted_data)
            
            # 检查解码后是否为空
            if not decoded_data:
                logger.warning("URL 解码后数据为空")
                return ""
            
            # Base64 解码
            decrypted_bytes = base64.b64decode(decoded_data)
            logger.debug(f"Base64 解码后长度: {len(decrypted_bytes)} bytes")
            
            # 检查 Base64 解码后是否为空
            if not decrypted_bytes:
                logger.warning("Base64 解码后数据为空")
                return ""
            
            # AES 解密
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            original = unpad(cipher.decrypt(decrypted_bytes), AES.block_size)
            result = original.decode('utf-8')
            
            logger.debug(f"解密完成 - 解密数据长度: {len(result)} bytes")
            return result
        except ValueError as e:
            if "Zero-length input cannot be unpadded" in str(e):
                logger.warning(f"解密数据为空或格式错误: {encrypted_data[:50]}...")
            else:
                logger.error(f"解密 ValueError: {e}")
            return ""
        except Exception as e:
            logger.error(f"AES 解密失败: {e}", exc_info=True)
            raise
    
    def encrypt_json(self, data: dict) -> str:
        """
        加密 JSON 数据
        
        Args:
            data: 待加密的字典
            
        Returns:
            URL 编码的 Base64 加密数据
        """
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            logger.info(f"加密 JSON 数据 - Keys: {list(data.keys())}, JSON长度: {len(json_str)} bytes")
            result = self.encrypt(json_str)
            logger.info(f"JSON 加密成功 - 加密后长度: {len(result)} chars")
            return result
        except Exception as e:
            logger.error(f"JSON 加密失败: {e}", exc_info=True)
            raise
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """
        解密 JSON 数据
        
        Args:
            encrypted_data: URL 编码的 Base64 加密数据
            
        Returns:
            解密后的字典
        """
        try:
            logger.info(f"开始解密 JSON - 加密数据长度: {len(encrypted_data)} chars")
            json_str = self.decrypt(encrypted_data)
            
            if not json_str:
                logger.warning("解密结果为空")
                return {}
            
            result = json.loads(json_str)
            logger.info(f"JSON 解密成功 - Keys: {list(result.keys())}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 解密后的内容: {json_str[:200]}...", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"JSON 解密失败: {e}", exc_info=True)
            raise
