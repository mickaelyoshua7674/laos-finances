from sqlalchemy import text
import pytest

class TestAPI:

    async def remove_user(self, conn, register_user):
        await conn.execute(text(f"DELETE FROM users WHERE email={register_user["email"]}"))
        await conn.commit()

    pytest.mark.asyncio
    @pytest.mark.dependency()
    async def test_register(self, client, register_user):
        response = await client.post("/register", json=register_user)

        assert response.status_code == 200
        assert response.json()["email"] == register_user["email"]

        self.remove_user()
    
    @pytest.mark.asyncio
    @pytest.mark.dependency(depends=["test_register"])
    async def test_login(self, client, register_user, login_user):
        res_register = await client.post("/register", json=register_user)
        res_login = await client.post("/login", json=login_user)

        assert res_login.status_code == 200
        assert res_register == res_login

        self.remove_user()
