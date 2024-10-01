import google.generativeai as genai
import re
from dotenv import load_dotenv
import os

from real_estate_calculator import RentalPropertyCalculator

# Initialize the Google Gemini API
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

property_data_sample = {
    'monthly_rent': None,
    'additional_monthly_income': 0,  # Added some additional income
    'vacancy_rate': 5,  # Adjusted vacancy rate
    'mortgage_monthly_payment': None,
    'property_monthly_taxes': None,  # Adjusted property taxes
    'insurance_monthly': None,  # Adjusted insurance_monthly
    'hoa_fees_monthly': 0,  # Added HOA fees
    'maintenance_monthly': 100,  # Adjusted maintenance_monthly
    'property_management_monthly_fees': 0,  # Added property management fees
    'utilities_monthly': 0,
    'advertising_monthly': 0,
    'other_expenses_monthly': 0,  # Added other expenses
    'capex_annual': None,  # Added capex_annual
    'tax_rate': 25,  # Adjusted tax rate
    'depreciation_anual': 0,
    'total_investment': None,  # Adjusted total investment
    'property_value': None,  # Adjusted property value
    'appreciation_rate': 3,  # Adjusted appreciation rate
}


def identify_missing_keys(property_data):
    """Identifies keys with missing (None) values."""
    return [key for key, value in property_data.items() if value is None]


def create_prompts(property_data, missing_keys):
    """Creates prompts for required and optional values."""
    required_prompts = [f"Please enter the {key.replace('_', ' ')}:" for key in missing_keys]
    optional_prompts = [
        f"* {key.replace('_', ' ')}: {value}"
        for key, value in property_data.items() if value is not None
    ]
    return required_prompts, optional_prompts


def extract_answer_from_response(response_text):
    """
    Extracts the user's numeric answer from the Gemini response text.
    """

    # Use regular expressions to find numeric values in the response
    numeric_values = re.findall(r"[-+]?\d*\.?\d+", response_text)

    if numeric_values:
        # If multiple numeric values are found, take the last one
        # (assuming it's the most likely answer)
        user_answer = numeric_values[-1]
    else:
        # Handle the case where no numeric value is found
        raise ValueError("No numeric value found in the response. Please provide a numerical answer.")

    return user_answer


def is_valid_numeric_input(user_input, key):
    """Checks if the user input is a valid numeric value for the given key."""
    try:
        if key in ['vacancy_rate', 'tax_rate', 'appreciation_rate']:
            value = float(user_input) / 100
            if not 0 <= value <= 1:
                return False
        else:
            value = float(user_input)
            if value < 0:
                return False
        return True
    except ValueError:
        return False


def get_user_input_with_gemini(prompt):
    """Gets user input via Gemini, handling dialog for numeric validation."""
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", )

    while True:
        print(prompt)
        user_input = input("Your answer: ")

        key = get_corresponding_key(prompt)

        # Check if key is None before proceeding
        if key is None:
            print("Invalid input. Please try again.")
            continue  # Go back to the start of the loop

        if is_valid_numeric_input(user_input, key):
            return user_input
        else:
            validation_prompt = f"Please provide a valid numeric value for {key.replace('_', ' ')}."
            validation_response = model.generate_content(validation_prompt)
            print(validation_response.text)


def validate_and_convert_input(user_input, key):
    """Validates and converts user input to the appropriate data type."""
    try:
        if key in ['vacancy_rate', 'tax_rate', 'appreciation_rate']:
            value = float(user_input) / 100
            if not 0 <= value <= 1:
                raise ValueError(f"{key.replace('_', ' ')} must be between 0 and 100%")
        else:
            value = float(user_input)
            if value < 0:
                raise ValueError(f"{key.replace('_', ' ')} cannot be negative")
        return value
    except ValueError as e:
        raise e  # Re-raise the ValueError for the outer loop to handle


def get_corresponding_key(prompt):
    """Maps a prompt to its corresponding key in the property_data dictionary."""

    key_mapping = {
        "Please enter the monthly rent:": 'monthly_rent',
        "Please enter the additional monthly income:": 'additional_monthly_income',
        "Please enter the vacancy rate:": 'vacancy_rate',
        "Please enter the mortgage monthly payment:": 'mortgage_monthly_payment',
        "Please enter the property monthly taxes:": 'property_monthly_taxes',
        "Please enter the insurance monthly:": 'insurance_monthly',
        "Please enter the monthly HOA fees:": 'hoa_fees_monthly',
        "Please enter the monthly maintenance & repairs (estimated monthly average):": 'maintenance_monthly',
        "Please enter the monthly property management fees:": 'property_management_monthly_fees',
        "Please enter the monthly utilities (if paid by landlord):": 'utilities_monthly',
        "Please enter the monthly advertising:": 'advertising_monthly',
        "Please enter the other monthly expenses:": 'other_expenses_monthly',
        "Please enter the capex annual:": 'capex_annual',
        "Please enter the tax rate:": 'tax_rate',
        "Please enter the annual depreciation_anual:": 'depreciation_anual',
        "Please enter the total investment:": 'total_investment',
        "Please enter the property value:": 'property_value',
        "Please enter the appreciation rate:": 'appreciation_rate'
    }

    # Handle optional prompts (assuming they start with "Would you like to update the...")
    if prompt.startswith("Would you like to update the "):
        key = prompt.replace("Would you like to update the ", "").replace(" (currently ", ": ").replace(")? (yes/no)",
                                                                                                        "")
        key = key.strip().replace(' ', '_')  # Convert spaces to underscores
        return key

    # Return the corresponding key from the mapping, or None if not found
    return key_mapping.get(prompt)


