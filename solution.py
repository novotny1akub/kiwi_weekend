# https://github.com/kiwicom/python-weekend-ba-task

import argparse
import os
import datetime
import csv
import json

# catching variables supplied by the user OR ones defined in the Spyder IDE for convenience
if any('SPYDER' in name for name in os.environ):
    os.chdir(r"C:\Users\novotny\Desktop\covid\kiwi_weekend\kiwi_weekend")
    csv_path="example\example3.csv"
    origin = "WUE"
    destination = "JBN"
    bags_count = 2
    return_flight = False
    import pandas as pd
    df = pd.read_csv(csv_path)
else:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        help='Provide path to the csv with flights data.'
        )
    parser.add_argument(
        'origin',
        help='Provide origin aka the place from which one departs.'
        )
    parser.add_argument(
        'destination',
        help='Provide destination aka the place to which one wants to arrive.'
        )
    parser.add_argument(
        "--bags",
        dest="bags",
        default=0,
        type=int
        )
    parser.add_argument(
        "--return",
        dest="return_flight",
        nargs='?',
        default=False,
        type=bool
        )

    args = parser.parse_args()
    csv_path = args.path
    origin = args.origin
    destination = args.destination
    bags_count = args.bags
    return_flight = args.return_flight
    
def input_validation(csv_path, bags_count):
    # validate the input from the user
    # to be more specific, check if the file under 'csv_path' exists and contain valid columns
    # also try to make an integer from 'bags_count'
    # raise errors if needed
    
    try:
        with open(csv_path) as f:
            expected_columns = ['flight_no','origin','destination','departure','arrival','base_price','bag_price','bags_allowed']
            clmns_in_file = next(csv.reader(f)) 
            tst = clmns_in_file == expected_columns
            if not tst:
                raise Exception('The csv file does not seem to contain the expected columns. Expected columns: {}. Columns found in the file: {}'\
                                .format(', '.join(expected_columns), ', '.join(clmns_in_file)))

        int(bags_count)
    except OSError:
        print("The path to the csv file does not seem to exist. Inserted path: {}".format(csv_path))
    except ValueError:
        print("The input for 'bags_count' does not seem to be a valid integer number. Inserted value: {}".format(bags_count))
    else:
        return True

