#!/usr/bin/env python
"""An extremely simple static REST service for teaching about REST itself."""

import collections
import copy
import datetime
import json
import unittest
import uuid

import ddt
import flask
import flask_restful as restful
from flask_restful import fields
from flask_restful import inputs
from flask_restful import reqparse
from werkzeug import routing

# static data
DATA = {
    "owners": collections.OrderedDict(),
    "pets": collections.OrderedDict(),
    "veterinarians": collections.OrderedDict(),
    "ownership": [],
    "vet assignments": {}
}

DATA["owners"]["511363b2-8693-4b30-ae4c-09964a4cebe0"] = {
    "name": "Goran Shain",
    "birthday": datetime.datetime(1981, 10, 27),
    "shoe_size": 10.5
}
DATA["owners"]["ee5479d6-7070-4109-bfb2-d44e3c42782b"] = {
    "name": "Remus Bergfalk",
    "birthday": datetime.datetime(1977, 5, 8),
    "shoe_size": 9.5
}
DATA["owners"]["35a85559-dc03-4aa2-85d2-947e17e310e5"] = {
    "name": "Jolanda Seaver",
    "birthday": datetime.datetime(1996, 8, 29),
    "shoe_size": 8.5
}
DATA["owners"]["5e174bc4-4135-4e7b-b957-9705bacc903d"] = {
    "name": "Fevziye Kristiansen",
    "birthday": datetime.datetime(1982, 7, 15),
    "shoe_size": 7.5
}

DATA["pets"]["a8533344-6371-4982-a86b-722331839514"] = {
    "name": "Tenchu",
    "species": "dog",
    "breed": "Shiba Inu"
}
DATA["pets"]["00182d56-9981-402b-821e-7b1c2906533c"] = {
    "name": "Slim",
    "species": "tortoise",
    "breed": "Hermann's"
}
DATA["pets"]["18e1588a-090e-4ace-94c2-f289617de0cb"] = {
    "name": "Scooter",
    "species": "mouse",
    "breed": "fancy"
}
DATA["pets"]["4dc4d7b0-a386-4919-9878-47d4eb8f49ec"] = {
    "name": "Scarface",
    "species": "dog",
    "breed": "English Bulldog"
}
DATA["pets"]["bf61616c-010e-48f2-8173-78b330804cd6"] = {
    "name": "Kisses",
    "species": "Hissing Cockroach"
}
DATA["pets"]["d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"] = {
    "name": "Zeta",
    "species": "betta"
}
DATA["pets"]["72f12e94-33ca-4537-9897-205ffe42350e"] = {
    "name": "Hellbringer the Befouler",
    "species": "cat",
    "breed": "domestic shorthair"
}

DATA["ownership"] = [{
    "owner": "511363b2-8693-4b30-ae4c-09964a4cebe0",
    "pet": "a8533344-6371-4982-a86b-722331839514"
}, {
    "owner": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
    "pet": "00182d56-9981-402b-821e-7b1c2906533c"
}, {
    "owner": "35a85559-dc03-4aa2-85d2-947e17e310e5",
    "pet": "18e1588a-090e-4ace-94c2-f289617de0cb"
}, {
    "owner": "35a85559-dc03-4aa2-85d2-947e17e310e5",
    "pet": "4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
}, {
    "owner": "5e174bc4-4135-4e7b-b957-9705bacc903d",
    "pet": "4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
}, {
    "owner": "511363b2-8693-4b30-ae4c-09964a4cebe0",
    "pet": "d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
}, {
    "owner": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
    "pet": "72f12e94-33ca-4537-9897-205ffe42350e"
}]

DATA["ownershipv2"] = {
    "5f5c1ded-32e7-4fb2-9b6f-b0aa05616d67": DATA["ownership"][0],
    "6b479d98-9db5-4bd7-9e8b-77beadb88bbb": DATA["ownership"][1],
    "a0cde759-127c-4c89-9cd5-f4bdcd542a2f": DATA["ownership"][2],
    "06d5a7ec-647c-46b9-95d8-1e6c07e49de6": DATA["ownership"][3],
    "7f68b34c-0c29-4880-b4dd-fc072efa89b7": DATA["ownership"][4],
    "44fc62fe-e8d8-43f8-971c-a615e361820d": DATA["ownership"][5],
    "ab80fc51-bf3f-420d-b0c4-7836e2b7ff89": DATA["ownership"][6]
}

DATA["veterinarians"]["f5df1cc0-4fa2-4605-af57-4da6479e8afa"] = {
    "name": "Marquita Jepson",
    "specialty": "dogs"
}
DATA["veterinarians"]["fd87a620-466d-41ae-a6b0-1527b5126c58"] = {
    "name": "Colobert Bannerman",
    "specialty": "cats"
}
DATA["veterinarians"]["3cfbb699-d2f2-45cd-b932-be5171887262"] = {
    "name": "Seong-Min Park"
}

DATA["vet assignments"] = {
    "a8533344-6371-4982-a86b-722331839514":
    "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
    "00182d56-9981-402b-821e-7b1c2906533c":
    "3cfbb699-d2f2-45cd-b932-be5171887262",
    "4dc4d7b0-a386-4919-9878-47d4eb8f49ec":
    "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
    "72f12e94-33ca-4537-9897-205ffe42350e":
    "fd87a620-466d-41ae-a6b0-1527b5126c58"
}

# creds for authn demonstration
USERNAME = "stpierre"
PASSWORD = "hunter2"
TOKEN = "6158a4ff-8d50-47bd-8316-c0008b7cbc88"

app = flask.Flask(__name__)
api = restful.Api(app)


class VersionedUrl(fields.Url):
    def output(self, key, obj):
        if "version" not in obj:
            new_obj = copy.deepcopy(obj)
            new_obj["version"] = flask.g.request_version
        else:
            new_obj = obj
        return super(VersionedUrl, self).output(key, obj)


class Endpoint(fields.Raw):
    def __init__(self, resource_name_field):
        self.resource_name_field = resource_name_field

    def output(self, key, obj):
        version = obj.get("version", flask.g.request_version)
        resource_cls = obj[self.resource_name_field]
        return api.url_for(resource_cls, version=version)


# marshalling fields. for the most part, Flask-RESTful's marshalling
# stuff isn't powerful enough for us, since we often have
# variable-length lists of links. I could probably write a custom
# field type for that, but it'd be quite complex, and this gives
# people a sufficient example of how to use the marshalling feature.
endpoint_fields = {"rel": fields.String, "href": Endpoint("resource")}

VERSIONS = ["v1", "v2"]


class VersionConverter(routing.BaseConverter):
    def __init__(self, url_map, only=None):
        self.only = only

    def to_python(self, value):
        if (self.only and value != self.only) or value not in VERSIONS:
            raise ValueError(value)
        return value

    def to_url(self, value):
        if (self.only and value != self.only) or value not in VERSIONS:
            raise ValueError("if (%s and %s != %s) or %s not in %s:" %
                             (self.only, value, self.only, value, VERSIONS))
            raise ValueError(value)
        return value


app.url_map.converters["version"] = VersionConverter


@app.url_value_preprocessor
def set_request_version(endpoint, values):
    if values is None:
        flask.g.request_version = None
    else:
        flask.g.request_version = values.pop("version", None)


@api.resource("/")
class Versions(restful.Resource):
    """List API versions."""

    @restful.marshal_with(endpoint_fields, envelope="links")
    def get(self):
        return [{
            "rel": version,
            "version": version,
            "resource": Endpoints
        } for version in VERSIONS]


@api.resource("/<version:version>/")
class Endpoints(restful.Resource):
    """List top-level endpoints."""

    @restful.marshal_with(endpoint_fields, envelope="links")
    def get(self):
        endpoints = [{
            "rel": "owner",
            "resource": Owners
        }, {
            "rel": "pet",
            "resource": Pets
        }, {
            "rel": "veterinarian",
            "resource": Veterinarians
        }]
        if flask.g.request_version == "v2":
            endpoints.append({
                "rel": "ownership",
                "resource": OwnershipRecords
            })
        return endpoints


