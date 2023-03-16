from vacations.models import Collaborator


def calculate_days(collaborator_id = None):
    """Summary

    Calculate available days of vacations for all collaborators

    Returns:
        TYPE: Description
    """

    if collaborator_id:
        sql_where = f'WHERE col.id = {collaborator_id}'

    else:
        sql_where = ''


    # collaborators = Collaborator.objects.raw(
    #     '''
    #     SELECT
    #         col.id,
    #         (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) AS days_vacations,
    #         COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0) AS days_taken,
    #         SUM(CASE WHEN bon.bonus_state THEN bon.extra_days ELSE 0 END) AS days_extra,
    #         (
    #             (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) +
    #             SUM(CASE WHEN bon.bonus_state THEN bon.extra_days ELSE 0 END) -
    #             COALESCE(SUM(CASE WHEN req.request_completed THEN req.business_days_taken ELSE 0 END), 0)
    #         ) AS days_available
    #     FROM vacations_collaborator AS col
    #     LEFT JOIN vacations_requests AS req ON req.collaborator_id = col.id
    #     LEFT JOIN vacations_bonus AS bon ON bon.collaborator_id = col.id
    #     {}
    #     GROUP BY col.id;
    #     '''.format(sql_where)
    # )

    collaborators = Collaborator.objects.raw(
        '''
        SELECT
            col.id,
            (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) AS days_vacations,
            (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) AS days_extra,
            (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE) AS days_taken,
            (
                (15::NUMERIC / 365) * (now()::DATE - entry_at::DATE) +
                (SELECT COALESCE(SUM(vacations_bonus.extra_days), 0) FROM vacations_bonus WHERE vacations_bonus.collaborator_id = col.id) -
                (SELECT COALESCE(SUM(vacations_requests.business_days_taken), 0) FROM vacations_requests WHERE vacations_requests.collaborator_id = col.id AND vacations_requests.request_completed = TRUE)
            ) AS days_available
        FROM vacations_collaborator AS col
        {};
        '''.format(sql_where)
    )

    return collaborators
