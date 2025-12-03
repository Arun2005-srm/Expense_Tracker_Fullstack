from utils import verify_password
hashed = "$2b$12$4lb/F5b72xOHFgW6zcOGDeXzI4V/6h5xiIJelwgcAG8Z5o/Y3Ff3a"
print(verify_password("Arun2005", hashed))
