import hashlib
import hmac
import os
import base64


class PasswordHasher:
    # 算法标识,便于将来切换算法或升级迭代次数
    ALGO = "pbkdf2_sha256"
    # 迭代次数(越高越慢越安全,推荐 >= 200000,可按性能调整)
    ITERATIONS = 200_000
    # 派生密钥长度(字节)
    KEY_LEN = 32
    # 盐长度(字节)
    SALT_LEN = 16

    @staticmethod
    def hash(password: str) -> str:
        """对明文密码进行哈希,返回带算法/迭代次数/盐/摘要的可解码字符串"""
        # 随机生成 salt
        salt = os.urandom(PasswordHasher.SALT_LEN)
        # 使用 PBKDF2-HMAC-SHA256 派生密钥
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PasswordHasher.ITERATIONS,
            dklen=PasswordHasher.KEY_LEN,
        )
        # 组合: algo$iterations$base64(salt)$base64(hash)
        salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
        hash_b64 = base64.urlsafe_b64encode(derived).decode("ascii")
        return f"{PasswordHasher.ALGO}${PasswordHasher.ITERATIONS}${salt_b64}${hash_b64}"

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """校验明文密码与已哈希密码是否匹配"""
        try:
            algo, iterations_str, salt_b64, hash_b64 = hashed_password.split("$")
            if algo != PasswordHasher.ALGO:
                return False
            iterations = int(iterations_str)
            salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
            stored_hash = base64.urlsafe_b64decode(hash_b64.encode("ascii"))
            # 用同样的参数重新派生
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(stored_hash),
            )
            # 常数时间比较,防止时序攻击
            return hmac.compare_digest(derived, stored_hash)
        except (ValueError, AttributeError, TypeError):
            return False
