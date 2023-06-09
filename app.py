from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exhibitions.db'
db = SQLAlchemy(app)
api = Api(app)

exhibition_model = api.model('Exhibition', {
    'id': fields.Integer(readonly=True, description='The unique identifier of an exhibition'),
    'name': fields.String(required=True, description='The name of the exhibition'),
    'date': fields.String(required=True, description='The date of the exhibition'),
    'location': fields.String(required=True, description='The location of the exhibition'),
    'participants': fields.Integer(required=True, description='The number of participants')
})

participants_model = api.model('Participants', {
    'participants': fields.Integer(required=True, description='The number of participants to add')
})


class Exhibition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    participants = db.Column(db.Integer, nullable=False)


@api.route('/exhibitions')
class ExhibitionResource(Resource):
    @api.doc('list_exhibitions')
    @api.marshal_list_with(exhibition_model)
    def get(self):
        '''List all exhibitions'''
        exhibitions = Exhibition.query.all()
        return exhibitions

    @api.doc('create_exhibition')
    @api.expect(exhibition_model)
    @api.marshal_with(exhibition_model, code=201)
    def post(self):
        '''Create a new exhibition'''
        name = api.payload.get('name')
        date = api.payload.get('date')
        location = api.payload.get('location')
        participants = api.payload.get('participants')

        exhibition = Exhibition(name=name, date=date, location=location, participants=participants)
        db.session.add(exhibition)
        db.session.commit()

        return exhibition, 201


@api.route('/exhibitions/<int:id>')
@api.param('id', 'The exhibition identifier')
class ExhibitionItemResource(Resource):
    @api.doc('update_exhibition')
    @api.expect(exhibition_model)
    @api.marshal_with(exhibition_model)
    def put(self, id):
        '''Update an exhibition'''
        exhibition = Exhibition.query.get(id)
        if exhibition:
            exhibition.name = api.payload.get('name')
            exhibition.date = api.payload.get('date')
            exhibition.location = api.payload.get('location')
            exhibition.participants = api.payload.get('participants')
            db.session.commit()
            return exhibition
        else:
            return {'message': 'Exhibition not found'}, 404

    @api.doc('delete_exhibition')
    @api.response(204, 'Exhibition deleted')
    def delete(self, id):
        '''Delete an exhibition'''
        exhibition = Exhibition.query.get(id)
        if exhibition:
            db.session.delete(exhibition)
            db.session.commit()
            return '', 204
        else:
            return {'message': 'Exhibition not found'}, 404


# @api.route('/exhibitions/<int:id>/participants')
# @api.param('id', 'The exhibition identifier')
# class ExhibitionParticipantsResource(Resource):
#     @api.doc('update_participants')
#     @api.expect(participants_model)
#     @api.marshal_with(exhibition_model)
#     def patch(self, id):
#         '''Update the participants of an exhibition'''
#         participants_to_add = api.payload.get('participants')
#
#         exhibition = Exhibition.query.get(id)
#         if exhibition:
#             exhibition.participants += participants_to_add
#             db.session.commit()
#             return exhibition
#         else:
#             return {'message': 'Exhibition not found'}, 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)