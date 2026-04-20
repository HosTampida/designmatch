import json

from sqlalchemy import UniqueConstraint

from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    project_description = db.Column(db.Text, nullable=True)

    designer_profile = db.relationship(
        "Designer",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Designer(db.Model):
    __tablename__ = "designers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=False, default="")
    portfolio_url = db.Column(db.String(255), nullable=False, default="")
    price_min = db.Column(db.Float, nullable=False, default=0)
    price_max = db.Column(db.Float, nullable=False, default=0)
    rating = db.Column(db.Float, nullable=False, default=0)

    user = db.relationship("User", back_populates="designer_profile")
    skills = db.relationship("DesignerSkill", back_populates="designer", cascade="all, delete-orphan")
    styles = db.relationship("DesignerStyle", back_populates="designer", cascade="all, delete-orphan")
    matches = db.relationship("Match", back_populates="designer", cascade="all, delete-orphan")

    def skill_ids(self):
        return [link.skill_id for link in self.skills]

    def style_ids(self):
        return [link.style_id for link in self.styles]

    def skill_names(self):
        return [link.skill.name for link in self.skills if link.skill]

    def style_names(self):
        return [link.style.name for link in self.styles if link.style]

    def to_card_dict(self):
        return {
            "designer_id": self.id,
            "name": self.user.name if self.user else "",
            "email": self.user.email if self.user else "",
            "bio": self.bio,
            "portfolio_url": self.portfolio_url,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "rating": round(float(self.rating or 0), 1),
            "skills": self.skill_names(),
            "styles": self.style_names(),
        }


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    designers = db.relationship("DesignerSkill", back_populates="skill", cascade="all, delete-orphan")


class Style(db.Model):
    __tablename__ = "styles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    designers = db.relationship("DesignerStyle", back_populates="style", cascade="all, delete-orphan")


class DesignerSkill(db.Model):
    __tablename__ = "designer_skills"
    __table_args__ = (UniqueConstraint("designer_id", "skill_id", name="uq_designer_skill"),)

    id = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey("designers.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    designer = db.relationship("Designer", back_populates="skills")
    skill = db.relationship("Skill", back_populates="designers")


class DesignerStyle(db.Model):
    __tablename__ = "designer_styles"
    __table_args__ = (UniqueConstraint("designer_id", "style_id", name="uq_designer_style"),)

    id = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey("designers.id"), nullable=False)
    style_id = db.Column(db.Integer, db.ForeignKey("styles.id"), nullable=False)

    designer = db.relationship("Designer", back_populates="styles")
    style = db.relationship("Style", back_populates="designers")


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    budget_min = db.Column(db.Float, nullable=False, default=0)
    budget_max = db.Column(db.Float, nullable=False, default=0)
    urgency = db.Column(db.String(20), nullable=False, default="medium")
    required_skill_ids = db.Column(db.Text, nullable=False, default="[]")
    preferred_style_ids = db.Column(db.Text, nullable=False, default="[]")

    matches = db.relationship("Match", back_populates="project", cascade="all, delete-orphan")

    def skill_ids(self):
        return _load_ids(self.required_skill_ids)

    def style_ids(self):
        return _load_ids(self.preferred_style_ids)

    def to_dict(self):
        return {
            "project_id": self.id,
            "title": self.title,
            "description": self.description,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "urgency": self.urgency,
            "skill_ids": self.skill_ids(),
            "style_ids": self.style_ids(),
        }


class Match(db.Model):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("project_id", "designer_id", name="uq_project_match"),)

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    designer_id = db.Column(db.Integer, db.ForeignKey("designers.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)

    project = db.relationship("Project", back_populates="matches")
    designer = db.relationship("Designer", back_populates="matches")


def _load_ids(raw_value):
    if not raw_value:
        return []

    try:
        parsed = json.loads(raw_value)
    except (TypeError, ValueError):
        return []

    clean_ids = []
    for value in parsed:
        try:
            clean_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    return clean_ids