class BaseResource(restful.Resource):
    @staticmethod
    def _ensure_record_exists(datasource, record_name, rid, code=404):
        if rid not in DATA[datasource]:
            restful.abort(code, message="No such %s %s" % (record_name, rid))

    def ensure_owner_exists(self, owner_id, code=404):
        self._ensure_record_exists("owners", "owner", owner_id, code=code)

    def ensure_pet_exists(self, pet_id, code=404):
        self._ensure_record_exists("pets", "pet", pet_id, code=code)

    def ensure_veterinarian_exists(self, vet_id, code=404):
        self._ensure_record_exists(
            "veterinarians", "veterinarian", vet_id, code=code)

    def ensure_ownership_exists(self, owner_id, pet_id, code=404):
        self.ensure_owner_exists(owner_id)
        self.ensure_pet_exists(pet_id)
        record = {"owner": owner_id, "pet": pet_id}
        if record not in DATA["ownership"]:
            restful.abort(
                code,
                message="Owner %s does not own pet %s" % (owner_id, pet_id))

    def ensure_vet_assignment_exists(self, pet_id, vet_id=None, code=404):
        self.ensure_pet_exists(pet_id)
        self.ensure_veterinarian_exists(vet_id)
        if pet_id not in DATA["vet assignments"]:
            return restful.abort(
                code, message="Pet %s has no veterinarian" % pet_id)
        if DATA["vet assignments"][pet_id] != vet_id:
            return restful.abort(
                code,
                message="Pet %s is not assigned to veterinarian %s" % (pet_id,
                                                                       vet_id))

    @staticmethod
    def get_owner_url(owner_id):
        return api.url_for(
            Owner, rid=owner_id, version=flask.g.request_version)

    def marshal_owner(self, owner_id, detailed=False, links=True):
        if detailed:
            retval = dict(DATA["owners"][owner_id])
            retval["pets"] = []
        else:
            retval = {}
        retval["id"] = owner_id
        if "birthday" in retval:
            retval["birthday"] = retval["birthday"].strftime("%Y-%m-%d")
        if links in [True, "self"]:
            retval["links"] = [{
                "rel": "self",
                "href": self.get_owner_url(owner_id)
            }]
        if detailed or links is True:
            for relation in DATA["ownership"]:
                if relation["owner"] == owner_id:
                    if links is True:
                        retval["links"].append({
                            "rel":
                            "pet",
                            "href":
                            self.get_pet_url(relation["pet"])
                        })
                    if detailed:
                        retval["pets"].append(relation["pet"])
        return retval

    @staticmethod
    def get_pet_url(pet_id):
        return api.url_for(Pet, rid=pet_id, version=flask.g.request_version)

    def marshal_pet(self, pet_id, record=None, detailed=False, links=True):
        if detailed:
            retval = dict(DATA["pets"][pet_id])
            retval["owners"] = []
            retval["veterinarian"] = None
        else:
            retval = {}
        retval["id"] = pet_id
        if links in [True, "self"]:
            retval["links"] = [{
                "rel": "self",
                "href": self.get_pet_url(pet_id)
            }]
        if detailed or links is True:
            for relation in DATA["ownership"]:
                if relation["pet"] == pet_id:
                    if links is True:
                        retval["links"].append({
                            "rel":
                            "owner",
                            "href":
                            self.get_owner_url(relation["owner"])
                        })
                    if detailed:
                        retval["owners"].append(relation["owner"])

            vet = DATA["vet assignments"].get(pet_id)
            if vet:
                if links is True:
                    retval["links"].append({
                        "rel":
                        "veterinarian",
                        "href":
                        self.get_veterinarian_url(vet)
                    })
                if detailed:
                    retval["veterinarian"] = vet
        return retval

    def marshal_ownership(self, owner_id, pet_id, detailed=False):
        retval = {}
        if detailed:
            retval["owner"] = self.marshal_owner(
                owner_id, detailed=True, links=False)
            retval["pet"] = self.marshal_pet(
                pet_id, detailed=True, links=False)
        else:
            retval["owner"] = owner_id
            retval["pet"] = pet_id
        retval["links"] = [{
            "rel": "owner",
            "href": self.get_owner_url(owner_id)
        }, {
            "rel": "pet",
            "href": self.get_pet_url(pet_id)
        }]
        return retval

    @staticmethod
    def get_veterinarian_url(vet_id):
        return api.url_for(
            Veterinarian, rid=vet_id, version=flask.g.request_version)

    def marshal_veterinarian(self, vet_id, detailed=False, links=True):
        if detailed:
            retval = dict(DATA["veterinarians"][vet_id])
        else:
            retval = {}
        retval["id"] = vet_id
        if links in [True, "self"]:
            retval["links"] = [{
                "rel": "self",
                "href": self.get_veterinarian_url(vet_id)
            }]
        if links is True:
            for pet_id, vet_id_ in DATA["vet assignments"].items():
                if vet_id_ == vet_id:
                    retval["links"].append({
                        "rel": "patient",
                        "href": self.get_pet_url(pet_id)
                    })

        return retval

    @staticmethod
    def get_vet_assignment_url(vet_id, pet_id):
        return api.url_for(
            AssignmentRecord,
            vet_id=vet_id,
            pet_id=pet_id,
            version=flask.g.request_version)

    def marshal_vet_assignment(self, vet_id, pet_id, detailed=False):
        return {
            "veterinarian":
            self.marshal_veterinarian(vet_id, links=False, detailed=detailed),
            "patient":
            self.marshal_pet(pet_id, links=False, detailed=detailed),
            "links": [{
                "rel": "self",
                "href": self.get_vet_assignment_url(vet_id, pet_id)
            }, {
                "rel": "veterinarian",
                "href": self.get_veterinarian_url(vet_id)
            }, {
                "rel": "patient",
                "href": self.get_pet_url(pet_id)
            }]
        }


class BaseMixin(BaseResource):
    record_name = None

    def get_url(self, *args, **kwargs):
        func = getattr(self, "get_%s_url" % self.record_name)
        return func(*args, **kwargs)

    def marshal(self, *args, **kwargs):
        func = getattr(self, "marshal_%s" % self.record_name)
        return func(*args, **kwargs)


class CollectionMixin(BaseMixin):
    """List and add records."""
    collection_name = None
    parser = None

    def get(self):
        detailed = bool(flask.request.args.get("detail", False))
        limit = int(flask.request.args.get("limit", -1))
        keys = DATA[self.datasource].keys()
        if limit > 0:
            keys = keys[0:limit]
        retval = [
            self.marshal(
                k, links=detailed if detailed else "self", detailed=detailed)
            for k in keys
        ]
        return {self.collection_name: retval}

    def post(self):
        args = {
            k: v
            for k, v in self.parser.parse_args(strict=True).items()
            if v is not None
        }
        rid = str(uuid.uuid4())
        DATA[self.datasource][rid] = args
        return flask.make_response(
            flask.jsonify(self.marshal(rid, detailed=True)), 201)


class RecordMixin(BaseMixin):
    """Work with individual records."""
    patch_parser = None
    parser = None
    datasource = None
    get_detailed_default = True

    def ensure_exists(self, rid):
        self._ensure_record_exists(self.datasource, self.record_name, rid)

    def get(self, rid):
        self.ensure_exists(rid)
        detailed = (self.get_detailed_default
                    or bool(flask.request.args.get("detail", False)))
        return flask.jsonify(self.marshal(rid, detailed=detailed))

    def put(self, rid):
        self.ensure_exists(rid)
        args = {
            k: v
            for k, v in self.parser.parse_args(strict=True).items()
            if v is not None
        }
        DATA[self.datasource][rid] = args
        return flask.jsonify(self.marshal(rid, detailed=True))

    def patch(self, rid):
        self.ensure_exists(rid)
        args = {
            k: v
            for k, v in self.patch_parser.parse_args(strict=True).items()
            if v is not None
        }
        DATA[self.datasource][rid].update(args)
        return flask.jsonify(self.marshal(rid, detailed=True))

    def delete_cascade(self, rid):
        pass

    def delete(self, rid):
        self.ensure_exists(rid)
        del DATA[self.datasource][rid]
        self.delete_cascade(rid)
        return flask.make_response("", 204)


class OwnersBase(object):
    datasource = "owners"

    collection_name = "owners"
    record_name = "owner"

    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True)
    parser.add_argument("birthday", type=inputs.date)
    parser.add_argument("shoe_size", type=float)

    patch_parser = reqparse.RequestParser()
    patch_parser.add_argument("name")
    patch_parser.add_argument("birthday", type=inputs.date)
    patch_parser.add_argument("shoe_size", type=float)


@api.resource("/<version:version>/owners/")
class Owners(OwnersBase, CollectionMixin):
    """List and add owners."""


