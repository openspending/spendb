import datetime
from pylons import app_globals
from openspending.reference import country
import logging
log = logging.getLogger(__name__)

def get_value(key, item):
    """
    Get value of key in an item dict where it can be nested with . as a
    separator. This should really be solved using a specific data structure
    common to all aggregation results
    """

    # Split the key to get all possible keys and subkeys
    keys = key.split('.')

    # Loop through and replace item with the result of the key
    for split_key in keys:
        item = item[split_key]

    # Item now contains the the value of key/subkey in item
    return item

def remove_excessive_time(keys, item):
    """
    Checks for time.year in keys and if not present deletes either time.year
    or time (if no time variable is present)
    """

    try:
        # First we check if there is no time at all in the keys and delete
        # time from item (and break out early since the next text would raise
        # a KeyError
        if 'time' not in [k.split('.')[0] for k in keys]:
            del item['time']
            return item
        
        # Delete only year if time.year is not in keys (this happens in the
        # rare case that a user drills down into time.month to compare months
        # and not years (or something similar)
        if 'time.year' not in keys:
            del item['time']['year']
    except KeyError:
        # We do nothing if a key error is raised (then time or its subitem
        # year didn't exist
        pass

    return item

def aggregate(dataset, measures=['amount'], drilldowns=None, cuts=None,
              page=1, pagesize=10000, order=None, inflate=None):
    """
    Do an aggregation over a single dataset. This method calls the aggregation
    method of the dataset but in case inflation is asked for, this method takes
    care of those computations
    """

    # If we have to inflate we need to add a year to the drilldowns 
    # (since inflation only supports years at the moment).
    if inflate:
        drilldowns.append('time.year')

    # Aggregate the dataset via its own aggregate function
    result = dataset.aggregate(measures=measures, drilldowns=drilldowns,
                               cuts=cuts, page=page,pagesize=pagesize,
                               order=order)

    # If we have to inflate we do some inflation calculations
    if inflate:
        try:
            # Get a datetime object for the year
            target_year = datetime.date(int(inflate[:4]), 1, 1)
            # Since different parts of the drilldowns are going to change
            # (differently) we need to recompute the sumamry total
            summary_total = 0
        
            # We collect adjusted drilldowns into a new dict since if
            # inflation fails we can still serve the uninflated content
            adjusted_drilldowns = {}
            # We remove the time.year we added to the drilldowns
            hash_key = drilldowns[:]
            hash_key.remove('time.year')

            # Lookup the country we're going to inflate for
            # This only checks for the first country in the dataset's
            # territories (which might cause errors)
            dataset_country = country.COUNTRIES.get(dataset.territories[0])
            for item in result['drilldown']:
                # Get the inflated amount for this year
                inflated_amount = app_globals.inflation.inflate(
                    item['amount'], target_year,
                    datetime.date(int(item['time']['year']),1,1),
                    country=dataset_country)
                # Get the inflation adjustment
                adjustment = {'original': item['amount'],
                              'inflated': inflated_amount,
                              'target': target_year.year,
                              'reference': int(item['time']['year'])}

                # Get the item key
                item_key = tuple([get_value(k, item) for k in hash_key])
                if item_key not in adjusted_drilldowns:
                    # We copy the item in case something happens (then we
                    # catch it and serve the original aggregation result)
                    adjusted_drilldown = item.copy()
                    remove_excessive_time(hash_key, adjusted_drilldown)
                    adjusted_drilldown['inflation_adjustment'] = [adjustment]
                    adjusted_drilldown['amount'] = inflated_amount
                    adjusted_drilldowns[item_key] = adjusted_drilldown
                else:
                    adjusted_drilldowns[item_key]['inflation_adjustment']\
                        .append(adjustment)
                    adjust_drilldowns[item_key]['amount'] += inflated_amount

                summary_total += inflated_amount
            
            result['drilldown'] = adjusted_drilldowns.values()
            result['summary']['origin'] = result['summary']['amount']
            result['summary']['amount'] = summary_total
        except KeyError, error:
            # If inflation fails because a date wasn't found in the inflation
            # data, then it raises a KeyError (returning the date in the
            # exception message

            # Note we do not remove time.year from the drilldown here since
            # it can help resolve the warning (and it's bothersome)
            result['warning'] = {'inflation':
                                     'Unable to do inflation adjustment',
                                 'error': error.message}

    return result



