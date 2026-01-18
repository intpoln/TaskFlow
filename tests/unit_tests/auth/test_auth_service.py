from src.services.auth import AuthService


class TestAuthService:
    def test_hash_password_creates_different_hashes(self):
        password = "SecretPass123"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        assert hash1 != hash2
        assert AuthService.verify_password(password, hash1)
        assert AuthService.verify_password(password, hash2)

    def test_verify_password_incorrect(self):
        hashed = AuthService.hash_password("CorrectPassword")
        assert not AuthService.verify_password("IncorrectPassword", hashed)

    def test_create_and_decode_access_token(self):
        data = {"user_id": 42}
        token = AuthService.create_access_token(data)
        assert token
        assert isinstance(token, str)

        decoded_token = AuthService.decode_access_token(token)
        assert decoded_token
        assert isinstance(decoded_token, dict)
        assert decoded_token["user_id"] == 42

    def test_decode_access_token_invalid_type(self):
        invalid_token = "invalid_token"
        decoded_invalid_token = AuthService.decode_access_token(invalid_token)
        assert decoded_invalid_token is None

    def test_create_and_decode_refresh_token(self):
        data = {"user_id": 42, "fingerprint": "Mozilla/5.0"}
        token = AuthService.create_refresh_token(data)
        assert token
        assert isinstance(token, str)

        decoded_token = AuthService.decode_refresh_token(token)
        assert decoded_token
        assert isinstance(decoded_token, dict)
        assert decoded_token["user_id"] == data["user_id"]
        assert decoded_token["fingerprint"] == data["fingerprint"]

    def test_decode_refresh_token_invalid_type(self):
        invalid_token = "invalid_token"
        decoded_invalid_token = AuthService.decode_refresh_token(invalid_token)
        assert decoded_invalid_token is None