def update_property_data(property_data, prompt, user_input):
    """Updates property_data based on user input."""
    key = get_corresponding_key(prompt)
    validated_input = validate_and_convert_input(user_input, key)
    property_data[key] = validated_input


def process_user_updates(property_data):
    """Processes user input to update optional values in property_data."""

    while True:
        user_input = input("Would you like to update any of these values? (yes/no): ")
        if user_input.lower() == 'no':
            return

        elif user_input.lower() == 'yes':
            while True:
                user_input = input(
                    "Please specify which value and its new value in the format 'key: value' (e.g., 'additional_monthly_income: 50'), or type 'done' to finish: ")

                if user_input.lower() == 'done':
                    break  # Exit the inner loop when the user types "done"

                else:
                    try:
                        key, value = user_input.split(':')
                        key = key.strip().replace(' ', '_')
                        if key not in property_data:
                            raise ValueError(f"Invalid key: '{key}'. Please check the available options.")

                        validated_input = validate_and_convert_input(value.strip(), key)
                        property_data[key] = validated_input
                        print(f"Updated {key.replace('_', ' ')} to {validated_input}")

                    except ValueError as e:
                        print(f"Error processing update '{user_input}': {e}. Please try again.")

            break  # Exit the outer loop after updates are done

        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def collect_property_data_with_gemini(property_data):
    """Main function to collect property data, with improved error handling and clarity."""

    missing_keys = identify_missing_keys(property_data)

    # Create prompts for required and optional values
    required_prompts, optional_prompts = create_prompts(property_data, missing_keys)

    # Collect required values
    if required_prompts:
        print("Let's start by gathering some essential information about the property.")
        for prompt in required_prompts:
            try:
                user_input = get_user_input_with_gemini(prompt)
                update_property_data(property_data, prompt, user_input)
            except ValueError as e:  # Catch potential validation errors
                print(f"Error: {e}. Please try again.")

    # Present optional values for updates
    if optional_prompts:
        optional_values_text = "\n".join(optional_prompts)
        user_input = input(f"\nHere are some additional details we have about the property:\n"
                           f"{optional_values_text}\n\n"
                           "Would you like to update any of these values?\n"
                           "If yes, please specify which value and its new value in the format 'key: value' (e.g., 'additional_monthly_income: 50').\n"
                           "If not, just say 'no'. \n")
        if user_input.lower() == 'no':
            return property_data
        for prompt in optional_prompts:
            try:
                update_property_data(property_data, prompt, user_input)
            except Exception as e:  # Catch potential errors during update processing
                print(f"Error processing updates: {e}. Please try again.")

    return property_data


def generate_agent_response(user_query, property_data):
    # Construct a prompt that incorporates the user query and relevant property data
    prompt = f"""
    You are a helpful real estate agent. 
    A user has asked the following question about a property:

    Question: {user_query}

    Here's the available information about the property:
    {property_data}

    Please provide a clear and concise answer that directly addresses the user's question, using the property data whenever relevant. 
    If the question is not related to real estate or the provided property data, politely indicate that you can't help with that specific query.
    """

    # Generate a response using the Gemini API
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    response = model.generate_content(prompt)

    # Extract and return the generated text
    return response.text


def interact_with_real_estate_agent():
    """Enables user interaction with a real estate agent,
    collecting property data first and then answering questions."""

    property_calculator = RentalPropertyCalculator()

    # 1. Collect property data from the user
    property_data = collect_property_data_with_gemini(property_data_sample)

    # 2. Perform calculations (if needed)
    property_calculator.calculate_metrics(property_data)

    property_calculator.display_results(property_data)
    property_calculator.compare_with_market(property_data)

    # 3. Interact with the agent
    print("\nGreat! Now you can ask me questions about the property or real estate in general.")

    while True:
        user_query = input("You: ")

        if user_query.lower() in ["exit", "quit", "goodbye"]:
            print("Agent: Goodbye! Feel free to reach out again if you have any more questions.")
            break

        response = generate_agent_response(user_query, property_data)
        print("Agent:", response)