@api.resource("/<version:version>/owners/<string:rid>")
class Owner(OwnersBase, RecordMixin):
    """Work with individual owners."""

    def get(self, rid):
        owner = super(Owner, self).get(rid)
        if flask.g.request_version == "v1":
            return owner
        else:
            for link in owner["links"]:
                link["method"] = "GET"
            owner["links"].extend([{
                "rel": "edit",
                "href": self.get_owner_url(rid),
                "method": "PUT"
            }, {
                "rel": "delete",
                "href": self.get_owner_url(rid),
                "method": "DELETE"
            }])
            return {
                "owner":
                owner,
                "links": [{
                    "rel":
                    "list",
                    "href":
                    api.url_for(Owners, version=flask.g.request_version),
                    "method":
                    "GET"
                }, {
                    "rel":
                    "create",
                    "href":
                    api.url_for(Owners, version=flask.g.request_version),
                    "method":
                    "POST"
                }]
            }

    def delete(self, rid):
        if flask.g.request_version == "v2":
            auth = flask.request.authorization
            if (not auth or auth.username != USERNAME
                    or auth.password != PASSWORD):
                restful.abort(
                    401,
                    message="Request requires authentication",
                    headers={
                        'WWW-Authenticate': 'Basic realm="Login Required"'
                    })
        return super(Owner, self).delete(rid)

    def delete_cascade(self, rid):
        to_delete = []
        for relation in DATA["ownership"]:
            if relation["owner"] == rid:
                to_delete.append(relation)
        for relation in to_delete:
            DATA["ownership"].remove(relation)


@api.resource("/<version:version>/owners/<string:owner_id>/pets/")
class OwnerPets(BaseResource):
    parser = reqparse.RequestParser()
    parser.add_argument("pet_id", required=True)

    def get(self, owner_id):
        self.ensure_owner_exists(owner_id)
        detailed = bool(flask.request.args.get("detail", False))
        limit = int(flask.request.args.get("limit", -1))
        pets = []
        links = []
        for record in DATA["ownership"]:
            if limit != -1 and len(pets) >= limit:
                break
            if record["owner"] == owner_id:
                if detailed:
                    pets.append(
                        self.marshal_pet(
                            record["pet"], detailed=True, links="self"))
                else:
                    pets.append(record["pet"])
                    links.append({
                        "rel": "pet",
                        "href": self.get_pet_url(record["pet"])
                    })
        if detailed:
            return flask.jsonify({"pets": pets})
        else:
            return flask.jsonify({"pets": pets, "links": links})

    def post(self, owner_id):
        self.ensure_owner_exists(owner_id)
        pet_id = self.parser.parse_args(strict=True)["pet_id"]
        self.ensure_pet_exists(pet_id, code=400)
        record = {"owner": owner_id, "pet": pet_id}
        if record in DATA["ownership"]:
            restful.abort(409, message="Duplicate ownership record")
        DATA["ownership"].append(record)
        return flask.make_response(
            flask.jsonify(self.marshal_ownership(owner_id, pet_id)), 201)


@api.resource(
    "/<version:version>/pets/<string:pet_id>/owners/<string:owner_id>",
    "/<version:version>/owners/<string:owner_id>/pets/<string:pet_id>")
class OwnershipRecord(BaseResource):
    def get(self, owner_id, pet_id):
        self.ensure_ownership_exists(owner_id, pet_id)
        return flask.jsonify(
            self.marshal_ownership(owner_id, pet_id, detailed=True))

    def put(self, owner_id, pet_id):
        self.ensure_owner_exists(owner_id)
        self.ensure_pet_exists(pet_id)
        record = {"owner": owner_id, "pet": pet_id}
        if record in DATA["ownership"]:
            restful.abort(409, message="Duplicate ownership record")
        DATA["ownership"].append(record)
        return flask.make_response(
            flask.jsonify(self.marshal_ownership(owner_id, pet_id)), 201)

    def delete(self, owner_id, pet_id):
        self.ensure_ownership_exists(owner_id, pet_id)
        record = {"owner": owner_id, "pet": pet_id}
        DATA["ownership"].remove(record)
        return flask.make_response("", 204)


class PetsBase(restful.Resource):
    datasource = "pets"

    collection_name = "pets"
    record_name = "pet"

    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True)
    parser.add_argument("species", required=True)
    parser.add_argument("breed")

    patch_parser = reqparse.RequestParser()
    patch_parser.add_argument("name")
    patch_parser.add_argument("species")
    patch_parser.add_argument("breed")


@api.resource("/<version:version>/pets/")
class Pets(PetsBase, CollectionMixin):
    """List and add pets."""


@api.resource("/<version:version>/pets/<string:rid>")
class Pet(PetsBase, RecordMixin):
    """Work with individual pets."""

    patch_v2_parser = reqparse.RequestParser()
    patch_v2_parser.add_argument("name")
    patch_v2_parser.add_argument("species")
    patch_v2_parser.add_argument("breed")
    patch_v2_parser.add_argument("veterinarian")
    patch_v2_parser.add_argument("owners", action="append")

    def patch(self, rid):
        if flask.g.request_version == "v1":
            return super(Pet, self).patch(rid)
        else:
            self.ensure_exists(rid)
            args = {
                k: v
                for k, v in self.patch_v2_parser.parse_args(strict=True)
                .items() if v is not None
            }

            vet_id = args.pop("veterinarian", None)
            if vet_id is not None:
                # NOTE(stpierre): do all validation before we change
                # any data
                self.ensure_veterinarian_exists(vet_id, code=400)

            owners = args.pop("owners", None)
            if owners is not None:
                for owner_id in owners:
                    self.ensure_owner_exists(owner_id, code=400)
                current_owners = [
                    r["owner"] for r in DATA["ownership"] if r["pet"] == rid
                ]
                old_owners = set(current_owners) - set(owners)
                for owner_id in old_owners:
                    DATA["ownership"].remove({"owner": owner_id, "pet": rid})

                new_owners = set(owners) - set(current_owners)
                for owner_id in new_owners:
                    DATA["ownership"].append({"owner": owner_id, "pet": rid})

            if vet_id is not None:
                DATA["vet assignments"][rid] = vet_id

            DATA[self.datasource][rid].update(args)
            return flask.jsonify(self.marshal(rid, detailed=True))

    def delete(self, rid):
        if flask.g.request_version == "v2":
            token = flask.request.headers.get("X-Token")
            if not token or token != TOKEN:
                restful.abort(
                    401,
                    message="Request requires authentication",
                    headers={
                        'WWW-Authenticate': 'Basic realm="Login Required"'
                    })
        return super(Pet, self).delete(rid)

    def delete_cascade(self, rid):
        to_delete = []
        for relation in DATA["ownership"]:
            if relation["pet"] == rid:
                to_delete.append(relation)
        for relation in to_delete:
            DATA["ownership"].remove(relation)

        if rid in DATA["vet assignments"]:
            del DATA["vet assignments"][rid]


@api.resource("/<version:version>/pets/<string:pet_id>/owners/")
class PetOwners(BaseResource):
    parser = reqparse.RequestParser()
    parser.add_argument("owner_id", required=True)

    def get(self, pet_id):
        self.ensure_pet_exists(pet_id)
        detailed = bool(flask.request.args.get("detail", False))
        limit = int(flask.request.args.get("limit", -1))
        owners = []
        links = []
        for record in DATA["ownership"]:
            if limit != -1 and len(owners) >= limit:
                break
            if record["pet"] == pet_id:
                if detailed:
                    owners.append(
                        self.marshal_owner(
                            record["owner"], detailed=True, links="self"))
                else:
                    owners.append(record["owner"])
                    links.append({
                        "rel": "owner",
                        "href": self.get_owner_url(record["owner"])
                    })
        if detailed:
            return flask.jsonify({"owners": owners})
        else:
            return flask.jsonify({"owners": owners, "links": links})

    def post(self, pet_id):
        self.ensure_pet_exists(pet_id)
        owner_id = self.parser.parse_args(strict=True)["owner_id"]
        self.ensure_owner_exists(owner_id, code=400)
        record = {"owner": owner_id, "pet": pet_id}
        if record in DATA["ownership"]:
            restful.abort(409, message="Duplicate ownership record")
        DATA["ownership"].append(record)
        return flask.make_response(
            flask.jsonify(self.marshal_ownership(owner_id, pet_id)), 201)


