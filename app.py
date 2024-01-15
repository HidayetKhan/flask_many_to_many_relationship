from flask import Flask,request
from flask_restful import Api,Resource
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api=Api(app)
db=SQLAlchemy(app)



user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(150))
    password=db.Column(db.String(200))
 
    roles = db.relationship('Role', secondary=user_roles, back_populates='users', lazy='dynamic')

    def __repr__(self):
        return f'<User{self.username}>'


class Role(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(100))

    users = db.relationship('User', secondary=user_roles, back_populates='roles', lazy='dynamic')

    def __repr__(self):
        return f'<Role{self.name}>'


class UserResorse(Resource):
    def get(self,user_id=None):
        if user_id:
            user=User.query.get(user_id)
            if user:
                roles=[{'id':role.id,'name':role.name}for role in roles]
                return {'id':user.id,'username':user.username,'password':user.password}
            else:
                return {'message':'user not found'}
        else:
            user=User.query.all()
            user_list = [{'id': user.id, 'username': user.username, 'password': user.password} for user in user]
            
            return {'users':user_list}
        
    def post(self):
        data = request.get_json()

        user_data = {
            'username': data['username'],
            'password': data['password']
        }

        role_data = data.get('roles', [])

        new_user = User(**user_data)
        db.session.add(new_user)

        for role_item in role_data:
            role = Role.query.filter_by(name=role_item['name']).first()
            if role is None:
                role = Role(name=role_item['name'])
            new_user.roles.append(role)

        db.session.commit()
        return {'message': 'New user and roles created successfully', 'user_id': new_user.id}

    def put(self,user_id):
        user=User.query.get(user_id)
        if user:
            data=request.get_json()
            user.username=data['username']
            user.password=data['password']
            user.roles=[]
            for role_item in data.get('roles',[]):
                role=Role.query.filter_by(name=role_item['name']).first()
                if role is None:
                    role=Role(name=role_item['name'])
                    user.roles.append(role)
            db.session.commit()
            return {'message':'user data is updated','user_id':user.id},200
        else:
            return {'message':'user not found'},404



    def delete(self,user_id):
        user=User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message':'user is deleted'}
        else:
            return {'message':'user is not found'}

class  RoleResource(Resource):
    def get(self,role_id=None):
        if role_id:
            role=Role.query.get(role_id)
            if role:
                users=[{'id':user.id,'username':user.username,'password':user.password}for user in users]
                return {'id':role.id,'name':role.name}
            else:
                return {'message':'user not found'},404
        else:
            role=Role.query.all()
            role_list=[{
                'id':role.id,
                'name':role.name,
                'users':[{
                    'id':user.id,
                    'username':user.username,
                    'password':user.password
                }for user in users]
            }for role in role_list]
            return {'role':role_list}
        
    def post(self):
        data=request.get_json()
        new_role=Role(name=data['name'])
        db.session.add(new_role)
        db.session.commit()
        return {'message':'new role created succssfully ','new_role':new_role.id}
    
    def put(self,role_id):
        role=Role.query.get(role_id)
        if role:
            data=request.get_json()
            role.name=data['name']
            db.session.commit()
            return {'message':'role is updated','role_id':role.id}
        else:
            return {'message':'user not found'},404
        
    def delete(self,role_id):
        role=Role.query.get(role_id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return {'message':'role is delted'}
        else:
            return {'message':'role not found'},404


api.add_resource(UserResorse, '/users', '/users/<int:user_id>')
api.add_resource(RoleResource, '/roles', '/roles/<int:role_id>')




if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)