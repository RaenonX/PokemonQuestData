from flask import (
    Blueprint, jsonify, request
)

from ._objs import *

api = Blueprint("api", __name__)

@api.route("/api/get-data-add-poke", methods=["GET"])
def get_data_for_add_poke():
    id = int(request.args.get('id'))
    return jsonify(pi.get_pokemon_data_add_poke(id))