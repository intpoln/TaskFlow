class TestTasksApi:
    base_url = "/v1/tasks"

    async def create_project(self, client, title: str) -> dict:
        response = await client.post("/v1/projects", json={"title": title})
        assert response.status_code == 201
        return response.json()

    async def create_task(
        self, client, project_id: int, title: str, description: str = "Desc"
    ) -> dict:
        response = await client.post(
            self.base_url,
            json={"title": title, "description": description, "project_id": project_id},
        )
        assert response.status_code == 201
        return response.json()

    async def test_user_get_tasks(self, user_ac):
        response = await user_ac.get(self.base_url)
        response_data = response.json()
        assert response.status_code == 200
        assert isinstance(response_data, list)

    async def test_anonymous_get_tasks(self, ac):
        response = await ac.get(self.base_url)
        assert response.status_code == 401

    async def test_user_create_task(self, user_ac):
        project = await self.create_project(user_ac, "UserCreateTaskProject")
        task = await self.create_task(user_ac, project["id"], "UserCreateTask")
        assert "title" in task
        assert "id" in task
        assert task["project_id"] == project["id"]

    async def test_user_get_task(self, user_ac):
        project = await self.create_project(user_ac, "UserGetTaskProject")
        task = await self.create_task(user_ac, project["id"], "UserGetTask")

        response = await user_ac.get(f"{self.base_url}/{task['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == task["id"]
        assert response.json()["project_id"] == project["id"]

    async def test_user_get_tasks_different_user(self, superuser_ac, user_ac):
        project = await self.create_project(user_ac, "UserGetDifUserTaskProject")
        task = await self.create_task(user_ac, project["id"], "DifUserGetTask")

        response = await user_ac.get(f"self.base_url/{task['id']}")
        assert response.status_code == 404

    async def test_anonymous_get_user_task(self, ac, user_ac):
        project = await self.create_project(user_ac, "AnonGetUserTaskProject")
        task = await self.create_task(user_ac, project["id"], "AnonGetTask")

        response = await ac.get(f"{self.base_url}/{task['id']}")
        assert response.status_code == 401

    async def test_user_put_task(self, user_ac):
        project = await self.create_project(user_ac, "UserPutTaskProject")
        task = await self.create_task(user_ac, project["id"], "UserPutTask")

        data = {
            "title": "UserPutNewTask",
            "description": "UserPutNewTask",
            "status": "DONE",
            "project_id": project["id"],
        }
        response = await user_ac.put(f"{self.base_url}/{task['id']}", json=data)
        assert response.status_code == 200
        assert response.json()["title"] == data["title"]
        assert response.json()["id"] == task["id"]

    async def test_user_patch_task(self, user_ac):
        project = await self.create_project(user_ac, "UserPatchProject")
        task = await self.create_task(user_ac, project["id"], "UserPatchTask")

        data = {
            "title": "UserPatchNewTask",
            "description": "UserPatchNewTask",
            "status": "DONE",
            "project_id": project["id"],
        }
        response = await user_ac.patch(f"{self.base_url}/{task['id']}", json=data)
        assert response.status_code == 200
        assert response.json()["title"] == data["title"]
        assert response.json()["id"] == task["id"]

    async def test_user_delete_task(self, user_ac):
        project = await self.create_project(user_ac, "UserDeleteTaskProject")
        task = await self.create_task(user_ac, project["id"], "UserDeleteTask")

        delete_response = await user_ac.delete(f"{self.base_url}/{task['id']}")
        assert delete_response.status_code == 200
        assert "title" not in delete_response.json()
        assert delete_response.json()["status"] is True
