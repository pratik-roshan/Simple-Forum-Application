from marshmallow import fields, Schema

class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.String()