from datetime import timedelta
import holidays_co

def calculate_days_taken(start_date, end_date):


    # Get date holidays days to take
    #   Get range of years from vacation period
    total_holidays = list()
    for year in set([start_date.year, end_date.year]):
        total_holidays.extend(holidays_co.get_colombia_holidays_by_year(year))

    total_holidays = list(set(total_holidays))

    #   Get holidays days in range
    def in_range(holiday_date, start_date, end_date):
        return (holiday_date > start_date) and (holiday_date < end_date)

    apply_holydays = [holiday[0] for holiday in total_holidays if in_range(holiday[0], start_date, end_date)]


    # Calculate calendar days to take, we add 1 for take the day from last day
    calendar_days = (end_date - start_date).days + 1


    # Calculate business days to take
    date_calendar_days = [start_date + timedelta(days=i) for i in range(calendar_days)]

    #   subtract week days and holydays that normally are business days
    business_days = len([calendar_day for calendar_day in date_calendar_days 
                            if (calendar_day.weekday() < 5) and (not calendar_day in apply_holydays)])

    return calendar_days, business_days
