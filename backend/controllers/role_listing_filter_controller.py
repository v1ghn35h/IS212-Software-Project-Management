from flask import request, jsonify
from database import db
from sqlalchemy import or_
from models.role_listing import RoleListing
from models.role import Role 
from models.category import Category
from models.staff import Staff
from blueprints.staff_blueprint import staff_blueprint
from models.staff_skill import StaffSkill
from models.role_skill import RoleSkill 
# from .role_skill_match_controller import role_skill_match
from .role_listing_controller import filter_listings_by_staff_and_deadline

# HELPER FUNCTION TO GET ROLE SKILL MATCH
def role_skill_match(staff_id, role_name):
    try:
        # Get all the skills based on the roles
        role_skills = [rs.skill_name for rs in RoleSkill.query.filter_by(role_name=role_name).all()]

        # Get all the skills that the staff has
        staff_skills = [ss.skill_name for ss in StaffSkill.query.filter_by(staff_id=staff_id).all()]

        # Determine skills that staff have and don't have based on the role's requirements
        staff_have = [skill for skill in role_skills if skill in staff_skills]
        staff_dont = [skill for skill in role_skills if skill not in staff_skills]

        # Calculate the percentage of roles matched
        match_percentage = round((len(staff_have) / (len(staff_have) + len(staff_dont))) * 100)

        return {
            "code": 200,
            "data": {
                "have": staff_have,
                "dont": staff_dont,
                "match_percentage": str(match_percentage)
            }
        }
    except Exception as e:
        # Return an error in a dictionary format
        return {
            "code": 500,
            "error": str(e)
        }

# HELPER FUNCTION TO GET ROLE LISTINGS WITHIN THE MATCH PERCENTAGE RANGE
def get_match_percentage_records(role_listings_query, match_percentage, staff_id):
        results = []
        # Get the upper and lower bound of the match percentage filter
        bounds = match_percentage.split('-')
        lower_bound = int(bounds[0])
        upper_bound = int(bounds[1])

        # For each role listing, get the role skill match and check if its between the match percentage
        for role_listing in role_listings_query:
            skill_match = role_skill_match(staff_id, role_listing.role_name)
            # If the skill match is successful
            if skill_match['code'] == 200:
                match_percentage = int(float(skill_match['data']["match_percentage"]))
                # Check if match percentage if between the lower and upper bound
                if match_percentage >= lower_bound and match_percentage <= upper_bound:
                    # Append the role listing to results if its between the bounds
                    results.append(role_listing)
        return results

# HELPER FUNCTION TO GET THE ROLE DESC AND THE SKILL MATCH TO RETURN BACK TO FRONTEND
def get_results(role_listings_query, staff_id):
        results = []

        # For each role listing, get the role skill match and check if its between the match percentage
        for role_listing in role_listings_query:
            skill_match = role_skill_match(staff_id, role_listing.role_name)
            # If the skill match is successful
            if skill_match['code'] == 200:
                # Get the role description
                roles = Role.query.filter_by(role_name=role_listing.role_name).first()
                role_desc = roles.role_desc
                listing = role_listing.json()
                # Add the role description to the role listing
                listing["role_desc"] = role_desc
                # Append the role listing information and the skill match information to results
                results.append({
                    "role_listing": listing,
                    "role_skill_match": skill_match['data']
                })
        return results

####################################################################################################################################

# STAFF: GET ALL FILTER OPTIONS 
@staff_blueprint.route('/filter_options', methods=['GET'])
def get_filter_options():
    try:
        # Get all the categories in the database
        categories = Category.query.all()

        result_category = []
        for category in categories:
            # Check if category is unique
            if category.category not in result_category:
                result_category.append(category.category)

        # Get all the staff in the database
        staffs = Staff.query.all()

        result_dept = []
        for staff in staffs:
            if staff.dept not in result_dept:
                result_dept.append(staff.dept)

        if result_category and result_dept:
            return jsonify({"code": 200, "data": {"department": result_dept, "category": result_category}}), 200
        else:
            return jsonify({"code": 404, "message": "Was no able to retrieve filter options"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
        
    

# STAFF: GET THE FILTERED ROLE LISTINGS
@staff_blueprint.route('/filter_role_listings/<int:staff_id>', methods=['GET'])
def get_filtered_roles(staff_id):
    try:

        # Extract data from the request
        data = request.get_json() 

        # Check if any one of the filter option is chosen
        if len(data['category']) == 0 and len(data["department"]) == 0 and len(data['match_percentage']) == 0:
            return jsonify({"code": 404, "message": "No filter options were chosen."}), 404

        all_role_listings = RoleListing.query
        # Get all role listing applicable for the staff
        avaliable_role_listings = filter_listings_by_staff_and_deadline(all_role_listings, staff_id).all()

        role_listings_query = []

        # If both category and department are in the filter options
        if len(data['category']) != 0 and len(data["department"]) != 0:
            # Get the list of department and category from the filter options
            filter_category = data['category']
            filter_department = data['department']

            # For each role listing, check if it has the given department
            for role_listing in avaliable_role_listings:
                if role_listing.department in filter_department:
                    # Check if the role listing has the given category
                    if role_listing.category in filter_category:
                        # Append to the role_listings_query list if it has both
                        role_listings_query.append(role_listing)
        
        # If only category is in the filter option
        elif len(data['category']) != 0 :
            # Get the list of department and category from the filter options
            filter_category = data['category']

            # For each role listing, check if it has the given category
            for role_listing in avaliable_role_listings:
                if role_listing.category in filter_category:
                    # Append to the role_listings_query list if it has both
                    role_listings_query.append(role_listing)
        
        # If only department is in the filter option
        elif len(data["department"]) != 0:
            # Get the list of department and category from the filter options
            filter_department = data['department']

            # For each role listing, check if it has the given department
            for role_listing in avaliable_role_listings:
                if role_listing.department in filter_department:
                    # Append to the role_listings_query list if it has both
                    role_listings_query.append(role_listing)        
        
        match_results = []
        # If match percentage if in the filter option along with the other filter options
        if len(data['match_percentage']) != 0 and len(role_listings_query) != 0:
            match_results = get_match_percentage_records(role_listings_query, data['match_percentage'], staff_id)
        # If only match percentage is in the filter option
        elif len(data['match_percentage']) != 0:
            match_results = get_match_percentage_records(avaliable_role_listings, data['match_percentage'], staff_id)
        # If only category and/or department are in the filter option
        
        # If there are match results then return the match results
        if match_results:
            results = get_results(match_results, staff_id)
            return jsonify({"code": 200, "data": {"role_listings": results}}), 200
        # If match percentage was not chosen as a filter option return role listing query results if there are any
        elif role_listings_query:
            results = get_results(role_listings_query, staff_id)
            return jsonify({"code": 200, "data": {"role_listings": results}}), 200
        # Else return that no role listings were found
        else:
            return jsonify({"code": 404, "message": "No role listings found for the given filter options."}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)), 500
