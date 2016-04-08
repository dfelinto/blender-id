import logging
import datetime

from application import db

log = logging.getLogger(__name__)


class SubclientToken(db.Model):
    subclient_specific_token = db.Column(db.String(32), primary_key=True)

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'),
        nullable=False,
    )
    user = db.relationship('User')

    subclient_id = db.Column(db.String(40))

    expires = db.Column(db.DateTime)
    host_label = db.Column(db.String(255))

    @classmethod
    def expire_tokens(cls):
        """Deletes all expired subclient-specific tokens.

        Always call this before querying tokens.
        """

        now = datetime.datetime.now()
        cls.query.filter(cls.expires <= now).delete()
        db.session.commit()
