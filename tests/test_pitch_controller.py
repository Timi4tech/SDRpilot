from tests.conftest import client, fake_pitch_repo

class FakePitch:
    def __init__(self, name, email, company_name, profession, pitch):
        self.name = name
        self.email = email
        self.company_name = company_name
        self.profession = profession
        self.pitch = pitch



async def test_get_pitch_success(client, fake_pitch_repo):
    fake_pitch_repo.seed("fake-user-1", FakePitch(
        name="Timi",
        email="timi@leadsengineops.com",
        company_name="LeadsEngineOps",
        profession="Founder",
        pitch="We automate lead gen for agencies.",
    ))

    response = await client.get("/protected/pitch/me")

    assert response.status_code == 200
    assert response.json()["Pitch_name"] == "Timi"


