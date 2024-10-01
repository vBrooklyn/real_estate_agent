from attom_api import AttomApi

# attom_api = AttomApi()

property_data_sample = {
    'monthly_rent': 2800,
    'additional_monthly_income': 0,  # Added some additional income
    'vacancy_rate': 5,  # Adjusted vacancy rate
    'mortgage_monthly_payment': 1500,
    'property_monthly_taxes': 250,  # Adjusted property taxes
    'insurance_monthly': 150,  # Adjusted insurance_monthly
    'hoa_fees_monthly': 50,  # Added HOA fees
    'maintenance_monthly': 150,  # Adjusted maintenance_monthly
    'property_management_monthly_fees': 0,  # Added property management fees
    'utilities_monthly': 0,
    'advertising_monthly': 0,
    'other_expenses_monthly': 0,  # Added other expenses
    'capex_anual': 1000,  # Added capex_anual
    'tax_rate': 25,  # Adjusted tax rate
    'depreciation_anual': 0,
    'total_investment': 50000,  # Adjusted total investment
    'property_value': 300000,  # Adjusted property value
    'appreciation_rate': 3,  # Adjusted appreciation rate
}


class RentalPropertyCalculator:
    def __init__(self):
        # Default market averages (can be overridden by user input)
        self.market_average_cash_on_cash_return = 8
        self.market_average_cap_rate = 6
        self.market_average_appreciation_rate = 3  # 3%
        self.market_average_annualized_return = 10  # Or get this from user input

        # Dictionary to store property data
        self.property_data = {}

    def calculate_metrics(self, property_data: dict):
        """Performs all the calculations based on the property_data."""

        # Calculate Total Monthly Income
        property_data['total_monthly_income'] = property_data['monthly_rent'] + property_data['additional_monthly_income']

        # Calculate Vacancy Loss
        property_data['vacancy_loss'] = property_data['total_monthly_income'] * property_data['vacancy_rate']

        # Calculate Effective Monthly Income
        property_data['effective_monthly_income'] = property_data['total_monthly_income'] - property_data['vacancy_loss']

        # Calculate Total Monthly Expenses
        property_data['total_monthly_expenses'] = sum([
            property_data['mortgage_monthly_payment'],
            property_data['property_monthly_taxes'],
            property_data['insurance_monthly'],
            property_data['hoa_fees_monthly'],
            property_data['maintenance_monthly'],
            property_data['property_management_monthly_fees'],
            property_data['utilities_monthly'],
            property_data['advertising_monthly'],
            property_data['other_expenses_monthly']
        ])

        # Calculate Annual Expenses (excluding mortgage for NOI calculation)
        property_data['annual_expenses'] = (property_data['total_monthly_expenses'] - property_data['mortgage_monthly_payment']) * 12

        # Calculate Cash Flow Metrics
        property_data['monthly_cash_flow'] = property_data['effective_monthly_income'] - property_data['total_monthly_expenses']
        property_data['annual_cash_flow'] = property_data['monthly_cash_flow'] * 12

        # Calculate Annualized Return (ROI)
        property_data['annualized_return'] = ((property_data['annual_cash_flow'] + (
                property_data['property_value'] * property_data['appreciation_rate'])) /
                                              property_data['total_investment']) * 100

        # Calculate Cap Rate
        noi = (property_data['monthly_rent'] * 12) - property_data['annual_expenses']
        property_data['noi'] = noi
        property_data['cap_rate'] = (noi / property_data['property_value']) * 100

        # Calculate Debt Service Coverage Ratio (DSCR)
        annual_debt_service = property_data['mortgage_monthly_payment'] * 12
        property_data['dscr'] = noi / annual_debt_service

        # Calculate Annual Taxable Income
        annual_taxable_income = noi - property_data['depreciation_anual']

        # Calculate Annual Taxes
        annual_taxes = annual_taxable_income * property_data['tax_rate']

        # Calculate After-Tax Cash Flow
        after_tax_cash_flow = property_data['annual_cash_flow'] - annual_taxes

        # Update Cash_on_Cash Return and Annualized Return using after-tax cash flow
        property_data['after_tax_cash_flow'] = after_tax_cash_flow
        property_data['cash_on_cash_return'] = (after_tax_cash_flow / property_data['total_investment']) * 100
        property_data['annualized_return'] = ((after_tax_cash_flow + (
                property_data['property_value'] * property_data['appreciation_rate'])) /
                                              property_data['total_investment']) * 100
        return property_data

    def compare_with_market(self, property_data: dict):
        """Compares calculated metrics with market averages and prints the results."""

        print("\nComparison with Market Averages:")

        for metric, value in [
            ('Cash_on_Cash Return', property_data['cash_on_cash_return']),
            ('Cap Rate', property_data['cap_rate']),
            ('Appreciation Rate', property_data['appreciation_rate'] * 100),
            ('Annualized Return', property_data['annualized_return'])
        ]:
            if metric == 'Cash_on_Cash Return':
                market_average = self.market_average_cash_on_cash_return
            else:
                market_average = getattr(self, f'market_average_{metric.lower().replace(" ", "_")}')

            if value > market_average:
                print(f"  - {metric} ({value:.2f}%) is ABOVE average ({market_average:.2f}%).")
            else:
                print(f"  - {metric} ({value:.2f}%) is BELOW average ({market_average:.2f}%).")
            if metric == 'Annualized Return':
                market_average = self.market_average_cash_on_cash_return  # Using CoC return as benchmark
            else:
                market_average = getattr(self, f'market_average_{metric.lower().replace(" ", "_")}')

    def display_results(self, property_data: dict):
        """Prints all the calculated metrics and the comparison with market averages."""

        print("\nIncome:")
        for key in ['monthly_rent', 'additional_monthly_income', 'total_monthly_income', 'vacancy_rate', 'vacancy_loss',
                    'effective_monthly_income']:
            print(f"  - {key.replace('_', ' ').title()}: ${property_data[key]:.2f}")

        print("\nExpenses:")
        for key in ['mortgage_monthly_payment', 'property_monthly_taxes', 'insurance_monthly', 'hoa_fees_monthly',
                    'maintenance_monthly',
                    'property_management_monthly_fees', 'utilities_monthly', 'advertising_monthly',
                    'other_expenses_monthly', 'total_monthly_expenses']:
            print(f"  - {key.replace('_', ' ').title()}: ${property_data[key]:.2f}")

        print("\nCash Flow:")
        for key in ['monthly_cash_flow', 'annual_cash_flow', 'cash_on_cash_return']:
            print(
                f"  - {key.replace('_', ' ').title()}: ${property_data[key]:.2f}" if key != 'cash_on_cash_return' else f"  - {key.replace('_', ' ').title()}: {property_data[key]:.2f}%")

        print("\nAdditional Metrics:")
        for key in ['noi', 'cap_rate', 'dscr']:
            print(f"  - {key.upper()}: ${property_data[key]:.2f}")

        print("\nROI:")
        for key in ['total_investment', 'property_value', 'appreciation_rate', 'annualized_return']:
            if key == 'appreciation_rate':
                print(f"  - {key.replace('_', ' ').title()}: {property_data[key] * 100:.2f}%")
            else:
                print(f"  - {key.replace('_', ' ').title()}: ${property_data[key]:.2f}")

        # Print After-Tax Cash Flow
        print("\nAfter-Tax Cash Flow:")
        print(f"  - Annual After-Tax Cash Flow: ${property_data['after_tax_cash_flow']:.2f}")