class OwnershipBase(object):
    datasource = "ownershipv2"

    collection_name = "ownership records"
    record_name = "ownership record"

    parser = reqparse.RequestParser()
    parser.add_argument("owner_id", required=True)
    parser.add_argument("pet_id", required=True)
    patch_parser = parser

    def get_url(self, rid):
        return api.url_for(OwnershipRecordV2, rid=rid, version="v2")

    def marshal(self, ownership_id, detailed=False):
        record = DATA["ownershipv2"][ownership_id]
        retval = self.marshal_ownership(
            owner_id=record["owner"], pet_id=record["pet"], detailed=detailed)
        retval["id"] = ownership_id
        retval["links"].append({
            "rel": "self",
            "href": self.get_url(ownership_id)
        })
        return retval


@api.resource("/<version(only=v2):version>/ownership/")
class OwnershipRecords(OwnershipBase, CollectionMixin):
    """List and add ownership records."""


@api.resource("/<version(only=v2):version>/ownership/<string:rid>")
class OwnershipRecordV2(OwnershipBase, RecordMixin):
    """Work with individual ownership records."""
    get_detailed_default = False


@api.resource("/<version:version>/pets/<string:pet_id>/veterinarians/",
              "/<version:version>/pets/<string:pet_id>/veterinarian/")
class PetVeterinarians(BaseResource):
    def get(self, pet_id):
        detailed = bool(flask.request.args.get("detail", False))
        self.ensure_pet_exists(pet_id)
        vet_id = DATA["vet assignments"].get(pet_id)
        if vet_id is None:
            return {
                "veterinarian": None,
                "links": {
                    "rel": "patient",
                    "href": self.get_pet_url(pet_id)
                }
            }
        if detailed:
            vet = self.marshal_veterinarian(vet_id, detailed=True, links=False)
        else:
            vet = vet_id
        return {
            "veterinarian":
            vet,
            "links": [{
                "rel": "veterinarian",
                "href": self.get_veterinarian_url(vet_id)
            }, {
                "rel": "patient",
                "href": self.get_pet_url(pet_id)
            }]
        }


class VeterinariansBase(restful.Resource):
    datasource = "veterinarians"

    collection_name = "veterinarians"
    record_name = "veterinarian"

    parser = reqparse.RequestParser()
    parser.add_argument("name", required=True)
    parser.add_argument("specialty")

    patch_parser = reqparse.RequestParser()
    patch_parser.add_argument("name")
    patch_parser.add_argument("specialty")


@api.resource("/<version:version>/veterinarians/")
class Veterinarians(VeterinariansBase, CollectionMixin):
    """List and add veterinarians."""


@api.resource("/<version:version>/veterinarians/<string:rid>")
class Veterinarian(VeterinariansBase, RecordMixin):
    """Work with individual veterinarians."""

    def delete(self, rid):
        if flask.g.request_version == "v2":
            token = flask.request.cookies.get("token")
            if not token or token != TOKEN:
                restful.abort(
                    401,
                    message="Request requires authentication",
                    headers={
                        'WWW-Authenticate': 'Basic realm="Login Required"'
                    })
        return super(Veterinarian, self).delete(rid)

    def delete_cascade(self, rid):
        to_delete = []
        for pet_id, vet_id in DATA["vet assignments"].items():
            if vet_id == rid:
                to_delete.append(pet_id)
        for pet_id in to_delete:
            del DATA["vet assignments"][pet_id]


@api.resource("/<version:version>/veterinarians/<string:vet_id>/patients/")
class VeterinarianPatients(BaseResource):
    parser = reqparse.RequestParser()
    parser.add_argument("pet_id", required=True)

    def get(self, vet_id):
        detailed = bool(flask.request.args.get("detail", False))
        limit = int(flask.request.args.get("limit", -1))
        self.ensure_veterinarian_exists(vet_id)
        pets = []
        links = [{
            "rel": "veterinarian",
            "href": self.get_veterinarian_url(vet_id)
        }]
        for pet_id, pet_vet_id in DATA["vet assignments"].items():
            if pet_vet_id != vet_id:
                continue
            if limit > 0 and len(pets) >= limit:
                break
            pets.append(
                self.marshal_pet(pet_id, detailed=detailed, links="self"))
        return {"patients": pets, "links": links}

    def post(self, vet_id):
        self.ensure_veterinarian_exists(vet_id)
        pet_id = self.parser.parse_args(strict=True)["pet_id"]
        self.ensure_pet_exists(pet_id, code=400)
        if pet_id in DATA["vet assignments"]:
            flask.abort(409, "Pet %s is already assigned to veterinarian %s" %
                        (pet_id, DATA["vet assignments"][pet_id]))
        DATA["vet assignments"][pet_id] = vet_id
        return flask.make_response(
            flask.jsonify(self.marshal_vet_assignment(vet_id, pet_id)), 201)


@api.resource(
    "/<version:version>/pets/<string:pet_id>/veterinarians/<string:vet_id>",
    "/<version:version>/pets/<string:pet_id>/veterinarian/<string:vet_id>",
    "/<version:version>/veterinarians/<string:vet_id>/patients/<string:pet_id>"
)
class AssignmentRecord(BaseResource):
    def get(self, pet_id, vet_id):
        self.ensure_vet_assignment_exists(pet_id, vet_id)
        detailed = bool(flask.request.args.get("detail", False))
        return flask.jsonify(
            self.marshal_vet_assignment(vet_id, pet_id, detailed=detailed))

    def put(self, pet_id, vet_id):
        self.ensure_pet_exists(pet_id)
        self.ensure_veterinarian_exists(vet_id)
        if pet_id not in DATA["vet assignments"]:
            code = 201
        else:
            code = 200
        DATA["vet assignments"][pet_id] = vet_id
        return flask.make_response(
            flask.jsonify(self.marshal_vet_assignment(vet_id, pet_id)), code)

    def delete(self, pet_id, vet_id):
        self.ensure_vet_assignment_exists(pet_id, vet_id)
        del DATA["vet assignments"][pet_id]
        return "", 204


@api.resource("/<version:version>/token/")
class Token(restful.Resource):
    def get(self):
        auth = flask.request.authorization
        if (not auth or auth.username != USERNAME
                or auth.password != PASSWORD):
            restful.abort(
                401,
                message="Request requires authentication",
                headers={'WWW-Authenticate': 'Basic realm="Login Required"'})
        elif flask.g.request_version == "v1":
            return {"token": TOKEN}
        else:
            resp = flask.make_response("", 204)
            resp.set_cookie("token", TOKEN)
            return resp


# unit tests start here


class BaseServiceTestCase(unittest.TestCase):
    maxDiff = 4096

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        self._backup = copy.deepcopy(DATA)

    def tearDown(self):
        for key, val in self._backup.items():
            DATA[key] = val

    def fetch_json(self, url, code=200, method="get", **kwargs):
        response = getattr(self.app, method.lower())(url, **kwargs)
        self.assertEqual(
            response.status_code,
            code,
            msg="%s != %s: %s" % (response.status_code, code,
                                  response.get_data()))
        if response.get_data():
            return json.loads(response.get_data())

    def find_self_link(self, links):
        for link in links:
            if link["rel"] == "self":
                return link
                break
        else:
            return None

    def assert_self_link(self, links, expected):
        link = self.find_self_link(links)
        if link is None:
            self.fail("No 'self' link found in %s" % links)
        else:
            self.assertEqual(link, {"rel": "self", "href": expected})


class TestBaseService(BaseServiceTestCase):
    def test_get_versions(self):
        self.assertItemsEqual({
            "links": [{
                "rel": "v1",
                "href": "/v1/"
            }, {
                "rel": "v2",
                "href": "/v2/"
            }]
        }, self.fetch_json("/"))

    def test_get_endpoints_v1(self):
        self.assertDictEqual({
            "links": [{
                "rel": "owner",
                "href": "/v1/owners/"
            }, {
                "rel": "pet",
                "href": "/v1/pets/"
            }, {
                "rel": "veterinarian",
                "href": "/v1/veterinarians/"
            }]
        }, self.fetch_json("/v1/"))

    def test_get_endpoints_v2(self):
        self.assertDictEqual({
            "links": [
                {
                    "rel": "owner",
                    "href": "/v2/owners/"
                },
                {
                    "rel": "pet",
                    "href": "/v2/pets/"
                },
                {
                    "rel": "veterinarian",
                    "href": "/v2/veterinarians/"
                },
                {
                    "rel": "ownership",
                    "href": "/v2/ownership/"
                },
            ]
        }, self.fetch_json("/v2/"))


