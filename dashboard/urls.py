from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from dashboard.views import (
    login,
    logout,
    dashboard_change_password,
    add_admin,
    edit_admin,
    get_admins,
    get_dashboard_profile,
    edit_dashboard_profile,
    reset_admin_password,
    get_access_list,
    get_access_groups,
    edit_access_groups,
    add_access_group,
    add_provider,
    edit_provider,
    get_providers,
    delete_provider,
    get_most_visited_contents,
    get_all_contents,
    edit_content,
    get_excel,
    get_chart_date,
    get_total_traffic

)

urls = {
    'login': login,
    'logout': logout,
    # TODO check these content management apis
    'getAllContents': get_all_contents,
    'editContent': edit_content,
    'getExcel': get_excel,
    # TODO check these profile page apis
    'addProvider': add_provider,
    'addAdmin': add_admin,
    'dashboardChangePassword': dashboard_change_password,
    'getProviders': get_providers,
    'deleteProvider': delete_provider,
    # chart
    'getChartData': get_chart_date,
    'getTotalTraffic': get_total_traffic,
    # 'editAdmin': edit_admin,
    # 'getAdmins': get_admins,
    # 'getDashboardProfile': get_dashboard_profile,
    # 'editDashboardProfile': edit_dashboard_profile,
    # 'ResetAdminPassword': reset_admin_password,
    # 'getAccessList': get_access_list,
    # 'getAccessGroups': get_access_groups,
    # 'editAccessGroups': edit_access_groups,
    # 'addAccessGroup': add_access_group,
    # 'editProvider': edit_provider,
    # ##########################
    # new content loading page
    # traffic page
    # content age
    # most visited page
    # 'getMostVisitedContents': get_most_visited_contents,

}


@api_view(http_method_names=['POST'])
def dashboard_routing(request, *args, **kwargs):
    return urls[request.api_method](request, *args, **kwargs)
    # if request.api_method not in urls.keys():
    #     return not_found(request, *args, **kwargs)
    # try:
    #     return urls[request.api_method](request, *args, **kwargs)
    # except Exception as e:
    #     return Response(status=status.HTTP_409_CONFLICT)


def not_found(request, *args, **kwargs):
    return Response(status=status.HTTP_404_NOT_FOUND)
