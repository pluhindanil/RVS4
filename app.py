from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///components.db'
db = SQLAlchemy(app)
api = Api(app)

component_model = api.model('Component', {
    'id': fields.Integer(readonly=True, description='The unique identifier of a component'),
    'name': fields.String(required=True, description='The name of the component'),
    'category': fields.String(required=True, description='The category of the component'),
    'price': fields.Float(required=True, description='The price of the component')
})

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

@api.route('/components')
class ComponentResource(Resource):
    @api.doc('list_components')
    @api.marshal_list_with(component_model)
    def get(self):
        '''List all components'''
        components = Component.query.all()
        return components

    @api.doc('create_component')
    @api.expect(component_model)
    @api.marshal_with(component_model, code=201)
    def post(self):
        '''Create a new component'''
        name = api.payload.get('name')
        category = api.payload.get('category')
        price = api.payload.get('price')

        component = Component(name=name, category=category, price=price)
        db.session.add(component)
        db.session.commit()

        return component, 201

@api.route('/components/<int:id>')
@api.param('id', 'The component identifier')
class ComponentItemResource(Resource):
    @api.doc('update_component')
    @api.expect(component_model)
    @api.marshal_with(component_model)
    def put(self, id):
        '''Update a component'''
        component = Component.query.get(id)
        if component:
            component.name = api.payload.get('name')
            component.category = api.payload.get('category')
            component.price = api.payload.get('price')
            db.session.commit()
            return component
        else:
            return {'message': 'Component not found'}, 404

    @api.doc('delete_component')
    @api.response(204, 'Component deleted')
    def delete(self, id):
        '''Delete a component'''
        component = Component.query.get(id)
        if component:
            db.session.delete(component)
            db.session.commit()
            return '', 204
        else:
            return {'message': 'Component not found'}, 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
