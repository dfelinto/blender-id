from application import db

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2), nullable=False)
    name = db.Column(db.String(45), nullable=False)

    def __str__(self):
        return unicode(self.name) or u''
