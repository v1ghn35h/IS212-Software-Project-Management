from database import db

class Skill(db.Model):
    __tablename__ = 'skills'

    skill_name = db.Column(db.String(50), primary_key=True)
    
    def __init__(self, skill_name):
        self.skill_name = skill_name

    def json(self):
        return {
            'skill_name': self.skill_name
        }