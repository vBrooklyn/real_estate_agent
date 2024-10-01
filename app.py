from flask import Flask, render_template, request, session

from real_estate_calculator import RentalPropertyCalculator
from real_estate_agent import *

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management


@app.route("/", methods=["GET", "POST"])
def index():
    if "property_data" not in session:
        session["property_data"] = property_data_sample.copy()
    property_data = session["property_data"]
    property_calculator = RentalPropertyCalculator()

    if request.method == "POST":
        if "user_query" in request.form:
            user_query = request.form["user_query"]
            response = generate_agent_response(user_query, property_data)
            return render_template("index.html", user_query=user_query, agent_response=response, property_data=property_data, show_results=True)

        elif "reset_form" in request.form:
            session.pop("property_data", None)
            return render_template("index.html", property_data=property_data_sample.copy())

        else:  # Collect property data
            for key in property_data_sample:
                try:
                    input_value = request.form[key.replace('_', ' ')]
                    try:
                        property_data[key] = float(input_value)
                    except ValueError:
                        property_data[key] = input_value
                except KeyError:
                    return "Missing property data. Please fill in all fields."

            property_calculator.calculate_metrics(property_data)
            session["property_data"] = property_data

            results = property_calculator.display_results(property_data)
            comparisons = property_calculator.compare_with_market(property_data)
            return render_template("index.html", property_data=property_data, results=results, comparisons=comparisons, show_results=True)

    # Sort property_data before rendering
    sorted_property_data = dict(sorted(property_data.items(), key=lambda item: item[1] is None, reverse=True))

    return render_template("index.html", property_data=sorted_property_data)

if __name__ == "__main__":
    app.run(debug=True)