from . import db

class Face(db.Model):
    """Model for faces."""

    __tablename__ = 'faces'
    id = db.Column(db.Integer,
                   primary_key=True)
    face_id = db.Column(db.String(64),
                         index=True,
                         unique=True,
                         nullable=False)
    size = db.Column(db.Integer,
                      index=False,
                      unique=False,
                      nullable=False)
    face_data = db.Column(db.Text,
                          index=False,
                          unique=False,
                          nullable=False)
    created_at = db.Column(db.DateTime,
                            index=False,
                            unique=False,
                            nullable=False)

    def __repr__(self):
        return '<Face {}>'.format(self.face_id)

def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()
