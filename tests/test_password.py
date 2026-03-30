from app.utils.password import hash_password, verify_password


def test_hash_password_returns_hash():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(hashed, password) is True


def test_verify_password_wrong():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(hashed, "wrongpassword") is False
