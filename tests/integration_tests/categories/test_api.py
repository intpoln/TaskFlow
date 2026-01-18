class TestCategoriesApi:
    base_url = "/v1/categories"

    async def test_user_get_categories(self, user_ac):
        response = await user_ac.get(self.base_url)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    async def test_anonymous_get_categories(self, ac):
        response = await ac.get(self.base_url)
        assert response.status_code == 401

    async def test_superuser_post_category(self, superuser_ac):
        categories = await superuser_ac.get(self.base_url)
        categories_len = len(categories.json())

        data = {"title": "TestCreateCategory"}
        response = await superuser_ac.post(self.base_url, json={"title": "TestCreateCategory"})
        assert response.status_code == 201
        assert isinstance(response.json(), dict)
        assert "title" in response.json()
        assert response.json()["title"] == data["title"]

        categories = await superuser_ac.get(self.base_url)
        categories_new_len = len(categories.json())
        assert categories_len < categories_new_len

    async def test_user_post_category(self, user_ac):
        categories = await user_ac.get(self.base_url)
        categories_len = len(categories.json())

        response = await user_ac.post(self.base_url, json={"title": "UserCategory"})
        assert response.status_code == 403
        assert "title" not in response.json()

        categories = await user_ac.get(self.base_url)
        categories_new_len = len(categories.json())
        assert categories_len == categories_new_len

    async def test_anonymous_post_category(self, ac):
        categories = await ac.get(self.base_url)
        categories_len = len(categories.json())

        response = await ac.post(self.base_url, json={"title": "AnonymousCategory"})
        assert response.status_code == 401
        assert "title" not in response.json()

        categories = await ac.get(self.base_url)
        categories_new_len = len(categories.json())
        assert categories_len == categories_new_len

    async def test_user_get_category(self, user_ac):
        response = await user_ac.get(f"{self.base_url}/1")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "title" in response.json()
        assert "id" in response.json()

    async def test_user_get_nonexistent_category(self, user_ac):
        response = await user_ac.get(f"{self.base_url}/4242")
        assert response.status_code == 404
        assert "title" not in response.json()

    async def test_anonymous_get_category(self, ac):
        response = await ac.get(f"{self.base_url}/1")
        assert response.status_code == 401
        assert "title" not in response.json()

    async def test_superuser_patch_category(self, superuser_ac):
        create_response = await superuser_ac.post(
            f"{self.base_url}",
            json={"title": "TestPatchCategory"},
        )
        assert create_response.status_code == 201
        category_id = create_response.json()["id"]

        data = {"title": "SuperuserPatchCategory"}
        response = await superuser_ac.patch(f"{self.base_url}/{category_id}", json=data)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "title" in response.json()
        assert response.json()["title"] == data["title"]

    async def test_user_patch_category(self, user_ac):
        response = await user_ac.patch(f"{self.base_url}/1", json={"title": "UserPatchCategory"})
        assert response.status_code == 403
        assert isinstance(response.json(), dict)
        assert "title" not in response.json()

    async def test_anonymous_patch_category(self, ac):
        response = await ac.patch(f"{self.base_url}/1", json={"title": "AnonymousPatchCategory"})
        assert response.status_code == 401
        assert "title" not in response.json()

    async def test_superuser_delete_category(self, superuser_ac):
        response_post = await superuser_ac.post(
            f"{self.base_url}", json={"title": "SuperuserDeleteCategory"}
        )
        assert response_post.status_code == 201
        response_data = response_post.json()
        category_id = response_data["id"]

        categories = await superuser_ac.get(self.base_url)
        categories_len = len(categories.json())

        response_delete = await superuser_ac.delete(f"{self.base_url}/{category_id}")
        assert response_delete.status_code == 200

        categories = await superuser_ac.get(f"{self.base_url}")
        categories_new_len = len(categories.json())
        assert categories_new_len < categories_len

    async def test_user_delete_category(self, user_ac, superuser_ac):
        response_post = await superuser_ac.post(
            f"{self.base_url}", json={"title": "UserDeleteCategory"}
        )
        assert response_post.status_code == 201
        response_data = response_post.json()
        category_id = response_data["id"]

        categories = await user_ac.get(self.base_url)
        categories_len = len(categories.json())

        response_delete = await user_ac.delete(f"{self.base_url}/{category_id}")
        assert response_delete.status_code == 403

        categories = await user_ac.get(f"{self.base_url}")
        categories_new_len = len(categories.json())
        assert categories_new_len == categories_len

    async def test_anonymous_delete_category(self, ac, superuser_ac):
        response_post = await superuser_ac.post(
            f"{self.base_url}", json={"title": "AnonymousDeleteCategory"}
        )
        assert response_post.status_code == 201
        response_data = response_post.json()
        category_id = response_data["id"]

        categories = await superuser_ac.get(self.base_url)
        categories_len = len(categories.json())

        response_delete = await ac.delete(f"{self.base_url}/{category_id}")
        assert response_delete.status_code == 401

        categories = await superuser_ac.get(f"{self.base_url}")
        categories_new_len = len(categories.json())
        assert categories_new_len == categories_len
