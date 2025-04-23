from flask import Blueprint
from .countries import countries_blueprint
from .diplomacy import diplomacy_blueprint
from .events import events_blueprint
from .policy import policy_blueprint
from .budget import budget_blueprint

api_blueprint = Blueprint('api', __name__)

api_blueprint.register_blueprint(countries_blueprint)
api_blueprint.register_blueprint(diplomacy_blueprint)
api_blueprint.register_blueprint(events_blueprint)
api_blueprint.register_blueprint(policy_blueprint)
api_blueprint.register_blueprint(budget_blueprint)

def init_app(app):
    app.register_blueprint(api_blueprint)