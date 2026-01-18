class TestProjectsApi:
    base_url = "/v1/projects"

    async def test_user_get_projects(self, user_ac):
        response = await user_ac.get(self.base_url)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_anonymous_get_projects(self, ac):
        response = await ac.get(self.base_url)
        assert response.status_code == 401

    async def test_user_post_project(self, user_ac):
        data = {"title": "New Project", "description": "Test description"}
        response = await user_ac.post(self.base_url, json=data)
        assert response.status_code == 201
        assert response.json()["title"] == data["title"]
        assert "id" in response.json()
        assert "owner_id" in response.json()

    async def test_user_post_project_duplicate_title(self, user_ac):
        data = {"title": "DuplicateProject"}
        response1 = await user_ac.post(self.base_url, json=data)
        assert response1.status_code == 201

        response2 = await user_ac.post(self.base_url, json=data)
        assert response2.status_code == 409

    async def test_anonymous_post_project(self, ac):
        data = {"title": "Anonymous Project"}
        response = await ac.post(self.base_url, json=data)
        assert response.status_code == 401

    async def test_user_get_project(self, user_ac):
        create_response = await user_ac.post(self.base_url, json={"title": "GetProject"})
        project_id = create_response.json()["id"]

        response = await user_ac.get(f"{self.base_url}/{project_id}")
        assert response.status_code == 200
        assert response.json()["id"] == project_id

    async def test_user_get_nonexistent_project(self, user_ac):
        response = await user_ac.get(f"{self.base_url}/4242")
        assert response.status_code == 404

    async def test_anonymous_get_project(self, ac):
        response = await ac.get(f"{self.base_url}/1")
        assert response.status_code == 401

    async def test_user_patch_project(self, user_ac):
        create_data = {"title": "PatchProject", "description": "Old description"}
        create_response = await user_ac.post(
            self.base_url, json=create_data
        )
        project_id = create_response.json()["id"]

        patch_data = {"description": "New description"}
        response = await user_ac.patch(f"{self.base_url}/{project_id}", json=patch_data)
        assert response.status_code == 200
        assert response.json()["description"] == patch_data["description"]
        assert response.json()["title"] == create_data["title"]

    async def test_anonymous_patch_project(self, ac):
        response = await ac.patch(f"{self.base_url}/1", json={"title": "Hacked"})
        assert response.status_code == 401

    async def test_user_put_project(self, user_ac):
        create_response = await user_ac.post(
            self.base_url, json={"title": "PutProject", "description": "Old"}
        )
        project_id = create_response.json()["id"]

        put_data = {"title": "PutProjectUpdated", "description": "New"}
        response = await user_ac.put(f"{self.base_url}/{project_id}", json=put_data)
        assert response.status_code == 200
        assert response.json()["title"] == put_data["title"]
        assert response.json()["description"] == put_data["description"]

    async def test_user_delete_project(self, user_ac):
        create_response = await user_ac.post(self.base_url, json={"title": "DeleteProject"})
        project_id = create_response.json()["id"]

        response = await user_ac.delete(f"{self.base_url}/{project_id}")
        assert response.status_code == 200
        assert response.json()["status"] is True

        get_response = await user_ac.get(f"{self.base_url}/{project_id}")
        assert get_response.status_code == 404

    async def test_user_delete_nonexistent_project(self, user_ac):
        response = await user_ac.delete(f"{self.base_url}/4242")
        assert response.status_code == 404

    async def test_anonymous_delete_project(self, ac):
        response = await ac.delete(f"{self.base_url}/1")
        assert response.status_code == 401

    async def test_user_cannot_see_other_user_project(self, user_ac, superuser_ac):
        create_response = await superuser_ac.post(
            self.base_url, json={"title": "Superuser Private Project"}
        )
        project_id = create_response.json()["id"]

        response = await user_ac.get(f"{self.base_url}/{project_id}")
        assert response.status_code == 404
