class TestAuthApi:
    base_url = "/v1/auth"
    register_url = f"{base_url}/register"
    login_url = f"{base_url}/login"
    me_url = f"{base_url}/me"
    logout_url = f"{base_url}/logout"
    refresh_url = f"{base_url}/refresh"

    reserved_user_data = {"email": "user1@mail.com", "username": "user1", "password": "TestPass"}

    async def test_register(self, ac):
        response = await ac.post(self.register_url, json=self.reserved_user_data)
        assert response.status_code == 201

    async def test_register_error_duplicate_email(self, ac):
        response = await ac.post(
            self.register_url,
            json={
                "email": self.reserved_user_data["email"],
                "username": "UniqueName",
                "password": "TestPass",
            },
        )
        assert response.status_code == 409

    async def test_login(self, ac):
        response = await ac.post(
            self.login_url,
            json={
                "email": self.reserved_user_data["email"],
                "password": self.reserved_user_data["password"],
            },
        )
        assert response.status_code == 200

    async def test_login_error_invalid_email(self, ac):
        response = await ac.post(
            self.login_url,
            json={"email": "random@mail.com", "password": self.reserved_user_data["password"]},
        )
        assert response.status_code == 401

    async def test_login_error_invalid_password(self, ac):
        response = await ac.post(
            self.login_url,
            json={"email": self.reserved_user_data["email"], "password": "RandomPass"},
        )
        assert response.status_code == 401

    async def test_get_me(self, ac):
        login = await ac.post(
            self.login_url,
            json={
                "email": self.reserved_user_data["email"],
                "password": self.reserved_user_data["password"],
            },
        )
        assert login.status_code == 200

        response = await ac.get(
            self.me_url,
            cookies=login.cookies,
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["email"] == self.reserved_user_data["email"]
        assert response_data["username"] == self.reserved_user_data["username"]

    async def test_logout(self, ac):
        login = await ac.post(
            self.login_url,
            json={
                "email": self.reserved_user_data["email"],
                "password": self.reserved_user_data["password"],
            },
        )
        assert login.status_code == 200
        assert "access_token" in login.cookies
        assert "refresh_token" in login.cookies

        response = await ac.post(
            self.logout_url,
            cookies=login.cookies,
        )
        assert response.status_code == 200
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies

    async def test_refresh(self, ac):
        login = await ac.post(
            self.login_url,
            json={
                "email": self.reserved_user_data["email"],
                "password": self.reserved_user_data["password"],
            },
        )
        assert login.status_code == 200

        response = await ac.post(
            self.refresh_url,
            cookies={"refresh_token": login.cookies["refresh_token"]},
        )
        assert response.status_code == 200
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"] != login.cookies["access_token"]
        assert response.cookies["refresh_token"] != login.cookies["refresh_token"]

    async def test_refresh_error_different_fingerprints(self, ac):
        login = await ac.post(
            self.login_url,
            json={
                "email": self.reserved_user_data["email"],
                "password": self.reserved_user_data["password"],
            },
            headers={"user-agent": "Firefox/5.0"},
        )
        assert login.status_code == 200

        response = await ac.post(
            self.refresh_url,
            cookies={"refresh_token": login.cookies["refresh_token"]},
            headers={"user-agent": "Chrome/42"},
        )
        assert response.status_code == 401
