from src.application.interfaces.repository import AbstractPitchRepository


class FakePitchRepository(AbstractPitchRepository):
    def __init__(self):
        self.pitches_by_creator = {}

    async def find_by_pitch(self, pitch_creator: str):
        return self.pitches_by_creator.get(pitch_creator)
    async def create_pitch(self, pitch):
        self.pitches_by_creator[pitch.creator] = pitch
        return pitch

    def seed(self, creator_id: str, pitch):
        self.pitches_by_creator[creator_id] = pitch