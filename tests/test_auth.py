from datamint.services.auth import hash_password, verify_password


def test_password_hash_verification():
    password_hash = hash_password("super-secret-password")
    assert password_hash != "super-secret-password"
    assert verify_password("super-secret-password", password_hash)
    assert not verify_password("wrong-password", password_hash)
