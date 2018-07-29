from flask import (
    Blueprint, jsonify, request
)

from ._objs import *

api = Blueprint("api", __name__)
    
# TODO: Integrate to one

@api.route("/api/get-bingos", methods=["GET"])
def get_pokemon_bingos():
    id = int(request.args.get('id'))

    return jsonify(pi.get_pokemon_bingo(int(id)))

@api.route("/api/get-skills", methods=["GET"])
def get_pokemon_skills():
    id = int(request.args.get('id'))

    return jsonify([skc.get_skill_data(sid).to_serialize() for sid in pkc.get_pokemon_by_id(int(id)).skill_ids])

@api.route("/api/get-params", methods=["GET"])
def get_pokemon_params():
    id = int(request.args.get('id'))

    return jsonify(pkc.get_max_params_of_pokemon(id).toJSON())

@api.route("/api/get-poke-name-zh", methods=["GET"])
def get_pokemon_name_zh():
    id = int(request.args.get('id'))

    return jsonify(pkc.get_pokemon_by_id(id).name_zh)
