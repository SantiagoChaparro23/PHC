import datetime

from django.db import connection
from django.shortcuts import render

from record_business_interactions.models import VisitRecord, InteractionType, Settings



def query(request):

    # Select query parameters
    #   Select input date or current date by default
    query_business_manager = request.POST.get('business_manager', None)
    query_client = request.POST.get('client', None)
    query_date = request.POST.get('date', None)


    # Take data and casting
    query_business_manager = None if query_business_manager is None else int(query_business_manager)
    query_client = None if query_client is None else int(query_client)

    
    if not query_date is None:
        year, month = query_date.split('-')
    
    else:
        today = datetime.date.today()
        year, month = today.year, today.month


    # Get list of names of business managers
    query = '''
        SELECT DISTINCT(user_id), auth_user.first_name || ' ' || auth_user.last_name AS name_user
               
        FROM record_business_interactions_visitrecord 

        INNER JOIN auth_user
        ON auth_user.id = record_business_interactions_visitrecord.user_id

        ORDER BY name_user

    '''

    cursor = connection.cursor()
    cursor.execute(query)

    #       Third element is used for selected option after execute a query
    business_managers = [(row[0], row[1], row[0]==query_business_manager) for row in cursor.fetchall()]
    #           This option will be used for see a sum from all business managers
    business_managers.insert(0, (-1, '– todos -'))


    # Get list of clients
    query = '''
        SELECT DISTINCT(client_id), client
               
        FROM record_business_interactions_visitrecord 

        INNER JOIN budgeted_hours_client
        ON budgeted_hours_client.id = record_business_interactions_visitrecord.client_id

        ORDER BY client

    '''

    cursor = connection.cursor()
    cursor.execute(query)

    clients = cursor.fetchall()
    clients.insert(0, (-1, ''))

    #       Third element is used for selected option after execute a query
    clients = [(row[0], row[1], row[0]==query_client) for row in clients]


    # Get query data from visit records
    print('query_business_manager: ', query_business_manager, type(query_business_manager))
    if not query_business_manager is None:
        #   This and depend from if a client are in the input
        # if query_business_manager 
        line_client = f"AND client_id = {query_client}" if (query_client != -1) and (query_client != None) else ''

        line_buss_man = f"AND user_id = {query_business_manager}" if (query_business_manager != -1) else ''

        query = f'''
            SELECT date_record,  
                   date_visit, 
                   phc_code, 
                   client, 
                   record_business_interactions_interactiontype.name,
                   customer_commitments,
                   is_in_crm,
                   validated_in_crm
                   
            FROM record_business_interactions_visitrecord 

            INNER JOIN budgeted_hours_client
            ON budgeted_hours_client.id = record_business_interactions_visitrecord.client_id

            INNER JOIN auth_user
            ON auth_user.id = record_business_interactions_visitrecord.user_id

            INNER JOIN record_business_interactions_interactiontype
            ON record_business_interactions_interactiontype.id = record_business_interactions_visitrecord.interaction_type_id

            WHERE EXTRACT(MONTH FROM date_visit) = {month}
            AND EXTRACT(YEAR FROM date_visit) = {year}

            {line_buss_man}

            {line_client}

            ORDER BY date_visit
        '''
       
        cursor = connection.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

        # Calculate help numbers
        goal_amount_of_visits = int(Settings.objects.filter(key='goal_amount_of_visits')[0].value)
        validated_interactions  = sum(1 for row in results if row[7])
        goal_fulfillment = validated_interactions/goal_amount_of_visits

    else:

        results = []

        # Calculate help numbers
        goal_amount_of_visits = int(Settings.objects.filter(key='goal_amount_of_visits')[0].value)
        validated_interactions  = ''
        goal_fulfillment = ''


    context = {
        'business_managers': business_managers,
        'clients' : clients,
        'year': year,
        'month': month,
        'results': results,

        'goal_amount_of_visits': goal_amount_of_visits,
        'goal_fulfillment': goal_fulfillment,
        'validated_interactions': validated_interactions 
    }

    return render(request,'query/query.html', context)