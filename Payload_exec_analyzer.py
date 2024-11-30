import re

# Initialize counters for success, failure, total requests, and XSS attempts
success_count = 0
failure_count = 0
xss_attempts = 0  # Counter for XSS attempts

# Initialize a list to store analyzed results
analyzed_results = []

# Open the results.txt file for reading
with open('results.txt', 'r') as result_file:
    # Read each line in the file
    for line in result_file:
        # Extract relevant data using regex
        match = re.search(r'POST (.*?) with payload:.*?param=(.*?) - Status: (\d+)', line)
        if match:
            url = match.group(1)
            payload = match.group(2)
            status = match.group(3)

            # Increment the XSS attempts count for each payload
            xss_attempts += 1

            # Analyze the response for success
            success = "No"
            if "alert('XSS')" in payload:  # Adjust this condition based on your criteria
                success = "Yes"
                success_count += 1
            else:
                failure_count += 1

            # Format the output for readability
            analyzed_results.append(
                f"URL: {url}\nPayload: {payload}\nStatus: {status}\nXSS Successful: {success}\n{'-'*50}"
            )

# Write the analyzed results to analysis_results.txt
with open('analysis_results.txt', 'w') as analysis_file:
    # Write the counts at the start of the file
    analysis_file.write(f"Total XSS Attempts: {xss_attempts}\n")
    analysis_file.write(f"Total Successful XSS Attempts: {success_count}\n")
    analysis_file.write(f"Total Failed XSS Attempts: {failure_count}\n")
    analysis_file.write("\n--- Analyzed Results ---\n\n")
    
    for result in analyzed_results:
        analysis_file.write(result + "\n")