def readin_csv(csv_path):
    # reads in the csv file as a dictionary
    # some datatypes are changed
    # unique id column added
    # departer and arrival times are transformed to number of seconds after 1970-01-01 and added as additional columns
    
    with open(csv_path) as f:
        reader = csv.reader(f)
        clms = next(reader)
        dct = {k: [] for k in clms}
        for row in reader:
            for index, itm in enumerate(row):
                dct[clms[index]].append(itm)
    
    dct['bag_price'] = [int(itm) for itm in dct['bag_price']]
    dct['bags_allowed'] = [int(itm) for itm in dct['bags_allowed']]
    dct['base_price'] = [float(itm) for itm in dct['base_price']]  
    dct['unique_id'] = [i for i, val in enumerate(dct['flight_no'])]
    dct['departure_timestamp'] = [datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S").timestamp() for i in dct['departure']]
    dct['arrival_timestamp'] = [datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S").timestamp() for i in dct['arrival']]
                
    return dct

def first_run(dct_input, origin, destination, bags_count):
    # this function uses dct_input with flights and performs the search for the first segment of the flight
    # the search means checking if conditions such as origin or number of bags are met
    # if the flight from the origin reaches the destination directly, such a flight is added to the 'completed_flights' list
    # if the flight from the origin does not reach the destination, it goes to the 'flghts_in_progress' list
    
    completed_flghts = list()
    flghts_in_progress = list()
    
    for i in dct_input['unique_id']:        
            right_origin = dct_input['origin'][i] == origin
            right_destination = dct_input['destination'][i] == destination
            right_bags_count = dct_input['bags_allowed'][i] >= bags_count
            
            if right_origin and right_destination and right_bags_count:
                completed_flghts.append([dct_input['unique_id'][i]])
            elif right_origin and not right_destination and right_bags_count:
                flghts_in_progress.append([dct_input['unique_id'][i]])
    
    return [completed_flghts, flghts_in_progress]

def following_runs(dct_input, origin, destination, bags_count, completed_flghts, flghts_in_progress):
    # this function, similarly to the 'first_run' function, searches the 'dct_input' for possible flights that meet the conditions
    # there are further checks performed (e.g. if there are not repeating airports in the journey) or if the connecting flights departs within 1 hour and 6 hours
    # journeys that reach the intended destination, goes to the completed_flghts list and the ones that are in progress and still have potential to reach the final destionation
    # goes to imd_flghts_in_progress
    # if there are still some flights in the imd_flghts_in_progress list, following_runs function is called recursively with updated imd_flghts_in_progress and completed_flghts
    # the search continues until there are still some possible flights
    # if there are not, completed_flghts list is returned
    
    imd_flghts_in_progress = list()
    for flgths_lst in flghts_in_progress:
        ii = flgths_lst[-1]
        for i in dct_input['unique_id']:
            no_repeating_flights =  not any([dct_input['destination'][i] == dct_input['destination'][flght] for flght in flgths_lst])
            no_return_to_origin = dct_input['destination'][i] != origin
            right_origin = dct_input['origin'][i] == dct_input['destination'][ii]
            right_departure_dt = dct_input['departure_timestamp'][i] >= (dct_input['arrival_timestamp'][ii] + 1*60)
            right_departure_dt = right_departure_dt and dct_input['departure_timestamp'][i] <= (dct_input['arrival_timestamp'][ii] + 6*60*60)
            right_destination = dct_input['destination'][i] == destination
            right_bags_count = dct_input['bags_allowed'][i] >= bags_count
            
            if no_repeating_flights and no_return_to_origin and right_origin and right_departure_dt and right_destination and right_bags_count:
                completed_flghts.append(flgths_lst + [dct_input['unique_id'][i]]) # remove from in progress add to the imd_cimpleted_flights the WHOLE  trip
            elif no_repeating_flights and no_return_to_origin and right_origin and right_departure_dt and not right_destination and right_bags_count:
                imd_flghts_in_progress.append(flgths_lst + [dct_input['unique_id'][i]])
    
    if imd_flghts_in_progress:
        return following_runs(dct_input, origin, destination, bags_count, completed_flghts, imd_flghts_in_progress)
    else:
        return completed_flghts

def json_output(dct_input, for_json, origin, destination, bags_count):
    # this function uses possible journeys represented as unique ids of flights
    # it transfers important information into json-like structure
    # json-like structure is returned even if there are no flights found
    
    # if no flights were found, an empty json is returned
    if not for_json['there']:
        ordered_json_out = [{
                "flights": [],
                "bags_allowed": 0,
                "bags_count": bags_count,
                "destination": destination,
                "origin": origin,
                "total_price": 0,
                "travel_time": ''
            }]
        
    # some flights have been found, therefore, json is to be prepared
    else:
        json_out = []
        ordering_total_price = []
        # looping through zipped segments for 'there' (i.e. travel segment from origin to destination) and 'back' (i.e. travel segment from destination to origin)
        for itm in zip(for_json['there'], for_json['back']):
            
            flights = list() # list of dictionaries with individual flights for segment 'there' and 'back'
            bags_allowed = list()
            total_price = list()
            travel_time = list()
            # if it is a return flight, the time spent at the destination is not to be included
            # it is first calculated. and subtracted later on
            if itm[1]:
                time_spent_at_destination = dct_input["departure_timestamp"][itm[1][0]] - dct_input["arrival_timestamp"][itm[0][-1]] 
            # this is for one-way trip
            else:
                time_spent_at_destination = 0
            
            for flgth_id in itm[0] + itm[1]: # itm[0] is flight segment 'there' and itm[1] is the flight segment 'back'
                # creating dictionaries for each flight
                flights.append({
                    "flight_no": dct_input["flight_no"][flgth_id],
                    "origin": dct_input["origin"][flgth_id],
                    "destination": dct_input["destination"][flgth_id],
                    "departure": dct_input["departure"][flgth_id],
                    "arrival": dct_input["arrival"][flgth_id],
                    "base_price": dct_input["base_price"][flgth_id],
                    "bag_price": dct_input["bag_price"][flgth_id],
                    "bags_allowed": dct_input["bags_allowed"][flgth_id]
                    })
                # creating lists combining information on, for example, number of bags allowed, for each flight
                bags_allowed.append(dct_input["bags_allowed"][flgth_id])
                total_price.append(dct_input["base_price"][flgth_id] + bags_count*dct_input["bag_price"][flgth_id])
                travel_time.append(dct_input["departure_timestamp"][flgth_id])
                travel_time.append(dct_input["arrival_timestamp"][flgth_id])
            
            # final Python structure that will be eventually used to create json
            json_out.append({
                "flights": flights,
                "bags_allowed": min(bags_allowed),
                "bags_count": bags_count,
                "destination": destination,
                "origin": origin,
                "total_price": sum(total_price),
                "travel_time": str(datetime.timedelta(seconds=travel_time[-1] - travel_time[0] - time_spent_at_destination))
                })
            # list of prices corresponding to each journey - used for ordering
            ordering_total_price.append(sum(total_price))
            
            # ordering the list so that the cheapest flight appears first 
            ordered_json_out = [x for (y,x) in sorted(zip(ordering_total_price,json_out), key=lambda pair: pair[0])]

    return json.dumps(ordered_json_out, indent=3)
            
def MAIN_find_flights(csv_path, origin, destination, bags_count, return_flight):
    # this is the workhorse function for flight search
    # it validates the input and reads in the csv file
    # subsequently, it performs search for flights to get from origin to destination
    # after that, it finds flights to get from destination to origin
    # flight segments 'from origin to destination' are combined with 'from destination to origin'
    # only flights where return happens after arrival are included
    # finally, a json summarizing possible journeys is created
    
    if input_validation(csv_path, bags_count):
            
        dct_input = readin_csv(csv_path)
        
        first_run_res = first_run(dct_input, origin, destination, bags_count)
        following_runs_res = following_runs(dct_input, origin, destination, bags_count, first_run_res[0], first_run_res[1])
        
        if return_flight:
            returnf_first_run_res = first_run(dct_input=dct_input, origin=destination, destination=origin, bags_count=bags_count)
            returnf_following_runs_res = following_runs(dct_input, destination, origin, bags_count, returnf_first_run_res[0], returnf_first_run_res[1])
            
            for_json = {'there':[], 'back': []}
            for i, itm in enumerate(following_runs_res):
                for j, itm2 in enumerate(returnf_following_runs_res):
                    if dct_input['arrival_timestamp'][itm[-1]] < dct_input['departure_timestamp'][itm2[0]]:
                        for_json['there'].append(itm) 
                        for_json['back'].append(itm2)
        else:
            for_json = {'there': following_runs_res, 'back': [[] for _ in range(len(following_runs_res))]}
        
        return json_output(dct_input, for_json, origin, destination, bags_count)
    else:
        return ''

json_out = MAIN_find_flights(csv_path, origin, destination, bags_count, return_flight)

print(json_out)