class BaseResourceTestMixin(object):
    collection = None
    base_url = None

    def _get_test_record_id(self):
        return DATA[self.collection].keys()[0]

    def _get_test_record(self):
        return DATA[self.collection].values()[0]

    def test_list(self):
        actual = [
            r["id"]
            for r in self.fetch_json("%s/" % self.base_url)[self.collection]
        ]
        self.assertItemsEqual(DATA[self.collection].keys(), actual)

    def test_list_limit(self):
        rid = DATA[self.collection].keys()[0]
        actual = [
            r["id"]
            for r in self.fetch_json("%s/?limit=1" % self.base_url)[
                self.collection]
        ]
        self.assertItemsEqual([rid], actual)

    def test_get_nonexistent(self):
        self.fetch_json("%s/not-a-real-uuid" % self.base_url, code=404)

    def test_update_put_nonexistent(self):
        self.fetch_json(
            "%s/not-a-real-uuid" % self.base_url,
            code=404,
            method="put",
            data=self._get_test_record())

    def test_update_put_extra_data(self):
        rid = self._get_test_record_id()
        updated_record = dict(DATA[self.collection][rid])
        updated_record["foobar"] = "bogus"
        self.fetch_json(
            "%s/%s" % (self.base_url, rid),
            code=400,
            method="put",
            data=updated_record)

    def test_update_patch_nonexistent(self):
        self.fetch_json(
            "%s/not-a-real-uuid" % self.base_url,
            code=404,
            method="patch",
            data={})

    def test_update_patch_extra_data(self):
        self.fetch_json(
            "%s/%s" % (self.base_url, self._get_test_record_id()),
            code=400,
            method="put",
            data={"foo": "bar"})

    def test_update_delete_nonexistent(self):
        self.fetch_json(
            "%s/not-a-real-uuid" % self.base_url, code=404, method="delete")

    def _test_update(self, rid, update, method="put"):
        uri = "%s/%s" % (self.base_url, rid)
        expected = self.fetch_json(uri)
        expected.update(update)

        if method == "patch":
            data = dict(update)
        else:
            data = dict(DATA[self.collection][rid])
            data.update(update)

        result = self.fetch_json(uri, method=method, data=data)
        self.assertDictEqual(result, expected)

        # read our writes
        record = self.fetch_json(uri)
        self.assertDictEqual(result, record)

    def _test_add(self, new_data, expected_additions=None):
        result = self.fetch_json(
            "%s/" % self.base_url, code=201, method="post", data=new_data)

        expected = dict(new_data)
        self.assertIn("id", result)
        expected["id"] = result["id"]
        expected_self_link = "%s/%s" % (self.base_url, expected["id"])
        expected["links"] = [{"rel": "self", "href": expected_self_link}]
        if expected_additions is not None:
            expected.update(expected_additions)
        self.assertDictEqual(result, expected)

        # read our writes
        self.assertDictEqual(result, self.fetch_json(expected_self_link))
        self.assertIn(expected["id"], [
            r["id"]
            for r in self.fetch_json("%s/" % self.base_url)[
                self.collection.lower()]
        ])

    def _test_delete(self, rid):
        self.fetch_json(
            "%s/%s" % (self.base_url, rid), method="delete", code=204)
        self.assertNotIn(rid,
                         self.fetch_json(
                             "%s/" % self.base_url)[self.collection.lower()])


class TestOwnersV1(BaseServiceTestCase, BaseResourceTestMixin):
    collection = "owners"
    base_url = "/v1/owners"

    def test_list_detail(self):
        self.assertDictEqual({
            "owners": [{
                "birthday":
                "1981-10-27",
                "id":
                "511363b2-8693-4b30-ae4c-09964a4cebe0",
                "name":
                "Goran Shain",
                "shoe_size":
                10.5,
                "pets": [
                    "a8533344-6371-4982-a86b-722331839514",
                    "d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
                ],
                "links": [
                    {
                        "rel": "self",
                        "href":
                        "/v1/owners/511363b2-8693-4b30-ae4c-09964a4cebe0"
                    },
                    {
                        "rel": "pet",
                        "href": "/v1/pets/a8533344-6371-4982-a86b-722331839514"
                    },
                    {
                        "rel": "pet",
                        "href": "/v1/pets/d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
                    },
                ]
            }]
        }, self.fetch_json("/v1/owners/?limit=1&detail=1"))

    def test_get(self):
        url = "/v1/owners/5e174bc4-4135-4e7b-b957-9705bacc903d"
        self.assertDictEqual({
            "birthday":
            "1982-07-15",
            "id":
            "5e174bc4-4135-4e7b-b957-9705bacc903d",
            "name":
            "Fevziye Kristiansen",
            "shoe_size":
            7.5,
            "pets": ["4dc4d7b0-a386-4919-9878-47d4eb8f49ec"],
            "links": [{
                "rel": "self",
                "href": url
            }, {
                "rel": "pet",
                "href": "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
            }]
        }, self.fetch_json(url))

    def test_add(self):
        birthday = datetime.datetime(1983, 2, 26)
        new_owner = {
            "name": "Jovka Garver",
            "birthday": birthday.strftime("%Y-%m-%d"),
            "shoe_size": 8
        }
        self._test_add(new_owner, {"pets": []})

    def test_update_put(self):
        owner_id = "ee5479d6-7070-4109-bfb2-d44e3c42782b"
        # we have to explicitly pass birthday here (even though we
        # aren't modifying it) because otherwise _test_update()
        # stringifies it incorrectly.
        self._test_update(owner_id, {
            "shoe_size":
            10.0,
            "birthday":
            DATA[self.collection][owner_id]["birthday"].strftime("%Y-%m-%d")
        })

    def test_update_patch(self):
        self._test_update(
            "ee5479d6-7070-4109-bfb2-d44e3c42782b", {"shoe_size": 10.0},
            method="patch")

    def test_delete(self):
        owner_id = "35a85559-dc03-4aa2-85d2-947e17e310e5"
        self._test_delete(owner_id)

        # deletes cascade properly
        self.assertFalse(
            any(r["owner"] == owner_id for r in DATA["ownership"]))


@ddt.ddt
class OwnershipTestMixin(object):
    collection_url = None
    record_url = None

    def test_list_nonexistent(self):
        self.fetch_json(
            self.collection_url %
            {"owner_id": "not-a-real-uuid",
             "pet_id": "not-a-real-uuid"},
            code=404)

    def test_add_nonexistent(self):
        self.fetch_json(
            self.collection_url %
            {"owner_id": "not-a-real-uuid",
             "pet_id": "not-a-real-uuid"},
            method="post",
            data={},
            code=404)

    @ddt.data({
        "owner_id": "not-a-real-uuid",
        "pet_id": "72f12e94-33ca-4537-9897-205ffe42350e"
    }, {
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
        "pet_id": "not-a-real-uuid"
    }, {
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
        "pet_id": "18e1588a-090e-4ace-94c2-f289617de0cb"
    })
    @ddt.unpack
    def test_get_nonexistent(self, owner_id, pet_id):
        self.fetch_json(
            self.record_url % {"owner_id": owner_id,
                               "pet_id": pet_id},
            code=404)

    def test_add_put(self):
        pet_id = "bf61616c-010e-48f2-8173-78b330804cd6"
        owner_id = "ee5479d6-7070-4109-bfb2-d44e3c42782b"
        result = self.fetch_json(
            self.record_url % {"owner_id": owner_id,
                               "pet_id": pet_id},
            method="put",
            code=201)
        self.assertDictEqual(result, {
            "owner":
            owner_id,
            "pet":
            pet_id,
            "links": [
                {
                    "rel": "owner",
                    "href": "/v1/owners/%s" % owner_id
                },
                {
                    "rel": "pet",
                    "href": "/v1/pets/%s" % pet_id
                },
            ]
        })

        # read our writes
        self.assertIn(owner_id,
                      self.fetch_json(
                          "/v1/pets/%s/owners/" % pet_id)["owners"])
        self.assertIn(pet_id,
                      self.fetch_json(
                          "/v1/owners/%s/pets/" % owner_id)["pets"])

    @ddt.data({
        "pet_id": "00182d56-9981-402b-821e-7b1c2906533c",
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
        "code": 409
    }, {
        "pet_id": "00182d56-9981-402b-821e-7b1c2906533c",
        "owner_id": "not-a-real-uuid"
    }, {
        "pet_id": "not-a-real-uuid",
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b"
    })
    @ddt.unpack
    def test_add_put_duplicate(self, pet_id, owner_id, code=404):
        self.fetch_json(
            self.record_url % {"owner_id": owner_id,
                               "pet_id": pet_id},
            method="put",
            code=code)

    def test_delete(self):
        pet_id = "00182d56-9981-402b-821e-7b1c2906533c"
        owner_id = "ee5479d6-7070-4109-bfb2-d44e3c42782b"
        self.fetch_json(
            self.record_url % {"owner_id": owner_id,
                               "pet_id": pet_id},
            method="delete",
            code=204)

        # read our writes
        self.assertNotIn(owner_id,
                         self.fetch_json(
                             "/v1/pets/%s/owners/" % pet_id)["owners"])
        self.assertNotIn(pet_id,
                         self.fetch_json(
                             "/v1/owners/%s/pets/" % owner_id)["pets"])

    @ddt.data({
        "owner_id": "not-a-real-uuid",
        "pet_id": "72f12e94-33ca-4537-9897-205ffe42350e"
    }, {
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
        "pet_id": "not-a-real-uuid"
    }, {
        "owner_id": "ee5479d6-7070-4109-bfb2-d44e3c42782b",
        "pet_id": "18e1588a-090e-4ace-94c2-f289617de0cb"
    })
    @ddt.unpack
    def test_delete_nonexistent(self, owner_id, pet_id):
        self.fetch_json(
            self.record_url % {"owner_id": owner_id,
                               "pet_id": pet_id},
            method="delete",
            code=404)


