from app import db
import datetime



class AboutPage(db.Model):
    __tablename__ = 'about_page'
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(255))
    hero_description = db.Column(db.Text)
    hero_image = db.Column(db.String(255))

    operations = db.relationship("Operation", backref="about_page", lazy=True, cascade="all, delete-orphan")
    focus_areas = db.relationship("FocusArea", backref="about_page", lazy=True, cascade="all, delete-orphan")
    core_pillars = db.relationship("CorePillar", backref="about_page", lazy=True, cascade="all, delete-orphan")
    team_members = db.relationship("TeamMember", backref="about_page", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "hero_title": self.hero_title,
            "hero_description": self.hero_description,
            "hero_image": self.hero_image,
            "operations": [op.to_dict() for op in self.operations],
            "focus_areas": [fa.to_dict() for fa in self.focus_areas],
            "core_pillars": [cp.to_dict() for cp in self.core_pillars],
            "team_members": [tm.to_dict() for tm in self.team_members],
        }


class Operation(db.Model):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    about_page_id = db.Column(db.Integer, db.ForeignKey('about_page.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.image,
            "about_page_id": self.about_page_id,
        }


class FocusArea(db.Model):
    __tablename__ = 'focus_areas'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    about_page_id = db.Column(db.Integer, db.ForeignKey('about_page.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "about_page_id": self.about_page_id,
        }


class CorePillar(db.Model):
    __tablename__ = 'core_pillars'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))
    about_page_id = db.Column(db.Integer, db.ForeignKey('about_page.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "about_page_id": self.about_page_id,
        }


class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    image = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    about_page_id = db.Column(db.Integer, db.ForeignKey('about_page.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "image": self.image,
            "facebook": self.facebook,
            "linkedin": self.linkedin,
            "about_page_id": self.about_page_id,
        }





class AdmissionApplication(db.Model):
    __tablename__ = 'admission_applications'

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    parent_email = db.Column(db.String(120), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    grade_applied = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Enrolled
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    rejection_reason = db.Column(db.Text, nullable=True)
    mgnt_student_id = db.Column(db.Integer, nullable=True)
    mgnt_admission_number = db.Column(db.String(50), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<AdmissionApplication {self.student_name} ({self.grade_applied})>"

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d'),
            'parent_name': self.parent_name,
            'parent_email': self.parent_email,
            'contact_number': self.contact_number,
            'grade_applied': self.grade_applied,
            'status': self.status,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            'rejection_reason': self.rejection_reason,
            'mgnt_student_id': self.mgnt_student_id,
            'mgnt_admission_number': self.mgnt_admission_number,
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None
        }



class WebsiteContactInfo(db.Model):
    __tablename__ = 'website_contact_info'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    map_embed_url = db.Column(db.Text, nullable=True)  # Google Maps embed link
    working_hours = db.Column(db.String(255), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ContactInfo {self.address}>"

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'phone_number': self.phone_number,
            'email': self.email,
            'map_embed_url': self.map_embed_url,
            'working_hours': self.working_hours,
            'additional_notes': self.additional_notes
        }




class WebsiteContactMessage(db.Model):
    __tablename__ = 'website_contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=False)

    responded = db.Column(db.Boolean, default=False, nullable=False)
    response_text = db.Column(db.Text, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False )
    
    reply = db.Column(db.Text) 
    replied_at = db.Column(db.DateTime)  
    def __repr__(self):
        return f"<ContactMessage from {self.first_name} {self.last_name} - {self.email or self.phone}>"




class FooterInfo(db.Model):
    __tablename__ = "footer_info"

    id = db.Column(db.Integer, primary_key=True)

    # Contact Info
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    # Social Links
    facebook = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
 



class Gallery(db.Model):
    __tablename__ = 'gallery'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)  # 'image' or 'video'

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'media_type': self.media_type,
            'image': f'/api/v1/gallery/files/{self.filename}'
        }



# models/home.py


class HomePage(db.Model):
    __tablename__ = 'home_page'
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(255))
    hero_subtitle = db.Column(db.Text)
    hero_image = db.Column(db.String(255))  # Background image
    about_title = db.Column(db.String(255))
    about_text = db.Column(db.Text)
    about_link = db.Column(db.String(255))  # Link to full About page
    core_values = db.Column(db.Text)  # JSON array of core values

    product_previews = db.relationship("ProductPreview", backref="home_page", lazy=True)
    gallery_images = db.relationship("GalleryImage", backref="home_page", lazy=True)

    def to_dict(self):
        import json
        core_values_list = []
        if self.core_values:
            try:
                core_values_list = json.loads(self.core_values) if isinstance(self.core_values, str) else self.core_values
            except:
                core_values_list = []
        
        return {
            'id': self.id,
            'hero_title': self.hero_title,
            'hero_subtitle': self.hero_subtitle,
            'hero_image': self.hero_image,
            'about_title': self.about_title,
            'about_text': self.about_text,
            'about_link': self.about_link,
            'core_values': core_values_list,
            'product_previews': [pp.to_dict() for pp in self.product_previews],
            'gallery_images': [gi.to_dict() for gi in self.gallery_images]
        }

class ProductPreview(db.Model):
    __tablename__ = 'product_previews'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image = db.Column(db.String(255))
    description = db.Column(db.Text)
    home_page_id = db.Column(db.Integer, db.ForeignKey('home_page.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'description': self.description
        }

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255))
    alt_text = db.Column(db.String(255))
    home_page_id = db.Column(db.Integer, db.ForeignKey('home_page.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'image': self.image,
            'alt_text': self.alt_text
        }


class WebsiteAnnouncement(db.Model):
    __tablename__ = 'website_announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WebsiteStudent(db.Model):
    __tablename__ = 'website_students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade
        }


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role
        }



