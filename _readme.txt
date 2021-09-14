This is a submission to the entry task for Kiwi's Python weekend. The submission was done by Jakub Novotny.

Code for this submission is in the solution.py file. Example calls could be:
	python solution.py example/example0.csv ECV WIW
	python solution.py example/example0.csv ECV WIW --bags 1 --return True
As you can see, there are five parameters:
	1st parameter: Python code location
	2nd parameter: a path to the csv with information on flights data
	3rd parameter: origin from which one wants to fly
	4rd parameter: destination to which one wants to travel
	5th parameter: number of bags one wants carry. The code finds only such combinations of flights that meet this condition on the whole journey. This parameter is optional. If not present, it defaults to 0.
	6th parameter: if it is one way or return flight

The code uses four helper functions(input_validation, readin_csv, first_run, following_runs, json_output) and one main function that uses the helper functions.
input_validation validates the input supplied from the user and tries to catch most obvious errors.
read_in csv reads the csv file for further processing.
first_run function is responsible for looking through the files and finding the first suitable segment of the journey.
following_runs goes on, provided any journeys from the origin have been found.