@ddt.ddt
class TestOwnerPetsV1(BaseServiceTestCase, OwnershipTestMixin):
    collection_url = "/v1/owners/%(owner_id)s/pets/"
    record_url = "/v1/owners/%(owner_id)s/pets/%(pet_id)s"

    def test_list(self):
        owner_id = "35a85559-dc03-4aa2-85d2-947e17e310e5"
        result = self.fetch_json("/v1/owners/%s/pets/" % owner_id)

        self.assertDictEqual({
            "pets": [
                "18e1588a-090e-4ace-94c2-f289617de0cb",
                "4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
            ],
            "links": [
                {
                    "rel": "pet",
                    "href": "/v1/pets/18e1588a-090e-4ace-94c2-f289617de0cb"
                },
                {
                    "rel": "pet",
                    "href": "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
                },
            ]
        }, result)

    def test_list_detailed(self):
        owner_id = "35a85559-dc03-4aa2-85d2-947e17e310e5"
        result = self.fetch_json("/v1/owners/%s/pets/?detail=1" % owner_id)

        self.assertDictEqual({
            "pets": [{
                "id":
                "18e1588a-090e-4ace-94c2-f289617de0cb",
                "name":
                "Scooter",
                "species":
                "mouse",
                "breed":
                "fancy",
                "owners": ["35a85559-dc03-4aa2-85d2-947e17e310e5"],
                "veterinarian":
                None,
                "links": [
                    {
                        "rel": "self",
                        "href": "/v1/pets/18e1588a-090e-4ace-94c2-f289617de0cb"
                    },
                ]
            }, {
                "id":
                "4dc4d7b0-a386-4919-9878-47d4eb8f49ec",
                "name":
                "Scarface",
                "species":
                "dog",
                "breed":
                "English Bulldog",
                "owners": [
                    "35a85559-dc03-4aa2-85d2-947e17e310e5",
                    "5e174bc4-4135-4e7b-b957-9705bacc903d"
                ],
                "veterinarian":
                "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
                "links": [
                    {
                        "rel": "self",
                        "href": "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
                    },
                ]
            }]
        }, result)

    def test_list_limit(self):
        owner_id = "35a85559-dc03-4aa2-85d2-947e17e310e5"
        result = self.fetch_json("/v1/owners/%s/pets/?limit=1" % owner_id)

        self.assertDictEqual({
            "pets": ["18e1588a-090e-4ace-94c2-f289617de0cb"],
            "links": [
                {
                    "rel": "pet",
                    "href": "/v1/pets/18e1588a-090e-4ace-94c2-f289617de0cb"
                },
            ]
        }, result)

    @ddt.data({
        "owner_id": "511363b2-8693-4b30-ae4c-09964a4cebe0",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6"
    }, {
        "owner_id": "511363b2-8693-4b30-ae4c-09964a4cebe0",
        "pet_id": "not-a-real-uuid",
        "code": 400
    }, {
        "owner_id": "511363b2-8693-4b30-ae4c-09964a4cebe0",
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "code": 409
    })
    @ddt.unpack
    def test_add(self, owner_id, pet_id, code=201):
        data = {"pet_id": pet_id}
        result = self.fetch_json(
            "/v1/owners/%s/pets/" % owner_id,
            method="post",
            data=data,
            code=code)
        if 200 <= code < 300:
            self.assertDictEqual(result, {
                "owner":
                owner_id,
                "pet":
                pet_id,
                "links": [{
                    "rel": "owner",
                    "href": "/v1/owners/%s" % owner_id
                }, {
                    "rel": "pet",
                    "href": "/v1/pets/%s" % pet_id
                }]
            })

            # read our writes
            self.assertIn(pet_id,
                          self.fetch_json(
                              "/v1/owners/%s/pets/" % owner_id)["pets"])

    def test_get(self):
        owner_id = "ee5479d6-7070-4109-bfb2-d44e3c42782b"
        pet_id = "72f12e94-33ca-4537-9897-205ffe42350e"
        result = self.fetch_json("/v1/owners/%s/pets/%s" % (owner_id, pet_id))
        self.assertDictEqual(result, {
            "owner": {
                "id":
                "ee5479d6-7070-4109-bfb2-d44e3c42782b",
                "name":
                "Remus Bergfalk",
                "birthday":
                "1977-05-08",
                "shoe_size":
                9.5,
                "pets": [
                    "00182d56-9981-402b-821e-7b1c2906533c",
                    "72f12e94-33ca-4537-9897-205ffe42350e"
                ]
            },
            "pet": {
                "id": "72f12e94-33ca-4537-9897-205ffe42350e",
                "name": "Hellbringer the Befouler",
                "breed": "domestic shorthair",
                "species": "cat",
                "owners": ["ee5479d6-7070-4109-bfb2-d44e3c42782b"],
                "veterinarian": "fd87a620-466d-41ae-a6b0-1527b5126c58"
            },
            "links": [
                {
                    "rel": "owner",
                    "href": "/v1/owners/ee5479d6-7070-4109-bfb2-d44e3c42782b"
                },
                {
                    "rel": "pet",
                    "href": "/v1/pets/72f12e94-33ca-4537-9897-205ffe42350e"
                },
            ]
        })


class TestPetsV1(BaseServiceTestCase, BaseResourceTestMixin):
    collection = "pets"
    base_url = "/v1/pets"

    def test_list_detail(self):
        self.assertDictEqual({
            "pets": [{
                "breed":
                "Shiba Inu",
                "id":
                "a8533344-6371-4982-a86b-722331839514",
                "name":
                "Tenchu",
                "species":
                "dog",
                "owners": ["511363b2-8693-4b30-ae4c-09964a4cebe0"],
                "veterinarian":
                "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
                "links": [
                    {
                        "rel": "self",
                        "href": "/v1/pets/a8533344-6371-4982-a86b-722331839514"
                    },
                    {
                        "rel": "owner",
                        "href":
                        "/v1/owners/511363b2-8693-4b30-ae4c-09964a4cebe0"
                    },
                    {
                        "rel":
                        "veterinarian",
                        "href":
                        "/v1/veterinarians/f5df1cc0-4fa2-4605-af57-4da6479e8afa"
                    },
                ]
            }]
        }, self.fetch_json("/v1/pets/?limit=1&detail=1"))

    def test_get(self):
        url = "/v1/pets/d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
        self.assertDictEqual({
            "id":
            "d25dcdd0-28f4-4fd3-9e5f-da1d9d224940",
            "name":
            "Zeta",
            "species":
            "betta",
            "owners": ["511363b2-8693-4b30-ae4c-09964a4cebe0"],
            "veterinarian":
            None,
            "links": [
                {
                    "rel": "self",
                    "href": "/v1/pets/d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
                },
                {
                    "rel": "owner",
                    "href": "/v1/owners/511363b2-8693-4b30-ae4c-09964a4cebe0"
                },
            ]
        }, self.fetch_json(url))

    def test_add(self):
        new_pet = {"name": "Peanut", "species": "hedgehog"}
        expected_additions = {"owners": [], "veterinarian": None}
        self._test_add(new_pet, expected_additions)

    def test_update_put(self):
        self._test_update("4dc4d7b0-a386-4919-9878-47d4eb8f49ec",
                          {"breed": "French Bulldog"})

    def test_update_patch(self):
        self._test_update(
            "4dc4d7b0-a386-4919-9878-47d4eb8f49ec",
            {"breed": "French Bulldog"},
            method="patch")

    def test_delete(self):
        pet_id = "4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
        self._test_delete(pet_id)

        # deletes cascade properly
        self.assertFalse(any(r["pet"] == pet_id for r in DATA["ownership"]))


