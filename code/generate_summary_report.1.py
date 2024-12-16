import pandas as pd


def generate_summary_report(input_csv, output_csv):
    try:
        # Read the CSV file
        data = pd.read_csv(input_csv)

        # Print the first few rows of the data for initial validation
        print("Data Preview:")
        print(data.head())

        # Generate summary statistics
        summary = data.describe(include="all")

        # Optionally, count unique values for categorical columns
        unique_counts = data.nunique()

        # Concatenate the summary and unique counts into one report
        report = pd.concat([summary, unique_counts.rename("Unique Counts")], axis=1)

        # Write the summary report to a new CSV file
        report.to_csv(output_csv)
        print(f"Summary report generated: {output_csv}")

    except FileNotFoundError:
        print(f"Error: The file {input_csv} was not found.")
    except pd.errors.EmptyDataError:
        print("Error: No data found in the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


# Example usage
generate_summary_report("input_data.csv", "summary_report.csv")
