from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import ok, get_model_by_id, delete_instance_by_id, validate_admin
from app.blueprints.organization.schemas import (
    QueryInputGetOrganization,
    QueryInputPutOrganization,
    QueryInputPostOrganization,
    QueryInputDeleteOrganization,
    OrganizationResponse,
    OrganizationIdResponse,
    OrganizationListResponse,
    OrganizationSchema
)
from app.persistence.models.organization_model import Organization
from app.persistence.session import get_session

bp = Blueprint('Organization', __name__, description='Operations on organization')


@bp.route('/organization')
class OrganizationAPI(MethodView):

    @login_required
    @validate_admin
    @bp.arguments(QueryInputGetOrganization, location='query')
    @bp.response(200, OrganizationResponse())
    def get(self, args):
        """Get organization by id"""
        organization_id = args.get("id")
        if organization_id is None:
            logger.info("Fetching all organizaciones")
            organizations = get_session().query(
                Organization
            ).filter(
                Organization.deleted_at.is_(None)
            ).all()
            return ok(OrganizationListResponse().dump(
                {"data": OrganizationSchema().dump(organizations, many=True)})
            )
        else:
            organization = get_model_by_id(organization_id, Organization, "Organization")
            logger.info(f"Fetching box con id {organization_id}.")
            return ok(OrganizationResponse().dump({"data": organization}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPostOrganization)
    @bp.response(200, OrganizationResponse())
    def post(self, args):
        """Add new organization"""

        logger.debug("Handling add organization request")
        organization = Organization(name=args['name'], description=args["description"])

        logger.info(f"Adding organization {organization}")
        get_session().add(organization)
        get_session().commit()
        return ok(OrganizationResponse().dump({"data": organization}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputDeleteOrganization, location='query')
    @bp.response(200, OrganizationIdResponse())
    def delete(self, args):
        """Delete an organization"""
        organization_id = args["id"]
        logger.info(f"Deleting organization {organization_id}")
        delete_instance_by_id(organization_id, Organization, "Organization")
        return ok(OrganizationIdResponse().dump({"data": {"id": organization_id}}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPutOrganization)
    @bp.response(200, OrganizationResponse())
    def put(self, args):
        """Modify organization details"""

        organization = get_model_by_id(args["id"], Organization, "Organization")
        logger.info(f"Editing organization {organization}")

        if args.get('description') is not None:
            organization.description = args.get('description')
        if args.get('name') is not None:
            organization.name = args.get('name')

        get_session().add(organization)
        get_session().commit()
        return ok(OrganizationResponse().dump({"data": organization}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