@ddt.ddt
class TestPetOwnersV1(BaseServiceTestCase, OwnershipTestMixin):
    collection_url = "/v1/pets/%(pet_id)s/owners/"
    record_url = "/v1/pets/%(pet_id)s/owners/%(owner_id)s"

    def test_list(self):
        pet_id = "00182d56-9981-402b-821e-7b1c2906533c"
        result = self.fetch_json("/v1/pets/%s/owners/" % pet_id)

        self.assertDictEqual({
            "owners": ["ee5479d6-7070-4109-bfb2-d44e3c42782b"],
            "links": [{
                "rel": "owner",
                "href": "/v1/owners/ee5479d6-7070-4109-bfb2-d44e3c42782b"
            }]
        }, result)

    def test_list_detailed(self):
        pet_id = "00182d56-9981-402b-821e-7b1c2906533c"
        result = self.fetch_json("/v1/pets/%s/owners/?detail=1" % pet_id)

        self.assertDictEqual({
            "owners": [{
                "id":
                "ee5479d6-7070-4109-bfb2-d44e3c42782b",
                "name":
                "Remus Bergfalk",
                "birthday":
                "1977-05-08",
                "shoe_size":
                9.5,
                "pets": [
                    "00182d56-9981-402b-821e-7b1c2906533c",
                    "72f12e94-33ca-4537-9897-205ffe42350e"
                ],
                "links": [
                    {
                        "rel": "self",
                        "href":
                        "/v1/owners/ee5479d6-7070-4109-bfb2-d44e3c42782b"
                    },
                ],
            }],
        }, result)

    def test_list_limit(self):
        pet_id = "4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
        result = self.fetch_json("/v1/pets/%s/owners/?limit=1" % pet_id)

        self.assertDictEqual({
            "owners": ["35a85559-dc03-4aa2-85d2-947e17e310e5"],
            "links": [{
                "rel": "owner",
                "href": "/v1/owners/35a85559-dc03-4aa2-85d2-947e17e310e5"
            }]
        }, result)

    @ddt.data({
        "owner_id": "511363b2-8693-4b30-ae4c-09964a4cebe0",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6"
    }, {
        "owner_id": "not-a-real-uuid",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6",
        "code": 400
    }, {
        "owner_id": "511363b2-8693-4b30-ae4c-09964a4cebe0",
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "code": 409
    })
    @ddt.unpack
    def test_add(self, pet_id, owner_id, code=201):
        data = {"owner_id": owner_id}
        result = self.fetch_json(
            "/v1/pets/%s/owners/" % pet_id,
            method="post",
            data=data,
            code=code)
        if 200 <= code < 300:
            self.assertItemsEqual(result, {
                "owner":
                owner_id,
                "pet":
                pet_id,
                "links": [{
                    "rel": "owner",
                    "href": "/v1/owners/%s" % owner_id
                }, {
                    "rel": "pet",
                    "href": "/v1/pets/%s" % pet_id
                }]
            })

            # read our writes
            self.assertIn(owner_id,
                          self.fetch_json(
                              "/v1/pets/%s/owners/" % pet_id)["owners"])

    def test_get(self):
        pet_id = "00182d56-9981-402b-821e-7b1c2906533c"
        owner_id = "ee5479d6-7070-4109-bfb2-d44e3c42782b"
        result = self.fetch_json("/v1/pets/%s/owners/%s" % (pet_id, owner_id))

        self.assertDictEqual({
            "owner": {
                "id":
                "ee5479d6-7070-4109-bfb2-d44e3c42782b",
                "name":
                "Remus Bergfalk",
                "birthday":
                "1977-05-08",
                "shoe_size":
                9.5,
                "pets": [
                    "00182d56-9981-402b-821e-7b1c2906533c",
                    "72f12e94-33ca-4537-9897-205ffe42350e"
                ],
            },
            "pet": {
                "id": "00182d56-9981-402b-821e-7b1c2906533c",
                "name": "Slim",
                "species": "tortoise",
                "breed": u"Hermann's",
                "owners": ["ee5479d6-7070-4109-bfb2-d44e3c42782b"],
                "veterinarian": "3cfbb699-d2f2-45cd-b932-be5171887262"
            },
            "links": [
                {
                    "rel": "owner",
                    "href": "/v1/owners/ee5479d6-7070-4109-bfb2-d44e3c42782b"
                },
                {
                    "rel": "pet",
                    "href": "/v1/pets/00182d56-9981-402b-821e-7b1c2906533c"
                },
            ]
        }, result)


class TestPetVeterinariansV1(BaseServiceTestCase):
    def test_list(self):
        pet_id = "a8533344-6371-4982-a86b-722331839514"
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        result = self.fetch_json("/v1/pets/%s/veterinarians/" % pet_id)

        self.assertDictEqual(result, {
            "veterinarian":
            vet_id,
            "links": [{
                "rel": "veterinarian",
                "href": "/v1/veterinarians/%s" % vet_id
            }, {
                "rel": "patient",
                "href": "/v1/pets/%s" % pet_id
            }]
        })

    def test_list_nonexistent(self):
        self.fetch_json("/v1/pets/not-a-real-uuid/veterinarians/", code=404)

    def test_list_detailed(self):
        pet_id = "a8533344-6371-4982-a86b-722331839514"
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        result = self.fetch_json(
            "/v1/pets/%s/veterinarians/?detail=1" % pet_id)

        self.assertDictEqual(result, {
            "veterinarian": {
                "id": vet_id,
                "name": "Marquita Jepson",
                "specialty": "dogs"
            },
            "links": [{
                "rel": "veterinarian",
                "href": "/v1/veterinarians/%s" % vet_id
            }, {
                "rel": "patient",
                "href": "/v1/pets/%s" % pet_id
            }]
        })


class TestVeterinariansV1(BaseServiceTestCase, BaseResourceTestMixin):
    collection = "veterinarians"
    base_url = "/v1/veterinarians"

    def test_list_detail(self):
        self.assertDictEqual({
            "veterinarians": [{
                "id":
                "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
                "name":
                "Marquita Jepson",
                "specialty":
                "dogs",
                "links": [{
                    "rel":
                    "self",
                    "href":
                    "/v1/veterinarians/f5df1cc0-4fa2-4605-af57-4da6479e8afa"
                }, {
                    "rel":
                    "patient",
                    "href":
                    "/v1/pets/a8533344-6371-4982-a86b-722331839514"
                }, {
                    "rel":
                    "patient",
                    "href":
                    "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
                }]
            }]
        }, self.fetch_json("/v1/veterinarians/?limit=1&detail=1"))

    def test_get(self):
        url = "/v1/veterinarians/f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        self.assertDictEqual({
            "id":
            "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
            "name":
            "Marquita Jepson",
            "specialty":
            "dogs",
            "links": [{
                "rel":
                "self",
                "href":
                "/v1/veterinarians/f5df1cc0-4fa2-4605-af57-4da6479e8afa"
            }, {
                "rel": "patient",
                "href": "/v1/pets/a8533344-6371-4982-a86b-722331839514"
            }, {
                "rel": "patient",
                "href": "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
            }]
        }, self.fetch_json(url))

    def test_add(self):
        new_vet = {"name": "Jovka Garver", "specialty": "livestock"}
        self._test_add(new_vet)

    def test_update_put(self):
        self._test_update("f5df1cc0-4fa2-4605-af57-4da6479e8afa",
                          {"specialty": "livestock"})

    def test_update_patch(self):
        self._test_update(
            "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
            {"name": "Marquita Jepson-Afolayan"},
            method="patch")

    def test_delete(self):
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        self._test_delete(vet_id)

        # deletes cascade properly
        self.assertNotIn(vet_id, DATA["vet assignments"].values())


