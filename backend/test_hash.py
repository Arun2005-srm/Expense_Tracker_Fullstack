from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "12345"
hashed = pwd_context.hash(password)

print("✅ Hashed:", hashed)
print("Verify result:", pwd_context.verify(password, hashed))