@ddt.ddt
class AssignmentRecordTestMixin(object):
    base_url = None

    def test_get(self):
        pet_id = "a8533344-6371-4982-a86b-722331839514"
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        result = self.fetch_json(
            self.base_url % {"pet_id": pet_id,
                             "vet_id": vet_id})
        self.assertDictEqual({
            "patient": {
                "id": pet_id
            },
            "veterinarian": {
                "id": vet_id
            },
            "links": [{
                "rel": "self",
                "href": "/v1/pets/%s/veterinarians/%s" % (pet_id, vet_id)
            }, {
                "rel": "veterinarian",
                "href": "/v1/veterinarians/%s" % vet_id
            }, {
                "rel": "patient",
                "href": "/v1/pets/%s" % pet_id
            }]
        }, result)

    @ddt.data({
        "pet_id": "not-a-real-uuid",
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
    }, {
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "vet_id": "not-a-real-uuid"
    }, {
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "vet_id": "3cfbb699-d2f2-45cd-b932-be5171887262"
    })
    @ddt.unpack
    def test_get_nonexistent(self, pet_id, vet_id):
        self.fetch_json(
            self.base_url % {"pet_id": pet_id,
                             "vet_id": vet_id}, code=404)

    @ddt.data({
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "not-a-real-uuid",
        "code": 404
    }, {
        "vet_id": "3cfbb699-d2f2-45cd-b932-be5171887262",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6",
        "code": 201
    }, {
        "vet_id": "3cfbb699-d2f2-45cd-b932-be5171887262",
        "pet_id": "4dc4d7b0-a386-4919-9878-47d4eb8f49ec",
        "code": 200
    }, {
        "vet_id": "not-a-real-uuid",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6",
        "code": 404
    }, {
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "code": 200
    })
    @ddt.unpack
    def test_put(self, pet_id, vet_id, code=201):
        result = self.fetch_json(
            self.base_url % {"pet_id": pet_id,
                             "vet_id": vet_id},
            method="put",
            code=code)
        if 200 <= code < 300:
            self.assertItemsEqual(result, {
                "veterinarian":
                vet_id,
                "patient":
                pet_id,
                "links": [{
                    "rel":
                    "self",
                    "href":
                    "/v1/veterinarians/%s/patients/%s/" % (vet_id, pet_id)
                }, {
                    "rel": "veterinarian",
                    "href": "/v1/veterinarians/%s" % vet_id
                }, {
                    "rel": "patient",
                    "href": "/v1/pets/%s" % pet_id
                }]
            })

            self.assertEqual(DATA["vet assignments"][pet_id], vet_id)

            # read our writes
            self.assertEqual(
                self.fetch_json("/v1/pets/%s" % pet_id)["veterinarian"],
                vet_id)
            self.assertIn(pet_id, [
                r["id"]
                for r in self.fetch_json(
                    "/v1/veterinarians/%s/patients/" % vet_id)["patients"]
            ])

    @ddt.data({
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "not-a-real-uuid",
        "code": 404
    }, {
        "vet_id": "3cfbb699-d2f2-45cd-b932-be5171887262",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6",
        "code": 404
    }, {
        "vet_id": "3cfbb699-d2f2-45cd-b932-be5171887262",
        "pet_id": "00182d56-9981-402b-821e-7b1c2906533c"
    }, {
        "vet_id": "not-a-real-uuid",
        "pet_id": "bf61616c-010e-48f2-8173-78b330804cd6",
        "code": 404
    })
    @ddt.unpack
    def test_delete(self, pet_id, vet_id, code=204):
        self.fetch_json(
            self.base_url % {"pet_id": pet_id,
                             "vet_id": vet_id},
            method="delete",
            code=code)
        if 200 <= code < 300:
            self.assertNotIn(pet_id, DATA["vet assignments"])

            # read our writes
            self.assertIsNone(
                self.fetch_json("/v1/pets/%s" % pet_id)["veterinarian"])
            self.assertNotIn(pet_id, [
                r["id"]
                for r in self.fetch_json(
                    "/v1/veterinarians/%s/patients/" % vet_id)["patients"]
            ])


class TestPetsVetV1(BaseServiceTestCase, AssignmentRecordTestMixin):
    base_url = "/v1/pets/%(pet_id)s/veterinarians/%(vet_id)s"


@ddt.ddt
class TestVeterinarianPatientsV1(BaseServiceTestCase,
                                 AssignmentRecordTestMixin):
    base_url = "/v1/veterinarians/%(vet_id)s/patients/%(pet_id)s"

    def test_list(self):
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        result = self.fetch_json("/v1/veterinarians/%s/patients/" % vet_id)

        self.assertDictEqual(result, {
            "patients": [{
                "id":
                "a8533344-6371-4982-a86b-722331839514",
                "links": [{
                    "rel":
                    "self",
                    "href":
                    "/v1/pets/a8533344-6371-4982-a86b-722331839514"
                }],
            }, {
                "id":
                "4dc4d7b0-a386-4919-9878-47d4eb8f49ec",
                "links": [{
                    "rel":
                    "self",
                    "href":
                    "/v1/pets/4dc4d7b0-a386-4919-9878-47d4eb8f49ec"
                }],
            }],
            "links": [{
                "rel": "veterinarian",
                "href": "/v1/veterinarians/%s" % vet_id
            }]
        })

    def test_list_nonexistent_vet(self):
        self.fetch_json(
            "/v1/veterinarians/not-a-real-uuid/patients/", code=404)

    def test_list_limit(self):
        vet_id = "f5df1cc0-4fa2-4605-af57-4da6479e8afa"
        result = self.fetch_json(
            "/v1/veterinarians/%s/patients/?limit=1" % vet_id)
        pet_id = "a8533344-6371-4982-a86b-722331839514"

        self.assertDictEqual(result, {
            "patients": [
                {
                    "id": pet_id,
                    "links": [{
                        "rel": "self",
                        "href": "/v1/pets/%s" % pet_id
                    }]
                },
            ],
            "links": [{
                "rel": "veterinarian",
                "href": "/v1/veterinarians/%s" % vet_id
            }]
        })

    def test_list_detailed(self):
        vet_id = "3cfbb699-d2f2-45cd-b932-be5171887262"
        result = self.fetch_json(
            "/v1/veterinarians/%s/patients/?detail=1" % vet_id)

        self.assertDictEqual(result, {
            "patients": [
                {
                    "id":
                    "00182d56-9981-402b-821e-7b1c2906533c",
                    "name":
                    "Slim",
                    "species":
                    "tortoise",
                    "breed":
                    "Hermann's",
                    "links": [
                        {
                            "rel": "self",
                            "href":
                            "/v1/pets/00182d56-9981-402b-821e-7b1c2906533c"
                        },
                    ],
                    "owners": ["ee5479d6-7070-4109-bfb2-d44e3c42782b"],
                    "veterinarian":
                    "3cfbb699-d2f2-45cd-b932-be5171887262",
                },
            ],
            "links": [
                {
                    "rel":
                    "veterinarian",
                    "href":
                    "/v1/veterinarians/3cfbb699-d2f2-45cd-b932-be5171887262"
                },
            ]
        })

    @ddt.data({
        "vet_id": "not-a-real-uuid",
        "pet_id": "72f12e94-33ca-4537-9897-205ffe42350e",
        "code": 404
    }, {
        "vet_id": "fd87a620-466d-41ae-a6b0-1527b5126c58",
        "pet_id": "not-a-real-uuid",
        "code": 400
    }, {
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "a8533344-6371-4982-a86b-722331839514",
        "code": 409
    }, {
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "00182d56-9981-402b-821e-7b1c2906533c",
        "code": 409
    }, {
        "vet_id": "f5df1cc0-4fa2-4605-af57-4da6479e8afa",
        "pet_id": "d25dcdd0-28f4-4fd3-9e5f-da1d9d224940"
    })
    @ddt.unpack
    def test_add(self, vet_id, pet_id, code=201):
        data = {"pet_id": pet_id}
        result = self.fetch_json(
            "/v1/veterinarians/%s/patients/" % vet_id,
            method="post",
            data=data,
            code=code)
        if 200 <= code < 300:
            expected = {
                "veterinarian": {
                    "id": vet_id
                },
                "patient": {
                    "id": pet_id
                },
                "links": [{
                    "rel": "veterinarian",
                    "href": "/v1/veterinarians/%s" % vet_id
                }, {
                    "rel": "patient",
                    "href": "/v1/pets/%s" % pet_id
                }, {
                    "rel":
                    "self",
                    "href":
                    "/v1/pets/%s/veterinarian/%s" % (pet_id, vet_id)
                }]
            }

            self.assertItemsEqual(result, expected)

            self.assertEqual(DATA["vet assignments"][pet_id], vet_id)

            # read our writes
            self.assertEqual(
                self.fetch_json("/v1/pets/%s" % pet_id)["veterinarian"],
                vet_id)
            self.assertIn(pet_id, [
                r["id"]
                for r in self.fetch_json(
                    "/v1/veterinarians/%s/patients/" % vet_id)["patients"]
            ])


if __name__ == "__main__":
    unittest.main()
